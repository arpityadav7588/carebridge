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


@app.get("/")
async def serve_index():
    """Serves the polished pure HTML/CSS/JS emergency navigator."""
    if not _HTML_PATH.exists():
        raise HTTPException(status_code=404, detail="carebridge.html not found")
    return FileResponse(_HTML_PATH, media_type="text/html")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "carebridge"}


@app.post("/api/assess")
async def assess_emergency(request: Request):
    """
    Intake triage endpoint for carebridge.html.
    Accepts raw user text, symptom hints, and coordinates.
    Returns urgency level (red/amber/green), whitelisted first-aid, and sorted facilities.
    """
    try:
        data: dict[str, Any] = await request.json()
    except Exception:
        data = {}

    raw_text = data.get("text", "")
    hints = data.get("hints", [])
    lang = data.get("lang", "hi")
    coords = data.get("coords") or {}

    # Extract user coordinates (default: Indore Rajwada)
    user_lat = coords.get("lat") if coords.get("lat") is not None else DEFAULT_INDORE_LAT
    user_lng = coords.get("lng") if coords.get("lng") is not None else DEFAULT_INDORE_LNG

    # Combine text with hints if available
    combined_query = raw_text
    if hints:
        hint_str = ", ".join(hints)
        combined_query = f"{raw_text} ({hint_str})" if raw_text else hint_str

    # Execute deterministic safety + urgency + facility matching pipeline
    result: PipelineResult = pipeline.process(
        text=combined_query,
        user_lat=float(user_lat),
        user_lng=float(user_lng),
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


@app.get("/api/facilities")
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
