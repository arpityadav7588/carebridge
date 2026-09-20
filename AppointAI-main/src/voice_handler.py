"""
Voice Handler Module
Handles voice input/output using Gemini API
For hackathon: Simulates real-time interaction with quick response times
"""

import google.generativeai as genai
from src.config import Config
import json
from typing import Optional, Dict, Any

class VoiceHandler:
    """Handles voice-based interaction with Gemini"""
    
    def __init__(self):
        """Initialize voice handler with Gemini API"""
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_TEXT_MODEL)
        self.conversation_history = []
        self.current_language = Config.DEFAULT_LANGUAGE
        
    def process_voice_input(self, text: str, language: str = 'en') -> Dict[str, Any]:
        """
        Process voice input text and generate response
        
        Args:
            text: Transcribed voice input
            language: Language code ('en' or 'bn')
            
        Returns:
            Dict with response text and metadata
        """
        self.current_language = language
        
        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': text
        })
        
        # Generate response
        try:
            response = self._generate_response(text, language)
            
            # Add to history
            self.conversation_history.append({
                'role': 'assistant',
                'content': response
            })
            
            return {
                'success': True,
                'response': response,
                'language': language,
                'can_interrupt': True  # Simulates interruptible conversation
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': self._get_error_message(language)
            }
    
    def _generate_response(self, text: str, language: str) -> str:
        """Generate AI response using Gemini"""
        
        # Build context-aware prompt
        system_prompt = self._get_system_prompt(language)
        full_prompt = f"{system_prompt}\n\nUser: {text}\n\nAssistant:"
        
        # Generate response
        response = self.model.generate_content(full_prompt)
        return response.text
    
    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt based on language"""
        
        if language == 'bn':
            return """আপনি একজন স্বাস্থ্যসেবা সহায়ক। আপনার কাজ হল:
1. রোগীর লক্ষণ বুঝুন
2. প্রয়োজনে স্পষ্টকারী প্রশ্ন জিজ্ঞাসা করুন
3. উপযুক্ত ডাক্তার এবং ক্লিনিক সুপারিশ করুন
4. জরুরি অবস্থা সনাক্ত করুন

সংক্ষিপ্ত, স্পষ্ট এবং সহানুভূতিশীল উত্তর দিন।"""
        
        else:  # English
            return """You are a healthcare assistant for Appoint. Your role is to:
1. Understand patient symptoms
2. Ask clarifying questions when needed
3. Recommend appropriate doctors and clinics
4. Detect emergency situations

Be concise, clear, and empathetic. Keep responses short and actionable."""
    
    def _get_error_message(self, language: str) -> str:
        """Get error message in appropriate language"""
        if language == 'bn':
            return "দুঃখিত, একটি ত্রুটি ঘটেছে। অনুগ্রহ করে আবার চেষ্টা করুন।"
        else:
            return "Sorry, an error occurred. Please try again."
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
    
    def get_conversation_context(self) -> str:
        """Get conversation history as context string"""
        context = ""
        for msg in self.conversation_history[-5:]:  # Last 5 messages
            role = msg['role'].capitalize()
            content = msg['content']
            context += f"{role}: {content}\n"
        return context


# For testing
if __name__ == "__main__":
    handler = VoiceHandler()
    
    # Test English
    print("Testing English...")
    result = handler.process_voice_input(
        "I have a severe headache and fever for 3 days",
        language='en'
    )
    print(f"Response: {result['response']}\n")
    
    # Test Bangla
    print("Testing Bangla...")
    result = handler.process_voice_input(
        "আমার মাথা ব্যথা এবং জ্বর আছে",
        language='bn'
    )
    print(f"Response: {result['response']}")
