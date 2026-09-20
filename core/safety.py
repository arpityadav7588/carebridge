"""
CareBridge — Deterministic Safety Guardrail
============================================
CRITICAL: This module executes BEFORE any LLM call.
No ML/LLM logic here — regex + keyword cluster only.
A match -> RED urgency + "Call 108 now" + dialer CTA.

Source: data/red_flags.json (authoritative).
TRD §7 compliance: Deterministic Guardrail First.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Optional

from core.models import SafetyResult

# ---------------------------------------------------------------------------
# Load red-flag data
# ---------------------------------------------------------------------------

_DATA_DIR = Path(__file__).parent.parent / "data"
_RED_FLAGS_PATH = _DATA_DIR / "red_flags.json"

with _RED_FLAGS_PATH.open(encoding="utf-8") as _f:
    _RED_FLAGS_DATA: dict = json.load(_f)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Unicode-normalize, strip diacritics/nuktas, and lowercase for safe Hindi + English matching."""
    text = unicodedata.normalize("NFC", text)
    # Hindi phonetic normalization: chandrabindu -> anusvara
    text = text.replace("\u0901", "\u0902")
    # Devanagari nukta sign and precomposed characters
    text = text.replace("\u093c", "")
    text = text.replace("\u0958", "\u0915")  # क़ -> क
    text = text.replace("\u0959", "\u0916")  # ख़ -> ख
    text = text.replace("\u095a", "\u0917")  # ग़ -> ग
    text = text.replace("\u095b", "\u091c")  # ज़ -> ज
    text = text.replace("\u095c", "\u0921")  # ड़ -> ड
    text = text.replace("\u095d", "\u0922")  # ढ़ -> ढ
    text = text.replace("\u095e", "\u092b")  # फ़ -> फ
    return text.lower().strip()


# Build flat keyword -> cluster lookup at import time (O(1) per check)
_RED_KEYWORDS: set[str] = set()
_YELLOW_KEYWORDS: set[str] = set()

for _cluster in _RED_FLAGS_DATA["RED"]["clusters"].values():
    for _kw in _cluster.get("keywords_en", []):
        _RED_KEYWORDS.add(_normalize(_kw))
    for _kw in _cluster.get("keywords_hi", []):
        _RED_KEYWORDS.add(_normalize(_kw))

for _cluster in _RED_FLAGS_DATA["YELLOW"]["clusters"].values():
    for _kw in _cluster.get("keywords_en", []):
        _YELLOW_KEYWORDS.add(_normalize(_kw))
    for _kw in _cluster.get("keywords_hi", []):
        _YELLOW_KEYWORDS.add(_normalize(_kw))


def _contains_keyword(text: str, keywords: set[str]) -> Optional[str]:
    """
    Returns the first matching keyword found in text, or None.
    Uses word-boundary regex for English/Latin; substring match for Hindi/Devanagari.
    """
    norm = _normalize(text)
    for kw in keywords:
        # Devanagari: no word-boundary concept — use substring
        if re.search(r"[\u0900-\u097F]", kw):
            if kw in norm:
                return kw
        else:
            # English / Latin: word boundary check
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, norm):
                return kw
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_safety(text: str) -> SafetyResult:
    """
    Deterministic, regex-based safety guardrail.

    Steps:
    1. Normalize input.
    2. Check RED clusters — any match -> RED + 108 CTA immediately.
    3. Check YELLOW clusters — any match -> YELLOW.
    4. Default -> GREEN.
    """
    if not text or not text.strip():
        return SafetyResult(
            level="GREEN",
            action_en="No symptoms described.",
            action_hi="कोई लक्षण वर्णित नहीं हैं।",
            must_call_108=False,
        )

    # 1. RED check (deterministic, highest priority)
    matched_red = _contains_keyword(text, _RED_KEYWORDS)
    if matched_red:
        return SafetyResult(
            level="RED",
            matched_keyword=matched_red,
            action_en="CRITICAL EMERGENCY: Call 108 immediately.",
            action_hi="गंभीर आपातकाल: तुरंत 108 पर कॉल करें।",
            must_call_108=True,
        )

    # 2. YELLOW check
    matched_yellow = _contains_keyword(text, _YELLOW_KEYWORDS)
    if matched_yellow:
        return SafetyResult(
            level="YELLOW",
            matched_keyword=matched_yellow,
            action_en="High priority: Seek care within 2 hours.",
            action_hi="उच्च प्राथमिकता: 2 घंटे के भीतर इलाज कराएं।",
            must_call_108=False,
        )

    # 3. GREEN (default)
    return SafetyResult(
        level="GREEN",
        action_en="Non-urgent: Schedule a clinic visit.",
        action_hi="सामान्य: क्लिनिक में अपॉइंटमेंट लें।",
        must_call_108=False,
    )


def is_safe_input(text: str) -> bool:
    """Convenience boolean check: True if GREEN (not urgent)."""
    return check_safety(text).level == "GREEN"


def get_red_clusters() -> dict:
    """Returns the raw RED cluster dictionary from red_flags.json."""
    return _RED_FLAGS_DATA["RED"]["clusters"]


def get_yellow_clusters() -> dict:
    """Returns the raw YELLOW cluster dictionary from red_flags.json."""
    return _RED_FLAGS_DATA["YELLOW"]["clusters"]
