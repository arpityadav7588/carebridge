"""
CareBridge — Facility Service
==============================
Business logic for nearby healthcare facility discovery and ranking.
Loads Indore emergency hospitals as primary source, with pan-India fallback.
Prioritizes ICU / 24h facilities for RED emergencies.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from adapters.geo.locator import DEFAULT_INDORE_LAT, DEFAULT_INDORE_LNG, haversine_km
from core.models import Facility

_DATA_DIR = Path(__file__).parent.parent / "data"


def _load_json(file_name: str) -> list[dict]:
    path = _DATA_DIR / file_name
    if not path.exists():
        return []
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


class FacilityService:
    """Manages facility data loading and spatial ranking."""

    def __init__(self):
        # 1. Primary: Indore emergency facilities
        self.indore_hospitals = _load_json("hospitals_indore.json")
        # 2. Secondary: Pan-India facilities
        self.india_hospitals = _load_json("hospitals_india.json")
        # 3. Blood banks
        self.blood_banks = _load_json("blood_banks.json")

    def _dict_to_facility(self, d: dict, distance_km: Optional[float] = None) -> Facility:
        return Facility(
            id=d.get("id", ""),
            name=d.get("name", ""),
            name_hi=d.get("name_hi", d.get("name", "")),
            facility_type=d.get("facility_type", "hospital"),
            address=d.get("address", ""),
            lat=float(d.get("lat", 0.0)),
            lng=float(d.get("lng", 0.0)),
            phone=d.get("phone", ""),
            emergency_number=d.get("emergency_number"),
            distance_km=distance_km,
            has_icu=d.get("has_icu"),
            has_blood_bank=d.get("has_blood_bank"),
            open_24h=d.get("open_24h"),
            specialties=d.get("specialties", []),
        )

    def get_nearby_facilities(
        self,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        facility_type: str = "hospital",
        radius_km: float = 50.0,
        limit: int = 5,
        urgency_level: str = "GREEN",
    ) -> list[Facility]:
        """
        Returns sorted list of nearby facilities.
        Falls back to Indore center if coordinates are None.
        """
        user_lat = lat if lat is not None else DEFAULT_INDORE_LAT
        user_lng = lng if lng is not None else DEFAULT_INDORE_LNG

        raw_pool: list[dict] = []
        if facility_type == "blood_bank":
            raw_pool = list(self.blood_banks)
        else:
            # Prefer Indore dataset first; append pan-India pool
            raw_pool = list(self.indore_hospitals) + [
                h for h in self.india_hospitals if h.get("id") not in {ih.get("id") for ih in self.indore_hospitals}
            ]

        results: list[Facility] = []
        for d in raw_pool:
            d_type = d.get("facility_type", "hospital")
            if facility_type and facility_type != "all" and d_type != facility_type:
                continue

            dist = haversine_km(user_lat, user_lng, float(d["lat"]), float(d["lng"]))
            if dist <= radius_km:
                results.append(self._dict_to_facility(d, distance_km=dist))

        # Triage-aware sorting:
        # For RED urgency, prioritize facilities with ICU capability and 24h open status
        if urgency_level == "RED":
            results.sort(
                key=lambda f: (
                    0 if (f.has_icu is True and f.open_24h is True) else 1,
                    f.distance_km if f.distance_km is not None else 9999.0,
                )
            )
        else:
            results.sort(key=lambda f: f.distance_km if f.distance_km is not None else 9999.0)

        return results[:limit]
