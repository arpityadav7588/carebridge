"""
Recommender Module
Recommends doctors and clinics based on symptoms, location, and availability
"""

import google.generativeai as genai
from src.config import Config
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta

class DoctorRecommender:
    """Recommends doctors and clinics based on patient needs"""
    
    def __init__(self):
        """Initialize recommender with mock hospital database"""
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_TEXT_MODEL)
        
        # Mock database of hospitals/clinics (for MVP)
        self.hospitals = self._create_mock_database()
    
    def _create_mock_database(self) -> List[Dict[str, Any]]:
        """Create mock hospital/clinic database"""
        return [
            {
                'id': 'h001',
                'name': 'City General Hospital',
                'location': 'Dhaka, Dhanmondi',
                'distance_km': 2.5,
                'rating': 4.5,
                'specialties': [
                    'Cardiology', 'Neurology', 'Orthopedics', 
                    'General Medicine', 'Emergency Medicine'
                ],
                'facilities': ['ICU', 'Emergency', 'Diagnostic Center', 'Pharmacy'],
                'doctors': [
                    {
                        'name': 'Dr. Ahmed Rahman',
                        'specialty': 'Cardiologist',
                        'experience_years': 15,
                        'available_slots': ['10:00 AM', '2:00 PM', '4:00 PM']
                    },
                    {
                        'name': 'Dr. Fatima Khan',
                        'specialty': 'Neurologist',
                        'experience_years': 12,
                        'available_slots': ['11:00 AM', '3:00 PM']
                    }
                ],
                'booking_method': 'online_portal',
                'portal_url': 'https://citygeneralhospital.com/appointments',
                'contact': '+880-2-9876543'
            },
            {
                'id': 'h002',
                'name': 'Square Hospital',
                'location': 'Dhaka, Panthapath',
                'distance_km': 5.0,
                'rating': 4.8,
                'specialties': [
                    'Cardiology', 'Oncology', 'Neurology', 'Pediatrics',
                    'Dermatology', 'Orthopedics', 'General Medicine'
                ],
                'facilities': ['ICU', 'NICU', 'Emergency', 'Diagnostic Center', 'Pharmacy', 'Ambulance'],
                'doctors': [
                    {
                        'name': 'Dr. Kamal Hossain',
                        'specialty': 'Cardiologist',
                        'experience_years': 20,
                        'available_slots': ['9:00 AM', '1:00 PM']
                    },
                    {
                        'name': 'Dr. Nadia Islam',
                        'specialty': 'Dermatologist',
                        'experience_years': 10,
                        'available_slots': ['10:00 AM', '2:00 PM', '5:00 PM']
                    }
                ],
                'booking_method': 'email',
                'email': 'appointments@squarehospital.com',
                'contact': '+880-2-8159457'
            },
            {
                'id': 'h003',
                'name': 'United Hospital',
                'location': 'Dhaka, Gulshan',
                'distance_km': 7.5,
                'rating': 4.7,
                'specialties': [
                    'Cardiology', 'Neurosurgery', 'Orthopedics',
                    'Gastroenterology', 'Nephrology', 'Emergency Medicine'
                ],
                'facilities': ['ICU', 'CCU', 'Emergency', 'Diagnostic Center', 'Pharmacy', 'Ambulance'],
                'doctors': [
                    {
                        'name': 'Dr. Rashid Ahmed',
                        'specialty': 'Orthopedic Surgeon',
                        'experience_years': 18,
                        'available_slots': ['11:00 AM', '4:00 PM']
                    },
                    {
                        'name': 'Dr. Sabrina Chowdhury',
                        'specialty': 'Gastroenterologist',
                        'experience_years': 14,
                        'available_slots': ['10:00 AM', '3:00 PM']
                    }
                ],
                'booking_method': 'online_portal',
                'portal_url': 'https://unitedhospital.com/book',
                'contact': '+880-2-8836000'
            }
        ]
    
    def recommend_doctors(
        self,
        specialists: List[str],
        location: str = "Dhaka",
        urgency: str = "MEDIUM",
        max_distance_km: float = 10.0
    ) -> Dict[str, Any]:
        """
        Recommend doctors and clinics based on requirements
        
        Args:
            specialists: List of required specialist types
            location: Patient location
            urgency: Urgency level (LOW/MEDIUM/HIGH/CRITICAL)
            max_distance_km: Maximum distance willing to travel
            
        Returns:
            Recommendations with trade-offs
        """
        try:
            # Filter hospitals by specialty and distance
            matching_hospitals = self._filter_hospitals(
                specialists, max_distance_km
            )
            
            if not matching_hospitals:
                return {
                    'success': False,
                    'message': 'No matching hospitals found',
                    'recommendations': []
                }
            
            # Rank hospitals
            ranked_hospitals = self._rank_hospitals(
                matching_hospitals, urgency
            )
            
            # Format recommendations
            recommendations = self._format_recommendations(
                ranked_hospitals, specialists
            )
            
            return {
                'success': True,
                'count': len(recommendations),
                'recommendations': recommendations,
                'urgency': urgency
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'recommendations': []
            }
    
    def _filter_hospitals(
        self,
        specialists: List[str],
        max_distance: float
    ) -> List[Dict[str, Any]]:
        """Filter hospitals by specialty and distance"""
        matching = []
        
        for hospital in self.hospitals:
            # Check distance
            if hospital['distance_km'] > max_distance:
                continue
            
            # Check if hospital has required specialty
            hospital_specialties_lower = [s.lower() for s in hospital['specialties']]
            
            # Check for general physician - all hospitals have this
            if any('general' in s.lower() for s in specialists):
                matching.append(hospital)
                continue
            
            for specialist in specialists:
                specialist_lower = specialist.lower()
                # Partial matching
                if any(specialist_lower in hs or hs in specialist_lower 
                       for hs in hospital_specialties_lower):
                    matching.append(hospital)
                    break
        
        return matching
    
    def _rank_hospitals(
        self,
        hospitals: List[Dict[str, Any]],
        urgency: str
    ) -> List[Dict[str, Any]]:
        """Rank hospitals based on urgency and other factors"""
        
        def calculate_score(hospital):
            score = 0
            
            # Rating (0-5 points)
            score += hospital['rating']
            
            # Distance (closer is better, 0-5 points)
            distance_score = max(0, 5 - (hospital['distance_km'] / 2))
            score += distance_score
            
            # Facilities (more is better, 0-3 points)
            facilities_score = min(3, len(hospital['facilities']) / 2)
            score += facilities_score
            
            # Urgency factor
            if urgency == 'CRITICAL':
                # Prioritize distance for emergencies
                score += (10 - hospital['distance_km'])
            elif urgency == 'HIGH':
                score += (5 - hospital['distance_km'] / 2)
            
            return score
        
        # Sort by score (descending)
        ranked = sorted(hospitals, key=calculate_score, reverse=True)
        return ranked
    
    def _format_recommendations(
        self,
        hospitals: List[Dict[str, Any]],
        specialists: List[str]
    ) -> List[Dict[str, Any]]:
        """Format hospital recommendations with trade-offs"""
        recommendations = []
        
        for hospital in hospitals:
            # Find matching doctors
            matching_doctors = []
            for doctor in hospital['doctors']:
                for specialist in specialists:
                    if specialist.lower() in doctor['specialty'].lower():
                        matching_doctors.append(doctor)
                        break
            
            # Calculate trade-offs
            trade_offs = self._calculate_trade_offs(hospital)
            
            recommendation = {
                'hospital_id': hospital['id'],
                'hospital_name': hospital['name'],
                'location': hospital['location'],
                'distance_km': hospital['distance_km'],
                'rating': hospital['rating'],
                'matching_doctors': matching_doctors,
                'facilities': hospital['facilities'],
                'booking_method': hospital['booking_method'],
                'contact': hospital['contact'],
                'trade_offs': trade_offs
            }
            
            # Add booking details
            if hospital['booking_method'] == 'online_portal':
                recommendation['portal_url'] = hospital.get('portal_url')
            elif hospital['booking_method'] == 'email':
                recommendation['email'] = hospital.get('email')
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _calculate_trade_offs(self, hospital: Dict[str, Any]) -> Dict[str, str]:
        """Calculate trade-offs for each hospital"""
        trade_offs = {}
        
        # Distance trade-off
        if hospital['distance_km'] < 3:
            trade_offs['distance'] = 'Very close - convenient'
        elif hospital['distance_km'] < 6:
            trade_offs['distance'] = 'Moderate distance'
        else:
            trade_offs['distance'] = 'Farther away - may need transport'
        
        # Rating trade-off
        if hospital['rating'] >= 4.5:
            trade_offs['quality'] = 'Highly rated'
        elif hospital['rating'] >= 4.0:
            trade_offs['quality'] = 'Good rating'
        else:
            trade_offs['quality'] = 'Average rating'
        
        # Facilities trade-off
        if len(hospital['facilities']) >= 5:
            trade_offs['facilities'] = 'Comprehensive facilities'
        elif len(hospital['facilities']) >= 3:
            trade_offs['facilities'] = 'Good facilities'
        else:
            trade_offs['facilities'] = 'Basic facilities'
        
        # Booking trade-off
        if hospital['booking_method'] == 'online_portal':
            trade_offs['booking'] = 'Easy online booking'
        else:
            trade_offs['booking'] = 'Email/phone booking required'
        
        return trade_offs
    
    def get_hospital_details(self, hospital_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific hospital"""
        for hospital in self.hospitals:
            if hospital['id'] == hospital_id:
                return hospital
        return None


# For testing
if __name__ == "__main__":
    recommender = DoctorRecommender()
    
    # Test recommendation
    print("Test: Recommend cardiologists")
    result = recommender.recommend_doctors(
        specialists=['Cardiologist'],
        urgency='HIGH'
    )
    
    print(f"\nFound {result['count']} recommendations:\n")
    for rec in result['recommendations']:
        print(f"Hospital: {rec['hospital_name']}")
        print(f"Distance: {rec['distance_km']} km")
        print(f"Rating: {rec['rating']}/5")
        print(f"Doctors: {len(rec['matching_doctors'])}")
        print(f"Trade-offs: {rec['trade_offs']}")
        print("-" * 50)
