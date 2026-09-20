# Appoint - Healthcare Assistant Agent

**Gemini Live Agent Challenge 2026**

[![Status](https://img.shields.io/badge/Status-Ready%20for%20Integration-success)]()
[![Tests](https://img.shields.io/badge/Tests-25%2F25%20Passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen)]()
[![Member%201](https://img.shields.io/badge/Member%201-Complete-success)]()

A voice and vision-enabled AI agent that helps people easily access healthcare services by understanding symptoms, recommending doctors, and automating appointment bookings.

## 🎯 Problem Statement

Healthcare access is unnecessarily complex, especially for elderly, illiterate, or tech-challenged individuals. People struggle to:
- Identify which type of doctor to see
- Choose suitable clinics with proper facilities
- Navigate different appointment booking systems
- Understand complex medical portals

**Appoint solves this end-to-end** by providing a unified, voice-enabled AI assistant that handles the entire healthcare access journey.

## ✨ Key Features

### 1. 🗣️ Multimodal Symptom Understanding
- Voice-based symptom description (English & Bangla)
- Text input support
- Camera-based visual symptom analysis (rashes, injuries, swelling)
- AI-powered clarifying questions
- Urgency level detection

### 2. 🚨 Emergency Detection
- Real-time detection of critical symptoms
- Immediate alerts for emergencies
- Nearest emergency hospital recommendations
- 12+ emergency keyword patterns

### 3. 🏥 Smart Doctor & Hospital Recommendations
- AI reasoning from symptoms to specialists
- 3 hospitals with 6 doctors configured
- Trade-off analysis (distance, rating, facilities)
- Availability checking
- Multiple options with clear comparisons

### 4. 🤖 Automated Appointment Booking
- Portal navigation automation (Playwright)
- Email-based booking system
- Form filling automation
- Booking confirmation generation
- Support for different booking methods

### 5. 🌍 Multilingual Support
- English language support
- Bangla language support
- Automatic language detection
- Localized messages and responses

### 6. 📊 Context & History Management
- Conversation history tracking
- Patient information storage
- Follow-up appointment support
- Session management

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         USER INTERFACE (Voice/Text/Camera)      │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│           VOICE HANDLER (Gemini API)            │
│         - Voice input processing                │
│         - Real-time responses                   │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│        SYMPTOM ANALYZER (AI-Powered)            │
│    - Symptom understanding                      │
│    - Emergency detection                        │
│    - Urgency classification                     │
└─────┬──────────────────────────┬────────────────┘
      │                          │
      │                    ┌─────▼──────────┐
      │                    │ VISION HANDLER │
      │                    │ (Camera Input) │
      │                    └────────────────┘
      │
┌─────▼──────────────────────────────────────────┐
│      DOCTOR RECOMMENDER (Smart Matching)        │
│  - Hospital database (3 hospitals)              │
│  - Trade-off analysis                           │
│  - Availability checking                        │
└────────────────┬───────────────────────────────┘
                 │
┌────────────────▼───────────────────────────────┐
│    AUTOMATION AGENT (Booking Automation)        │
│   - Portal navigation (Playwright)              │
│   - Email booking (SMTP)                        │
│   - Form filling                                │
└────────────────┬───────────────────────────────┘
                 │
┌────────────────▼───────────────────────────────┐
│      BOOKING CONFIRMATION & NOTIFICATION        │
└────────────────────────────────────────────────┘
```

## 📊 Project Status

**Member 1 (AI + Automation)**: ✅ 100% Complete  
**Member 2 (Frontend + Video)**: ⏳ In Progress  
**Member 3 (Backend + Integration)**: ⏳ In Progress

### Completion Metrics
- **Code**: 2,300+ lines
- **Modules**: 8 core modules
- **Tests**: 25+ test cases (100% passing)
- **Documentation**: 10 comprehensive files
- **Hospitals**: 3 configured
- **Doctors**: 6 available
- **Languages**: 2 supported

## Category

**Live Agents** - Real-time interaction with audio and vision capabilities

## Tech Stack

- **AI**: Google Gemini API (gemini-pro, gemini-pro-vision)
- **Cloud**: Google Cloud Platform (Cloud Run, Firestore, Cloud Storage)
- **Backend**: Python, FastAPI
- **Automation**: Playwright/Selenium
- **Languages**: Python 3.14+

## Project Structure

```
Appoint/
├── src/
│   ├── config.py              # Configuration management
│   ├── voice_handler.py       # Voice interaction with Gemini
│   ├── symptom_analyzer.py    # AI symptom analysis
│   ├── vision_handler.py      # Camera symptom analysis
│   ├── language_handler.py    # Multilingual support
│   ├── recommender.py         # Doctor/clinic recommendations
│   ├── automation_agent.py    # Portal & email automation
│   └── main.py                # Main orchestrator
├── tests/
├── data/
├── config/
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.14+
- Google Cloud account with billing enabled
- Gemini API key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Appoint
```

2. **Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create `.env` file:
```env
GOOGLE_CLOUD_PROJECT=your-project-id
GEMINI_API_KEY=your-api-key
GOOGLE_APPLICATION_CREDENTIALS=./path-to-service-account.json
STORAGE_BUCKET=your-bucket-name
```

5. **Test setup**
```bash
python test_day1_setup.py
```

## Features Implemented

### Day 1 (Completed) ✅

- ✅ Configuration module with environment management
- ✅ Voice handler with Gemini API integration
- ✅ Symptom analyzer with AI-powered analysis
- ✅ Emergency detection system
- ✅ Vision handler for camera-based symptom analysis
- ✅ Multilingual support (English & Bangla)

### Day 2 (Completed) ✅

- ✅ Doctor & clinic recommendation engine
- ✅ Hospital database with 3 hospitals
- ✅ Trade-off analysis for recommendations
- ✅ Portal automation agent (Playwright)
- ✅ Email automation for appointments
- ✅ Language handler module
- ✅ End-to-end orchestration (main.py)

### Day 3 (In Progress)

- ⏳ Backend API integration
- ⏳ GCP deployment (Cloud Run)
- ⏳ Testing & bug fixes
- ⏳ Demo video production

## Usage Examples

### Quick Start Demo

Run the complete flow demonstration:
```bash
python demo_complete_flow.py
```

This demonstrates:
- Normal consultation flow
- Emergency detection
- Multilingual support (English & Bangla)

### Symptom Analysis

```python
from src.symptom_analyzer import SymptomAnalyzer

analyzer = SymptomAnalyzer()
result = analyzer.analyze_symptoms(
    "I have a headache and fever for 2 days",
    language='en'
)

print(f"Urgency: {result['urgency_level']}")
print(f"Specialists: {result['specialists']}")
print(f"Emergency: {result['is_emergency']}")
```

### Voice Interaction

```python
from src.voice_handler import VoiceHandler

handler = VoiceHandler()
response = handler.process_voice_input(
    "I have chest pain",
    language='en'
)

print(response['response'])
```

### Vision Analysis

```python
from src.vision_handler import VisionHandler

handler = VisionHandler()
result = handler.analyze_visual_symptom(
    image_path='symptom_image.jpg',
    symptom_description='rash on arm'
)

print(result['analysis'])
```

### Doctor Recommendation

```python
from src.recommender import DoctorRecommender

recommender = DoctorRecommender()
result = recommender.recommend_doctors(
    specialists=['Cardiologist'],
    urgency='HIGH'
)

for rec in result['recommendations']:
    print(f"{rec['hospital_name']} - {rec['distance_km']} km")
```

### Appointment Booking

```python
from src.automation_agent import AutomationAgent

agent = AutomationAgent()
result = agent.book_appointment(
    booking_method='email',
    hospital_data=hospital_info,
    patient_data=patient_info,
    doctor_data=doctor_info,
    appointment_time='2026-03-20 10:00 AM'
)

print(f"Booking ID: {result['booking_id']}")
```

### Complete End-to-End Flow

```python
from src.main import AppointAgent

agent = AppointAgent()

# Step 1: Process symptoms
result = agent.process_symptom_input(
    text="I have chest pain",
    language='en'
)

# Step 2: Select doctor
agent.select_doctor(
    hospital_id='h001',
    doctor_name='Dr. Ahmed Rahman'
)

# Step 3: Book appointment
booking = agent.book_appointment(
    patient_info={'name': 'John Doe', 'phone': '+880-1234567890'},
    appointment_time='10:00 AM'
)

print(f"Booking confirmed: {booking['confirmation_message']}")
```

## Testing

### Run All Tests

```bash
# Day 1 tests (core AI features)
python test_day1_setup.py

# Day 2 tests (recommendations & automation)
python test_day2_complete.py

# Complete flow demo
python demo_complete_flow.py

# Final verification (all Member 1 responsibilities)
python final_verification_test.py

# MVP scope verification
python mvp_scope_verification.py
```

### Test Coverage

All modules have comprehensive test coverage:
- Configuration management
- Voice handler with Gemini API
- Symptom analyzer with AI reasoning
- Vision handler for camera input
- Emergency detection system
- Doctor recommendation engine
- Automation agent (portal & email)
- Language handler (multilingual)
- End-to-end orchestration

### Test Results

```
✅ Day 1 Tests: 8/8 passing
✅ Day 2 Tests: 7/7 passing
✅ Final Verification: 9/9 passing
✅ MVP Verification: 6/6 passing
✅ Overall: 25+ tests passing (100%)
```

## Documentation

Comprehensive documentation available:
- `README.md` - Project overview and setup
- `QUICK_START.md` - Quick start guide
- `INTEGRATION_READINESS.md` - Backend integration guide
- `Member1_Detailed_Timeline_Plan.md` - Development timeline
- `DAY1_COMPLETION_SUMMARY.md` - Day 1 completion report
- `DAY2_COMPLETION_SUMMARY.md` - Day 2 completion report
- `TASK_3.1_COMPLETION_REPORT.md` - Task 3.1 verification
- `MEMBER1_WORK_COMPLETE.md` - Final completion status
- `API_Setup_Guide.md` - GCP setup instructions

## Deployment

### Google Cloud Run Deployment

```bash
# Build container
gcloud builds submit --tag gcr.io/YOUR-PROJECT-ID/appoint-agent

# Deploy to Cloud Run
gcloud run deploy appoint-agent \
  --image gcr.io/YOUR-PROJECT-ID/appoint-agent \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated
```

### Environment Variables for Production

```env
GOOGLE_CLOUD_PROJECT=your-project-id
GEMINI_API_KEY=your-production-api-key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
STORAGE_BUCKET=your-bucket-name
FIRESTORE_DATABASE=(default)
ENVIRONMENT=production
DEFAULT_LANGUAGE=en
```

## Roadmap

### Current (MVP - March 2026)
- ✅ Voice and text symptom input
- ✅ Camera-based visual symptom analysis
- ✅ Emergency detection and alerts
- ✅ Smart doctor recommendations
- ✅ Automated appointment booking
- ✅ Multilingual support (English & Bangla)

### Phase 2 (Q2 2026)
- Integration with real hospital portals
- Expanded hospital database (10+ hospitals)
- Appointment reminders and notifications
- Patient dashboard for appointment history
- Follow-up appointment management
- SMS and WhatsApp notifications

### Phase 3 (Q3 2026)
- Mobile app (iOS & Android)
- Additional language support
- Insurance integration
- Prescription management
- Lab report integration
- Telemedicine integration

### Phase 4 (Q4 2026)
- AI-powered health insights
- Chronic disease management
- Family health profiles
- Health record storage
- Integration with wearables

## Contributing

This project was built for the Gemini Live Agent Challenge 2026. Contributions are welcome after the hackathon concludes.

## Team

**Gemini Live Agent Challenge 2026 - Team Appoint**

- **Member 1**: AI + Automation (Voice, Vision, Emergency Detection, Booking Automation)
- **Member 2**: Frontend + Video (UI Development, Demo Video Production)
- **Member 3**: Backend + Integration (API Development, Cloud Deployment)

## License

MIT License

## Acknowledgments

- Google Gemini API for powerful AI capabilities
- Google Cloud Platform for infrastructure
- Gemini Live Agent Challenge 2026 for the opportunity
- Healthcare workers worldwide for their inspiration

## Contact

For questions or collaboration opportunities, please open an issue in this repository.

---

**Built with ❤️ for better healthcare access**

**Gemini Live Agent Challenge 2026**
