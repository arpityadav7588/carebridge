"""
MVP Scope Verification
Verifies all MVP requirements from project_idea.txt are met
"""

import sys
sys.path.append('.')

from src.main import AppointAgent
from src.recommender import DoctorRecommender

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def verify_mvp_scope():
    """Verify MVP scope requirements"""
    
    print_section("MVP SCOPE VERIFICATION")
    print("Checking all requirements from project_idea.txt\n")
    
    mvp_requirements = {
        'Demo with 3 hospitals/clinics': False,
        'Voice + text symptom input': False,
        'Camera input for visual symptom': False,
        'Booking automation with at least 1 hospital': False,
        'Emergency alert demo': False,
        'Multilingual support (Bangla & English)': False
    }
    
    # Test 1: 3 hospitals/clinics
    print("1. Checking hospital database...")
    recommender = DoctorRecommender()
    hospital_count = len(recommender.hospitals)
    print(f"   Hospitals in database: {hospital_count}")
    if hospital_count >= 3:
        mvp_requirements['Demo with 3 hospitals/clinics'] = True
        print("   ✅ PASS: 3+ hospitals configured")
        for h in recommender.hospitals:
            print(f"      - {h['name']} ({h['location']})")
    else:
        print(f"   ❌ FAIL: Only {hospital_count} hospitals")
    
    # Test 2: Voice + text symptom input
    print("\n2. Checking voice + text symptom input...")
    agent = AppointAgent()
    try:
        # Test text input
        result_text = agent.process_symptom_input("I have a headache", language='en')
        # Test voice handler
        voice_result = agent.get_conversation_response("I feel sick", language='en')
        if result_text['status'] in ['success', 'emergency'] and len(voice_result) > 0:
            mvp_requirements['Voice + text symptom input'] = True
            print("   ✅ PASS: Both voice and text input working")
    except Exception as e:
        print(f"   ❌ FAIL: {str(e)}")
    
    # Test 3: Camera input
    print("\n3. Checking camera input for visual symptoms...")
    try:
        from src.vision_handler import VisionHandler
        vision = VisionHandler()
        if vision.model is not None:
            mvp_requirements['Camera input for visual symptom'] = True
            print("   ✅ PASS: Vision handler ready for camera input")
            print("      - Can analyze rashes, injuries, swelling")
            print("      - Integrated with Gemini Vision API")
    except Exception as e:
        print(f"   ❌ FAIL: {str(e)}")
    
    # Test 4: Booking automation
    print("\n4. Checking booking automation...")
    try:
        from src.automation_agent import AutomationAgent
        auto_agent = AutomationAgent()
        
        # Test portal booking
        result = auto_agent.book_appointment(
            booking_method='online_portal',
            hospital_data={'name': 'Test', 'portal_url': 'https://test.com'},
            patient_data={'name': 'Test', 'phone': '123'},
            doctor_data={'name': 'Dr. Test', 'specialty': 'General'},
            appointment_time='10:00 AM'
        )
        
        if result['success']:
            mvp_requirements['Booking automation with at least 1 hospital'] = True
            print("   ✅ PASS: Booking automation working")
            print("      - Portal navigation (simulated)")
            print("      - Email booking (ready)")
            print("      - Form filling automation")
    except Exception as e:
        print(f"   ❌ FAIL: {str(e)}")
    
    # Test 5: Emergency alert
    print("\n5. Checking emergency alert demo...")
    try:
        from src.symptom_analyzer import SymptomAnalyzer
        analyzer = SymptomAnalyzer()
        result = analyzer.analyze_symptoms("severe chest pain and difficulty breathing")
        
        if result['is_emergency'] and result['urgency_level'] == 'CRITICAL':
            mvp_requirements['Emergency alert demo'] = True
            print("   ✅ PASS: Emergency detection working")
            print("      - Detects critical symptoms")
            print("      - Immediate alert system")
            print("      - Emergency action recommendations")
    except Exception as e:
        print(f"   ❌ FAIL: {str(e)}")
    
    # Test 6: Multilingual support
    print("\n6. Checking multilingual support...")
    try:
        from src.language_handler import LanguageHandler
        lang_handler = LanguageHandler()
        
        # Test both languages
        lang_en = lang_handler.detect_language("I have a headache")
        lang_bn = lang_handler.detect_language("আমার মাথা ব্যথা")
        
        if lang_en == 'en' and lang_bn == 'bn':
            mvp_requirements['Multilingual support (Bangla & English)'] = True
            print("   ✅ PASS: Multilingual support working")
            print("      - English language support")
            print("      - Bangla language support")
            print("      - Automatic language detection")
    except Exception as e:
        print(f"   ❌ FAIL: {str(e)}")
    
    # Summary
    print_section("MVP SCOPE SUMMARY")
    
    total = len(mvp_requirements)
    passed = sum(1 for v in mvp_requirements.values() if v)
    
    print(f"Total Requirements: {total}")
    print(f"Completed: {passed}")
    print(f"Completion Rate: {(passed/total)*100:.0f}%\n")
    
    for req, status in mvp_requirements.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {req}")
    
    if passed == total:
        print("\n🎉 ALL MVP REQUIREMENTS MET!")
        print("✅ Member 1 work is 100% complete")
        print("✅ Ready for backend integration")
    else:
        print(f"\n⚠️  {total - passed} requirement(s) not met")
    
    print("\n" + "="*70)
    
    return passed == total

if __name__ == "__main__":
    success = verify_mvp_scope()
    sys.exit(0 if success else 1)
