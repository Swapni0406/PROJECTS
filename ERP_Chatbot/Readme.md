# ERP Chatbot (Public Demo Version)

A Flask-based AI-powered ERP chatbot that integrates with any ERP backend using GPT for intent recognition.

## 🚀 Features
- GPT-powered natural language intent detection
- Leave management and clock-in/out modules
- Modular and environment-based configuration
- Secure `.env` handling
- REST API endpoints for chatbot interaction

## 🧠 Endpoints
| Endpoint | Description |
|-----------|-------------|
| `/chat` | Main chatbot endpoint |
| `/nn_interface` | Shows conceptual neural network pipeline |
| `/health` | Health check |

## ⚙️ Setup
```bash
pip install -r requirements.txt
python app.py
```

## 🧩 Example Query
```json
{"message": "Apply sick leave from tomorrow to Friday due to fever"}
```
