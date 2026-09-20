"""
CareBridge — Geolocation & Locator Adapter
==========================================
Provides user location resolution with graceful fallbacks.
Primary location focus: Indore, Madhya Pradesh.
Guaranteed fallback to Indore center if GPS is unavailable.
"""

from __future__ import annotations

import math
from typing import NamedTuple, Optional

_EARTH_RADIUS_KM = 6371.0

# Indore default center (Rajwada / Central Indore)
DEFAULT_INDORE_LAT = 22.7196
DEFAULT_INDORE_LNG = 75.8577

# Known Indore neighborhood coordinates for quick location pickers
INDORE_AREAS: dict[str, tuple[float, float]] = {
    "Palasia / Old Palasia": (22.7235, 75.8856),
    "Vijay Nagar / Scheme 54": (22.7539, 75.8872),
    "Bhawarkua / AB Road": (22.6917, 75.8671),
    "Rajwada / Central Indore": (22.7196, 75.8577),
    "Eastern Ring Road": (22.7533, 75.8937),
    "Manik Bagh": (22.6958, 75.8459),
    "Dhar Road / Sirpur": (22.7092, 75.8236),
    "Annapurna": (22.6985, 75.8362),
    "Bhawrasla / Sanwer Road": (22.7932, 75.8427),
    "Rau": (22.6372, 75.8055),
}


class Coordinates(NamedTuple):
    lat: float
    lng: float
    label: str = "Custom / Current GPS"


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculates great-circle distance in km between two lat/lng points."""
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return _EARTH_RADIUS_KM * c


def get_area_coordinates(area_name: Optional[str]) -> Coordinates:
    """
    Resolves area coordinates from name.
    Falls back to Indore center if area is not recognized or None.
    """
    if area_name and area_name in INDORE_AREAS:
        lat, lng = INDORE_AREAS[area_name]
        return Coordinates(lat=lat, lng=lng, label=area_name)
    return Coordinates(lat=DEFAULT_INDORE_LAT, lng=DEFAULT_INDORE_LNG, label="Indore Central (Default)")
