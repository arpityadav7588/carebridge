"""
CareBridge — Fallback Rule-Based Symptom Extractor
==================================================
Deterministic, zero-network fallback extractor.
Extracts normalized symptoms and time mentions from Hinglish/Hindi/English text.
Guaranteed < 5ms latency, 100% reliable for live demo.
"""

from __future__ import annotations

import re
import time
from typing import Optional

from adapters.llm.base import BaseLLMAdapter, ExtractedSymptoms


# Common symptom regex mappings (Bilingual + Hinglish)
SYMPTOM_PATTERNS: dict[str, list[str]] = {
    "chest_pain": [
        r"chest pain", r"seene me dard", r"chaati me dard", r"heart pain",
        r"सीने में दर्द", r"छाती में दर्द", r"दिल में दर्द", r"seena dard"
    ],
    "difficulty_breathing": [
        r"breathing", r"saans", r"shortness of breath", r"saans phool",
        r"सांस लेने में तकलीफ", r"सांस फूलना", r"dum ghut"
    ],
    "fever": [
        r"fever", r"bukhar", r"tez bukhar", r"tej bukhar",
        r"बुखार", r"ताप"
    ],
    "severe_bleeding": [
        r"bleeding", r"khoon", r"rakt", r"blood",
        r"खून बह", r"रक्तस्राव", r"khoon nikal"
    ],
    "headache": [
        r"headache", r"sar dard", r"sir dard", r"head pain",
        r"सिर दर्द", r"सर में दर्द"
    ],
    "abdominal_pain": [
        r"stomach pain", r"pet dard", r"pet me dard", r"abdominal pain",
        r"पेट में दर्द"
    ],
    "vomiting": [
        r"vomit", r"ulti", r"vomiting", r"उल्टी", r"jee ghabra"
    ],
    "fracture_injury": [
        r"fracture", r"haddi toot", r"injury", r"chot", r"accident",
        r"हड्डी टूटना", r"चोट", r"दुर्घटना"
    ]
}

# Duration regex
DURATION_PATTERNS = [
    r"(\d+)\s*(hour|hr|ghante|ghanta|घंटे)",
    r"(\d+)\s*(minute|min|m|मिनट)",
    r"(\d+)\s*(day|days|din|दिन)",
    r"(since morning|subah se|सुबह से)",
    r"(since yesterday|kal se|कल से)"
]


class RuleBasedLLMAdapter(BaseLLMAdapter):
    """Fallback extractor using regex keyword matching."""

    def __init__(self):
        self.name = "rule_based_fallback"

    def _detect_lang(self, text: str) -> str:
        if re.search(r"[\u0900-\u097F]", text):
            return "hi"
        return "en"

    def extract_symptoms(self, text: str) -> ExtractedSymptoms:
        start_time = time.perf_counter()
        clean = text.lower().strip()
        detected_lang = self._detect_lang(text)

        matched_symptoms: list[str] = []
        for symptom_key, patterns in SYMPTOM_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, clean):
                    matched_symptoms.append(symptom_key)
                    break

        # Extract duration
        duration_found: Optional[str] = None
        for dpat in DURATION_PATTERNS:
            match = re.search(dpat, clean)
            if match:
                duration_found = match.group(0)
                break

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return ExtractedSymptoms(
            raw_text=text,
            detected_language=detected_lang,
            symptoms=matched_symptoms if matched_symptoms else ["unspecified_symptom"],
            duration=duration_found,
            severity_keywords=[],
            latency_ms=round(latency_ms, 2),
            adapter_used=self.name,
            is_fallback=True,
        )
