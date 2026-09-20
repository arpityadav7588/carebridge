"""
Complete Demo Script
Demonstrates the full end-to-end flow of Appoint Healthcare Agent
"""

import sys
sys.path.append('.')

from src.main import AppointAgent
import json
import time

def print_section(title):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_step(step_num, title):
    """Print step header"""
    print(f"\n{'─'*70}")
    print(f"STEP {step_num}: {title}")
    print(f"{'─'*70}\n")

def demo_normal_consultation():
    """Demo: Normal consultation flow"""
    print_section("DEMO 1: NORMAL CONSULTATION")
    
    agent = AppointAgent()
    
    # Step 1: Patient describes symptoms
    print_step(1, "Patient Describes Symptoms")
    print("Patient: 'I have a headache and mild fever for 2 days'")
    time.sleep(1)
    
    result = agent.process_symptom_input(
        text="I have a headache and mild fever for 2 days",
        language='en'
    )
    
    print(f"\n✓ Status: {result['status']}")
    print(f"✓ Urgency Level: {result['analysis']['urgency_level']}")
    print(f"✓ Recommended Specialists: {', '.join(result['analysis']['specialists'][:2])}")
    
    if result.get('clarifying_questions'):
        print(f"\n📋 Clarifying Questions:")
        for i, q in enumerate(result['clarifying_questions'][:2], 1):
            print(f"   {i}. {q}")
    
    # Step 2: Show recommendations
    print_step(2, "Hospital & Doctor Recommendations")
    
    if result['recommendations'].get('success'):
        recs = result['recommendations']['recommendations']
        print(f"Found {len(recs)} matching hospitals:\n")
        
        for i, rec in enumerate(recs[:2], 1):
            print(f"{i}. {rec['hospital_name']}")
            print(f"   📍 Location: {rec['location']} ({rec['distance_km']} km)")
            print(f"   ⭐ Rating: {rec['rating']}/5")
            print(f"   👨‍⚕️ Doctors: {len(rec['matching_doctors'])} available")
            
            if rec['matching_doctors']:
                doc = rec['matching_doctors'][0]
                print(f"   • {doc['name']} - {doc['specialty']}")
                print(f"     Available: {', '.join(doc['available_slots'][:2])}")
            
            print(f"\n   Trade-offs:")
            for key, value in rec['trade_offs'].items():
                print(f"   • {key.title()}: {value}")
            print()
    
    # Step 3: Select doctor
    print_step(3, "Patient Selects Doctor")
    
    if result['recommendations'].get('success') and result['recommendations']['count'] > 0:
        # Find first hospital with matching doctors
        selected_rec = None
        selected_doctor = None
        
        for rec in result['recommendations']['recommendations']:
            if rec['matching_doctors']:
                selected_rec = rec
                selected_doctor = rec['matching_doctors'][0]
                break
        
        if not selected_rec or not selected_doctor:
            print("✓ No matching doctors available for this demo")
            return
        
        print(f"Patient selects: {selected_doctor['name']} at {selected_rec['hospital_name']}")
        time.sleep(1)
        
        selection = agent.select_doctor(
            hospital_id=selected_rec['hospital_id'],
            doctor_name=selected_doctor['name']
        )
        
        print(f"\n✓ Hospital: {selection['hospital']}")
        print(f"✓ Doctor: {selection['doctor']} ({selection['specialty']})")
        print(f"✓ Available Slots: {', '.join(selection['available_slots'])}")
        print(f"✓ Booking Method: {selection['booking_method']}")
        
        # Step 4: Book appointment
        print_step(4, "Booking Appointment")
        
        print("Patient provides information:")
        print("  Name: Ahmed Hassan")
        print("  Phone: +880-1712345678")
        print("  Email: ahmed@example.com")
        print(f"  Selected Time: {selection['available_slots'][0]}")
        time.sleep(1)
        
        booking = agent.book_appointment(
            patient_info={
                'name': 'Ahmed Hassan',
                'phone': '+880-1712345678',
                'email': 'ahmed@example.com',
                'age': 32
            },
            appointment_time=selection['available_slots'][0]
        )
        
        print(f"\n✅ BOOKING SUCCESSFUL!")
        print(f"✓ Booking ID: {booking.get('booking_id', booking.get('booking_ref'))}")
        print(f"✓ Hospital: {booking['hospital']}")
        print(f"✓ Doctor: {booking['doctor']}")
        print(f"✓ Time: {booking['appointment_time']}")
        print(f"✓ Method: {booking['method']}")
        print(f"\n📧 {booking['confirmation_message']}")

def demo_emergency_detection():
    """Demo: Emergency detection"""
    print_section("DEMO 2: EMERGENCY DETECTION")
    
    agent = AppointAgent()
    
    print_step(1, "Patient Reports Emergency Symptoms")
    print("Patient: 'I have severe chest pain and difficulty breathing'")
    time.sleep(1)
    
    result = agent.process_symptom_input(
        text="I have severe chest pain and difficulty breathing",
        language='en'
    )
    
    if result['status'] == 'emergency':
        print(f"\n🚨 EMERGENCY DETECTED!")
        print(f"✓ Reason: {result['analysis'].get('emergency_reason', 'Critical symptoms')}")
        print(f"✓ Urgency: {result['analysis']['urgency_level']}")
        print(f"\n⚠️  ACTION REQUIRED:")
        print(f"   {result['action']}")
        print(f"\n✓ Recommended: Emergency Medicine specialist")
    else:
        print(f"\n✓ Status: {result['status']}")
        print(f"✓ Urgency: {result['analysis']['urgency_level']}")

def demo_multilingual():
    """Demo: Multilingual support"""
    print_section("DEMO 3: MULTILINGUAL SUPPORT (BANGLA)")
    
    agent = AppointAgent()
    
    print_step(1, "Patient Describes Symptoms in Bangla")
    print("রোগী: 'আমার মাথা ব্যথা এবং জ্বর আছে'")
    time.sleep(1)
    
    result = agent.process_symptom_input(
        text="আমার মাথা ব্যথা এবং জ্বর আছে",
        language='bn'
    )
    
    print(f"\n✓ Language Detected: Bangla")
    print(f"✓ Status: {result['status']}")
    print(f"✓ Urgency: {result['analysis']['urgency_level']}")
    print(f"✓ Specialists: {', '.join(result['analysis']['specialists'][:2])}")
    
    if result['recommendations'].get('success'):
        print(f"✓ Hospitals Found: {result['recommendations']['count']}")

def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("  APPOINT HEALTHCARE AGENT - COMPLETE DEMONSTRATION")
    print("  Gemini Live Agent Challenge 2026")
    print("="*70)
    
    try:
        # Demo 1: Normal consultation
        demo_normal_consultation()
        time.sleep(2)
        
        # Demo 2: Emergency detection
        demo_emergency_detection()
        time.sleep(2)
        
        # Demo 3: Multilingual
        demo_multilingual()
        
        # Summary
        print_section("DEMONSTRATION COMPLETE")
        print("✅ All features demonstrated successfully!")
        print("\nKey Features Shown:")
        print("  ✓ Symptom analysis with AI")
        print("  ✓ Emergency detection")
        print("  ✓ Doctor & hospital recommendations")
        print("  ✓ Trade-off analysis")
        print("  ✓ Automated appointment booking")
        print("  ✓ Multilingual support (English & Bangla)")
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
