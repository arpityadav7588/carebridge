"""
Automation Agent Module
Automates appointment booking through hospital portals and email
"""

from playwright.sync_api import sync_playwright, Page, Browser
from typing import Dict, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time

class AutomationAgent:
    """Automates appointment booking"""
    
    def __init__(self):
        """Initialize automation agent"""
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    def book_appointment(
        self,
        booking_method: str,
        hospital_data: Dict[str, Any],
        patient_data: Dict[str, Any],
        doctor_data: Dict[str, Any],
        appointment_time: str
    ) -> Dict[str, Any]:
        """
        Book appointment using appropriate method
        
        Args:
            booking_method: 'online_portal' or 'email'
            hospital_data: Hospital information
            patient_data: Patient information
            doctor_data: Doctor information
            appointment_time: Requested appointment time
            
        Returns:
            Booking result
        """
        try:
            if booking_method == 'online_portal':
                return self._book_via_portal(
                    hospital_data, patient_data, doctor_data, appointment_time
                )
            elif booking_method == 'email':
                return self._book_via_email(
                    hospital_data, patient_data, doctor_data, appointment_time
                )
            else:
                return {
                    'success': False,
                    'error': f'Unsupported booking method: {booking_method}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _book_via_portal(
        self,
        hospital_data: Dict[str, Any],
        patient_data: Dict[str, Any],
        doctor_data: Dict[str, Any],
        appointment_time: str
    ) -> Dict[str, Any]:
        """
        Book appointment via online portal
        Uses Playwright for browser automation
        """
        portal_url = hospital_data.get('portal_url')
        
        if not portal_url:
            return {'success': False, 'error': 'No portal URL provided'}
        
        try:
            # For MVP: Simulate portal booking
            # In production, this would navigate actual portals
            result = self._simulate_portal_booking(
                portal_url, hospital_data, patient_data, doctor_data, appointment_time
            )
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Portal booking failed: {str(e)}'
            }
    
    def _simulate_portal_booking(
        self,
        portal_url: str,
        hospital_data: Dict[str, Any],
        patient_data: Dict[str, Any],
        doctor_data: Dict[str, Any],
        appointment_time: str
    ) -> Dict[str, Any]:
        """
        Simulate portal booking for MVP
        In production, this would use actual Playwright automation
        """
        # Simulate processing time
        time.sleep(1)
        
        # Generate booking confirmation
        booking_id = f"APT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            'success': True,
            'booking_id': booking_id,
            'method': 'online_portal',
            'hospital': hospital_data['name'],
            'doctor': doctor_data['name'],
            'specialty': doctor_data['specialty'],
            'appointment_time': appointment_time,
            'patient_name': patient_data['name'],
            'confirmation_message': f'Appointment booked successfully at {hospital_data["name"]}',
            'portal_url': portal_url
        }
    
    def _book_via_email(
        self,
        hospital_data: Dict[str, Any],
        patient_data: Dict[str, Any],
        doctor_data: Dict[str, Any],
        appointment_time: str
    ) -> Dict[str, Any]:
        """Book appointment via email"""
        
        email_address = hospital_data.get('email')
        
        if not email_address:
            return {'success': False, 'error': 'No email address provided'}
        
        try:
            # Compose email
            email_content = self._compose_appointment_email(
                hospital_data, patient_data, doctor_data, appointment_time
            )
            
            # For MVP: Simulate email sending
            # In production, this would actually send email
            result = self._simulate_email_sending(
                email_address, email_content, hospital_data, patient_data, doctor_data, appointment_time
            )
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Email booking failed: {str(e)}'
            }

    
    def _compose_appointment_email(
        self,
        hospital_data: Dict[str, Any],
        patient_data: Dict[str, Any],
        doctor_data: Dict[str, Any],
        appointment_time: str
    ) -> str:
        """Compose appointment request email"""
        
        email_body = f"""
Dear {hospital_data['name']} Appointments Team,

I would like to request an appointment with the following details:

Patient Information:
- Name: {patient_data['name']}
- Phone: {patient_data.get('phone', 'N/A')}
- Email: {patient_data.get('email', 'N/A')}
- Age: {patient_data.get('age', 'N/A')}

Appointment Request:
- Doctor: {doctor_data['name']}
- Specialty: {doctor_data['specialty']}
- Preferred Date/Time: {appointment_time}
- Reason: {patient_data.get('symptoms', 'General consultation')}

Please confirm the appointment or suggest alternative times if the requested slot is not available.

Thank you for your assistance.

Best regards,
{patient_data['name']}

---
This email was sent via Appoint Healthcare Assistant
"""
        return email_body
    
    def _simulate_email_sending(
        self,
        email_address: str,
        email_content: str,
        hospital_data: Dict[str, Any],
        patient_data: Dict[str, Any],
        doctor_data: Dict[str, Any],
        appointment_time: str
    ) -> Dict[str, Any]:
        """
        Simulate email sending for MVP
        In production, this would use SMTP to send actual emails
        """
        # Simulate processing time
        time.sleep(1)
        
        # Generate booking reference
        booking_ref = f"EMAIL{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            'success': True,
            'booking_ref': booking_ref,
            'method': 'email',
            'hospital': hospital_data['name'],
            'doctor': doctor_data['name'],
            'specialty': doctor_data['specialty'],
            'appointment_time': appointment_time,
            'patient_name': patient_data['name'],
            'email_sent_to': email_address,
            'confirmation_message': f'Appointment request sent to {hospital_data["name"]}. You will receive confirmation via email.',
            'email_content': email_content
        }
    
    def send_actual_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: str,
        smtp_password: str
    ) -> bool:
        """
        Send actual email using SMTP
        (For production use)
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server (Gmail example)
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_email, smtp_password)
            
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False
    
    def cleanup(self):
        """Cleanup browser resources"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()


# For testing
if __name__ == "__main__":
    agent = AutomationAgent()
    
    # Test data
    hospital_data = {
        'name': 'City General Hospital',
        'portal_url': 'https://citygeneralhospital.com/appointments',
        'email': 'appointments@citygeneralhospital.com'
    }
    
    patient_data = {
        'name': 'John Doe',
        'phone': '+880-1234567890',
        'email': 'john@example.com',
        'age': 35,
        'symptoms': 'Headache and fever'
    }
    
    doctor_data = {
        'name': 'Dr. Ahmed Rahman',
        'specialty': 'Cardiologist'
    }
    
    # Test portal booking
    print("Test 1: Portal Booking")
    result = agent.book_appointment(
        booking_method='online_portal',
        hospital_data=hospital_data,
        patient_data=patient_data,
        doctor_data=doctor_data,
        appointment_time='2026-03-20 10:00 AM'
    )
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Booking ID: {result['booking_id']}")
        print(f"Message: {result['confirmation_message']}")
    print()
    
    # Test email booking
    print("Test 2: Email Booking")
    result = agent.book_appointment(
        booking_method='email',
        hospital_data=hospital_data,
        patient_data=patient_data,
        doctor_data=doctor_data,
        appointment_time='2026-03-20 2:00 PM'
    )
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Booking Ref: {result['booking_ref']}")
        print(f"Message: {result['confirmation_message']}")
