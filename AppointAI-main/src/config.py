"""
Configuration module for Appoint Healthcare Agent
Loads environment variables and provides configuration settings
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Google Cloud
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', 'your-project-id')
    PROJECT_ID = os.getenv('PROJECT_ID', 'your-project-id')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Firestore
    FIRESTORE_DATABASE = os.getenv('FIRESTORE_DATABASE', '(default)')
    
    # Cloud Storage
    STORAGE_BUCKET = os.getenv('STORAGE_BUCKET', 'your-bucket-name')
    
    # Application
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'en')
    
    # Gemini Models
    GEMINI_TEXT_MODEL = 'gemini-pro'
    GEMINI_VISION_MODEL = 'gemini-pro-vision'
    GEMINI_FLASH_MODEL = 'gemini-2.0-flash-exp'
    
    # Supported Languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'bn': 'Bangla'
    }
    
    # Emergency Keywords
    EMERGENCY_KEYWORDS = [
        'chest pain', 'heart attack', 'stroke', 'severe bleeding',
        'difficulty breathing', 'unconscious', 'seizure', 'severe burn',
        'broken bone', 'head injury', 'poisoning', 'severe allergic reaction'
    ]
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        return True

# Validate configuration on import
Config.validate()
