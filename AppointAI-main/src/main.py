"""
Main Orchestrator Module
Coordinates all components for end-to-end appointment booking
"""

from src.voice_handler import VoiceHandler
from src.symptom_analyzer import SymptomAnalyzer
from src.vision_handler import VisionHandler
from src.language_handler import LanguageHandler
from src.recommender import DoctorRecommender
from src.automation_agent import AutomationAgent
from typing import Dict, Any, Optional
import json

class AppointAgent:
    """Main agent orchestrating all components"""
    
    def __init__(self):
        """Initialize all components"""
        self.voice_handler = VoiceHandler()
        self.symptom_analyzer = SymptomAnalyzer()
        self.vision_handler = VisionHandler()
        self.language_handler = LanguageHandler()
        self.recommender = DoctorRecommender()
        self.automation_agent = AutomationAgent()
        
        self.session_data = {
            'language': 'en',
            'symptoms': None,
            'analysis': None,
            'selected_hospital': None,
            'selected_doctor': None,
            'patient_info': {}
        }
    
    def process_symptom_input(
        self,
        text: str,
        language: str = 'en',
        image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process symptom input (text and/or image)
        
        Returns complete analysis with recommendations
        """
        self.session_data['language'] = language
        self.session_data['symptoms'] = text
        
        # Analyze text symptoms
        analysis = self.symptom_analyzer.analyze_symptoms(text, language)
        self.session_data['analysis'] = analysis
        
        # If image provided, analyze visual symptoms
        if image_path:
            vision_result = self.vision_handler.analyze_visual_symptom(
                image_path=image_path,
                symptom_description=text,
                language=language
            )
            if vision_result['success']:
                # Merge specialists
                analysis['specialists'].extend(vision_result['recommended_specialists'])
                analysis['specialists'] = list(set(analysis['specialists']))  # Remove duplicates
        
        # Check for emergency
        if analysis.get('is_emergency'):
            return {
                'status': 'emergency',
                'message': self.language_handler.get_message('emergency_detected', language),
                'action': analysis['recommended_action'],
                'analysis': analysis
            }
        
        # Get doctor recommendations
        recommendations = self.recommender.recommend_doctors(
            specialists=analysis['specialists'],
            urgency=analysis['urgency_level']
        )
        
        return {
            'status': 'success',
            'analysis': analysis,
            'recommendations': recommendations,
            'clarifying_questions': analysis.get('clarifying_questions', [])
        }
    
    def select_doctor(
        self,
        hospital_id: str,
        doctor_name: str
    ) -> Dict[str, Any]:
        """Select a doctor for appointment"""
        
        hospital = self.recommender.get_hospital_details(hospital_id)
        
        if not hospital:
            return {
                'success': False,
                'error': 'Hospital not found'
            }
        
        # Find doctor
        doctor = None
        for doc in hospital['doctors']:
            if doc['name'] == doctor_name:
                doctor = doc
                break
        
        if not doctor:
            return {
                'success': False,
                'error': 'Doctor not found'
            }
        
        self.session_data['selected_hospital'] = hospital
        self.session_data['selected_doctor'] = doctor
        
        return {
            'success': True,
            'hospital': hospital['name'],
            'doctor': doctor['name'],
            'specialty': doctor['specialty'],
            'available_slots': doctor['available_slots'],
            'booking_method': hospital['booking_method']
        }
    
    def book_appointment(
        self,
        patient_info: Dict[str, Any],
        appointment_time: str
    ) -> Dict[str, Any]:
        """Book appointment with selected doctor"""
        
        if not self.session_data['selected_hospital'] or not self.session_data['selected_doctor']:
            return {
                'success': False,
                'error': 'Please select a doctor first'
            }
        
        # Add symptoms to patient info
        patient_info['symptoms'] = self.session_data['symptoms']
        self.session_data['patient_info'] = patient_info
        
        # Book appointment
        result = self.automation_agent.book_appointment(
            booking_method=self.session_data['selected_hospital']['booking_method'],
            hospital_data=self.session_data['selected_hospital'],
            patient_data=patient_info,
            doctor_data=self.session_data['selected_doctor'],
            appointment_time=appointment_time
        )
        
        return result
    
    def get_conversation_response(self, user_input: str, language: str = 'en') -> str:
        """Get conversational response using voice handler"""
        result = self.voice_handler.process_voice_input(user_input, language)
        return result.get('response', '')
    
    def reset_session(self):
        """Reset session data"""
        self.session_data = {
            'language': 'en',
            'symptoms': None,
            'analysis': None,
            'selected_hospital': None,
            'selected_doctor': None,
            'patient_info': {}
        }
        self.voice_handler.reset_conversation()


# For testing
if __name__ == "__main__":
    print("="*60)
    print("APPOINT AGENT - END-TO-END TEST")
    print("="*60)
    
    agent = AppointAgent()
    
    # Step 1: Process symptoms
    print("\nStep 1: Processing symptoms...")
    result = agent.process_symptom_input(
        text="I have chest pain and shortness of breath",
        language='en'
    )
    
    print(f"Status: {result['status']}")
    if result['status'] == 'emergency':
        print(f"EMERGENCY: {result['message']}")
    else:
        print(f"Urgency: {result['analysis']['urgency_level']}")
        print(f"Specialists: {', '.join(result['analysis']['specialists'])}")
        print(f"Recommendations: {result['recommendations']['count']} hospitals found")
        
        # Step 2: Select doctor
        if result['recommendations']['count'] > 0:
            print("\nStep 2: Selecting doctor...")
            first_rec = result['recommendations']['recommendations'][0]
            first_doctor = first_rec['matching_doctors'][0]
            
            selection = agent.select_doctor(
                hospital_id=first_rec['hospital_id'],
                doctor_name=first_doctor['name']
            )
            
            print(f"Selected: {selection['doctor']} at {selection['hospital']}")
            print(f"Available slots: {', '.join(selection['available_slots'])}")
            
            # Step 3: Book appointment
            print("\nStep 3: Booking appointment...")
            booking = agent.book_appointment(
                patient_info={
                    'name': 'Test Patient',
                    'phone': '+880-1234567890',
                    'email': 'test@example.com',
                    'age': 35
                },
                appointment_time=selection['available_slots'][0]
            )
            
            print(f"Booking success: {booking['success']}")
            if booking['success']:
                print(f"Booking ID: {booking.get('booking_id', booking.get('booking_ref'))}")
                print(f"Message: {booking['confirmation_message']}")
    
    print("\n" + "="*60)
    print("END-TO-END TEST COMPLETED")
    print("="*60)
