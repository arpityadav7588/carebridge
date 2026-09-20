"""
CareBridge — End-to-End Triage & Intake Pipeline
=================================================
Application Orchestration Layer:
  Step 1: Ingest & Normalize (Hinglish/Hindi/English)
  Step 2: DETERMINISTIC SAFETY GUARDRAIL (Zero-LLM regex/blocklist)
  Step 3: Urgency Classification & Whitelist First-Aid
  Step 4: Optional LLM Entity Extraction (BioMistral or Rule Fallback)
  Step 5: Facility Geo-Matching & Sorting (Indore priority)

Strict adherence to TRD §7 (Safety first) and TRD §9 (Latency budget).
"""

from __future__ import annotations

import re
import time
from typing import Optional

from adapters.geo.locator import DEFAULT_INDORE_LAT, DEFAULT_INDORE_LNG
from adapters.llm.base import BaseLLMAdapter
from adapters.llm.biomistral import BioMistralAdapter
from core.models import Facility, PipelineResult, SafetyResult, UrgencyResult
from core.safety import check_safety
from core.urgency import classify_urgency
from services.facility_service import FacilityService


class IntakePipeline:
    """Orchestrates intake, guardrail, triage, and facility matching."""

    def __init__(
        self,
        llm_adapter: Optional[BaseLLMAdapter] = None,
        facility_service: Optional[FacilityService] = None,
    ):
        self.llm_adapter = llm_adapter or BioMistralAdapter()
        self.facility_service = facility_service or FacilityService()

    def _detect_lang(self, text: Optional[str]) -> str:
        if not text or not isinstance(text, str):
            return "en"
        if re.search(r"[\u0900-\u097F]", text):
            return "hi"
        return "en"

    def process(
        self,
        text: Optional[str] = "",
        user_lat: Optional[float] = None,
        user_lng: Optional[float] = None,
        facility_type: str = "hospital",
        limit_facilities: int = 5,
        use_llm: bool = False,
    ) -> PipelineResult:
        """
        Executes the full pipeline and tracks stage latencies.
        """
        text = str(text or "").strip()
        pipeline_start = time.perf_counter()
        latencies: dict[str, float] = {}

        # Step 1: Ingestion & Language detection
        t0 = time.perf_counter()
        detected_lang = self._detect_lang(text)
        latencies["ingestion"] = round((time.perf_counter() - t0) * 1000.0, 2)

        # Step 2: Deterministic Safety Guardrail (Zero-LLM, mandatory)
        t0 = time.perf_counter()
        safety: SafetyResult = check_safety(text)
        latencies["safety_guardrail"] = round((time.perf_counter() - t0) * 1000.0, 2)

        # Step 3: Urgency Triage & Whitelist First-Aid
        t0 = time.perf_counter()
        urgency: UrgencyResult = classify_urgency(text)
        latencies["urgency_triage"] = round((time.perf_counter() - t0) * 1000.0, 2)

        # Step 4: Optional LLM Symptom Extraction (Only if requested and not critical RED bypass)
        if use_llm and safety.level != "RED":
            t0 = time.perf_counter()
            _ = self.llm_adapter.extract_symptoms(text)
            latencies["llm_extraction"] = round((time.perf_counter() - t0) * 1000.0, 2)
        else:
            latencies["llm_extraction"] = 0.0

        # Step 5: Facility Matching
        t0 = time.perf_counter()
        effective_lat = user_lat if user_lat is not None else DEFAULT_INDORE_LAT
        effective_lng = user_lng if user_lng is not None else DEFAULT_INDORE_LNG

        facilities: list[Facility] = self.facility_service.get_nearby_facilities(
            lat=effective_lat,
            lng=effective_lng,
            facility_type=facility_type,
            limit=limit_facilities,
            urgency_level=urgency.level,
        )
        latencies["facility_matching"] = round((time.perf_counter() - t0) * 1000.0, 2)

        total_latency = round((time.perf_counter() - pipeline_start) * 1000.0, 2)

        return PipelineResult(
            input_text=text,
            detected_lang=detected_lang,
            safety=safety,
            urgency=urgency,
            facilities=facilities,
            stage_latencies_ms=latencies,
            total_latency_ms=total_latency,
        )
