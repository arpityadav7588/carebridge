# SPRINT.md — Current Sprint State

## Current Sprint Goal
- **Sprint Goal:** S2 — Clean Layered Architecture + Indore Facility Integration + BioMistral Adapter
- **Phase:** Completed & Verified (81/81 Tests Green)

## Sprint History & Roadmap
- [x] **S0:** Scaffold monorepo + CI + facility seed script ✅ DONE
- [x] **S1:** Deterministic guardrail + urgency rules + adversarial suite ✅ DONE
- [x] **S2:** Clean 4-Layer Architecture (`core/`, `adapters/`, `services/`, `ui/`) + Indore hospital dataset + BioMistral-7B fail-safe adapter + 81/81 tests passing ✅ DONE
- [x] **S3:** Demo Polish: Hindi TTS audio playback + Folium map lock (`returned_objects=[]`) + Judge Demo Preset Switcher ✅ DONE
- [x] **S4:** FastAPI Web Server (`app/server.py`) serving `carebridge.html` on port 8000 + `/api/assess` triage + `/api/facilities` ✅ DONE
- [x] **S5:** Indore facility dataset (16 seeds) + 1-Click Judge Presets (RED/YELLOW/GREEN) integrated into pure HTML frontend ✅ DONE
- [x] **S6:** WhatsApp SOS + 108/112 sticky dialers + Leaflet interactive map active on port 8000 ✅ DONE
- [ ] **S7:** Demo hardening: 3 timed runs < 15s, fallback drills

## Architecture Status (Clean 4-Layer System)
- **Domain (`core/`):**
  - `core/models.py` — Typed Dataclasses (`SafetyResult`, `UrgencyResult`, `Facility`, `PipelineResult`)
  - `core/safety.py` — Deterministic regex guardrail (zero LLM, mandatory first step)
  - `core/urgency.py` — RED/YELLOW/GREEN classifier + whitelisted first-aid
  - `core/disclaimer.py` — Bilingual disclaimer strip
- **Adapters (`adapters/`):**
  - `adapters/llm/` — BioMistral-7B adapter with sub-5ms rule-based fallback
  - `adapters/geo/` — Indore neighborhood presets (Palasia, Vijay Nagar, etc.) + default coords
  - `adapters/maps/` — Folium Leaflet + Google Maps nav URI + OSM iframe fallback
  - `adapters/sos/` — wa.me deeplink, SMS, 108 tel protocol
  - `adapters/voice/` — Hinglish normalizer, language detector, quick chips, TTS generator
- **Services (`services/`):**
  - `services/pipeline.py` — End-to-end orchestrator with TRD §9 per-stage latency tracking
  - `services/facility_service.py` — Proximity sorting with Indore priority and ICU-aware emergency ranking
- **Data (`data/`):**
  - `data/hospitals_indore.json` — 12 verified emergency centers (MY Hospital, Bombay Hospital, Medanta, CHL, Choithram, etc.)
  - `data/hospitals_india.json` — 21 hospitals across 12 cities
  - `data/red_flags.json` — 10 RED + 4 YELLOW keyword clusters

## Test Status
- `pytest tests/ -v`: **81 passed in 0.15s** (100% green)
