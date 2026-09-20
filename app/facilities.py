"""
CareBridge — Facility Service Re-export
=======================================
ponytail: delegates to services.facility_service and core.models.
"""

from adapters.geo.locator import haversine_km
from core.models import Facility
from services.facility_service import FacilityService

_service = FacilityService()


def find_nearby_hospitals(
    lat: float,
    lng: float,
    urgency_level: str = "GREEN",
    max_results: int = 5,
    max_radius_km: float = 50.0,
) -> list[Facility]:
    return _service.get_nearby_facilities(
        lat=lat,
        lng=lng,
        facility_type="hospital",
        radius_km=max_radius_km,
        limit=max_results,
        urgency_level=urgency_level,
    )


def find_nearby_blood_banks(
    lat: float,
    lng: float,
    max_results: int = 3,
    max_radius_km: float = 50.0,
) -> list[Facility]:
    return _service.get_nearby_facilities(
        lat=lat,
        lng=lng,
        facility_type="blood_bank",
        radius_km=max_radius_km,
        limit=max_results,
    )


def get_facilities_for_urgency(
    lat: float,
    lng: float,
    urgency_level: str,
    max_results: int = 5,
) -> dict[str, list[Facility]]:
    hospitals = find_nearby_hospitals(lat, lng, urgency_level, max_results)
    blood_banks = find_nearby_blood_banks(lat, lng, max_results=3) if urgency_level in ("RED", "YELLOW") else []
    return {"hospitals": hospitals, "blood_banks": blood_banks}


__all__ = [
    "Facility",
    "haversine_km",
    "find_nearby_hospitals",
    "find_nearby_blood_banks",
    "get_facilities_for_urgency",
]
