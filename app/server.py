"""
CareBridge — FastAPI Application Server
=======================================
Serves the pure HTML/CSS/JS frontend (carebridge.html) and provides the
REST API for deterministic emergency triage and Indore facility matching.

Run:
  uvicorn app.server:app --port 8000 --reload
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from adapters.geo.locator import DEFAULT_INDORE_LAT, DEFAULT_INDORE_LNG
from core.models import PipelineResult
from services.facility_service import FacilityService
from services.pipeline import IntakePipeline

_BASE_DIR = Path(__file__).parent.parent
_HTML_PATH = _BASE_DIR / "carebridge.html"

app = FastAPI(
    title="CareBridge — Emergency Healthcare Navigator API",
    description="Non-diagnostic emergency triage and nearby facility discovery API",
    version="1.0.0",
)

# Allow CORS for development / local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = IntakePipeline()
facility_service = FacilityService()


@app.api_route("/", methods=["GET", "HEAD"])
async def serve_index():
    """Serves the polished pure HTML/CSS/JS emergency navigator."""
    if not _HTML_PATH.exists():
        raise HTTPException(status_code=404, detail="carebridge.html not found")
    return FileResponse(_HTML_PATH, media_type="text/html")


@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "healthy", "service": "carebridge"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global fail-safe handler to prevent uncaught 500 errors."""
    return JSONResponse(
        status_code=200,
        content={
            "urgency": "red",
            "raw_level": "RED",
            "label": "🔴 आपातकाल",
            "guidance": "तुरंत 108 पर कॉल करें।",
            "must_call_108": True,
            "steps": ["शांत रहें और 108 पर कॉल करें।"],
            "facilities": [],
            "error": str(exc),
        },
    )


@app.post("/api/assess")
async def assess_emergency(request: Request):
    """
    Intake triage endpoint for carebridge.html.
    Accepts raw user text, symptom hints, and coordinates.
    Returns urgency level (red/amber/green), whitelisted first-aid, and sorted facilities.
    Guaranteed zero-crash: returns safe emergency guidance on any exception.
    """
    try:
        data: dict[str, Any] = await request.json()
    except Exception:
        data = {}

    raw_text = str(data.get("text") or "").strip()
    raw_hints = data.get("hints")
    hints = [str(h).strip() for h in raw_hints if h] if isinstance(raw_hints, list) else []
    lang = str(data.get("lang") or "hi").strip()
    coords = data.get("coords") if isinstance(data.get("coords"), dict) else {}

    # Extract user coordinates with safe float parsing (default: Indore Rajwada)
    try:
        user_lat = float(coords.get("lat")) if coords.get("lat") is not None else DEFAULT_INDORE_LAT
    except (ValueError, TypeError):
        user_lat = DEFAULT_INDORE_LAT

    try:
        user_lng = float(coords.get("lng")) if coords.get("lng") is not None else DEFAULT_INDORE_LNG
    except (ValueError, TypeError):
        user_lng = DEFAULT_INDORE_LNG

    # Combine text with hints if available
    combined_query = raw_text
    if hints:
        hint_str = ", ".join(hints)
        combined_query = f"{raw_text} ({hint_str})" if raw_text else hint_str

    try:
        # Execute deterministic safety + urgency + facility matching pipeline
        result: PipelineResult = pipeline.process(
            text=combined_query,
            user_lat=user_lat,
            user_lng=user_lng,
            limit_facilities=6,
            use_llm=False,  # deterministic rules first for instant demo latency (<10ms)
        )

        # Map core UrgencyLevel ("RED", "YELLOW", "GREEN") to carebridge.html classes ("red", "amber", "green")
        urgency_map = {
            "RED": "red",
            "YELLOW": "amber",
            "GREEN": "green",
        }
        frontend_urgency = urgency_map.get(result.urgency.level, "green")

        # Select bilingual output strings
        is_hi = (lang == "hi")
        label = result.urgency.label_hi if is_hi else result.urgency.label_en
        guidance = result.urgency.guidance_hi if is_hi else result.urgency.guidance_en
        first_aid_steps = result.urgency.first_aid_hi if is_hi else result.urgency.first_aid_en

        # Serialize facilities with distance and honest ICU markers
        facility_list = [f.to_dict() for f in result.facilities]

        return JSONResponse({
            "urgency": frontend_urgency,
            "raw_level": result.urgency.level,
            "label": label,
            "guidance": guidance,
            "must_call_108": result.safety.must_call_108,
            "steps": first_aid_steps,
            "facilities": facility_list,
            "latency_ms": result.total_latency_ms,
            "stage_latencies": result.stage_latencies_ms,
        })
    except Exception as exc:
        is_hi = (lang == "hi")
        return JSONResponse({
            "urgency": "amber",
            "raw_level": "YELLOW",
            "label": "🟡 उच्च प्राथमिकता" if is_hi else "🟡 HIGH PRIORITY",
            "guidance": "2 घंटे के भीतर डॉक्टर या अस्पताल जाएं। आपातकाल में 108 पर कॉल करें।" if is_hi else "Visit a hospital within 2 hours. Call 108 in emergency.",
            "must_call_108": False,
            "steps": [
                "शांत रहें और व्यक्ति को आराम से रखें।" if is_hi else "Stay calm and keep the person comfortable.",
                "तुरंत पास के अस्पताल जाएं।" if is_hi else "Proceed to a nearby hospital.",
            ],
            "facilities": [],
            "latency_ms": 0.0,
            "stage_latencies": {},
            "fallback": True,
            "error_detail": str(exc),
        })


@app.api_route("/api/facilities", methods=["GET", "HEAD"])
async def get_facilities(
    lat: float = DEFAULT_INDORE_LAT,
    lng: float = DEFAULT_INDORE_LNG,
    category: str = "hospital",
    urgency: str = "GREEN",
    radius: float = 30.0,
    limit: int = 10,
):
    """Returns sorted healthcare facilities around user coordinates."""
    fac_type = "blood_bank" if category in ("blood", "blood_bank") else "hospital"
    facilities = facility_service.get_nearby_facilities(
        lat=lat,
        lng=lng,
        facility_type=fac_type,
        radius_km=radius,
        limit=limit,
        urgency_level=urgency,
    )
    return {"facilities": [f.to_dict() for f in facilities]}
