# Complete API & SDK Setup Guide for Appoint Project
## Getting Access to Gemini Live API, Google Cloud, and All Required Tools

---

## STEP 1: Google Cloud Platform Setup

### 1.1 Create Google Cloud Account
1. Go to: https://cloud.google.com/
2. Click "Get started for free" or "Console" (top right)
3. Sign in with your Google account (or create one)
4. You'll get **$300 free credits** for 90 days (new users)

### 1.2 Create a New Project
1. Go to: https://console.cloud.google.com/
2. Click the project dropdown (top left, next to "Google Cloud")
3. Click "NEW PROJECT"
4. Enter project name: `appoint-healthcare-agent`
5. Click "CREATE"
6. Wait for project creation, then select it

### 1.3 Enable Billing
1. Go to: https://console.cloud.google.com/billing
2. Link a billing account (required even for free tier)
3. Add payment method (won't be charged if you stay within free limits)
4. **For hackathon credits:** Fill this form by March 13: https://forms.gle/rKNPXA1o6XADvQGb7
   - Request $100 Google Cloud credits
   - Approval within 72 business hours

---

## STEP 2: Enable Required APIs

### 2.1 Enable Gemini API (Vertex AI)
1. Go to: https://console.cloud.google.com/apis/library
2. Search for "Vertex AI API"
3. Click on it, then click "ENABLE"
4. Wait for activation (takes 1-2 minutes)

### 2.2 Enable Other Required APIs
Enable these APIs the same way:

- **Cloud Run API** (for deployment)
- **Cloud Functions API** (alternative deployment)
- **Cloud Storage API** (for storing data)
- **Firestore API** (for database)
- **Cloud Vision API** (for image analysis)
- **Cloud Speech-to-Text API** (if needed)
- **Cloud Text-to-Speech API** (if needed)

Quick way: Go to https://console.cloud.google.com/apis/dashboard and enable all at once

---

## STEP 3: Get API Keys & Credentials

### 3.1 Create API Key (Simple Method)
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "CREATE CREDENTIALS" → "API key"
3. Copy the API key immediately
4. Click "RESTRICT KEY" (recommended):
   - Under "API restrictions", select "Restrict key"
   - Choose: Vertex AI API, Cloud Vision API, etc.
   - Click "SAVE"

### 3.2 Create Service Account (Recommended for Production)
1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click "CREATE SERVICE ACCOUNT"
3. Name: `appoint-service-account`
4. Click "CREATE AND CONTINUE"
5. Grant roles:
   - Vertex AI User
   - Cloud Run Admin
   - Storage Admin
   - Firestore User
6. Click "DONE"
7. Click on the service account you just created
8. Go to "KEYS" tab
9. Click "ADD KEY" → "Create new key"
10. Choose "JSON"
11. Download the JSON file (keep it safe!)

---

## STEP 4: Install Google Cloud SDK & Tools

### 4.1 Install Google Cloud CLI
**Windows:**
```cmd
# Download installer from:
https://cloud.google.com/sdk/docs/install

# Or use PowerShell:
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

**After installation:**
```cmd
gcloud init
gcloud auth login
gcloud config set project appoint-healthcare-agent
```

### 4.2 Install Python & Required Libraries
```cmd
# Check Python version (need 3.8+)
python --version

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install Google AI SDK
pip install google-generativeai
pip install google-cloud-aiplatform
pip install google-cloud-vision
pip install google-cloud-storage
pip install google-cloud-firestore
```

---

## STEP 5: Gemini API Access

### 5.1 Get Gemini API Key (AI Studio - Easiest)
1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Select your Google Cloud project: `appoint-healthcare-agent`
5. Copy the API key

### 5.2 Test Gemini API
Create a test file `test_gemini.py`:
```python
import google.generativeai as genai

# Configure API key
genai.configure(api_key="YOUR_API_KEY_HERE")

# Test basic text generation
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Hello, how are you?")
print(response.text)
```

Run:
```cmd
python test_gemini.py
```

---

## STEP 6: Gemini Live API Setup (Bidirectional Streaming)

### 6.1 Install ADK (Agent Development Kit)
```cmd
pip install google-genai
```

### 6.2 Test Live API
Create `test_live_api.py`:
```python
from google import genai

client = genai.Client(api_key="YOUR_API_KEY_HERE")

# Test live session
response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents='Tell me about healthcare',
)
print(response.text)
```

### 6.3 For Real-time Audio Streaming
Check official examples:
- https://github.com/google-gemini/cookbook
- Look for "live_api" or "bidirectional_streaming" examples

---

## STEP 7: Vision API Setup (Camera Symptom Analysis)

### 7.1 Test Vision API
Create `test_vision.py`:
```python
import google.generativeai as genai
from PIL import Image

genai.configure(api_key="YOUR_API_KEY_HERE")

# Load image
img = Image.open('test_symptom.jpg')

# Analyze with Gemini Vision
model = genai.GenerativeModel('gemini-pro-vision')
response = model.generate_content([
    "Describe any visible medical symptoms in this image",
    img
])
print(response.text)
```

---

## STEP 8: Portal Automation Setup

### 8.1 Install Playwright
```cmd
pip install playwright
playwright install
```

### 8.2 Test Automation
Create `test_automation.py`:
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://example-hospital.com")
    # Add your automation logic
    browser.close()
```

---

## STEP 9: Environment Variables Setup

### 9.1 Create `.env` File
```env
GOOGLE_CLOUD_PROJECT=appoint-healthcare-agent
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
```

### 9.2 Install python-dotenv
```cmd
pip install python-dotenv
```

### 9.3 Load in Your Code
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
```

---

## STEP 10: Project Structure Setup

Create this folder structure:
```
appoint-healthcare-agent/
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── src/
│   ├── voice_handler.py
│   ├── symptom_analyzer.py
│   ├── vision_handler.py
│   ├── language_handler.py
│   ├── recommender.py
│   └── automation_agent.py
├── tests/
│   └── test_*.py
└── config/
    └── service-account-key.json
```

---

## STEP 11: Create requirements.txt

```txt
google-generativeai>=0.3.0
google-cloud-aiplatform>=1.38.0
google-cloud-vision>=3.4.0
google-cloud-storage>=2.10.0
google-cloud-firestore>=2.13.0
google-genai>=0.1.0
playwright>=1.40.0
python-dotenv>=1.0.0
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
```

Install all:
```cmd
pip install -r requirements.txt
```

---

## QUICK START CHECKLIST

- [ ] Google Cloud account created
- [ ] Project created: `appoint-healthcare-agent`
- [ ] Billing enabled (free tier or hackathon credits)
- [ ] Vertex AI API enabled
- [ ] Gemini API key obtained from AI Studio
- [ ] Service account created & JSON key downloaded
- [ ] Google Cloud CLI installed & authenticated
- [ ] Python environment set up
- [ ] All required libraries installed
- [ ] `.env` file created with API keys
- [ ] Test scripts run successfully

---

## IMPORTANT LINKS

- **Google Cloud Console:** https://console.cloud.google.com/
- **AI Studio (API Keys):** https://aistudio.google.com/app/apikey
- **Vertex AI:** https://console.cloud.google.com/vertex-ai
- **Gemini Cookbook:** https://github.com/google-gemini/cookbook
- **ADK Documentation:** https://ai.google.dev/gemini-api/docs/adk
- **Hackathon Credits Form:** https://forms.gle/rKNPXA1o6XADvQGb7
- **Free Trial:** https://cloud.google.com/free

---

## TROUBLESHOOTING

### Issue: "API not enabled"
**Solution:** Go to APIs & Services → Enable the specific API

### Issue: "Quota exceeded"
**Solution:** Check billing, request hackathon credits, or upgrade plan

### Issue: "Authentication failed"
**Solution:** Run `gcloud auth application-default login`

### Issue: "Module not found"
**Solution:** Activate virtual environment: `venv\Scripts\activate`

---

## SECURITY BEST PRACTICES

1. **Never commit API keys to GitHub**
   - Add `.env` to `.gitignore`
   - Add `config/*.json` to `.gitignore`

2. **Use environment variables**
   - Store all secrets in `.env`
   - Load with `python-dotenv`

3. **Restrict API keys**
   - Limit to specific APIs
   - Set usage quotas

4. **Use service accounts for production**
   - More secure than API keys
   - Better access control

---

**You're all set! Start with Step 1 and work through each step. Most steps take 5-10 minutes.**
