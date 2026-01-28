import os
import json
import re
import calendar
import requests
import threading
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# ==============================================
#  Load environment variables
# ==============================================
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BACKEND_TOKEN = os.getenv("BACKEND_TOKEN")
LEAVE_BASE_URL = os.getenv("LEAVE_BASE_URL", "https://your-backend-url.com/api/model_new/save")
CLOCK_BASE_URL = os.getenv("CLOCK_BASE_URL", "https://your-backend-url.com/api/model/save")

app = Flask(__name__)
_sessions_lock = threading.Lock()
user_sessions = {}

# ==============================================
#  Authorization Helper
# ==============================================
def _auth_headers():
    return {"Authorization": f"Bearer {BACKEND_TOKEN}", "Content-Type": "application/json"}


# ==============================================
#  Short GPT Response Generator
# ==============================================
def get_openai_response(payload_data: dict, feature_name: str = "Request") -> str:
    """Summarize backend response or payload into a concise line."""
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    prompt = (
        f"You are an ERP chatbot. Summarize this {feature_name} in one short sentence "
        f"(max 14 words). Respond only with plain text.\n\n{json.dumps(payload_data, indent=2)}"
    )
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 40,
    }

    try:
        resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return f"{feature_name} processed."


# ==============================================
#  Intent + Entity Extraction Logic
# ==============================================
def normalize_relative_date(text, ref_date=None):
    """Convert relative dates like 'tomorrow' or 'next monday' into ISO format."""
    if not text:
        return None
    t = text.strip().lower()
    ref = ref_date or datetime.utcnow().date()

    if t in ("today",):
        return ref.isoformat()
    if t in ("tomorrow",):
        return (ref + timedelta(days=1)).isoformat()
    if t in ("day after tomorrow",):
        return (ref + timedelta(days=2)).isoformat()

    weekdays = {d.lower(): i for i, d in enumerate(calendar.day_name)}
    m = re.match(r"(next\s+)?(" + "|".join(weekdays.keys()) + r")", t)
    if m:
        next_word, weekday = m.groups()
        target_idx = weekdays[weekday]
        curr_idx = ref.weekday()
        days_ahead = (target_idx - curr_idx) % 7
        if days_ahead == 0 and next_word:
            days_ahead = 7
        return (ref + timedelta(days=days_ahead)).isoformat()

    iso_match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if iso_match:
        return iso_match.group(1)

    return None


def fallback_extract(ai_json, user_message):
    """Add missing intent-related fields using keyword-based fallback."""
    msg = user_message.lower()
    if ai_json.get("leave_type") in (None, "", "unknown"):
        if "sick" in msg:
            ai_json["leave_type"] = "sick"
        elif "casual" in msg:
            ai_json["leave_type"] = "casual"
    if ai_json.get("request_type") in (None, "", "unknown"):
        if "clock in" in msg:
            ai_json["request_type"] = "Clock-In"
        elif "clock out" in msg:
            ai_json["request_type"] = "Clock-Out"
    return ai_json


def analyze_user_message(user_message):
    """Use GPT to detect intent and extract relevant entities."""
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}

    few_shot_examples = """
    User: I need sick leave from 2025-10-10 to 2025-10-12 due to fever.
    JSON: {"intent":"apply_leave","leave_type":"sick","start_date":"2025-10-10","end_date":"2025-10-12","reason":"fever"}

    User: Please mark me clocked in today at 09:15 because I forgot to punch in.
    JSON: {"intent":"clock_in_out","request_type":"Clock-In","date":"today","time":"09:15","reason":"forgot to punch in"}

    User: Show my pending leaves
    JSON: {"intent":"view_leave_status"}
    """

    prompt = f"""
    You are an intent+entity extraction assistant for an ERP chatbot.
    Return a strict JSON object with the following possible keys:
    - intent (apply_leave, view_leave_status, clock_in_out, unknown)
    - leave_type
    - start_date
    - end_date
    - reason
    - date
    - time
    - request_type

    Examples:
    {few_shot_examples}

    User message: "{user_message}"
    JSON:
    """

    payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0, "max_tokens": 200}
    try:
        resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[Intent Extraction Error]: {e}")
        return {"intent": "unknown"}

    match = re.search(r"(\{.*\})", text, re.S)
    json_text = match.group(1) if match else text

    try:
        ai_data = json.loads(json_text)
    except Exception:
        ai_data = {"intent": "unknown"}

    # Normalize date/time and fill fallbacks
    for field in ["start_date", "end_date", "date"]:
        if ai_data.get(field):
            nd = normalize_relative_date(ai_data[field])
            ai_data[f"{field}_normalized"] = nd or ai_data[field]

    ai_data = fallback_extract(ai_data, user_message)
    return ai_data


# ==============================================
#  Module Handlers
# ==============================================
def handle_leave_auto(ai_data):
    """Apply leave automatically or ask for missing details."""
    leave_type = ai_data.get("leave_type")
    start_date = ai_data.get("start_date_normalized") or ai_data.get("start_date")
    end_date = ai_data.get("end_date_normalized") or ai_data.get("end_date")
    reason = ai_data.get("reason")

    missing = [f for f in ["leave_type", "start_date", "end_date", "reason"] if not ai_data.get(f)]
    if missing:
        return jsonify({"message": f"Please provide {', '.join(missing)} to apply for leave."})

    payload = {"leave_type": leave_type, "begin_date": start_date, "end_date": end_date, "reason": reason}
    try:
        resp = requests.post(f"{LEAVE_BASE_URL}/Leave", headers=_auth_headers(), json=payload, timeout=10)
        backend_data = resp.json()
    except Exception as e:
        backend_data = {"error": str(e)}

    summary = get_openai_response(payload, "Leave Request")
    return jsonify({"message": summary, "payload": payload, "backend_response": backend_data})


def handle_clock_auto(ai_data):
    """Clock in/out automatically or ask for missing details."""
    date = ai_data.get("date_normalized") or ai_data.get("date")
    time = ai_data.get("time")
    request_type = ai_data.get("request_type")
    reason = ai_data.get("reason")

    missing = [f for f in ["date", "time", "request_type", "reason"] if not ai_data.get(f)]
    if missing:
        return jsonify({"message": f"Please provide {', '.join(missing)} for clock request."})

    payload = {"date": date, "time": time, "request_type": request_type, "reason": reason}
    try:
        resp = requests.post(f"{CLOCK_BASE_URL}/ClockIn", headers=_auth_headers(), json=payload, timeout=10)
        backend_data = resp.json()
    except Exception as e:
        backend_data = {"error": str(e)}

    summary = get_openai_response(payload, "Clock Request")
    return jsonify({"message": summary, "payload": payload, "backend_response": backend_data})


# ==============================================
#  Chat Endpoint
# ==============================================
@app.route("/chat", methods=["POST"])
def chat_ai_router():
    data = request.get_json(force=True) or {}
    user_message = (data.get("message") or "").strip()
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    ai_data = analyze_user_message(user_message)
    intent = ai_data.get("intent", "unknown")

    if intent == "apply_leave":
        return handle_leave_auto(ai_data)
    elif intent == "view_leave_status":
        try:
            resp = requests.get(f"{LEAVE_BASE_URL}/Leave", headers=_auth_headers(), timeout=10)
            leaves = resp.json()
            summary = get_openai_response({"total_leaves": len(leaves)}, "Leave Status")
            return jsonify({"message": summary, "leaves": leaves})
        except Exception as e:
            return jsonify({"message": f"Error fetching leave status: {str(e)}"})
    elif intent == "clock_in_out":
        return handle_clock_auto(ai_data)
    else:
        return jsonify({"message": "Sorry, we don’t have this feature yet."})


# ==============================================
#  Neural Network Interface (Conceptual)
# ==============================================
@app.route("/nn_interface", methods=["GET"])
def neural_network_interface():
    nn_flow = {
        "input_layer": "User message embeddings",
        "hidden_layers": [
            "Transformer self-attention layers",
            "Feed-forward neural layers",
            "Residual + normalization layers"
        ],
        "output_layer": "Predicted intent + extracted entities",
        "model_used": "gpt-4o-mini (Transformer Neural Network)"
    }
    return jsonify(nn_flow)

#  Health Check
# ==============================================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
