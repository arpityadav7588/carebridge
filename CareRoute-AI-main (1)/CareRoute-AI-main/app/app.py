import streamlit as st
import sys
from pathlib import Path
import io
import math
import pandas as pd


# ============================================================
# PATHS
# ============================================================

APP_DIR = Path(__file__).parent
PROJECT_DIR = APP_DIR.parent

sys.path.append(str(APP_DIR))


# ============================================================
# IMPORTS
# ============================================================

from questions import SYMPTOMS, TRANSLATIONS
from safety import check_red_flags
from triage import (
    predict_department,
    rule_based_prediction,
    MODEL,
    FEATURES
)

from recommendations import (
    get_department_description,
    get_department_name
)

from maps import (
    get_nearby_hospitals_url,
    get_emergency_hospital_url
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareRoute AI",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = 1

if "language" not in st.session_state:
    st.session_state.language = "English"


# ============================================================
# UI TEXT
# ============================================================

UI = {

    # ========================================================
    # ENGLISH
    # ========================================================

    "English": {

        "title": "CareRoute AI",
        "subtitle": "Smart Healthcare Guidance",

        "language": "🌐 Select Your Language",
        "language_help": "Choose the language you want to use.",
        "continue": "Continue →",

        "what": "✨ What You Can Do",
        "what_subtitle":
            "Simple and accessible healthcare navigation.",

        "speak": "Speak Your Symptoms",
        "speak_desc":
            "Tell us what you are experiencing using your voice.",

        "department": "Get Department",
        "department_desc":
            "Receive a healthcare department recommendation.",

        "hospital": "Find Nearby Hospitals",
        "hospital_desc":
            "Open Google Maps to find nearby healthcare facilities.",

        # PAGE 2

        "back": "← Back",

        "page2_title":
            "Tell Us Your Symptoms",

        "page2_subtitle":
            "Speak your symptoms or select them manually.",

        "patient":
            "👤 Patient Information",

        "name":
            "Name",

        "name_placeholder":
            "Enter patient name",

        "age":
            "Age",

        "voice_title":
            "🎙️ Speak Your Symptoms",

        "voice_desc":
            "Describe what you are experiencing naturally.",

        "voice_instruction":
            "Click the microphone and speak clearly.",

        "record":
            "🎙️ Record Your Symptoms",

        "record_received":
            "✅ Voice recording received.",

        "understood":
            "📝 What we understood:",

        "detected":
            "🔎 Detected symptoms:",

        "voice_no_symptom":
            "No known symptom was detected from your speech. "
            "Please try again or select symptoms manually.",

        "voice_error":
            "We could not understand the voice recording. "
            "Please try recording again or select the symptoms manually.",

        "manual_title":
            "🩺 Select Symptoms",

        "manual_desc":
            "Optional: select any additional symptoms.",

        "symptom_question":
            "What symptoms are you experiencing?",

        "symptom_placeholder":
            "Select one or more symptoms",

        "additional":
            "📋 Additional Information",

        "duration":
            "How long have you had these symptoms?",

        "duration_options": [
            "Less than 1 day",
            "1–3 days",
            "4–7 days",
            "More than 1 week",
            "More than 1 month"
        ],

        "severity":
            "How severe are your symptoms?",

        "severity_options": [
            "Mild",
            "Moderate",
            "Severe"
        ],

        "recommend":
            "🔍 Find My Recommendation",

        "no_symptoms":
            "Please speak or select at least one symptom.",

        "urgent":
            "🚨 Urgent Attention Recommended",

        "urgent_message":
            "Some of the symptoms you selected may require urgent "
            "medical attention. Please seek immediate medical care "
            "or contact your local emergency service.",

        "urgent_warning":
            "Do not rely on this application for emergency medical "
            "decisions. Please seek immediate professional medical care.",

        "recommended":
            "🏥 Recommended Department",

        "why":
            "💡 Why this department?",

        "summary":
            "📄 Patient Summary",

        "summary_name":
            "Name",

        "summary_age":
            "Age",

        "summary_language":
            "Language",

        "summary_symptoms":
            "Symptoms",

        "summary_duration":
            "Duration",

        "summary_severity":
            "Severity",

        "summary_department":
            "Recommended Department",

        "nearby":
            "📍 Nearby Hospitals",

        "nearby_desc":
            "Find healthcare facilities related to the recommended department.",

        "maps":
            "📍 Open Google Maps",

        "listen":
            "🔊 Listen to Recommendation",

        "model_note":
            "This recommendation is based on the symptoms provided "
            "and the trained CareRoute AI model.",

        "new_patient":
            "👤 Continue With Another Patient",

        "new_patient_desc":
            "Start a fresh assessment for another patient.",

        "new_patient_button":
            "➕ Continue With Another Patient",

        "disclaimer":
            "⚠️ CareRoute AI provides general healthcare navigation only. "
            "It does not diagnose diseases or replace professional medical advice.",

        "footer":
            "CareRoute AI • Healthcare navigation support • Not a diagnostic system"
    },


    # ========================================================
    # TELUGU
    # ========================================================

    "Telugu": {

        "title":
            "కేర్‌రూట్ AI",

        "subtitle":
            "స్మార్ట్ ఆరోగ్య మార్గదర్శకత్వం",

        "language":
            "🌐 మీ భాషను ఎంచుకోండి",

        "language_help":
            "మీరు ఉపయోగించాలనుకునే భాషను ఎంచుకోండి.",

        "continue":
            "కొనసాగించండి →",

        "what":
            "✨ మీరు ఏమి చేయవచ్చు",

        "what_subtitle":
            "సులభమైన ఆరోగ్య మార్గదర్శకత్వం.",

        "speak":
            "మీ లక్షణాలను చెప్పండి",

        "speak_desc":
            "మీకు ఉన్న లక్షణాలను మీ స్వరంతో చెప్పండి.",

        "department":
            "విభాగాన్ని పొందండి",

        "department_desc":
            "మీ లక్షణాల ఆధారంగా ఆరోగ్య విభాగం సూచన పొందండి.",

        "hospital":
            "సమీపంలోని ఆసుపత్రులను కనుగొనండి",

        "hospital_desc":
            "సమీపంలోని ఆరోగ్య కేంద్రాలను కనుగొనడానికి Google Maps తెరవండి.",

        "back":
            "← వెనక్కి",

        "page2_title":
            "మీ లక్షణాలను చెప్పండి",

        "page2_subtitle":
            "మీ లక్షణాలను మాట్లాడండి లేదా మాన్యువల్‌గా ఎంచుకోండి.",

        "patient":
            "👤 రోగి సమాచారం",

        "name":
            "పేరు",

        "name_placeholder":
            "రోగి పేరును నమోదు చేయండి",

        "age":
            "వయస్సు",

        "voice_title":
            "🎙️ మీ లక్షణాలను మాట్లాడండి",

        "voice_desc":
            "మీకు ఉన్న సమస్యలను సహజంగా మాట్లాడి చెప్పండి.",

        "voice_instruction":
            "మైక్రోఫోన్‌పై క్లిక్ చేసి స్పష్టంగా మాట్లాడండి.",

        "record":
            "🎙️ మీ లక్షణాలను రికార్డ్ చేయండి",

        "record_received":
            "✅ మీ వాయిస్ రికార్డింగ్ అందింది.",

        "understood":
            "📝 మేము అర్థం చేసుకున్నది:",

        "detected":
            "🔎 గుర్తించిన లక్షణాలు:",

        "voice_no_symptom":
            "మీ మాటల నుండి తెలిసిన లక్షణం గుర్తించబడలేదు. "
            "మళ్ళీ ప్రయత్నించండి లేదా లక్షణాలను మాన్యువల్‌గా ఎంచుకోండి.",

        "voice_error":
            "వాయిస్ రికార్డింగ్‌ను అర్థం చేసుకోలేకపోయాము. "
            "దయచేసి మళ్ళీ రికార్డ్ చేయండి లేదా లక్షణాలను మాన్యువల్‌గా ఎంచుకోండి.",

        "manual_title":
            "🩺 లక్షణాలను ఎంచుకోండి",

        "manual_desc":
            "ఐచ్ఛికం: అవసరమైతే అదనపు లక్షణాలను ఎంచుకోండి.",

        "symptom_question":
            "మీకు ప్రస్తుతం ఏ లక్షణాలు ఉన్నాయి?",

        "symptom_placeholder":
            "ఒకటి లేదా అంతకంటే ఎక్కువ లక్షణాలను ఎంచుకోండి",

        "additional":
            "📋 అదనపు సమాచారం",

        "duration":
            "ఈ లక్షణాలు మీకు ఎంతకాలంగా ఉన్నాయి?",

        "duration_options": [
            "1 రోజు కంటే తక్కువ",
            "1–3 రోజులు",
            "4–7 రోజులు",
            "1 వారం కంటే ఎక్కువ",
            "1 నెల కంటే ఎక్కువ"
        ],

        "severity":
            "మీ లక్షణాల తీవ్రత ఎంత?",

        "severity_options": [
            "తక్కువ",
            "మధ్యస్థం",
            "తీవ్రమైనది"
        ],

        "recommend":
            "🔍 నా సిఫార్సును పొందండి",

        "no_symptoms":
            "దయచేసి కనీసం ఒక లక్షణాన్ని మాట్లాడండి లేదా ఎంచుకోండి.",

        "urgent":
            "🚨 అత్యవసర వైద్య సహాయం అవసరం కావచ్చు",

        "urgent_message":
            "మీరు ఎంచుకున్న కొన్ని లక్షణాలకు తక్షణ వైద్య సహాయం అవసరం కావచ్చు. "
            "దయచేసి వెంటనే వైద్య సహాయం పొందండి లేదా స్థానిక అత్యవసర సేవలను సంప్రదించండి.",

        "urgent_warning":
            "అత్యవసర వైద్య నిర్ణయాల కోసం ఈ అప్లికేషన్‌పై ఆధారపడకండి. "
            "వెంటనే వైద్య సహాయం పొందండి.",

        "recommended":
            "🏥 సిఫార్సు చేసిన విభాగం",

        "why":
            "💡 ఈ విభాగాన్ని ఎందుకు సూచించాము?",

        "summary":
            "📄 రోగి సారాంశం",

        "summary_name":
            "పేరు",

        "summary_age":
            "వయస్సు",

        "summary_language":
            "భాష",

        "summary_symptoms":
            "లక్షణాలు",

        "summary_duration":
            "లక్షణాల వ్యవధి",

        "summary_severity":
            "తీవ్రత",

        "summary_department":
            "సిఫార్సు చేసిన విభాగం",

        "nearby":
            "📍 సమీపంలోని ఆసుపత్రులు",

        "nearby_desc":
            "సిఫార్సు చేసిన విభాగానికి సంబంధించిన ఆరోగ్య కేంద్రాలను కనుగొనండి.",

        "maps":
            "📍 Google Maps తెరవండి",

        "listen":
            "🔊 సిఫార్సును వినండి",

        "model_note":
            "ఈ సిఫార్సు మీరు అందించిన లక్షణాలు మరియు CareRoute AI మోడల్‌పై ఆధారపడి ఉంటుంది.",

        "new_patient":
            "👤 మరొక రోగితో కొనసాగించండి",

        "new_patient_desc":
            "మరొక రోగి కోసం కొత్త ఆరోగ్య అంచనాను ప్రారంభించండి.",

        "new_patient_button":
            "➕ మరొక రోగితో కొనసాగించండి",

        "disclaimer":
            "⚠️ CareRoute AI సాధారణ ఆరోగ్య మార్గదర్శకత్వం కోసం మాత్రమే. "
            "ఇది వ్యాధులను నిర్ధారించదు మరియు వైద్యుల సలహాకు ప్రత్యామ్నాయం కాదు.",

        "footer":
            "కేర్‌రూట్ AI • ఆరోగ్య మార్గదర్శకత్వం • వ్యాధి నిర్ధారణ వ్యవస్థ కాదు"
    },


    # ========================================================
    # HINDI
    # ========================================================

    "Hindi": {

        "title":
            "CareRoute AI",

        "subtitle":
            "स्मार्ट स्वास्थ्य मार्गदर्शन",

        "language":
            "🌐 अपनी भाषा चुनें",

        "language_help":
            "वह भाषा चुनें जिसका आप उपयोग करना चाहते हैं।",

        "continue":
            "जारी रखें →",

        "what":
            "✨ आप क्या कर सकते हैं",

        "what_subtitle":
            "सरल और सुलभ स्वास्थ्य मार्गदर्शन।",

        "speak":
            "अपने लक्षण बोलें",

        "speak_desc":
            "अपनी समस्या के बारे में अपनी आवाज़ में बताएं।",

        "department":
            "विभाग की सिफारिश पाएं",

        "department_desc":
            "आपके लक्षणों के आधार पर स्वास्थ्य विभाग की सिफारिश पाएं।",

        "hospital":
            "पास के अस्पताल खोजें",

        "hospital_desc":
            "पास के स्वास्थ्य केंद्र खोजने के लिए Google Maps खोलें।",

        "back":
            "← वापस",

        "page2_title":
            "अपने लक्षण बताएं",

        "page2_subtitle":
            "अपने लक्षण बोलें या उन्हें मैन्युअल रूप से चुनें।",

        "patient":
            "👤 रोगी की जानकारी",

        "name":
            "नाम",

        "name_placeholder":
            "रोगी का नाम दर्ज करें",

        "age":
            "उम्र",

        "voice_title":
            "🎙️ अपने लक्षण बोलें",

        "voice_desc":
            "आप जो महसूस कर रहे हैं उसके बारे में स्वाभाविक रूप से बोलें।",

        "voice_instruction":
            "माइक्रोफोन पर क्लिक करें और स्पष्ट रूप से बोलें।",

        "record":
            "🎙️ अपने लक्षण रिकॉर्ड करें",

        "record_received":
            "✅ आपकी आवाज़ की रिकॉर्डिंग प्राप्त हुई।",

        "understood":
            "📝 हमने यह समझा:",

        "detected":
            "🔎 पहचाने गए लक्षण:",

        "voice_no_symptom":
            "आपकी आवाज़ से कोई ज्ञात लक्षण नहीं मिला। "
            "फिर से कोशिश करें या लक्षणों को मैन्युअल रूप से चुनें।",

        "voice_error":
            "आवाज़ की रिकॉर्डिंग को समझ नहीं सके। "
            "कृपया फिर से रिकॉर्ड करें या लक्षणों को मैन्युअल रूप से चुनें।",

        "manual_title":
            "🩺 लक्षण चुनें",

        "manual_desc":
            "वैकल्पिक: आवश्यकता होने पर अतिरिक्त लक्षण चुनें।",

        "symptom_question":
            "आपको वर्तमान में कौन से लक्षण हो रहे हैं?",

        "symptom_placeholder":
            "एक या अधिक लक्षण चुनें",

        "additional":
            "📋 अतिरिक्त जानकारी",

        "duration":
            "आपको ये लक्षण कितने समय से हैं?",

        "duration_options": [
            "1 दिन से कम",
            "1–3 दिन",
            "4–7 दिन",
            "1 सप्ताह से अधिक",
            "1 महीने से अधिक"
        ],

        "severity":
            "आपके लक्षण कितने गंभीर हैं?",

        "severity_options": [
            "हल्के",
            "मध्यम",
            "गंभीर"
        ],

        "recommend":
            "🔍 मेरी सिफारिश पाएं",

        "no_symptoms":
            "कृपया कम से कम एक लक्षण बोलें या चुनें।",

        "urgent":
            "🚨 तुरंत चिकित्सा सहायता की आवश्यकता हो सकती है",

        "urgent_message":
            "आपके द्वारा बताए गए कुछ लक्षणों के लिए तत्काल चिकित्सा सहायता की आवश्यकता हो सकती है। "
            "कृपया तुरंत चिकित्सा सहायता लें या स्थानीय आपातकालीन सेवा से संपर्क करें।",

        "urgent_warning":
            "आपातकालीन चिकित्सा निर्णयों के लिए इस एप्लिकेशन पर निर्भर न रहें। "
            "तुरंत पेशेवर चिकित्सा सहायता लें।",

        "recommended":
            "🏥 सुझाया गया विभाग",

        "why":
            "💡 यह विभाग क्यों सुझाया गया?",

        "summary":
            "📄 रोगी सारांश",

        "summary_name":
            "नाम",

        "summary_age":
            "उम्र",

        "summary_language":
            "भाषा",

        "summary_symptoms":
            "लक्षण",

        "summary_duration":
            "लक्षणों की अवधि",

        "summary_severity":
            "गंभीरता",

        "summary_department":
            "सुझाया गया विभाग",

        "nearby":
            "📍 पास के अस्पताल",

        "nearby_desc":
            "अनुशंसित विभाग से संबंधित स्वास्थ्य सुविधाएं खोजें।",

        "maps":
            "📍 Google Maps खोलें",

        "listen":
            "🔊 सुझाव सुनें",

        "model_note":
            "यह सुझाव आपके बताए गए लक्षणों और CareRoute AI के प्रशिक्षित मॉडल पर आधारित है।",

        "new_patient":
            "👤 दूसरे रोगी के साथ जारी रखें",

        "new_patient_desc":
            "दूसरे रोगी के लिए नया स्वास्थ्य मूल्यांकन शुरू करें।",

        "new_patient_button":
            "➕ दूसरे रोगी के साथ जारी रखें",

        "disclaimer":
            "⚠️ CareRoute AI केवल सामान्य स्वास्थ्य मार्गदर्शन प्रदान करता है। "
            "यह बीमारी का निदान नहीं करता और डॉक्टर की सलाह का विकल्प नहीं है।",

        "footer":
            "CareRoute AI • स्वास्थ्य मार्गदर्शन • निदान प्रणाली नहीं"
    }
}


# ============================================================
# VOICE LANGUAGE CODES
# ============================================================

VOICE_LANGUAGE_CODES = {
    "English": "en-IN",
    "Telugu": "te-IN",
    "Hindi": "hi-IN"
}


# ============================================================
# TEXT TO SPEECH LANGUAGE CODES
# ============================================================

TTS_LANGUAGE_CODES = {
    "English": "en",
    "Telugu": "te",
    "Hindi": "hi"
}


# ============================================================
# VOICE KEYWORDS
# ============================================================

VOICE_KEYWORDS = {

    "English": {

        "Headache": [
            "headache",
            "head pain"
        ],

        "Fever": [
            "fever",
            "temperature"
        ],

        "Cough": [
            "cough",
            "coughing"
        ],

        "Shortness of breath": [
            "shortness of breath",
            "difficulty breathing",
            "breathing problem",
            "breathlessness"
        ],

        "Chest discomfort": [
            "chest discomfort",
            "chest pain",
            "pain in chest"
        ],

        "Palpitations": [
            "palpitations",
            "heart beating fast",
            "heart racing"
        ],

        "Abdominal pain": [
            "abdominal pain",
            "stomach pain",
            "belly pain",
            "stomach ache"
        ],

        "Nausea": [
            "nausea",
            "feeling nauseous"
        ],

        "Vomiting": [
            "vomiting",
            "vomit",
            "throwing up"
        ],

        "Diarrhea": [
            "diarrhea",
            "loose motions",
            "loose stools"
        ],

        "Joint pain": [
            "joint pain",
            "pain in joints"
        ],

        "Back pain": [
            "back pain",
            "pain in back"
        ],

        "Skin rash": [
            "skin rash",
            "rash"
        ],

        "Itching": [
            "itching",
            "itchy"
        ],

        "Ear pain": [
            "ear pain",
            "pain in ear"
        ],

        "Hearing difficulty": [
            "hearing difficulty",
            "difficulty hearing",
            "hearing problem"
        ],

        "Sore throat": [
            "sore throat",
            "throat pain"
        ],

        "Nasal congestion": [
            "nasal congestion",
            "blocked nose",
            "stuffy nose"
        ],

        "Eye pain": [
            "eye pain",
            "pain in eye"
        ],

        "Blurred vision": [
            "blurred vision",
            "blurry vision"
        ],

        "Dizziness": [
            "dizziness",
            "dizzy",
            "feeling dizzy"
        ],

        "Numbness": [
            "numbness",
            "numb",
            "feeling numb"
        ],

        "Fatigue": [
            "fatigue",
            "tired",
            "very tired"
        ]
    },


    "Telugu": {

        "Headache": [
            "తలనొప్పి",
            "తల నొప్పి"
        ],

        "Fever": [
            "జ్వరం",
            "టెంపరేచర్"
        ],

        "Cough": [
            "దగ్గు"
        ],

        "Shortness of breath": [
            "శ్వాస తీసుకోవడంలో ఇబ్బంది",
            "శ్వాస ఇబ్బంది",
            "ఊపిరి తీసుకోవడం కష్టం"
        ],

        "Chest discomfort": [
            "ఛాతీలో అసౌకర్యం",
            "ఛాతి నొప్పి",
            "ఛాతీలో నొప్పి"
        ],

        "Palpitations": [
            "గుండె దడ",
            "గుండె వేగంగా కొట్టుకోవడం"
        ],

        "Abdominal pain": [
            "కడుపు నొప్పి",
            "పొట్ట నొప్పి"
        ],

        "Nausea": [
            "వికారం"
        ],

        "Vomiting": [
            "వాంతులు",
            "వాంతి"
        ],

        "Diarrhea": [
            "విరేచనాలు",
            "లూజ్ మోషన్స్"
        ],

        "Joint pain": [
            "కీళ్ల నొప్పి",
            "కీళ్ళ నొప్పి"
        ],

        "Back pain": [
            "వెన్నునొప్పి",
            "వెన్ను నొప్పి"
        ],

        "Skin rash": [
            "చర్మంపై దద్దుర్లు",
            "దద్దుర్లు"
        ],

        "Itching": [
            "దురద"
        ],

        "Ear pain": [
            "చెవి నొప్పి"
        ],

        "Hearing difficulty": [
            "వినికిడి సమస్య",
            "వినడం కష్టం"
        ],

        "Sore throat": [
            "గొంతు నొప్పి"
        ],

        "Nasal congestion": [
            "ముక్కు దిబ్బడ",
            "ముక్కు మూసుకుపోవడం"
        ],

        "Eye pain": [
            "కంటి నొప్పి"
        ],

        "Blurred vision": [
            "చూపు మసకబారడం",
            "మసకగా కనిపించడం"
        ],

        "Dizziness": [
            "తల తిరగడం",
            "తల తిరుగుతోంది"
        ],

        "Numbness": [
            "తిమ్మిరి",
            "మొద్దుబారడం"
        ],

        "Fatigue": [
            "అలసట",
            "చాలా అలసట"
        ]
    },


    # ========================================================
    # HINDI
    # ========================================================

    "Hindi": {

        "Headache": [
            "सिरदर्द",
            "सिर दर्द",
            "सिर में दर्द",
            "मेरे सिर में दर्द",
            "मुझे सिर में दर्द",
            "सिर में बहुत दर्द"
        ],

        "Fever": [
            "बुखार",
            "मुझे बुखार",
            "तेज बुखार",
            "बहुत तेज बुखार",
            "शरीर में गर्मी"
        ],

        "Cough": [
            "खांसी",
            "मुझे खांसी",
            "बहुत खांसी",
            "खांस रहा",
            "खांस रही"
        ],

        "Shortness of breath": [
            "सांस लेने में कठिनाई",
            "सांस लेने में दिक्कत",
            "सांस लेने में परेशानी",
            "सांस फूलना",
            "सांस लेने में समस्या",
            "सांस नहीं आ रही",
            "सांस लेने में मुश्किल",
            "सांस लेने में तकलीफ"
        ],

        "Chest discomfort": [
            "सीने में असहजता",
            "सीने में दर्द",
            "छाती में दर्द",
            "सीने में तकलीफ",
            "छाती में तकलीफ",
            "सीने में भारीपन",
            "छाती में भारीपन"
        ],

        "Palpitations": [
            "दिल की धड़कन तेज",
            "दिल तेजी से धड़कना",
            "दिल की धड़कन",
            "दिल बहुत तेज धड़क रहा है",
            "दिल जोर से धड़क रहा है",
            "दिल धड़क रहा है"
        ],

        "Abdominal pain": [
            "पेट दर्द",
            "पेट में दर्द",
            "मेरे पेट में दर्द",
            "मुझे पेट में दर्द",
            "पेट में बहुत दर्द"
        ],

        "Nausea": [
            "मतली",
            "जी मिचलाना",
            "मुझे मतली",
            "जी मिचला रहा है",
            "जी मिचला रही है"
        ],

        "Vomiting": [
            "उल्टी",
            "उल्टियां",
            "मुझे उल्टी",
            "उल्टी हो रही है",
            "उल्टी आ रही है"
        ],

        "Diarrhea": [
            "दस्त",
            "पतले दस्त",
            "बार बार दस्त",
            "लूज मोशन",
            "लूज मोशन हो रहे हैं",
            "बार बार लूज मोशन"
        ],

        "Joint pain": [
            "जोड़ों का दर्द",
            "जोड़ों में दर्द",
            "जोड़ों में तकलीफ",
            "मेरे जोड़ों में दर्द",
            "जोड़ों में बहुत दर्द"
        ],

        "Back pain": [
            "कमर दर्द",
            "पीठ दर्द",
            "कमर में दर्द",
            "पीठ में दर्द",
            "मेरी कमर में दर्द",
            "मेरी पीठ में दर्द"
        ],

        "Skin rash": [
            "त्वचा पर चकत्ते",
            "चकत्ते",
            "शरीर पर चकत्ते",
            "त्वचा पर दाने",
            "शरीर पर दाने",
            "दाने हो रहे हैं"
        ],

        "Itching": [
            "खुजली",
            "मुझे खुजली",
            "बहुत खुजली",
            "शरीर में खुजली",
            "त्वचा में खुजली"
        ],

        "Ear pain": [
            "कान में दर्द",
            "कान दर्द",
            "मेरे कान में दर्द",
            "कान में बहुत दर्द"
        ],

        "Hearing difficulty": [
            "सुनने में कठिनाई",
            "सुनने में दिक्कत",
            "सुनाई नहीं देना",
            "कम सुनाई देना",
            "सुनने में परेशानी",
            "सुनने में तकलीफ"
        ],

        "Sore throat": [
            "गले में खराश",
            "गले में दर्द",
            "गला दर्द",
            "मेरे गले में दर्द",
            "गले में तकलीफ",
            "गले में बहुत दर्द"
        ],

        "Nasal congestion": [
            "नाक बंद",
            "नाक बंद होना",
            "नाक बंद है",
            "नाक में जकड़न",
            "नाक बंद हो गई",
            "नाक से सांस नहीं आ रही"
        ],

        "Eye pain": [
            "आंखों में दर्द",
            "आंख में दर्द",
            "मेरी आंख में दर्द",
            "आंखों में तकलीफ",
            "आंख में बहुत दर्द"
        ],

        "Blurred vision": [
            "धुंधला दिखाई देना",
            "धुंधला दिखना",
            "साफ दिखाई नहीं देना",
            "दृष्टि धुंधली",
            "आंखों से धुंधला दिखना",
            "मुझे धुंधला दिखाई देता है"
        ],

        "Dizziness": [
            "चक्कर आना",
            "चक्कर",
            "मुझे चक्कर आ रहे हैं",
            "सिर घूमना",
            "सिर घूम रहा है",
            "बहुत चक्कर आ रहे हैं"
        ],

        "Numbness": [
            "सुन्नपन",
            "सुन्न होना",
            "हाथ सुन्न होना",
            "पैर सुन्न होना",
            "शरीर सुन्न होना",
            "हाथ में सुन्नपन",
            "पैर में सुन्नपन"
        ],

        "Fatigue": [
            "थकान",
            "बहुत थकान",
            "मुझे बहुत थकान",
            "कमजोरी",
            "बहुत कमजोरी",
            "मुझे कमजोरी महसूस हो रही है"
        ]
    }
}


# ============================================================
# DETECT VOICE SYMPTOMS
# ============================================================

def detect_voice_symptoms(transcript, language):

    if not transcript:
        return []

    transcript_lower = transcript.strip().lower()

    detected = []

    language_keywords = VOICE_KEYWORDS.get(
        language,
        {}
    )

    for symptom in SYMPTOMS:

        keywords = language_keywords.get(
            symptom,
            []
        )

        for keyword in keywords:

            if keyword.lower() in transcript_lower:

                detected.append(symptom)

                break

    return list(
        dict.fromkeys(detected)
    )


# ============================================================
# TEXT TO SPEECH
# ============================================================

def generate_voice_response(text, language):

    try:

        from gtts import gTTS

        audio_buffer = io.BytesIO()

        speech = gTTS(
            text=text,
            lang=TTS_LANGUAGE_CODES.get(
                language,
                "en"
            ),
            slow=False
        )

        speech.write_to_fp(
            audio_buffer
        )

        audio_buffer.seek(0)

        return audio_buffer

    except Exception:

        return None


# ============================================================
# EXTRA UI TEXT FOR THE ENHANCED TRIAGE FLOW
# ============================================================

UI["English"].update({
    "other_symptoms_title": "✍️ Add Other Symptoms",
    "other_symptoms_placeholder": "Type any symptom that is not listed above...",
    "other_symptoms_help": "Use simple words. The system will match known symptom terms when possible.",
    "voice_confirm": "I confirm that these are the symptoms I described.",
    "voice_confirm_help": "Voice-detected symptoms are used only after confirmation.",
    "analysis_quality": "Recommendation reliability",
    "agreement": "Rule and ML agreement",
    "support": "Supporting symptoms",
    "followup_title": "🎯 A Few Quick Questions",
    "followup_desc": "We only ask extra questions when they can improve routing. Your answers are used for this assessment only.",
    "sudden": "Did the main symptom start suddenly?",
    "worsening": "Are the symptoms getting worse?",
    "followup_not_sure": "Not sure",
    "followup_yes": "Yes",
    "followup_no": "No",
    "refine": "🔍 Refine My Recommendation",
    "recommend_ready": "Your information is ready. You can get the recommendation now.",
    "unknown_note": "Some typed symptoms could not be matched to the supported symptom vocabulary. They were kept as context and were not treated as a known model feature.",
    "voice_confirm_needed": "Please confirm the detected voice symptoms before they are used.",
    "confidence_high": "High",
    "confidence_medium": "Moderate",
    "confidence_low": "Low",
    "confidence_note": "This is a model/rule consistency signal, not a medical probability or diagnosis.",
    "maps_external": "Google Maps is an external search service. Check hospital details directly before relying on availability or services.",
    "new_patient": "👤 Continue With Another Patient",
    "new_patient_desc": "Start a fresh assessment. The current assessment will be cleared and no patient history is stored.",
    "new_patient_button": "➕ Continue With Another Patient",
})

UI["Telugu"].update({
    "other_symptoms_title": "✍️ ఇతర లక్షణాలను నమోదు చేయండి",
    "other_symptoms_placeholder": "పై జాబితాలో లేని లక్షణాన్ని నమోదు చేయండి...",
    "other_symptoms_help": "సులభమైన పదాలను ఉపయోగించండి. సాధ్యమైనప్పుడు సిస్టమ్ తెలిసిన లక్షణాలతో సరిపోల్చుతుంది.",
    "voice_confirm": "గుర్తించిన లక్షణాలు నేను చెప్పినవేనని నిర్ధారిస్తున్నాను.",
    "voice_confirm_help": "వాయిస్ ద్వారా గుర్తించిన లక్షణాలు నిర్ధారణ తర్వాత మాత్రమే ఉపయోగించబడతాయి.",
    "analysis_quality": "సిఫార్సు విశ్వసనీయత",
    "agreement": "రూల్ మరియు ML సరిపోలిక",
    "support": "సహాయక లక్షణాలు",
    "followup_title": "🎯 కొన్ని చిన్న ప్రశ్నలు",
    "followup_desc": "సరైన విభాగాన్ని ఎంచుకోవడానికి అవసరమైనప్పుడు మాత్రమే అదనపు ప్రశ్నలు అడుగుతాము.",
    "sudden": "ప్రధాన లక్షణం అకస్మాత్తుగా ప్రారంభమైందా?",
    "worsening": "లక్షణాలు మరింత తీవ్రమవుతున్నాయా?",
    "followup_not_sure": "తెలియదు",
    "followup_yes": "అవును",
    "followup_no": "కాదు",
    "refine": "🔍 నా సిఫార్సును మెరుగుపరచండి",
    "recommend_ready": "మీ సమాచారం సిద్ధంగా ఉంది. ఇప్పుడు సిఫార్సును పొందవచ్చు.",
    "unknown_note": "మీరు నమోదు చేసిన కొన్ని లక్షణాలను సిస్టమ్ తెలిసిన లక్షణాలతో సరిపోల్చలేకపోయింది. అవి సందర్భంగా ఉంచబడ్డాయి కానీ తెలిసిన మోడల్ ఫీచర్‌గా ఉపయోగించబడలేదు.",
    "voice_confirm_needed": "గుర్తించిన వాయిస్ లక్షణాలను ఉపయోగించే ముందు దయచేసి నిర్ధారించండి.",
    "confidence_high": "అధిక",
    "confidence_medium": "మధ్యస్థ",
    "confidence_low": "తక్కువ",
    "confidence_note": "ఇది మోడల్/రూల్ సరిపోలికను సూచిస్తుంది; ఇది వైద్య సంభావ్యత లేదా నిర్ధారణ కాదు.",
    "maps_external": "Google Maps ఒక బాహ్య శోధన సేవ. అందుబాటు లేదా సేవలపై ఆధారపడే ముందు ఆసుపత్రి వివరాలను నేరుగా తనిఖీ చేయండి.",
    "new_patient": "👤 మరొక రోగితో కొనసాగించండి",
    "new_patient_desc": "కొత్త అంచనాను ప్రారంభించండి. ప్రస్తుత అంచనా క్లియర్ చేయబడుతుంది మరియు రోగి చరిత్ర నిల్వ చేయబడదు.",
    "new_patient_button": "➕ మరొక రోగితో కొనసాగించండి",
})

UI["Hindi"].update({
    "other_symptoms_title": "✍️ अन्य लक्षण लिखें",
    "other_symptoms_placeholder": "ऊपर सूची में न दिया गया कोई लक्षण लिखें...",
    "other_symptoms_help": "सरल शब्दों का उपयोग करें। सिस्टम संभव होने पर ज्ञात लक्षणों से मिलान करेगा।",
    "voice_confirm": "मैं पुष्टि करता/करती हूँ कि ये वही लक्षण हैं जो मैंने बताए।",
    "voice_confirm_help": "आवाज़ से पहचाने गए लक्षण पुष्टि के बाद ही उपयोग होंगे।",
    "analysis_quality": "सिफारिश विश्वसनीयता",
    "agreement": "रूल और ML सहमति",
    "support": "सहायक लक्षण",
    "followup_title": "🎯 कुछ छोटे सवाल",
    "followup_desc": "सही विभाग चुनने में मदद मिलने पर ही अतिरिक्त सवाल पूछे जाते हैं।",
    "sudden": "क्या मुख्य लक्षण अचानक शुरू हुआ?",
    "worsening": "क्या लक्षण बढ़ रहे हैं?",
    "followup_not_sure": "पता नहीं",
    "followup_yes": "हाँ",
    "followup_no": "नहीं",
    "refine": "🔍 मेरी सिफारिश सुधारें",
    "recommend_ready": "आपकी जानकारी तैयार है। अब सिफारिश प्राप्त कर सकते हैं।",
    "unknown_note": "आपके लिखे कुछ लक्षणों का समर्थित लक्षण शब्दावली से मिलान नहीं हो सका। उन्हें संदर्भ के रूप में रखा गया है, लेकिन ज्ञात मॉडल फीचर के रूप में उपयोग नहीं किया गया।",
    "voice_confirm_needed": "पहचाने गए आवाज़ के लक्षणों का उपयोग करने से पहले कृपया पुष्टि करें।",
    "confidence_high": "उच्च",
    "confidence_medium": "मध्यम",
    "confidence_low": "कम",
    "confidence_note": "यह मॉडल/रूल की संगति का संकेत है; यह चिकित्सा संभावना या निदान नहीं है।",
    "maps_external": "Google Maps एक बाहरी खोज सेवा है। उपलब्धता या सेवाओं पर भरोसा करने से पहले अस्पताल की जानकारी सीधे जांचें।",
    "new_patient": "👤 दूसरे रोगी के साथ जारी रखें",
    "new_patient_desc": "नया मूल्यांकन शुरू करें। वर्तमान मूल्यांकन साफ हो जाएगा और रोगी इतिहास संग्रहीत नहीं किया जाएगा।",
    "new_patient_button": "➕ दूसरे रोगी के साथ जारी रखें",
})


# ============================================================
# ENHANCED TRIAGE HELPERS
# ============================================================

def normalize_text(text):
    return " ".join(str(text or "").strip().lower().split())


def detect_text_symptoms(text):
    """Match free text against multilingual symptom keywords without diagnosing."""
    normalized = normalize_text(text)
    if not normalized:
        return []

    detected = []

    # Direct canonical names first.
    for symptom in SYMPTOMS:
        if normalize_text(symptom) in normalized:
            detected.append(symptom)

    # Then multilingual voice vocabulary.
    for language_keywords in VOICE_KEYWORDS.values():
        for symptom in SYMPTOMS:
            for keyword in language_keywords.get(symptom, []):
                if normalize_text(keyword) and normalize_text(keyword) in normalized:
                    detected.append(symptom)
                    break

    return list(dict.fromkeys(detected))


def model_signal(symptoms):
    """Return a non-clinical model consistency signal for the current symptom set."""
    known = [s for s in symptoms if s in FEATURES]
    if not known:
        return {"department": None, "confidence": 0.0, "label": "Low", "scores": {}}

    input_data = {feature: 0 for feature in FEATURES}
    for symptom in known:
        input_data[symptom] = 1

    X = pd.DataFrame([input_data], columns=FEATURES)
    scores = {}

    try:
        if hasattr(MODEL, "predict_proba"):
            probabilities = MODEL.predict_proba(X)[0]
            classes = list(MODEL.classes_)
            scores = {str(c): float(p) for c, p in zip(classes, probabilities)}
            top_department = max(scores, key=scores.get)
            top_score = scores[top_department]
        else:
            raw = MODEL.decision_function(X)
            classes = list(MODEL.classes_)
            values = raw[0] if getattr(raw, "ndim", 1) > 1 else raw
            # Convert margins to a relative softmax signal. This is NOT a calibrated probability.
            exp_values = [math.exp(float(v) - max(values)) for v in values]
            total = sum(exp_values) or 1.0
            scores = {str(c): e / total for c, e in zip(classes, exp_values)}
            top_department = max(scores, key=scores.get)
            top_score = scores[top_department]
    except Exception:
        try:
            top_department = str(MODEL.predict(X)[0])
            top_score = 0.0
        except Exception:
            return {"department": None, "confidence": 0.0, "label": "Low", "scores": {}}

    if top_score >= 0.75:
        label = "High"
    elif top_score >= 0.50:
        label = "Moderate"
    else:
        label = "Low"

    return {
        "department": top_department,
        "confidence": float(top_score),
        "label": label,
        "scores": scores,
    }


def hybrid_analysis(symptoms):
    """Combine deterministic symptom routing and ML output without presenting either as diagnosis."""
    rule_department = rule_based_prediction(symptoms) if symptoms else None
    ml_info = model_signal(symptoms)
    ml_department = ml_info["department"]
    agreement = bool(rule_department and ml_department and rule_department == ml_department)

    if rule_department and ml_department and agreement:
        final_department = rule_department
    elif rule_department:
        final_department = rule_department
    elif ml_department:
        final_department = ml_department
    else:
        final_department = "General Medicine"

    supporting = sum(
        1 for symptom in symptoms
        if symptom in SYMPTOMS
    )

    if agreement and ml_info["label"] == "High":
        quality = "High"
    elif agreement or ml_info["label"] in {"High", "Moderate"}:
        quality = "Moderate"
    else:
        quality = "Low"

    return {
        "department": final_department,
        "rule_department": rule_department,
        "ml_department": ml_department,
        "agreement": agreement,
        "quality": quality,
        "ml_info": ml_info,
        "supporting": supporting,
    }


def followup_questions(symptoms, language):
    """Return at most two lightweight contextual questions only for lower-confidence routing."""
    question_set = []
    symptom_set = set(symptoms)

    if symptom_set.intersection({"Headache", "Dizziness", "Numbness", "Blurred vision"}):
        question_set.append("sudden")

    if symptom_set.intersection({"Chest discomfort", "Palpitations", "Shortness of breath", "Abdominal pain", "Vomiting", "Diarrhea"}):
        question_set.append("worsening")

    return question_set[:2]


# ============================================================
# CLEAR PATIENT DATA
# ============================================================

def clear_patient_data():
    """Clear the active assessment only; no history is stored."""
    keys_to_clear = [
        "patient_name", "patient_age", "manual_symptoms", "voice_input",
        "typed_symptoms", "duration", "severity", "voice_transcript",
        "voice_detected_symptoms", "voice_confirmed", "all_selected_symptoms",
        "free_text_detected", "recommendation_result", "followup_answers",
        "adaptive_answers", "show_recommendation", "recommend_button"
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)

    for index in range(len(SYMPTOMS)):
        st.session_state.pop(f"symptom_checkbox_{index}", None)

    st.session_state.page = 2

# ============================================================
# PAGE 1
# ============================================================

def show_page_one():

    # --------------------------------------------------------
    # LOGO
    # --------------------------------------------------------

    logo_path = (
        PROJECT_DIR
        / "assets"
        / "care_route_logo.png"
    )

    if logo_path.exists():

        # Center the logo
        left_col, center_col, right_col = st.columns(
            [1, 2, 1]
        )

        with center_col:
            st.image(
                str(logo_path),
                width=390
            )

    else:

        st.markdown(
            '<div class="main-title">🏥 CareRoute AI</div>',
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # SUBTITLE
    # --------------------------------------------------------

    st.markdown(
        '<div class="main-subtitle">'
        'Smart Healthcare Guidance'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # LANGUAGE
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title" style="font-size:24px;">'
        '🌐 Select Your Language'
        '</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Choose the language you want to use."
    )

    # --------------------------------------------------------
    # LANGUAGE OPTIONS
    # --------------------------------------------------------

    language_options = [
        "English",
        "తెలుగు",
        "हिन्दी"
    ]

    current_language = st.session_state.language

    if current_language == "English":
        current_display_language = "English"

    elif current_language == "Telugu":
        current_display_language = "తెలుగు"

    else:
        current_display_language = "हिन्दी"

    selected_display_language = st.selectbox(
        "Language",
        language_options,
        index=language_options.index(
            current_display_language
        ),
        label_visibility="collapsed",
        key="welcome_language"
    )

    # --------------------------------------------------------
    # CONVERT DISPLAY LANGUAGE
    # --------------------------------------------------------

    if selected_display_language == "English":

        selected_language = "English"

    elif selected_display_language == "తెలుగు":

        selected_language = "Telugu"

    elif selected_display_language == "हिन्दी":

        selected_language = "Hindi"

    else:

        selected_language = "English"

    st.session_state.language = selected_language

    T = UI[selected_language]

    # --------------------------------------------------------
    # CONTINUE
    # --------------------------------------------------------

    st.write("")

    if st.button(
        T["continue"],
        use_container_width=True,
        key="continue_button"
    ):

        st.session_state.page = 2
        st.rerun()

    # --------------------------------------------------------
    # WHAT YOU CAN DO
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="section-title">
            {T["what"]}
        </div>

        <div class="section-subtitle">
            {T["what_subtitle"]}
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(
        3,
        gap="large"
    )

    with col1:

        with st.container(
            border=True
        ):

            st.markdown(
                '<div class="icon-circle">🎙️</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div class="card-title">
                    {T["speak"]}
                </div>

                <div class="card-text">
                    {T["speak_desc"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    with col2:

        with st.container(
            border=True
        ):

            st.markdown(
                '<div class="icon-circle">🩺</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div class="card-title">
                    {T["department"]}
                </div>

                <div class="card-text">
                    {T["department_desc"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    with col3:

        with st.container(
            border=True
        ):

            st.markdown(
                '<div class="icon-circle">📍</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div class="card-title">
                    {T["hospital"]}
                </div>

                <div class="card-text">
                    {T["hospital_desc"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    st.caption(
        T["disclaimer"]
    )

# ============================================================
# PAGE 2 — ENHANCED TRIAGE FLOW
# ============================================================

def show_page_two():
    language = st.session_state.get("language", "English")
    T = UI[language]

    if st.button(T["back"], key="back_button"):
        st.session_state.page = 1
        st.rerun()

    st.markdown(
        f"""
        <div class="main-title">{T["page2_title"]}</div>
        <div class="main-subtitle">{T["page2_subtitle"]}</div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # PATIENT INFORMATION
    # --------------------------------------------------------
    with st.container(border=True):
        st.markdown(
            f'<div class="card-title" style="font-size:23px;text-align:left;">{T["patient"]}</div>',
            unsafe_allow_html=True
        )
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(T["name"], placeholder=T["name_placeholder"], key="patient_name")
        with col2:
            st.number_input(T["age"], min_value=1, max_value=120, value=18, step=1, key="patient_age")

    # --------------------------------------------------------
    # VOICE FIRST
    # --------------------------------------------------------
    with st.container(border=True):
        st.markdown(
            f'<div class="card-title" style="font-size:25px;text-align:left;">{T["voice_title"]}</div>'
            f'<div class="card-text" style="text-align:left;">{T["voice_desc"]}</div>',
            unsafe_allow_html=True
        )
        st.caption(T["voice_instruction"])
        voice_audio = st.audio_input(T["record"], key="voice_input")

    voice_detected_symptoms = []
    voice_transcript = ""

    if voice_audio is not None:
        st.success(T["record_received"])
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            recognizer.dynamic_energy_threshold = True
            recognizer.energy_threshold = 200
            recognizer.pause_threshold = 1.0
            recognizer.phrase_threshold = 0.2
            recognizer.non_speaking_duration = 0.5

            audio_bytes = voice_audio.getvalue()
            if audio_bytes:
                audio_file = sr.AudioFile(io.BytesIO(audio_bytes))
                with audio_file as source:
                    audio_data = recognizer.record(source)

                recognition_languages = [
                    ("English", "en-IN"),
                    ("English-US", "en-US"),
                    ("Hindi", "hi-IN"),
                    ("Telugu", "te-IN"),
                ]
                all_transcripts = []
                recognition_errors = []

                for recognition_name, recognition_code in recognition_languages:
                    try:
                        transcript = recognizer.recognize_google(
                            audio_data,
                            language=recognition_code
                        ).strip()
                        if transcript:
                            all_transcripts.append((recognition_name, transcript))
                    except Exception as error:
                        recognition_errors.append(f"{recognition_name}: {error}")

                best_language = None
                best_transcript = ""
                best_symptoms = []
                best_score = -1

                for recognition_name, transcript in all_transcripts:
                    detected = detect_text_symptoms(transcript)
                    score = len(detected)
                    if score > best_score:
                        best_score = score
                        best_language = recognition_name
                        best_transcript = transcript
                        best_symptoms = detected

                if not best_transcript and all_transcripts:
                    best_language, best_transcript = all_transcripts[0]
                    best_symptoms = detect_text_symptoms(best_transcript)

                if best_transcript:
                    voice_transcript = best_transcript
                    voice_detected_symptoms = best_symptoms
                    st.info(f"**{T['understood']}**\n\n{voice_transcript}")
                    st.caption(f"Recognition language: {best_language}")

                    if voice_detected_symptoms:
                        translated = [
                            TRANSLATIONS[language].get(symptom, symptom)
                            for symptom in voice_detected_symptoms
                        ]
                        st.success(f"**{T['detected']}** {', '.join(translated)}")
                        st.checkbox(
                            T["voice_confirm"],
                            key="voice_confirmed",
                            help=T["voice_confirm_help"]
                        )
                    else:
                        st.warning(T["voice_no_symptom"])
                else:
                    st.warning(T["voice_no_symptom"])
                    if recognition_errors:
                        with st.expander("Voice recognition details"):
                            for message in recognition_errors:
                                st.write(message)
            else:
                st.warning(T["voice_no_symptom"])
        except Exception as error:
            st.error(T["voice_error"])
            with st.expander("Voice processing details"):
                st.write(str(error))

    st.session_state.voice_transcript = voice_transcript
    st.session_state.voice_detected_symptoms = voice_detected_symptoms

    # --------------------------------------------------------
    # MANUAL SYMPTOMS
    # --------------------------------------------------------
    with st.container(border=True):
        st.markdown(
            f'<div class="card-title" style="font-size:23px;text-align:left;">{T["manual_title"]}</div>'
            f'<div class="card-text" style="text-align:left;">{T["manual_desc"]}</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="color:#07538c;font-size:17px;font-weight:600;margin-top:10px;margin-bottom:10px;">{T["symptom_question"]}</div>',
            unsafe_allow_html=True
        )

        symptom_col1, symptom_col2 = st.columns(2)
        for index, english_symptom in enumerate(SYMPTOMS):
            translated_symptom = TRANSLATIONS[language][english_symptom]
            checkbox_key = f"symptom_checkbox_{index}"
            target = symptom_col1 if index % 2 == 0 else symptom_col2
            with target:
                st.checkbox(translated_symptom, key=checkbox_key)

    selected_symptoms = []
    for index, english_symptom in enumerate(SYMPTOMS):
        if st.session_state.get(f"symptom_checkbox_{index}", False):
            selected_symptoms.append(english_symptom)

    # --------------------------------------------------------
    # FREE TEXT
    # --------------------------------------------------------
    typed_symptoms = st.text_area(
        T["other_symptoms_title"],
        placeholder=T["other_symptoms_placeholder"],
        help=T["other_symptoms_help"],
        height=90,
        key="typed_symptoms"
    )
    free_text_detected = detect_text_symptoms(typed_symptoms)
    unknown_typed_text = typed_symptoms.strip() if typed_symptoms.strip() and not free_text_detected else ""

    if free_text_detected:
        translated_free = [TRANSLATIONS[language].get(s, s) for s in free_text_detected]
        st.success(f"**{T['detected']}** {', '.join(translated_free)}")
    elif unknown_typed_text:
        st.info(T["unknown_note"])

    # --------------------------------------------------------
    # COMBINE INPUTS
    # --------------------------------------------------------
    confirmed_voice = st.session_state.get("voice_confirmed", False)
    if voice_detected_symptoms and not confirmed_voice:
        voice_for_triage = []
    else:
        voice_for_triage = voice_detected_symptoms

    all_selected_symptoms = list(dict.fromkeys(
        selected_symptoms + voice_for_triage + free_text_detected
    ))
    st.session_state.all_selected_symptoms = all_selected_symptoms
    st.session_state.free_text_detected = free_text_detected

    if voice_detected_symptoms and not confirmed_voice:
        st.warning(T["voice_confirm_needed"])

    if all_selected_symptoms:
        translated_current = [TRANSLATIONS[language].get(s, s) for s in all_selected_symptoms]
        st.info(f"**{T['summary_symptoms']}:** {', '.join(translated_current)}")

    # --------------------------------------------------------
    # MINIMAL FOLLOW-UP QUESTIONS
    # --------------------------------------------------------
    preliminary = hybrid_analysis(all_selected_symptoms) if all_selected_symptoms else None
    followups = []
    if preliminary and preliminary["quality"] == "Low":
        followups = followup_questions(all_selected_symptoms, language)

    followup_answers = {}
    if followups:
        with st.container(border=True):
            st.markdown(
                f'<div class="card-title" style="font-size:22px;text-align:left;">{T["followup_title"]}</div>'
                f'<div class="card-text" style="text-align:left;">{T["followup_desc"]}</div>',
                unsafe_allow_html=True
            )
            options = [T["followup_not_sure"], T["followup_yes"], T["followup_no"]]
            for key in followups:
                followup_answers[key] = st.radio(
                    T[key], options, horizontal=True, key=f"adaptive_{key}"
                )
            st.session_state.followup_answers = followup_answers
    else:
        st.caption(T["recommend_ready"])

    # --------------------------------------------------------
    # OPTIONAL BASIC CONTEXT — shown only when symptoms exist
    # --------------------------------------------------------
    with st.container(border=True):
        st.header(T["additional"])
        col3, col4 = st.columns(2)
        with col3:
            duration = st.selectbox(T["duration"], T["duration_options"], key="duration")
        with col4:
            severity = st.select_slider(
                T["severity"],
                options=T["severity_options"],
                value=T["severity_options"][1],
                key="severity"
            )

    # --------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------
    st.write("")
    recommend = st.button(T["recommend"], use_container_width=True, key="recommend_button")

    if recommend:
        if not all_selected_symptoms:
            st.warning(T["no_symptoms"])
            return

        if voice_detected_symptoms and not confirmed_voice and not selected_symptoms and not free_text_detected:
            st.warning(T["voice_confirm_needed"])
            return

        patient_name = st.session_state.get("patient_name", "")
        patient_age = st.session_state.get("patient_age", 18)
        display_name = patient_name.strip() or (
            "Not provided" if language == "English" else
            "పేరు ఇవ్వలేదు" if language == "Telugu" else
            "नाम नहीं दिया गया"
        )
        language_display = {"English": "English", "Telugu": "తెలుగు", "Hindi": "हिन्दी"}
        translated_final_symptoms = [TRANSLATIONS[language].get(s, s) for s in all_selected_symptoms]

        is_red_flag = check_red_flags(all_selected_symptoms)
        analysis = hybrid_analysis(all_selected_symptoms)
        department = analysis["department"]
        display_department = get_department_name(department, language)
        department_description = get_department_description(department, language)

        # ----------------------------------------------------
        # PATIENT REPORT
        # ----------------------------------------------------
        st.divider()
        st.subheader(T["summary"])
        report_data = {
            T["summary_name"]: display_name,
            T["summary_age"]: str(patient_age),
            T["summary_language"]: language_display[language],
            T["summary_symptoms"]: ", ".join(translated_final_symptoms),
            T["summary_duration"]: duration,
            T["summary_severity"]: severity,
        }
        with st.container(border=True):
            for label, value in report_data.items():
                st.markdown(
                    f'<div style="padding:8px 0;font-size:17px;"><strong>{label}:</strong> {value}</div>',
                    unsafe_allow_html=True
                )

        if unknown_typed_text:
            st.caption(f"Additional typed context: {unknown_typed_text}")

        # ----------------------------------------------------
        # SAFETY OVERRIDE
        # ----------------------------------------------------
        if is_red_flag:
            st.error(T["urgent"])
            st.warning(T["urgent_message"])
            st.warning(T["urgent_warning"])
            emergency_url = get_emergency_hospital_url()
            st.link_button("📍 Find Emergency Care on Google Maps", emergency_url, use_container_width=True)
            st.caption(T["maps_external"])
            urgent_voice = generate_voice_response(T["urgent_message"], language)
            if urgent_voice is not None:
                st.subheader(T["listen"])
                st.audio(urgent_voice, format="audio/mp3")
        else:
            # ------------------------------------------------
            # RECOMMENDATION
            # ------------------------------------------------
            st.write("")
            st.markdown('<div class="result-icon">🏥</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="result-title">{T["recommended"]}</div>'
                f'<div style="text-align:center;color:#07538c;font-size:30px;font-weight:800;margin-top:8px;">{display_department}</div>',
                unsafe_allow_html=True
            )
            st.subheader(T["why"])
            st.info(department_description)

            # ------------------------------------------------
            # MODEL / RULE TRANSPARENCY
            # ------------------------------------------------
            st.subheader(T["analysis_quality"])
            quality_map = {
                "High": T["confidence_high"],
                "Moderate": T["confidence_medium"],
                "Low": T["confidence_low"],
            }
            st.metric(T["analysis_quality"], quality_map[analysis["quality"]])
            st.write(f"**{T['agreement']}:** {'Yes' if analysis['agreement'] else 'Not confirmed'}")
            st.write(f"**{T['support']}:** {analysis['supporting']} known symptom(s)")
            if analysis["ml_department"]:
                st.caption(
                    f"ML output: {get_department_name(analysis['ml_department'], language)} | "
                    f"Rule output: {get_department_name(analysis['rule_department'], language) if analysis['rule_department'] else 'None'}"
                )
            st.caption(T["confidence_note"])

            if followups:
                st.caption("Adaptive questions were shown because the initial rule/ML signal was less consistent.")

            st.subheader(T["nearby"])
            st.write(T["nearby_desc"])
            maps_url = get_nearby_hospitals_url(department)
            st.link_button(T["maps"], maps_url, use_container_width=True)
            st.caption(T["maps_external"])

            speech_text = f"{T['recommended']}. {display_department}. {department_description}"
            voice_result = generate_voice_response(speech_text, language)
            if voice_result is not None:
                st.subheader(T["listen"])
                st.audio(voice_result, format="audio/mp3")

            st.caption(T["model_note"])

    # --------------------------------------------------------
    # NEW PATIENT — NO HISTORY
    # --------------------------------------------------------
    st.write("")
    st.divider()
    st.subheader(T["new_patient"])
    st.caption(T["new_patient_desc"])

    if st.button(T["new_patient_button"], use_container_width=True, key="new_patient_button"):
        clear_patient_data()
        st.rerun()

    st.write("")
    st.caption(T["disclaimer"])
    st.caption(T["footer"])

# ============================================================
# CSS
# ============================================================


st.markdown(
    """
    <style>

    .stApp {

        background:
            radial-gradient(
                circle at 5% 15%,
                rgba(92, 211, 255, 0.14),
                transparent 28%
            ),

            radial-gradient(
                circle at 95% 75%,
                rgba(92, 211, 255, 0.12),
                transparent 28%
            ),

            #ffffff;
    }


    .main-title {

        text-align: center;

        color: #07538c;

        font-size: 36px;

        font-weight: 800;

        margin-bottom: 4px;
    }


    .main-subtitle {

        text-align: center;

        color: #54799c;

        font-size: 18px;

        margin-bottom: 30px;
    }


    .section-title {

        text-align: center;

        color: #07538c;

        font-size: 29px;

        font-weight: 800;

        margin-top: 35px;

        margin-bottom: 5px;
    }


    .section-subtitle {

        text-align: center;

        color: #54799c;

        font-size: 16px;

        margin-bottom: 25px;
    }


    .card-title {

        color: #07538c;

        font-size: 20px;

        font-weight: 750;

        text-align: center;
    }


    .card-text {

        color: #54799c;

        font-size: 15px;

        line-height: 1.5;

        text-align: center;
    }


    .icon-circle {

        width: 105px;

        height: 105px;

        border-radius: 50%;

        background: #edfaff;

        margin: 0 auto 15px auto;

        display: flex;

        align-items: center;

        justify-content: center;

        font-size: 55px;
    }


    .result-title {

        text-align: center;

        color: #07538c;

        font-size: 30px;

        font-weight: 800;
    }


    .result-icon {

        text-align: center;

        font-size: 48px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PAGE ROUTING
# ============================================================

if st.session_state.page == 1:

    show_page_one()

else:

    show_page_two()