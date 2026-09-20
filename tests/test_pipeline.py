"""
Tests for CareBridge Clean Architecture Services and Adapters
=============================================================
Verifies:
1. End-to-end pipeline returns proper urgency and latency logging
2. RED emergency prompts trigger immediate RED safety and 108 CTA
3. Indore hospital discovery returns valid nearby facilities sorted by distance
4. BioMistral adapter gracefully falls back to rule-based extractor
5. Geo locator falls back to Indore center
"""

import pytest

from adapters.geo.locator import (
    DEFAULT_INDORE_LAT,
    DEFAULT_INDORE_LNG,
    get_area_coordinates,
    haversine_km,
)
from adapters.llm.base import ExtractedSymptoms
from adapters.llm.biomistral import BioMistralAdapter
from adapters.llm.fallback_rules import RuleBasedLLMAdapter
from core.models import UrgencyLevel
from services.facility_service import FacilityService
from services.pipeline import IntakePipeline


def test_haversine_accuracy():
    # Distance between Vijay Nagar and Palasia in Indore is roughly 3.5 - 4.5 km
    vijay_nagar = (22.7539, 75.8872)
    palasia = (22.7235, 75.8856)
    dist = haversine_km(vijay_nagar[0], vijay_nagar[1], palasia[0], palasia[1])
    assert 3.0 <= dist <= 4.0


def test_indore_geo_fallback():
    coords = get_area_coordinates("NonExistentArea")
    assert coords.lat == DEFAULT_INDORE_LAT
    assert coords.lng == DEFAULT_INDORE_LNG


def test_rule_based_llm_extractor():
    adapter = RuleBasedLLMAdapter()
    res: ExtractedSymptoms = adapter.extract_symptoms("Mujhe 2 ghante se tez bukhar hai")
    assert "fever" in res.symptoms
    assert res.is_fallback is True
    assert res.detected_language == "en" or res.detected_language == "hi"


def test_biomistral_fallback_without_key():
    # Without an API key, BioMistralAdapter must return rule-based fallback without raising exception
    adapter = BioMistralAdapter(api_key=None)
    res = adapter.extract_symptoms("severe chest pain since 30 minutes")
    assert "chest_pain" in res.symptoms
    assert res.is_fallback is True


def test_indore_facility_service():
    service = FacilityService()
    # Query from Indore Center
    facilities = service.get_nearby_facilities(
        lat=DEFAULT_INDORE_LAT,
        lng=DEFAULT_INDORE_LNG,
        radius_km=20.0,
        limit=5,
        urgency_level="RED",
    )
    assert len(facilities) > 0
    # Nearest facility should be within 10 km of central Indore
    assert facilities[0].distance_km is not None
    assert facilities[0].distance_km < 10.0
    # Must have honest unknown representation for ICU if boolean
    assert facilities[0].icu_display in ("✅", "❌", "?")


def test_pipeline_red_emergency():
    pipeline = IntakePipeline()
    res = pipeline.process(
        text="Heart attack! Severe chest pain and sweating",
        user_lat=DEFAULT_INDORE_LAT,
        user_lng=DEFAULT_INDORE_LNG,
        use_llm=False,
    )
    assert res.safety.level == "RED"
    assert res.urgency.level == "RED"
    assert res.safety.must_call_108 is True
    assert res.urgency.cta_phone == "108"
    assert "safety_guardrail" in res.stage_latencies_ms
    assert res.total_latency_ms > 0.0


def test_pipeline_non_urgent_green():
    pipeline = IntakePipeline()
    res = pipeline.process(
        text="I have had a mild cough and cold since last week",
        user_lat=DEFAULT_INDORE_LAT,
        user_lng=DEFAULT_INDORE_LNG,
        use_llm=False,
    )
    assert res.safety.level == "GREEN"
    assert res.urgency.level == "GREEN"
    assert res.safety.must_call_108 is False
