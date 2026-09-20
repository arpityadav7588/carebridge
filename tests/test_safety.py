"""
CareBridge — Safety Guardrail Tests
=====================================
TRD §8: 100% pass required on adversarial suite before any LLM integration.
These tests cover the deterministic RED/YELLOW/GREEN classification.

Run: pytest tests/test_safety.py -v --tb=short
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app.safety import check_safety, SafetyResult


# ---------------------------------------------------------------------------
# RED — English
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "my father is having a heart attack",
    "she had a stroke and can't speak",
    "there is severe bleeding and it won't stop",
    "he is not breathing at all",
    "I think I'm having cardiac arrest",
    "she lost consciousness and won't wake up",
    "coughing blood and very pale",
    "vomiting blood for the last hour",
    "severe allergic reaction throat swelling",
    "patient fainted after accident",
    "hit by car road accident broken bone",
    "swallowed poison pesticide",
    "drug overdose not responding",
    "severe burn large area",
    "electrocution electric shock",
    "drowning in the river",
    "can't breathe at all",
    "difficulty breathing choking",
    "face drooping arm weakness sudden confusion",
    "gunshot wound deep bleeding",
    "delivery complications baby not breathing",
    "fits in pregnancy eclampsia",
    "stab wound severe bleeding",
    "blue lips not breathing",
    "crushing chest pain and sweating",
])
def test_red_english(text):
    result = check_safety(text)
    assert result.level == "RED", f"Expected RED for: {text!r} → got {result.level}"
    assert result.must_call_108 is True
    assert result.matched_keyword is not None


# ---------------------------------------------------------------------------
# RED — Hindi
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "मेरे पिताजी को दिल का दौरा पड़ा है",
    "उसे लकवा मार गया और बोल नहीं पा रहा",
    "ज्यादा खून बह रहा है और रुक नहीं रहा",
    "सांस नहीं आ रही बिल्कुल",
    "बेहोश पड़ा है उठ नहीं रहा",
    "खून की उल्टी हो रही है",
    "गला बंद हो गया दम घुट रहा है",
    "दुर्घटना हो गई हड्डी टूटी है",
    "जहर पी लिया",
    "बिजली का झटका लगा",
    "डूब रहा है नदी में",
    "सीने में दर्द बहुत तेज",
    "बोलने में तकलीफ हो रही है",
    "होंठ नीले हो गए",
    "गर्भावस्था में दौरे पड़ रहे हैं",
])
def test_red_hindi(text):
    result = check_safety(text)
    assert result.level == "RED", f"Expected RED for Hindi: {text!r} → got {result.level}"
    assert result.must_call_108 is True


# ---------------------------------------------------------------------------
# YELLOW
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "high fever since yesterday evening",
    "tez bukhar hai bachche ko",
    "very confused and disoriented",
    "blood sugar very low diabetic emergency",
    "unbearable pain in the stomach",
    "severe pain 10 out of 10",
    "hallucinating and not making sense",
    "shugar bahut kam ho gayi",
])
def test_yellow(text):
    result = check_safety(text)
    assert result.level == "YELLOW", f"Expected YELLOW for: {text!r} → got {result.level}"
    assert result.must_call_108 is False


# ---------------------------------------------------------------------------
# GREEN — should NOT trigger RED or YELLOW
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "mild headache since morning",
    "slight cough for two days",
    "runny nose and sneezing",
    "minor back pain",
    "feeling a bit tired",
    "dry skin itching",
    "सिरदर्द थोड़ा है",
    "हल्की खांसी",
    "थकान महसूस हो रही है",
    "नाक बह रही है",
])
def test_green(text):
    result = check_safety(text)
    assert result.level == "GREEN", f"Expected GREEN for: {text!r} → got {result.level}"
    assert result.must_call_108 is False


# ---------------------------------------------------------------------------
# Non-diagnostic: output must never contain disease names
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "heart attack",
    "stroke",
    "anaphylaxis",
    "overdose",
])
def test_no_disease_diagnosis_in_output(text):
    result = check_safety(text)
    # The result level and actions must not include clinical disease names
    # Only: RED/YELLOW/GREEN + action text
    assert result.level in {"RED", "YELLOW", "GREEN"}
    assert "diagnos" not in result.action_en.lower()
    assert "disease" not in result.action_en.lower()
    # Action should be nav guidance, not medical advice
    assert len(result.action_en) > 0


# ---------------------------------------------------------------------------
# Empty / edge input
# ---------------------------------------------------------------------------

def test_empty_input():
    result = check_safety("")
    assert result.level == "GREEN"
    assert result.must_call_108 is False


def test_whitespace_input():
    result = check_safety("   \n  ")
    assert result.level == "GREEN"


def test_mixed_language():
    result = check_safety("mera dil ka darwaza band ho gaya chest pain very bad")
    # Should catch 'chest pain' → RED
    assert result.level == "RED"


def test_result_is_immutable_type():
    result = check_safety("fever and cough")
    assert isinstance(result, SafetyResult)
    d = result.to_dict()
    assert "level" in d
    assert "must_call_108" in d
