"""
CareBridge — Map & Routing Adapter
===================================
Generates Leaflet/OpenStreetMap map components and navigation URLs.
Free, open-source stack (Folium / OpenStreetMap / Google Maps URI fallback).
No paid API key required.
"""

from __future__ import annotations

from typing import Optional
from urllib.parse import quote_plus

try:
    import folium
    _FOLIUM_AVAILABLE = True
except ImportError:
    _FOLIUM_AVAILABLE = False

from adapters.geo.locator import DEFAULT_INDORE_LAT, DEFAULT_INDORE_LNG
from core.models import Facility

# Urgency colour -> map pin colour
_LEVEL_TO_COLOR = {
    "RED": "red",
    "YELLOW": "orange",
    "GREEN": "green",
}


def get_google_maps_directions_url(
    dest_lat: float,
    dest_lng: float,
    dest_name: str = "",
) -> str:
    """Returns a Google Maps deep-link for turn-by-turn navigation."""
    query = f"{dest_lat},{dest_lng}"
    label = quote_plus(dest_name or query)
    return (
        f"https://www.google.com/maps/dir/?api=1"
        f"&destination={query}"
        f"&destination_place_id={label}"
        "&travelmode=driving"
        "&dir_action=navigate"
    )


def get_call_url(phone_number: str) -> str:
    """Returns tel: URL for click-to-call buttons."""
    clean = "".join(c for c in phone_number if c.isdigit() or c == "+")
    return f"tel:{clean}"


def build_facility_map(
    arg1,
    arg2: Optional[float | list[Facility]] = None,
    arg3: Optional[float | list[Facility]] = None,
    urgency_level: str = "GREEN",
    zoom: int = 13,
) -> Optional[folium.Map]:
    """
    Builds an interactive Folium Leaflet map with user & facility markers.
    Accepts either (facilities, user_lat, user_lng) or (user_lat, user_lng, facilities).
    """
    if not _FOLIUM_AVAILABLE:
        return None

    if isinstance(arg1, (int, float)) and isinstance(arg2, (int, float)):
        user_lat = float(arg1)
        user_lng = float(arg2)
        facilities: list[Facility] = arg3 if isinstance(arg3, list) else []
    else:
        facilities = arg1 if isinstance(arg1, list) else []
        user_lat = float(arg2) if isinstance(arg2, (int, float)) else DEFAULT_INDORE_LAT
        user_lng = float(arg3) if isinstance(arg3, (int, float)) else DEFAULT_INDORE_LNG

    c_lat = user_lat if user_lat is not None else DEFAULT_INDORE_LAT
    c_lng = user_lng if user_lng is not None else DEFAULT_INDORE_LNG

    m = folium.Map(
        location=[c_lat, c_lng],
        zoom_start=zoom,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    # User location marker (blue pulse)
    folium.Marker(
        location=[c_lat, c_lng],
        popup="<b>📍 Your Location / आपकी लोकेशन</b>",
        tooltip="Your Location",
        icon=folium.Icon(color="blue", icon="user", prefix="fa"),
    ).add_to(m)

    pin_color = _LEVEL_TO_COLOR.get(urgency_level, "green")

    for f in facilities:
        dist_str = f"{f.distance_km:.1f} km" if f.distance_km is not None else ""
        nav_url = get_google_maps_directions_url(f.lat, f.lng, f.name)

        popup_html = f"""
        <div style="font-family:sans-serif; min-width:180px;">
            <b style="font-size:13px;">{f.name}</b><br/>
            <span style="color:#666;font-size:11px;">{f.address}</span><br/>
            <b>Distance:</b> {dist_str}<br/>
            <b>ICU:</b> {f.icu_display} | <b>24h:</b> {f.open_display}<br/>
            <a href="{get_call_url(f.emergency_number or f.phone)}"
               style="color:#D32F2F;font-weight:bold;">📞 Call</a> |
            <a href="{nav_url}" target="_blank"
               style="color:#1976D2;font-weight:bold;">🧭 Navigate</a>
        </div>
        """

        folium.Marker(
            location=[f.lat, f.lng],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{f.name} ({dist_str})",
            icon=folium.Icon(color=pin_color, icon="plus", prefix="fa"),
        ).add_to(m)

    return m


def get_map_embed_iframe(lat: float, lng: float, zoom: int = 14) -> str:
    """Fallback static OpenStreetMap iframe when Folium is unavailable."""
    delta = 0.02
    bbox = f"{lng - delta},{lat - delta},{lng + delta},{lat + delta}"
    return (
        f'<iframe width="100%" height="350" frameborder="0" scrolling="no" '
        f'src="https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={lat},{lng}">'
        f'</iframe>'
    )
