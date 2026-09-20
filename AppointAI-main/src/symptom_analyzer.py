"""
Symptom Analyzer Module
Analyzes patient symptoms and recommends appropriate medical specialists
"""

import google.generativeai as genai
from src.config import Config
from typing import Dict, List, Any, Optional
import json
import re

class SymptomAnalyzer:
    """Analyzes symptoms and provides doctor recommendations"""
    
    def __init__(self):
        """Initialize symptom analyzer"""
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_TEXT_MODEL)
        
        # Symptom to specialty mapping
        self.specialty_mapping = {
            'heart': ['cardiologist', 'cardiac surgeon'],
            'chest pain': ['cardiologist', 'emergency medicine'],
            'breathing': ['pulmonologist', 'cardiologist'],
            'skin': ['dermatologist'],
            'rash': ['dermatologist', 'allergist'],
            'bone': ['orthopedic surgeon', 'orthopedist'],
            'joint': ['orthopedic surgeon', 'rheumatologist'],
            'stomach': ['gastroenterologist', 'general physician'],
            'digestive': ['gastroenterologist'],
            'eye': ['ophthalmologist', 'optometrist'],
            'ear': ['ENT specialist', 'otolaryngologist'],
            'throat': ['ENT specialist'],
            'mental': ['psychiatrist', 'psychologist'],
            'anxiety': ['psychiatrist', 'psychologist'],
            'depression': ['psychiatrist', 'psychologist'],
            'pregnancy': ['obstetrician', 'gynecologist'],
            'women': ['gynecologist'],
            'child': ['pediatrician'],
            'fever': ['general physician', 'infectious disease specialist'],
            'diabetes': ['endocrinologist', 'diabetologist'],
            'thyroid': ['endocrinologist'],
            'kidney': ['nephrologist', 'urologist'],
            'liver': ['hepatologist', 'gastroenterologist'],
            'brain': ['neurologist', 'neurosurgeon'],
            'headache': ['neurologist', 'general physician'],
            'back pain': ['orthopedic surgeon', 'neurosurgeon', 'physiotherapist']
        }
    
    def analyze_symptoms(self, symptom_text: str, language: str = 'en') -> Dict[str, Any]:
        """
        Analyze symptoms and provide recommendations
        
        Args:
            symptom_text: Patient's symptom description
            language: Language code
            
        Returns:
            Analysis results with doctor recommendations
        """
        try:
            # Check for emergency
            is_emergency, emergency_reason = self._check_emergency(symptom_text)
            
            if is_emergency:
                return {
                    'is_emergency': True,
                    'emergency_reason': emergency_reason,
                    'urgency_level': 'CRITICAL',
                    'recommended_action': self._get_emergency_action(language),
                    'specialists': ['Emergency Medicine'],
                    'clarifying_questions': []
                }
            
            # Get AI analysis
            analysis = self._get_ai_analysis(symptom_text, language)
            
            # Extract specialists
            specialists = self._extract_specialists(symptom_text, analysis)
            
            # Generate clarifying questions
            questions = self._generate_clarifying_questions(symptom_text, analysis, language)
            
            # Determine urgency
            urgency = self._determine_urgency(symptom_text, analysis)
            
            return {
                'is_emergency': False,
                'urgency_level': urgency,
                'specialists': specialists,
                'analysis_summary': analysis.get('summary', ''),
                'clarifying_questions': questions,
                'possible_conditions': analysis.get('conditions', []),
                'language': language
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'specialists': ['General Physician'],
                'urgency_level': 'MEDIUM'
            }
    
    def _check_emergency(self, text: str) -> tuple[bool, Optional[str]]:
        """Check if symptoms indicate an emergency"""
        text_lower = text.lower()
        
        for keyword in Config.EMERGENCY_KEYWORDS:
            if keyword in text_lower:
                return True, keyword
        
        # Additional emergency patterns
        emergency_patterns = [
            r'can\'t breathe',
            r'cannot breathe',
            r'severe pain',
            r'losing consciousness',
            r'heavy bleeding',
            r'suicide',
            r'heart attack'
        ]
        
        for pattern in emergency_patterns:
            if re.search(pattern, text_lower):
                return True, pattern
        
        return False, None
    
    def _get_ai_analysis(self, symptom_text: str, language: str) -> Dict[str, Any]:
        """Get AI-powered symptom analysis"""
        
        prompt = f"""Analyze these medical symptoms and provide:
1. Brief summary of the condition
2. Possible medical conditions (list 2-3)
3. Severity level (LOW/MEDIUM/HIGH)

Symptoms: {symptom_text}

Respond in JSON format:
{{
    "summary": "brief analysis",
    "conditions": ["condition1", "condition2"],
    "severity": "MEDIUM"
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            # Try to parse JSON from response
            response_text = response.text.strip()
            
            # Extract JSON if wrapped in markdown
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            return json.loads(response_text)
        except:
            # Fallback
            return {
                'summary': 'Medical consultation recommended',
                'conditions': ['General health concern'],
                'severity': 'MEDIUM'
            }
    
    def _extract_specialists(self, symptom_text: str, analysis: Dict) -> List[str]:
        """Extract recommended specialists based on symptoms"""
        specialists = set()
        text_lower = symptom_text.lower()
        
        # Check keyword mapping
        for keyword, specs in self.specialty_mapping.items():
            if keyword in text_lower:
                specialists.update(specs)
        
        # If no match, default to general physician
        if not specialists:
            specialists.add('General Physician')
        
        return list(specialists)[:3]  # Return top 3
    
    def _generate_clarifying_questions(self, symptom_text: str, analysis: Dict, language: str) -> List[str]:
        """Generate clarifying questions"""
        
        prompt = f"""Based on these symptoms, generate 2-3 brief clarifying questions a doctor would ask.

Symptoms: {symptom_text}

Language: {'Bangla' if language == 'bn' else 'English'}

Return only the questions, one per line."""
        
        try:
            response = self.model.generate_content(prompt)
            questions = [q.strip() for q in response.text.split('\n') if q.strip() and len(q.strip()) > 10]
            return questions[:3]
        except:
            if language == 'bn':
                return [
                    "এই লক্ষণগুলি কতদিন ধরে আছে?",
                    "ব্যথার মাত্রা কেমন (১-১০ স্কেলে)?",
                    "আপনার কি অন্য কোনো স্বাস্থ্য সমস্যা আছে?"
                ]
            else:
                return [
                    "How long have you had these symptoms?",
                    "On a scale of 1-10, how severe is the pain?",
                    "Do you have any other medical conditions?"
                ]
    
    def _determine_urgency(self, symptom_text: str, analysis: Dict) -> str:
        """Determine urgency level"""
        severity = analysis.get('severity', 'MEDIUM').upper()
        
        if severity == 'HIGH':
            return 'HIGH'
        elif severity == 'LOW':
            return 'LOW'
        else:
            return 'MEDIUM'
    
    def _get_emergency_action(self, language: str) -> str:
        """Get emergency action message"""
        if language == 'bn':
            return "অবিলম্বে নিকটতম জরুরি বিভাগে যান বা ৯৯৯ এ কল করুন!"
        else:
            return "Go to the nearest emergency department immediately or call emergency services!"


# For testing
if __name__ == "__main__":
    analyzer = SymptomAnalyzer()
    
    # Test normal symptoms
    print("Test 1: Normal symptoms")
    result = analyzer.analyze_symptoms(
        "I have a headache and mild fever for 2 days",
        language='en'
    )
    print(json.dumps(result, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Test emergency
    print("Test 2: Emergency symptoms")
    result = analyzer.analyze_symptoms(
        "I have severe chest pain and difficulty breathing",
        language='en'
    )
    print(json.dumps(result, indent=2))
