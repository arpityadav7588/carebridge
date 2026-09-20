# DECISIONS.md — Architecture & Technical Decision Records

## Format
- **ID:** ADR-xxx
- **Date:** YYYY-MM-DD
- **Context & Problem:**
- **Decision:**
- **Consequences:**

---

## ADR-001: Source of Truth & Conflict Precedence
- **Date:** 2026-09-20
- **Context:** Ensuring deterministic, hackathon-winning architecture aligned with SlowBros Labs Track 3 requirements.
- **Decision:** Conflict precedence established strictly as:
  `Safety (TRD §7) > Scope (PRD §5.3) > Performance (TRD §9) > Everything else.`
- **Consequences:** Any ambiguity defaults to safety guardrails and strict non-diagnostic outputs.

---

## ADR-002: Clean Layered Architecture with Swappable Adapters
- **Date:** 2026-09-20
- **Context:** Project needed clean separation of concerns without risking live demo failure through complex orchestrators (LangGraph/PostGIS).
- **Decision:** Split codebase into 4 explicit layers:
  1. `core/`: Pure domain logic (safety regex, urgency triage, models, zero network I/O).
  2. `adapters/`: Pluggable I/O (BioMistral LLM, Leaflet/Folium maps, Geo locator, WhatsApp/SMS SOS, Web voice).
  3. `services/`: Use-case orchestration (IntakePipeline with TRD §9 latency logging, FacilityService).
  4. `ui/` & `app/`: Streamlit presentation layer with panic-context UX (≥56px touch targets).
- **Consequences:** Any external service (BioMistral, Twilio, browser GPS) can fail or be disabled without breaking the core emergency triage or facility discovery.

---

## ADR-003: Indore Hospital Data Priority and Fail-Safe Fallback
- **Date:** 2026-09-20
- **Context:** User requested Indore-focused facility data and 100% demo reliability.
- **Decision:** Seeded `data/hospitals_indore.json` with 12+ verified major hospitals and trauma centers in Indore (MY Hospital, Bombay Hospital, Medanta, CHL, Choithram, Apollo, etc.). Default coordinates set to Indore Central (22.7196° N, 75.8577° E) with neighborhood presets.
- **Consequences:** Demo works accurately for local Indore scenarios without relying on live GPS locks. Pan-India dataset remains as secondary fallback.

---

## ADR-004: Dual Presentation Strategy — FastAPI Serving Pure Mobile-First Frontend
- **Date:** 2026-09-20
- **Context:** The project has both an internal Streamlit administrative interface and a high-fidelity, mobile-first pure HTML/CSS/JS frontend (`carebridge.html`) with Web Speech API, Leaflet maps, sticky emergency dialers, and WhatsApp SOS.
- **Decision:** Created `app/server.py` using FastAPI to serve `carebridge.html` directly at `/` and expose REST triage endpoint `POST /api/assess` and `GET /api/facilities` backed by the domain `IntakePipeline`. Updated `carebridge.html` with real Indore facility seeds and 1-click judge presets.
- **Consequences:** Provides judges with a 100% native mobile app feel (360px+ responsive, zero-friction, instant voice/touch interactions) running on port 8000, while preserving the full Python deterministic guardrails (<2ms latency).
