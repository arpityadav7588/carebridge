"""
Language Handler Module
Manages multilingual support for English and Bangla
"""

from typing import Dict, Any
from src.config import Config

class LanguageHandler:
    """Handles language detection and translation"""
    
    def __init__(self):
        """Initialize language handler"""
        self.supported_languages = Config.SUPPORTED_LANGUAGES
        self.current_language = Config.DEFAULT_LANGUAGE
    
    def detect_language(self, text: str) -> str:
        """
        Detect language from text
        Simple detection based on character sets
        """
        # Check for Bangla characters (Unicode range)
        bangla_chars = sum(1 for char in text if '\u0980' <= char <= '\u09FF')
        
        if bangla_chars > len(text) * 0.3:  # If 30%+ Bangla chars
            return 'bn'
        return 'en'
    
    def get_message(self, key: str, language: str = None) -> str:
        """Get localized message"""
        if language is None:
            language = self.current_language
        
        messages = self._get_messages()
        return messages.get(language, {}).get(key, messages['en'].get(key, ''))
    
    def _get_messages(self) -> Dict[str, Dict[str, str]]:
        """Get all localized messages"""
        return {
            'en': {
                'welcome': 'Welcome to Appoint! How can I help you today?',
                'describe_symptoms': 'Please describe your symptoms.',
                'emergency_detected': 'EMERGENCY DETECTED! Seeking immediate help...',
                'booking_success': 'Appointment booked successfully!',
                'booking_failed': 'Failed to book appointment. Please try again.',
                'no_doctors_found': 'No doctors found matching your requirements.',
                'select_doctor': 'Please select a doctor from the list.',
                'thank_you': 'Thank you for using Appoint!'
            },
            'bn': {
                'welcome': 'অ্যাপয়েন্টে স্বাগতম! আজ আমি আপনাকে কীভাবে সাহায্য করতে পারি?',
                'describe_symptoms': 'অনুগ্রহ করে আপনার লক্ষণগুলি বর্ণনা করুন।',
                'emergency_detected': 'জরুরি অবস্থা সনাক্ত! অবিলম্বে সাহায্য খোঁজা হচ্ছে...',
                'booking_success': 'অ্যাপয়েন্টমেন্ট সফলভাবে বুক করা হয়েছে!',
                'booking_failed': 'অ্যাপয়েন্টমেন্ট বুক করতে ব্যর্থ। অনুগ্রহ করে আবার চেষ্টা করুন।',
                'no_doctors_found': 'আপনার প্রয়োজনীয়তা মেলে এমন কোনো ডাক্তার পাওয়া যায়নি।',
                'select_doctor': 'অনুগ্রহ করে তালিকা থেকে একজন ডাক্তার নির্বাচন করুন।',
                'thank_you': 'অ্যাপয়েন্ট ব্যবহার করার জন্য ধন্যবাদ!'
            }
        }
