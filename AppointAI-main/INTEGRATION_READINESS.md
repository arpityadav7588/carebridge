# Integration Readiness Document
## Member 1 → Member 3 Backend Integration

**Date**: March 16, 2026  
**Status**: ✅ READY FOR INTEGRATION  
**Member 1 Completion**: 100%

---

## Executive Summary

All Member 1 (AI + Automation) components are complete, tested, and ready for backend integration. This document provides everything Member 3 needs to integrate the AI modules with the backend.

---

## Available Modules

### 1. Main Orchestrator (`src/main.py`)
**Class**: `AppointAgent`

**Key Methods**:
```python
# Process symptoms
process_symptom_input(text: str, language: str, image_path: Optional[str])
→ Returns: analysis, recommendations, questions

# Select doctor
select_doctor(hospital_id: str, doctor_name: str)
→ Returns: selection confirmation

# Book appointment
book_appointment(patient_info: dict, appointment_time: str)
→ Returns: booking confirmation

# Get conversation response
get_conversation_response(user_input: str, language: str)
→ Returns: AI response text

# Reset session
reset_session()
```

### 2. Symptom Analyzer (`src/symptom_analyzer.py`)
**Class**: `SymptomAnalyzer`

**Key Methods**:
```python
analyze_symptoms(symptom_text: str, language: str)
→ Returns: {
    'is_emergency': bool,
    'urgency_level': str,
    'specialists': list,
    'analysis_summary': str,
    'clarifying_questions': list,
    'possible_conditions': list
}
```

### 3. Doctor Recommender (`src/recommender.py`)
**Class**: `DoctorRecommender`

**Key Methods**:
```python
recommend_doctors(specialists: list, location: str, urgency: str, max_distance_km: float)
→ Returns: {
    'success': bool,
    'count': int,
    'recommendations': [
        {
            'hospital_id': str,
            'hospital_name': str,
            'location': str,
            'distance_km': float,
            'rating': float,
            'matching_doctors': list,
            'facilities': list,
            'booking_method': str,
            'trade_offs': dict
        }
    ]
}

get_hospital_details(hospital_id: str)
→ Returns: hospital dict
```

### 4. Automation Agent (`src/automation_agent.py`)
**Class**: `AutomationAgent`

**Key Methods**:
```python
book_appointment(
    booking_method: str,
    hospital_data: dict,
    patient_data: dict,
    doctor_data: dict,
    appointment_time: str
)
→ Returns: {
    'success': bool,
    'booking_id': str,  # or 'booking_ref'
    'method': str,
    'hospital': str,
    'doctor': str,
    'appointment_time': str,
    'confirmation_message': str
}
```

### 5. Vision Handler (`src/vision_handler.py`)
**Class**: `VisionHandler`

**Key Methods**:
```python
analyze_visual_symptom(
    image_path: str,
    image_bytes: bytes,
    symptom_description: str,
    language: str
)
→ Returns: {
    'success': bool,
    'analysis': str,
    'severity': str,
    'recommended_specialists': list,
    'requires_immediate_attention': bool
}
```

### 6. Language Handler (`src/language_handler.py`)
**Class**: `LanguageHandler`

**Key Methods**:
```python
detect_language(text: str) → str  # 'en' or 'bn'
get_message(key: str, language: str) → str
```

---

## Data Structures

### Patient Data
```python
{
    'name': str,
    'phone': str,
    'email': str,
    'age': int,
    'symptoms': str  # optional
}
```

### Hospital Data
```python
{
    'id': str,
    'name': str,
    'location': str,
    'distance_km': float,
    'rating': float,
    'specialties': list[str],
    'facilities': list[str],
    'doctors': list[dict],
    'booking_method': str,  # 'online_portal' or 'email'
    'portal_url': str,  # if online_portal
    'email': str,  # if email
    'contact': str
}
```

### Doctor Data
```python
{
    'name': str,
    'specialty': str,
    'experience_years': int,
    'available_slots': list[str]
}
```

### Booking Confirmation
```python
{
    'success': bool,
    'booking_id': str,
    'method': str,
    'hospital': str,
    'doctor': str,
    'specialty': str,
    'appointment_time': str,
    'patient_name': str,
    'confirmation_message': str
}
```

---

## API Endpoint Suggestions

### 1. Symptom Analysis
```
POST /api/symptoms/analyze
Body: {
    "text": str,
    "language": str,
    "image": base64 (optional)
}
Response: {
    "is_emergency": bool,
    "urgency_level": str,
    "specialists": list,
    "clarifying_questions": list
}
```

### 2. Doctor Recommendations
```
GET /api/doctors/recommend
Query: {
    "specialists": str (comma-separated),
    "location": str,
    "urgency": str
}
Response: {
    "count": int,
    "recommendations": list
}
```

### 3. Book Appointment
```
POST /api/appointments/book
Body: {
    "hospital_id": str,
    "doctor_name": str,
    "patient_info": dict,
    "appointment_time": str
}
Response: {
    "success": bool,
    "booking_id": str,
    "confirmation": str
}
```

### 4. Get Appointment History
```
GET /api/appointments/history/{patient_id}
Response: {
    "appointments": list
}
```

### 5. Emergency Alert
```
POST /api/emergency/alert
Body: {
    "symptoms": str,
    "location": str
}
Response: {
    "nearest_hospital": dict,
    "alert_sent": bool
}
```

---

## Integration Steps

### Step 1: Import Modules
```python
from src.main import AppointAgent
from src.symptom_analyzer import SymptomAnalyzer
from src.recommender import DoctorRecommender
from src.automation_agent import AutomationAgent
```

### Step 2: Initialize Components
```python
agent = AppointAgent()
# All sub-components are initialized automatically
```

### Step 3: Use in API Endpoints
```python
# Example: Symptom analysis endpoint
@app.post("/api/symptoms/analyze")
async def analyze_symptoms(request: SymptomRequest):
    result = agent.process_symptom_input(
        text=request.text,
        language=request.language
    )
    return result
```

---

## Environment Variables Required

```env
GOOGLE_CLOUD_PROJECT=your-project-id
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_APPLICATION_CREDENTIALS=./your-service-account.json
FIRESTORE_DATABASE=(default)
STORAGE_BUCKET=your-bucket-name
ENVIRONMENT=development
DEFAULT_LANGUAGE=en
```

---

## Testing Integration

### Test Script
```python
from src.main import AppointAgent

# Initialize
agent = AppointAgent()

# Test 1: Symptom analysis
result = agent.process_symptom_input("I have a headache", "en")
print(result)

# Test 2: Select doctor
if result['recommendations']['count'] > 0:
    rec = result['recommendations']['recommendations'][0]
    if rec['matching_doctors']:
        selection = agent.select_doctor(
            rec['hospital_id'],
            rec['matching_doctors'][0]['name']
        )
        print(selection)

# Test 3: Book appointment
booking = agent.book_appointment(
    {'name': 'Test', 'phone': '123'},
    '10:00 AM'
)
print(booking)
```

---

## Error Handling

All modules return structured responses with error information:

```python
{
    'success': bool,
    'error': str,  # if success is False
    'data': dict   # if success is True
}
```

---

## Performance Considerations

- **Gemini API calls**: ~1-3 seconds per request
- **Symptom analysis**: ~2-4 seconds
- **Doctor recommendation**: <1 second (local database)
- **Booking automation**: ~1-2 seconds (simulated)

---

## Dependencies

All dependencies are in `requirements.txt`:
```
google-generativeai>=0.3.0
google-cloud-aiplatform>=1.38.0
google-cloud-vision>=3.4.0
playwright>=1.40.0
python-dotenv>=1.0.0
pillow>=10.0.0
```

---

## Contact Points

**Member 1 Modules Ready**: ✅  
**Integration Support**: Available  
**Testing Support**: Available  
**Documentation**: Complete

---

## Next Steps for Member 3

1. Review this integration document
2. Set up backend API endpoints
3. Import Member 1 modules
4. Test integration with provided test scripts
5. Deploy to Google Cloud Run
6. Coordinate final testing

---

**Status**: ✅ READY FOR INTEGRATION  
**Member 1 Availability**: Ready to support integration
