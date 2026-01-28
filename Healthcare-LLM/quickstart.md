# 🚀 Quick Start Guide

## Get Running in 5 Minutes

### Step 1: Get OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create a new secret key
3. Copy it (you won't see it again!)

### Step 2: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install everything
pip install -r requirements.txt

# Install Tesseract OCR
# macOS: brew install tesseract
# Ubuntu: sudo apt-get install tesseract-ocr
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
```

### Step 3: Configure API Key

```bash
# Copy environment template
cp .env.example .env

# Edit and add your key
nano .env
```

Add this line:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 4: Run the Server

```bash
uvicorn app.main:app --reload
```

✅ **Server running at http://localhost:8000**
✅ **API Docs at http://localhost:8000/docs**

### Step 5: Test It!

#### Option A: Use the Interactive Docs
1. Open http://localhost:8000/docs
2. Click on "POST /api/analyze"
3. Click "Try it out"
4. Upload `data/sample_reports/blood_test_sample.txt`
5. Click "Execute"

#### Option B: Use curl
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/sample_reports/blood_test_sample.txt"
```

#### Option C: Use Python
```python
import requests

with open('data/sample_reports/blood_test_sample.txt', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/analyze',
        files={'file': f}
    )
    print(response.json()['patient_friendly_summary'])
```

## 🎯 API Endpoints Quick Reference

### 1. Analyze Report
```bash
POST /api/analyze
Content-Type: multipart/form-data

# Upload any medical report (PDF, TXT, PNG, JPG)
```

### 2. Chat
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "What does high cholesterol mean?",
  "context": "optional report text"
}
```

### 3. Explain Term
```bash
POST /api/explain-term?term=hemoglobin
```

### 4. Compare Reports
```bash
POST /api/compare-reports
Content-Type: multipart/form-data

# Upload two reports to compare
```

## 📊 Test with Sample Data

The `data/sample_reports/` folder has test files:

```bash
# Test blood test analysis
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@data/sample_reports/blood_test_sample.txt"

# Test chat
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is cholesterol?"}'

# Test term explanation
curl -X POST "http://localhost:8000/api/explain-term?term=LDL"
```

## 🐛 Troubleshooting

### "ModuleNotFoundError"
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "OpenAI API error"
```bash
# Check your API key is set
cat .env | grep OPENAI_API_KEY

# Test the key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer sk-your-key-here"
```

### "Tesseract not found"
```bash
# Install Tesseract OCR
# macOS:
brew install tesseract

# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# Windows:
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### Port already in use
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

## 💡 Next Steps

1. **Test all endpoints** using the docs at http://localhost:8000/docs
2. **Try your own reports** - upload real medical reports (remember to remove personal info!)
3. **Customize prompts** - edit `app/utils/prompts.py` to change how the AI responds
4. **Add features** - extend the API with new endpoints
5. **Deploy** - push to Heroku, Railway, or your cloud provider

## 📝 For Your Resume

**One-line description:**
"FastAPI backend with OpenAI GPT-4 integration for medical report analysis and patient Q&A"

**Key technologies:**
Python, FastAPI, OpenAI API, LangChain, PyPDF2, Tesseract OCR, Pydantic

**GitHub README should show:**
- Clear installation steps ✓
- API endpoint examples ✓
- Code samples ✓
- Sample data for testing ✓

## 🚀 Deploy This

### Quick Deploy to Heroku
```bash
# Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

# Create Procfile
echo "web: uvicorn app.main:app --host=0.0.0.0 --port=\$PORT" > Procfile

# Deploy
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your-key
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

### Quick Deploy to Railway
```bash
# Install Railway CLI: https://docs.railway.app/develop/cli

railway login
railway init
railway up
railway variables set OPENAI_API_KEY=your-key
```

## ✅ You're Done!

You now have a working healthcare LLM API that you can:
- Show in interviews
- Add to your portfolio
- Deploy online
- Extend with new features
- Use as reference for other projects

**Cost:** ~$0.001-0.003 per analysis with GPT-4o-mini

Good luck! 🎉
