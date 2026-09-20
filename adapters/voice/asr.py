"""
CareBridge — Speech-to-Text (ASR) & Normalization Adapter
=========================================================
Multilingual voice input support (Hindi + English + Hinglish).
Fallback: text input + quick-chip selection if ASR is unavailable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

# Quick-chip definitions (bilingual symptom shortcuts)
QUICK_CHIPS: list[dict] = [
    {"id": "chest_pain",      "label_en": "Chest Pain",        "label_hi": "सीने में दर्द",    "urgency_hint": "RED"},
    {"id": "breathing",       "label_en": "Breathing Trouble",  "label_hi": "सांस में तकलीफ",  "urgency_hint": "RED"},
    {"id": "unconscious",     "label_en": "Unconscious Person", "label_hi": "बेहोश व्यक्ति",   "urgency_hint": "RED"},
    {"id": "accident",        "label_en": "Accident / Injury",  "label_hi": "दुर्घटना / चोट",  "urgency_hint": "RED"},
    {"id": "heavy_bleeding",  "label_en": "Heavy Bleeding",     "label_hi": "ज्यादा खून",      "urgency_hint": "RED"},
    {"id": "high_fever",      "label_en": "High Fever",         "label_hi": "तेज बुखार",        "urgency_hint": "YELLOW"},
    {"id": "severe_pain",     "label_en": "Severe Pain",        "label_hi": "तेज दर्द",         "urgency_hint": "YELLOW"},
    {"id": "vomiting",        "label_en": "Vomiting",           "label_hi": "उल्टी",            "urgency_hint": "GREEN"},
    {"id": "headache",        "label_en": "Headache",           "label_hi": "सिरदर्द",          "urgency_hint": "GREEN"},
    {"id": "fever",           "label_en": "Fever",              "label_hi": "बुखार",            "urgency_hint": "GREEN"},
    {"id": "cough",           "label_en": "Cough",              "label_hi": "खांसी",            "urgency_hint": "GREEN"},
    {"id": "diarrhea",        "label_en": "Diarrhea",           "label_hi": "दस्त",             "urgency_hint": "GREEN"},
]

CHIP_ID_TO_TEXT: dict[str, str] = {c["id"]: c["label_en"] for c in QUICK_CHIPS}
CHIP_ID_TO_TEXT_HI: dict[str, str] = {c["id"]: c["label_hi"] for c in QUICK_CHIPS}

_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")

# Common Hinglish phonetic normalizations
_HINGLISH_MAP: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bseene\s+me\s+dard\b", re.I), "chest pain"),
    (re.compile(r"\bchaati\s+me\s+dard\b", re.I), "chest pain"),
    (re.compile(r"\bsaans\s+nahi\s+aa\s+rahi\b", re.I), "difficulty breathing"),
    (re.compile(r"\bsaans\s+phool\s+rahi\b", re.I), "difficulty breathing"),
    (re.compile(r"\bkhoon\s+beh\s+raha\b", re.I), "severe bleeding"),
    (re.compile(r"\bbehosh\b", re.I), "loss of consciousness"),
    (re.compile(r"\btez\s+bukhar\b", re.I), "high fever"),
    (re.compile(r"\btej\s+bukhar\b", re.I), "high fever"),
    (re.compile(r"\bchakkar\b", re.I), "dizziness"),
    (re.compile(r"\bulti\b", re.I), "vomiting"),
    (re.compile(r"\bdast\b", re.I), "diarrhea"),
]


def detect_language(text: str) -> str:
    """Returns 'hi' if text contains Devanagari script; else 'en'."""
    if _DEVANAGARI_RE.search(text):
        return "hi"
    return "en"


def normalize_hinglish(text: str) -> str:
    """Expands common Hinglish medical phrases into standardized keywords."""
    result = text
    for pattern, replacement in _HINGLISH_MAP:
        result = pattern.sub(f"{replacement} ({pattern.pattern[2:-2]})", result)
    return result


@dataclass
class VoiceInputResult:
    raw_text: str
    normalized_text: str
    detected_lang: str
    chip_texts: list[str]
    combined_text: str
    source: str                         # 'voice' | 'text' | 'chip_only'


def process_input(
    raw_text: str,
    selected_chip_ids: Optional[list[str]] = None,
    source: str = "text",
) -> VoiceInputResult:
    """Combines raw user text + selected quick-chips into an inquiry string."""
    chips = selected_chip_ids or []
    chip_texts_en = [CHIP_ID_TO_TEXT[cid] for cid in chips if cid in CHIP_ID_TO_TEXT]
    clean_text = raw_text.strip()
    detected_lang = detect_language(clean_text) if clean_text else "en"
    normalized = normalize_hinglish(clean_text) if clean_text else ""

    parts = []
    if normalized:
        parts.append(normalized)
    if chip_texts_en:
        parts.append("; ".join(chip_texts_en))

    combined = ". ".join(parts) if parts else ""

    actual_source = source
    if not clean_text and chips:
        actual_source = "chip_only"

    return VoiceInputResult(
        raw_text=clean_text,
        normalized_text=normalized,
        detected_lang=detected_lang,
        chip_texts=chip_texts_en,
        combined_text=combined,
        source=actual_source,
    )
