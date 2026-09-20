"""
CareBridge — Maps Re-export
===========================
ponytail: thin alias to adapters.maps.map_view.
"""

from adapters.maps.map_view import (
    _FOLIUM_AVAILABLE,
    _LEVEL_TO_COLOR,
    build_facility_map,
    get_call_url,
    get_google_maps_directions_url,
    get_map_embed_iframe,
)
from core.models import Facility

INDIA_DEFAULT_LAT = 20.5937
INDIA_DEFAULT_LNG = 78.9629
INDIA_DEFAULT_ZOOM = 5

__all__ = [
    "_FOLIUM_AVAILABLE",
    "_LEVEL_TO_COLOR",
    "Facility",
    "build_facility_map",
    "get_call_url",
    "get_google_maps_directions_url",
    "get_map_embed_iframe",
    "INDIA_DEFAULT_LAT",
    "INDIA_DEFAULT_LNG",
    "INDIA_DEFAULT_ZOOM",
]
