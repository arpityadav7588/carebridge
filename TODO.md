# TODO.md — CareBridge Task Checklist

## ✅ Completed
- [x] Propose & implement clean 4-layer architecture (`core/`, `adapters/`, `services/`, `ui/`)
- [x] `core/models.py` — Domain models (`UrgencyLevel`, `SafetyResult`, `UrgencyResult`, `Facility`, `PipelineResult`)
- [x] `core/safety.py` — Bilingual deterministic guardrail (10 RED clusters, 0 LLM)
- [x] `core/urgency.py` — RED/YELLOW/GREEN classifier + whitelisted first-aid
- [x] `core/disclaimer.py` — Bilingual disclaimer strip
- [x] `data/hospitals_indore.json` — 12 verified Indore emergency hospitals (MY Hospital, Bombay Hospital, Medanta, CHL, etc.)
- [x] `adapters/llm/` — BioMistral-7B adapter with fail-safe rule-based fallback
- [x] `adapters/geo/` — Indore neighborhood locator & presets (Palasia, Vijay Nagar, Bhawarkua, etc.)
- [x] `adapters/maps/` — Folium/Leaflet + Google Maps nav deeplinks + OSM iframe fallback
- [x] `adapters/sos/` — wa.me deeplink, SMS, 108 tel link
- [x] `adapters/voice/` — Hinglish normalizer, language detection, quick chips, TTS adapter
- [x] `services/facility_service.py` — Proximity sorting + triage-aware ICU ranking
- [x] `services/pipeline.py` — Full pipeline with TRD §9 per-stage latency tracking
- [x] `app/main.py` — Updated with Indore area picker, BioMistral toggle, stage latencies
- [x] `tests/test_pipeline.py` — Pipeline, adapter fallback, and Indore facility tests
- [x] Automated test suite passing: **81/81 tests green**
- [x] Architecture Decision Records (`ADR-001`, `ADR-002`, `ADR-003` in `DECISIONS.md`)
- [x] **Demo Polish #1:** Hindi TTS Voice Playback button (`st.audio`) on result screen
- [x] **Demo Polish #2:** Folium map locked (`returned_objects=[]`) to prevent pan/zoom page re-runs
- [x] **Demo Polish #3:** Demo Preset Switcher for judges (1-click Heart Attack RED, High Fever YELLOW, Headache GREEN)

## 🔄 Next Actions (Demo Readiness & PWA)
- [ ] HTML5 Browser Geolocation auto-fill widget in Streamlit
- [ ] PWA wrapper (`frontend/index.html`) with Web Speech API
- [ ] Timed demo runs (<15s voice flow rehearsal)
