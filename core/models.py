"""
CareBridge — Core Domain Models
================================
Typed, immutable/dataclass models for the non-diagnostic triage pipeline.
Zero external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class UrgencyLevel(str, Enum):
    RED = "RED"          # Life-threatening emergency -> Call 108
    YELLOW = "YELLOW"    # High priority -> Urgent care within 2 hours
    GREEN = "GREEN"      # Non-urgent -> Clinic / OPD visit


@dataclass(frozen=True)
class SafetyResult:
    """Immutable result from deterministic safety guardrail check."""
    level: str                           # "RED" | "YELLOW" | "GREEN"
    matched_keyword: Optional[str] = None
    action_en: str = ""
    action_hi: str = ""
    must_call_108: bool = False

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "matched_keyword": self.matched_keyword,
            "action_en": self.action_en,
            "action_hi": self.action_hi,
            "must_call_108": self.must_call_108,
        }


@dataclass
class UrgencyResult:
    """Result from urgency triage classification."""
    level: str                           # "RED" | "YELLOW" | "GREEN"
    label_en: str
    label_hi: str
    color: str                           # HEX color token
    facility_type_en: str
    facility_type_hi: str
    guidance_en: str
    guidance_hi: str
    cta_phone: Optional[str] = None
    matched_keyword: Optional[str] = None
    must_call_108: bool = False
    first_aid_en: list[str] = field(default_factory=list)
    first_aid_hi: list[str] = field(default_factory=list)
    latency_ms: float = 0.0

    @property
    def is_emergency(self) -> bool:
        return self.level == "RED"

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "label_en": self.label_en,
            "label_hi": self.label_hi,
            "color": self.color,
            "facility_type_en": self.facility_type_en,
            "facility_type_hi": self.facility_type_hi,
            "guidance_en": self.guidance_en,
            "guidance_hi": self.guidance_hi,
            "cta_phone": self.cta_phone,
            "matched_keyword": self.matched_keyword,
            "must_call_108": self.must_call_108,
            "first_aid_en": self.first_aid_en,
            "first_aid_hi": self.first_aid_hi,
            "latency_ms": self.latency_ms,
        }


@dataclass
class Facility:
    """Healthcare facility entity."""
    id: str
    name: str
    name_hi: str
    facility_type: str                  # 'hospital' | 'blood_bank' | 'clinic' | 'pharmacy'
    address: str
    lat: float
    lng: float
    phone: str
    emergency_number: Optional[str] = None
    distance_km: Optional[float] = None
    has_icu: Optional[bool] = None      # None = unknown -> displays "?"
    has_blood_bank: Optional[bool] = None
    open_24h: Optional[bool] = None     # None = unknown -> displays "?"
    specialties: list[str] = field(default_factory=list)

    @property
    def icu_display(self) -> str:
        """Honest display: never show false checkmark (TRD §8)."""
        if self.has_icu is True:
            return "✅"
        if self.has_icu is False:
            return "❌"
        return "?"

    @property
    def open_display(self) -> str:
        if self.open_24h is True:
            return "24h"
        if self.open_24h is False:
            return "Limited"
        return "?"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "name_hi": self.name_hi,
            "facility_type": self.facility_type,
            "address": self.address,
            "lat": self.lat,
            "lng": self.lng,
            "phone": self.phone,
            "emergency_number": self.emergency_number,
            "distance_km": round(self.distance_km, 2) if self.distance_km is not None else None,
            "has_icu": self.icu_display,
            "has_blood_bank": self.has_blood_bank,
            "open_24h": self.open_display,
            "specialties": self.specialties,
        }


@dataclass
class PipelineResult:
    """Complete end-to-end intake result with stage latency tracking."""
    input_text: str
    detected_lang: str
    safety: SafetyResult
    urgency: UrgencyResult
    facilities: list[Facility]
    stage_latencies_ms: dict[str, float] = field(default_factory=dict)
    total_latency_ms: float = 0.0
