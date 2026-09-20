"""
CareBridge — Urgency Classifier Tests
=======================================
Tests for urgency.classify_urgency():
  - Level assignment matches safety guardrail
  - Bilingual labels present
  - Facility type returned (not disease name)
  - CTA phone numbers correct
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app.urgency import classify_urgency, UrgencyResult, URGENCY_LEVELS


def test_red_level_english():
    result = classify_urgency("heart attack severe chest pain")
    assert result.level == "RED"
    assert result.must_call_108 is True
    assert result.cta_phone == "108"


def test_red_level_hindi():
    result = classify_urgency("दिल का दौरा पड़ा है")
    assert result.level == "RED"
    assert result.must_call_108 is True


def test_yellow_level():
    result = classify_urgency("high fever very confused")
    assert result.level == "YELLOW"
    assert result.must_call_108 is False


def test_green_level():
    result = classify_urgency("mild cough and runny nose")
    assert result.level == "GREEN"
    assert result.must_call_108 is False
    assert result.cta_phone is None


def test_bilingual_labels_present():
    for level in ["RED", "YELLOW", "GREEN"]:
        meta = URGENCY_LEVELS[level]
        assert meta["label_en"]
        assert meta["label_hi"]
        assert meta["facility_type_en"]
        assert meta["facility_type_hi"]
        assert meta["guidance_en"]
        assert meta["guidance_hi"]


def test_facility_type_not_disease():
    """Facility type must describe a place, not a disease."""
    for level in ["RED", "YELLOW", "GREEN"]:
        meta = URGENCY_LEVELS[level]
        ftype = meta["facility_type_en"].lower()
        # Must not contain clinical disease terms
        assert "diagnos" not in ftype
        assert "disease" not in ftype
        assert "cancer" not in ftype
        # Must contain facility-related words
        assert any(word in ftype for word in [
            "hospital", "emergency", "clinic", "centre", "center", "department", "care", "health"
        ]), f"Facility type for {level} doesn't sound like a facility: {ftype!r}"


def test_result_to_dict():
    result = classify_urgency("accident road")
    d = result.to_dict()
    expected_keys = {
        "level", "label_en", "label_hi", "color",
        "facility_type_en", "facility_type_hi",
        "guidance_en", "guidance_hi", "cta_phone",
        "matched_keyword", "must_call_108"
    }
    assert expected_keys.issubset(d.keys())


def test_urgency_result_type():
    result = classify_urgency("fever")
    assert isinstance(result, UrgencyResult)
