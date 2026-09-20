"""
CareBridge — Urgency Classifier
================================
Classifies user-reported distress into urgency levels:
  RED    -> Emergency (life-threatening)
  YELLOW -> High Priority (needs care within hours)
  GREEN  -> Non-Urgent (routine clinic visit)

Rules are deterministic keyword clusters (TRD §7).
The LLM is NEVER used for urgency decisions.

Output vocabulary: urgency level + facility type only.
Never names diseases or makes clinical diagnoses (PRD §5.3).
"""

from __future__ import annotations

import time
from typing import Optional

from core.models import UrgencyResult
from core.safety import SafetyResult, check_safety


# ---------------------------------------------------------------------------
# Urgency levels
# ---------------------------------------------------------------------------

URGENCY_LEVELS = {
    "RED": {
        "label_en": "🔴 EMERGENCY",
        "label_hi": "🔴 आपातकाल",
        "color": "#D32F2F",
        "facility_type_en": "Emergency Department (24-hour)",
        "facility_type_hi": "आपातकालीन विभाग (24 घंटे)",
        "guidance_en": "Call 108 immediately. Go to the nearest Emergency Department.",
        "guidance_hi": "तुरंत 108 पर कॉल करें। निकटतम आपातकालीन विभाग में जाएं।",
        "cta_phone": "108",
    },
    "YELLOW": {
        "label_en": "🟡 HIGH PRIORITY",
        "label_hi": "🟡 उच्च प्राथमिकता",
        "color": "#F57C00",
        "facility_type_en": "Urgent Care / Hospital OPD",
        "facility_type_hi": "अर्जेंट केयर / अस्पताल OPD",
        "guidance_en": "Seek care within 2 hours. Go to a hospital or urgent care center.",
        "guidance_hi": "2 घंटे के भीतर इलाज कराएं। अस्पताल या अर्जेंट केयर सेंटर जाएं।",
        "cta_phone": "112",
    },
    "GREEN": {
        "label_en": "🟢 NON-URGENT",
        "label_hi": "🟢 सामान्य",
        "color": "#388E3C",
        "facility_type_en": "Clinic / Primary Health Centre",
        "facility_type_hi": "क्लिनिक / प्राथमिक स्वास्थ्य केंद्र",
        "guidance_en": "Schedule a clinic appointment. Not an emergency.",
        "guidance_hi": "क्लिनिक में अपॉइंटमेंट लें। यह आपातकाल नहीं है।",
        "cta_phone": None,
    },
}


# ---------------------------------------------------------------------------
# First-aid whitelist (NON-DIAGNOSTIC, curated, TRD §7)
# ---------------------------------------------------------------------------

FIRST_AID_WHITELIST: dict[str, dict[str, list[str]]] = {
    "chest_pain": {
        "en": [
            "Sit upright and rest — do not walk or exert yourself.",
            "Loosen tight clothing around the neck and chest.",
            "Stay calm and take slow, deep breaths.",
            "If prescribed nitroglycerin, take it as directed.",
            "Do NOT drive yourself to the hospital — call 108.",
        ],
        "hi": [
            "सीधे बैठें और आराम करें — चलें नहीं।",
            "गर्दन और छाती के कपड़े ढीले करें।",
            "शांत रहें और धीमी, गहरी सांसें लें।",
            "यदि डॉक्टर ने नाइट्रोग्लिसरीन दी है, तो निर्देशानुसार लें।",
            "खुद गाड़ी न चलाएं — 108 पर कॉल करें।",
        ],
    },
    "severe_bleeding": {
        "en": [
            "Apply firm, direct pressure with a clean cloth or bandage.",
            "Do not remove the cloth if soaked — add more cloth on top.",
            "Elevate the injured limb above the heart if possible.",
            "Keep the person lying down and warm.",
        ],
        "hi": [
            "साफ कपड़े से घाव पर सीधा और मजबूत दबाव डालें।",
            "कपड़ा भीग जाए तो हटाएं नहीं — ऊपर से और कपड़ा लगाएं।",
            "संभव हो तो चोट वाले हिस्से को दिल के स्तर से ऊपर उठाएं।",
            "व्यक्ति को लिटाकर रखें और गर्म रखें।",
        ],
    },
    "burns": {
        "en": [
            "Cool the burn with cool (not freezing) running water for 10-20 minutes.",
            "Do not apply ice, butter, or oil to the burn.",
            "Cover loosely with a clean, dry, non-stick cloth.",
            "Do not break blisters.",
        ],
        "hi": [
            "जले हुए हिस्से पर 10-20 मिनट तक ठंडा (बर्फ नहीं) पानी डालें।",
            "जले पर बर्फ, मक्खन या तेल न लगाएं।",
            "साफ, सूखे कपड़े से ढीला ढकें।",
            "छालों को न फोड़ें।",
        ],
    },
    "default": {
        "en": [
            "Stay calm and keep the person comfortable.",
            "Do not offer solid food or drink until evaluated.",
            "Note the exact time symptoms started.",
            "Have emergency contacts and medical history ready.",
        ],
        "hi": [
            "शांत रहें और व्यक्ति को आराम से रखें।",
            "जांच होने तक कुछ खाने या पीने को न दें।",
            "लक्षण कब शुरू हुए, समय याद रखें।",
            "आपातकालीन संपर्क और पुरानी दवाइयों की जानकारी तैयार रखें।",
        ],
    },
}


# ---------------------------------------------------------------------------
# Classification logic
# ---------------------------------------------------------------------------

def classify_urgency(text: str) -> UrgencyResult:
    """
    Main triage function.

    1. Runs deterministic guardrail (check_safety).
    2. Maps SafetyResult level to UrgencyResult.
    3. Attaches curated first-aid steps (whitelisted, non-diagnostic).
    4. Logs classification latency.
    """
    start_time = time.perf_counter()
    safety: SafetyResult = check_safety(text)
    latency_ms = (time.perf_counter() - start_time) * 1000.0

    level_meta = URGENCY_LEVELS[safety.level]

    # Select appropriate first-aid guidance
    first_aid = FIRST_AID_WHITELIST["default"]
    if safety.matched_keyword:
        kw = safety.matched_keyword.lower()
        if any(w in kw for w in ["chest", "छाती", "heart", "सीने"]):
            first_aid = FIRST_AID_WHITELIST.get("chest_pain", first_aid)
        elif any(w in kw for w in ["bleed", "खून", "रक्त"]):
            first_aid = FIRST_AID_WHITELIST.get("severe_bleeding", first_aid)
        elif any(w in kw for w in ["burn", "जल", "आग"]):
            first_aid = FIRST_AID_WHITELIST.get("burns", first_aid)

    return UrgencyResult(
        level=safety.level,
        label_en=level_meta["label_en"],
        label_hi=level_meta["label_hi"],
        color=level_meta["color"],
        facility_type_en=level_meta["facility_type_en"],
        facility_type_hi=level_meta["facility_type_hi"],
        guidance_en=level_meta["guidance_en"],
        guidance_hi=level_meta["guidance_hi"],
        cta_phone=level_meta["cta_phone"],
        matched_keyword=safety.matched_keyword,
        must_call_108=safety.must_call_108,
        first_aid_en=first_aid["en"],
        first_aid_hi=first_aid["hi"],
        latency_ms=round(latency_ms, 2),
    )
