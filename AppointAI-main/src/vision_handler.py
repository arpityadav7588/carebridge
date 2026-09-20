"""
Vision Handler Module
Analyzes visual symptoms using Gemini Vision API
"""

import google.generativeai as genai
from src.config import Config
from PIL import Image
from typing import Dict, Any, Optional
import io
import base64

class VisionHandler:
    """Handles camera-based symptom analysis"""
    
    def __init__(self):
        """Initialize vision handler"""
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_VISION_MODEL)
    
    def analyze_visual_symptom(
        self, 
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        symptom_description: str = "",
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Analyze visual symptoms from image
        
        Args:
            image_path: Path to image file
            image_bytes: Image as bytes
            symptom_description: Text description of symptom
            language: Language code
            
        Returns:
            Analysis results
        """
        try:
            # Load image
            if image_path:
                img = Image.open(image_path)
            elif image_bytes:
                img = Image.open(io.BytesIO(image_bytes))
            else:
                return {'error': 'No image provided'}
            
            # Analyze with Gemini Vision
            analysis = self._analyze_image(img, symptom_description, language)
            
            return {
                'success': True,
                'analysis': analysis['description'],
                'severity': analysis['severity'],
                'recommended_specialists': analysis['specialists'],
                'requires_immediate_attention': analysis['urgent'],
                'language': language
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'analysis': self._get_error_message(language)
            }
    
    def _analyze_image(self, image: Image.Image, description: str, language: str) -> Dict[str, Any]:
        """Analyze image using Gemini Vision"""
        
        # Build prompt
        if language == 'bn':
            prompt = f"""এই ছবিতে দৃশ্যমান চিকিৎসা লক্ষণ বিশ্লেষণ করুন।

রোগীর বর্ণনা: {description if description else 'কোনো বর্ণনা নেই'}

নিম্নলিখিত প্রদান করুন:
1. লক্ষণের সংক্ষিপ্ত বিবরণ
2. তীব্রতা স্তর (নিম্ন/মাঝারি/উচ্চ)
3. প্রস্তাবিত বিশেষজ্ঞ
4. জরুরি মনোযোগ প্রয়োজন কিনা (হ্যাঁ/না)

সংক্ষিপ্ত এবং স্পষ্ট থাকুন।"""
        else:
            prompt = f"""Analyze the visible medical symptom in this image.

Patient description: {description if description else 'No description provided'}

Provide:
1. Brief description of what you see
2. Severity level (LOW/MEDIUM/HIGH)
3. Recommended medical specialist
4. Whether immediate attention is needed (YES/NO)

Be concise and clear."""
        
        try:
            # Generate analysis
            response = self.model.generate_content([prompt, image])
            response_text = response.text
            
            # Parse response
            severity = 'MEDIUM'
            if 'HIGH' in response_text.upper() or 'SEVERE' in response_text.upper():
                severity = 'HIGH'
            elif 'LOW' in response_text.upper() or 'MILD' in response_text.upper():
                severity = 'LOW'
            
            urgent = 'YES' in response_text.upper() or 'IMMEDIATE' in response_text.upper()
            
            # Extract specialists
            specialists = self._extract_specialists_from_text(response_text)
            
            return {
                'description': response_text,
                'severity': severity,
                'specialists': specialists,
                'urgent': urgent
            }
            
        except Exception as e:
            return {
                'description': f'Unable to analyze image: {str(e)}',
                'severity': 'MEDIUM',
                'specialists': ['Dermatologist', 'General Physician'],
                'urgent': False
            }
    
    def _extract_specialists_from_text(self, text: str) -> list:
        """Extract specialist names from analysis text"""
        specialists = []
        text_lower = text.lower()
        
        specialist_keywords = {
            'dermatologist': 'Dermatologist',
            'skin': 'Dermatologist',
            'orthopedic': 'Orthopedic Surgeon',
            'bone': 'Orthopedic Surgeon',
            'eye': 'Ophthalmologist',
            'ophthalmologist': 'Ophthalmologist',
            'ent': 'ENT Specialist',
            'ear': 'ENT Specialist',
            'throat': 'ENT Specialist',
            'wound': 'General Surgeon',
            'burn': 'Burn Specialist',
            'emergency': 'Emergency Medicine'
        }
        
        for keyword, specialist in specialist_keywords.items():
            if keyword in text_lower:
                specialists.append(specialist)
        
        if not specialists:
            specialists = ['Dermatologist', 'General Physician']
        
        return list(set(specialists))[:2]  # Return unique, max 2
    
    def _get_error_message(self, language: str) -> str:
        """Get error message in appropriate language"""
        if language == 'bn':
            return "ছবি বিশ্লেষণ করতে অক্ষম। অনুগ্রহ করে আবার চেষ্টা করুন।"
        else:
            return "Unable to analyze image. Please try again."
    
    def validate_image(self, image_path: str) -> bool:
        """Validate if image is suitable for analysis"""
        try:
            img = Image.open(image_path)
            # Check size
            if img.size[0] < 100 or img.size[1] < 100:
                return False
            # Check format
            if img.format not in ['JPEG', 'PNG', 'JPG']:
                return False
            return True
        except:
            return False


# For testing
if __name__ == "__main__":
    handler = VisionHandler()
    
    print("Vision Handler initialized successfully!")
    print("To test, provide an image path:")
    print("result = handler.analyze_visual_symptom(image_path='path/to/image.jpg', symptom_description='rash on arm')")
