// Disease-Symptom Database
const diseases = {
    'Common Cold': {
        symptoms: ['runny nose', 'sneezing', 'cough', 'mild fever', 'sore throat', 'headache'],
        description: 'A viral infection of the upper respiratory tract.',
        precautions: ['Rest well', 'Stay hydrated', 'Use throat lozenges', 'Gargle with warm salt water'],
        severity: 'mild'
    },
    'Influenza (Flu)': {
        symptoms: ['high fever', 'body aches', 'fatigue', 'cough', 'headache', 'sore throat'],
        description: 'A contagious respiratory illness caused by influenza viruses.',
        precautions: ['Bed rest', 'Fluids', 'Antiviral medications if prescribed', 'Avoid contact with others'],
        severity: 'moderate'
    },
    'Migraine': {
        symptoms: ['severe headache', 'nausea', 'sensitivity to light', 'sensitivity to sound', 'vomiting'],
        description: 'A neurological condition causing intense, debilitating headaches.',
        precautions: ['Rest in dark quiet room', 'Stay hydrated', 'Avoid triggers', 'Take prescribed medications'],
        severity: 'moderate'
    },
    'Gastroenteritis': {
        symptoms: ['nausea', 'vomiting', 'diarrhea', 'stomach pain', 'fever', 'headache'],
        description: 'Inflammation of the stomach and intestines, typically caused by a viral or bacterial infection.',
        precautions: ['Stay hydrated with ORS', 'Rest', 'Eat bland foods', 'Avoid dairy and caffeine'],
        severity: 'moderate'
    },
    'Allergic Rhinitis': {
        symptoms: ['runny nose', 'sneezing', 'itchy eyes', 'nasal congestion', 'watery eyes'],
        description: 'An allergic response causing symptoms similar to a cold.',
        precautions: ['Avoid allergens', 'Use air purifiers', 'Take antihistamines', 'Nasal irrigation'],
        severity: 'mild'
    },
    'Bronchitis': {
        symptoms: ['cough', 'chest discomfort', 'fatigue', 'mild fever', 'shortness of breath'],
        description: 'Inflammation of the bronchial tubes lining.',
        precautions: ['Rest', 'Increase fluid intake', 'Use humidifier', 'Avoid smoke and pollutants'],
        severity: 'moderate'
    },
    'Hypertension': {
        symptoms: ['headache', 'dizziness', 'blurred vision', 'chest pain', 'shortness of breath'],
        description: 'High blood pressure that can lead to serious health complications.',
        precautions: ['Regular exercise', 'Reduce sodium intake', 'Manage stress', 'Take prescribed medications'],
        severity: 'severe'
    },
    'Diabetes (Early Signs)': {
        symptoms: ['frequent urination', 'excessive thirst', 'fatigue', 'blurred vision', 'slow healing'],
        description: 'Metabolic disorder affecting blood sugar regulation.',
        precautions: ['Monitor blood sugar', 'Follow diabetic diet', 'Regular exercise', 'Regular checkups'],
        severity: 'severe'
    },
    'Anxiety Disorder': {
        symptoms: ['restlessness', 'fatigue', 'difficulty concentrating', 'irritability', 'sleep problems', 'muscle tension'],
        description: 'Mental health condition characterized by excessive worry and fear.',
        precautions: ['Practice relaxation techniques', 'Regular exercise', 'Limit caffeine', 'Seek professional help'],
        severity: 'moderate'
    },
    'Dengue Fever': {
        symptoms: ['high fever', 'severe headache', 'joint pain', 'muscle pain', 'rash', 'nausea'],
        description: 'A mosquito-borne viral infection common in tropical areas.',
        precautions: ['Stay hydrated', 'Rest', 'Monitor platelet count', 'Seek immediate medical care'],
        severity: 'severe'
    }
};

// Symptom list for UI
const symptomList = [
    'headache', 'fever', 'cough', 'runny nose', 'sore throat',
    'body aches', 'fatigue', 'nausea', 'vomiting', 'diarrhea',
    'stomach pain', 'chest pain', 'shortness of breath', 'dizziness',
    'blurred vision', 'joint pain', 'muscle pain', 'rash',
    'sneezing', 'itchy eyes', 'nasal congestion', 'watery eyes',
    'sensitivity to light', 'sensitivity to sound', 'restlessness',
    'difficulty concentrating', 'irritability', 'sleep problems',
    'muscle tension', 'excessive thirst', 'frequent urination',
    'slow healing', 'mild fever', 'high fever', 'severe headache'
];

// Hospitals data — major hospitals across India
const hospitals = [
    // Delhi / NCR
    { id: 1, name: 'AIIMS New Delhi', type: 'Government', address: 'Ansari Nagar, New Delhi', city: 'Delhi', phone: '011-26588500', rating: 4.7, lat: 28.5672, lng: 77.2100 },
    { id: 2, name: 'Apollo Hospital Delhi', type: 'Private Hospital', address: 'Sarita Vihar, New Delhi', city: 'Delhi', phone: '011-71791090', rating: 4.5, lat: 28.5330, lng: 77.2820 },
    { id: 3, name: 'Fortis Escorts Heart Institute', type: 'Cardiac Specialty', address: 'Okhla Road, New Delhi', city: 'Delhi', phone: '011-47122222', rating: 4.6, lat: 28.5635, lng: 77.2760 },
    { id: 4, name: 'Medanta – The Medicity', type: 'Multi-specialty', address: 'Sector 38, Gurugram', city: 'Gurugram', phone: '0124-4141414', rating: 4.5, lat: 28.2610, lng: 77.0650 },
    // Mumbai
    { id: 5, name: 'Kokilaben Dhirubhai Ambani Hospital', type: 'Multi-specialty', address: 'Andheri West, Mumbai', city: 'Mumbai', phone: '022-42696969', rating: 4.6, lat: 19.1330, lng: 72.8230 },
    { id: 6, name: 'Tata Memorial Hospital', type: 'Cancer Specialty', address: 'Parel, Mumbai', city: 'Mumbai', phone: '022-24177000', rating: 4.5, lat: 18.9970, lng: 72.8420 },
    { id: 7, name: 'Lilavati Hospital', type: 'Private Hospital', address: 'Bandra West, Mumbai', city: 'Mumbai', phone: '022-26751000', rating: 4.4, lat: 19.0470, lng: 72.8300 },
    // Bengaluru
    { id: 8, name: 'Manipal Hospital Old Airport Road', type: 'Multi-specialty', address: 'Kodihalli, Bengaluru', city: 'Bengaluru', phone: '080-25024444', rating: 4.4, lat: 12.9550, lng: 77.6480 },
    { id: 9, name: 'Narayana Health City', type: 'Multi-specialty', address: 'Bommasandra, Bengaluru', city: 'Bengaluru', phone: '080-71222222', rating: 4.5, lat: 12.8000, lng: 77.6900 },
    // Chennai
    { id: 10, name: 'Apollo Hospitals Greams Road', type: 'Multi-specialty', address: 'Greams Road, Chennai', city: 'Chennai', phone: '044-28296569', rating: 4.5, lat: 13.0620, lng: 80.2540 },
    { id: 11, name: 'MIOT International', type: 'Multi-specialty', address: 'Manapakkam, Chennai', city: 'Chennai', phone: '044-42002288', rating: 4.4, lat: 13.0170, lng: 80.1780 },
    // Hyderabad
    { id: 12, name: 'Apollo Hospitals Jubilee Hills', type: 'Multi-specialty', address: 'Jubilee Hills, Hyderabad', city: 'Hyderabad', phone: '040-23607777', rating: 4.5, lat: 17.4260, lng: 78.4120 },
    { id: 13, name: 'Yashoda Hospitals Somajiguda', type: 'Multi-specialty', address: 'Somajiguda, Hyderabad', city: 'Hyderabad', phone: '040-45678900', rating: 4.3, lat: 17.4200, lng: 78.4500 },
    // Kolkata
    { id: 14, name: 'Apollo Multispecialty Hospitals', type: 'Multi-specialty', address: 'Canal Circular Road, Kolkata', city: 'Kolkata', phone: '033-39882000', rating: 4.4, lat: 22.5700, lng: 88.3900 },
    { id: 15, name: 'Fortis Hospital Anandapur', type: 'Private Hospital', address: 'Anandapur, Kolkata', city: 'Kolkata', phone: '033-66284444', rating: 4.3, lat: 22.5020, lng: 88.3950 },
    // Other major cities
    { id: 16, name: 'PGIMER Chandigarh', type: 'Government', address: 'Sector 12, Chandigarh', city: 'Chandigarh', phone: '0172-2747585', rating: 4.5, lat: 30.7620, lng: 76.7720 },
    { id: 17, name: 'SMS Hospital Jaipur', type: 'Government', address: 'JLN Marg, Jaipur', city: 'Jaipur', phone: '0141-2518121', rating: 4.1, lat: 26.8900, lng: 75.8100 },
    { id: 18, name: 'King George Medical University', type: 'Government', address: 'Chowk, Lucknow', city: 'Lucknow', phone: '0522-2257450', rating: 4.2, lat: 26.8670, lng: 80.9200 },
    { id: 19, name: 'CMC Vellore', type: 'Multi-specialty', address: 'Ida Scudder Road, Vellore', city: 'Vellore', phone: '0416-2281000', rating: 4.7, lat: 12.9240, lng: 79.1360 },
    { id: 20, name: 'KEM Hospital Pune', type: 'Government', address: 'Rasta Peth, Pune', city: 'Pune', phone: '020-26123000', rating: 4.2, lat: 18.5200, lng: 73.8720 }
];

// Health tips
const healthTips = [
    "Stay hydrated! Drinking 8 glasses of water daily helps maintain optimal body function.",
    "Get 7-9 hours of sleep each night to support immune function and mental health.",
    "Take regular breaks from screens to reduce eye strain and headaches.",
    "Practice deep breathing exercises to manage stress and anxiety.",
    "Maintain a balanced diet rich in fruits and vegetables for better immunity.",
    "Regular physical activity can reduce the risk of chronic diseases.",
    "Wash your hands frequently to prevent the spread of infections."
];

// Translation data
const translations = {
    en: {
        welcome: 'Hello! I\'m your AI Health Assistant.',
        emergency: 'Emergency Mode Active',
        predictResults: 'Based on your symptoms, here are possible conditions:'
    },
    hi: {
        welcome: 'नमस्ते! मैं आपका AI स्वास्थ्य सहायक हूं।',
        emergency: 'आपातकालीन मोड सक्रिय',
        predictResults: 'आपके लक्षणों के आधार पर, संभावित स्थितियां यहां दी गई हैं:'
    },
    te: {
        welcome: 'నమస్కారం! నేను మీ AI ఆరోగ్య సహాయకుడిని.',
        emergency: 'అత్యవసర మోడ్ యాక్టివ్',
        predictResults: 'మీ లక్షణాల ఆధారంగా, ఇక్కడ సంభావ్య పరిస్థితులు ఉన్నాయి:'
    }
};