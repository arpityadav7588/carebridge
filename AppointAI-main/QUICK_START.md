# Quick Start Guide - Appoint

## Run Tests

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run Day 1 tests
python test_day1_setup.py

# Run Day 2 tests
python test_day2_complete.py

# Run complete demo
python demo_complete_flow.py
```

## Use Individual Modules

### Symptom Analyzer
```python
from src.symptom_analyzer import SymptomAnalyzer

analyzer = SymptomAnalyzer()
result = analyzer.analyze_symptoms("I have a headache", language='en')
print(result)
```

### Voice Handler
```python
from src.voice_handler import VoiceHandler

handler = VoiceHandler()
response = handler.process_voice_input("I feel sick", language='en')
print(response['response'])
```

### Vision Handler
```python
from src.vision_handler import VisionHandler

handler = VisionHandler()
result = handler.analyze_visual_symptom(
    image_path='image.jpg',
    symptom_description='rash'
)
print(result['analysis'])
```

### Doctor Recommender
```python
from src.recommender import DoctorRecommender

recommender = DoctorRecommender()
result = recommender.recommend_doctors(
    specialists=['Cardiologist'],
    urgency='HIGH'
)
print(f"Found {result['count']} hospitals")
```

### Automation Agent
```python
from src.automation_agent import AutomationAgent

agent = AutomationAgent()
result = agent.book_appointment(
    booking_method='online_portal',
    hospital_data=hospital_info,
    patient_data=patient_info,
    doctor_data=doctor_info,
    appointment_time='10:00 AM'
)
print(f"Booking ID: {result['booking_id']}")
```

### Complete Flow
```python
from src.main import AppointAgent

agent = AppointAgent()

# Process symptoms
result = agent.process_symptom_input(
    text="I have chest pain",
    language='en'
)

# Select doctor
agent.select_doctor(
    hospital_id='h001',
    doctor_name='Dr. Ahmed Rahman'
)

# Book appointment
booking = agent.book_appointment(
    patient_info={'name': 'John Doe', 'phone': '+880-1234567890'},
    appointment_time='10:00 AM'
)
```

## Project Credentials

- **Project ID**: your-project-id
- **API Key**: Stored in `.env`
- **Service Account**: `your-service-account.json`
- **Firestore**: asia-south1
- **Storage Bucket**: your-bucket-name

## Important Commands

```bash
# Activate venv
.venv\Scripts\activate

# Install new package
pip install package-name

# Run tests
python test_day1_setup.py

# Check Python version
python --version
```

## Next Steps

1. ✅ Day 1 completed - Core AI features
2. ✅ Day 2 completed - Recommendations & automation
3. ⏳ Day 3 - Integration with backend & deployment
4. ⏳ Create demo video
5. ⏳ Submit to hackathon

## Files to Review

- `README.md` - Full documentation
- `Member1_Detailed_Timeline_Plan.md` - Original task timeline
- `DAY1_COMPLETION_SUMMARY.md` - Day 1 progress
- `DAY2_COMPLETION_SUMMARY.md` - Day 2 progress
- `MEMBER1_FINAL_STATUS.md` - Overall status
- `demo_complete_flow.py` - Working demonstration
