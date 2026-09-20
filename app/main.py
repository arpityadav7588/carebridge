"""
CareBridge — Main Application
================================
Bilingual (Hindi + English) emergency healthcare navigator.
Voice-first, non-diagnostic, privacy-preserving.

Flow:
  User speaks/types distress → Safety check → Urgency level
  → Nearby facilities on map → One-click navigate / call / SOS

Run:
  streamlit run app/main.py

TRD §9 Performance budget:
  Guardrail < 50ms | Urgency < 50ms | Facility sort < 200ms
"""

from __future__ import annotations

import os
import sys
import time

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from app.disclaimer import get_disclaimer, DISCLAIMER_SHORT_EN, DISCLAIMER_SHORT_HI
from app.voice import (
    QUICK_CHIPS,
    CHIP_ID_TO_TEXT,
    CHIP_ID_TO_TEXT_HI,
    process_input,
    SPEECH_RECOGNITION_LANGS,
)
from app.urgency import classify_urgency, UrgencyResult
from app.facilities import get_facilities_for_urgency, Facility
from app.maps import (
    build_facility_map,
    get_google_maps_directions_url,
    get_call_url,
    get_map_embed_iframe,
    _FOLIUM_AVAILABLE,
)
from app.sos import build_sos_actions, EMERGENCY_CONTACTS
from adapters.geo.locator import INDORE_AREAS, DEFAULT_INDORE_LAT, DEFAULT_INDORE_LNG
from adapters.llm.biomistral import BioMistralAdapter
from adapters.voice.tts import generate_audio_guidance


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="CareBridge | Emergency Healthcare Navigator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------------------------
# Custom CSS (panic-context UX — large targets, high contrast)
# ---------------------------------------------------------------------------

st.markdown("""
<style>
/* ---------- Global ---------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ---------- Urgency banners ---------- */
.banner-red {
    background: #D32F2F; color: #fff;
    padding: 18px 24px; border-radius: 12px;
    font-size: 1.4rem; font-weight: 900;
    text-align: center; animation: pulse 1s infinite;
}
.banner-yellow {
    background: #F57C00; color: #fff;
    padding: 14px 20px; border-radius: 12px;
    font-size: 1.2rem; font-weight: 700; text-align: center;
}
.banner-green {
    background: #388E3C; color: #fff;
    padding: 12px 18px; border-radius: 12px;
    font-size: 1.1rem; font-weight: 600; text-align: center;
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(211,47,47,.7); }
    50%       { box-shadow: 0 0 0 14px rgba(211,47,47,0); }
}

/* ---------- Facility card ---------- */
.facility-card {
    border: 1px solid #ddd; border-radius: 10px;
    padding: 14px 16px; margin-bottom: 10px;
    background: #fafafa;
}
.facility-name { font-weight: 700; font-size: 1rem; }
.facility-sub  { color: #555; font-size: 0.85rem; }

/* ---------- Action buttons (≥56px touch target) ---------- */
.stButton > button {
    min-height: 56px !important;
    font-size: 1rem !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

/* ---------- Disclaimer strip ---------- */
.disclaimer-strip {
    background: #FFF8E1; color: #5D4037;
    border-left: 4px solid #FFC107;
    padding: 8px 14px; border-radius: 4px;
    font-size: 0.8rem; margin-top: 8px;
}

/* ---------- Quick chips ---------- */
.chip-btn > button {
    background: #EEF2FF !important; color: #1A237E !important;
    border: 1.5px solid #7986CB !important;
    border-radius: 24px !important;
    min-height: 44px !important;
    padding: 6px 16px !important;
    font-size: 0.9rem !important;
}
.chip-btn-red > button {
    background: #FFEBEE !important; color: #C62828 !important;
    border: 1.5px solid #EF5350 !important;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

def _init_state():
    defaults = {
        "lang": "en",
        "step": "input",          # 'input' | 'result'
        "user_text": "",
        "chip_ids": [],
        "urgency_result": None,
        "facilities": {},
        "user_lat": DEFAULT_INDORE_LAT,
        "user_lng": DEFAULT_INDORE_LNG,
        "user_area": "Rajwada / Central Indore",
        "emergency_contact": "",
        "latency_log": {},
        "use_llm": False,
        "extracted_symptoms": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _t(en: str, hi: str) -> str:
    """Return text for current language."""
    return hi if st.session_state.lang == "hi" else en


def _disclaimer_strip():
    text = DISCLAIMER_SHORT_HI if st.session_state.lang == "hi" else DISCLAIMER_SHORT_EN
    st.markdown(f'<div class="disclaimer-strip">⚠️ {text}</div>', unsafe_allow_html=True)


def _run_pipeline(text: str, chip_ids: list[str]):
    """
    Execute the full pipeline and store results in session state.
    Logs per-stage latency (TRD §9).
    """
    latency = {}

    # Stage 1: Input normalisation
    t0 = time.perf_counter()
    voice_input = process_input(text, chip_ids, source="text")
    combined = voice_input.combined_text
    latency["input_ms"] = round((time.perf_counter() - t0) * 1000, 1)

    # Stage 2: Urgency classification (includes deterministic safety guardrail)
    t0 = time.perf_counter()
    result: UrgencyResult = classify_urgency(combined)
    latency["urgency_ms"] = round((time.perf_counter() - t0) * 1000, 1)

    # Stage 2.5: Optional LLM symptom extraction (BioMistral with instant fallback)
    if st.session_state.use_llm and result.level != "RED":
        t0 = time.perf_counter()
        adapter = BioMistralAdapter()
        extracted = adapter.extract_symptoms(combined)
        st.session_state.extracted_symptoms = extracted
        latency["llm_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    else:
        st.session_state.extracted_symptoms = None

    # Stage 3: Facility lookup (Default: Indore)
    t0 = time.perf_counter()
    lat = st.session_state.user_lat or DEFAULT_INDORE_LAT
    lng = st.session_state.user_lng or DEFAULT_INDORE_LNG
    facilities = get_facilities_for_urgency(lat, lng, result.level, max_results=5)
    latency["facility_ms"] = round((time.perf_counter() - t0) * 1000, 1)

    # Store
    st.session_state.urgency_result = result
    st.session_state.facilities = facilities
    st.session_state.latency_log = latency
    st.session_state.step = "result"


# ---------------------------------------------------------------------------
# UI: Header
# ---------------------------------------------------------------------------

def _render_header():
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown("## 🏥 CareBridge")
        st.caption(_t(
            "Emergency Healthcare Navigator · Non-Diagnostic",
            "आपातकालीन स्वास्थ्य नेविगेटर · गैर-निदानात्मक",
        ))
    with col2:
        lang_choice = st.selectbox(
            "🌐", ["English", "हिन्दी"],
            index=0 if st.session_state.lang == "en" else 1,
            label_visibility="collapsed",
        )
        st.session_state.lang = "hi" if lang_choice == "हिन्दी" else "en"

    _disclaimer_strip()
    st.divider()


# ---------------------------------------------------------------------------
# UI: Input screen (Step 1)
# ---------------------------------------------------------------------------

def _render_input_screen():
    # ── Demo Presets (For Judges & Instant Evaluation) ─────────────────────────
    st.markdown("🎯 **" + _t("⚡ Demo Presets for Judges:", "⚡ जजों व परीक्षण के लिए डेमो प्रीसेट:") + "**")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        if st.button("🔴 Heart Attack (RED)", key="preset_red_btn", use_container_width=True):
            p_text = "Seene mein bahut tez dard hai aur saans nahi aa rahi"
            st.session_state.user_text = p_text
            st.session_state.chip_ids = []
            st.session_state["tts_audio"] = None
            _run_pipeline(p_text, [])
            st.rerun()
    with col_p2:
        if st.button("🟡 High Fever (YELLOW)", key="preset_yellow_btn", use_container_width=True):
            p_text = "Tez bukhar hai 3 din se, kamzori bhi hai"
            st.session_state.user_text = p_text
            st.session_state.chip_ids = []
            st.session_state["tts_audio"] = None
            _run_pipeline(p_text, [])
            st.rerun()
    with col_p3:
        if st.button("🟢 Mild Headache (GREEN)", key="preset_green_btn", use_container_width=True):
            p_text = "I have a mild headache since morning"
            st.session_state.user_text = p_text
            st.session_state.chip_ids = []
            st.session_state["tts_audio"] = None
            _run_pipeline(p_text, [])
            st.rerun()

    preset_choice = st.selectbox(
        _t("Or select a scenario dropdown:", "या ड्रॉपडाउन से परिदृश्य चुनें:"),
        [
            "-- " + _t("Choose scenario to test", "परीक्षण के लिए परिदृश्य चुनें") + " --",
            "🔴 Preset 1: Heart Attack (RED - Hindi)",
            "🟡 Preset 2: High Fever (YELLOW - Hinglish)",
            "🟢 Preset 3: Mild Headache (GREEN - English)",
        ],
        index=0,
        key="preset_dropdown_selector",
        label_visibility="collapsed",
    )
    if preset_choice.startswith("🔴"):
        st.session_state["tts_audio"] = None
        _run_pipeline("Seene mein bahut tez dard hai aur saans nahi aa rahi", [])
        st.rerun()
    elif preset_choice.startswith("🟡"):
        st.session_state["tts_audio"] = None
        _run_pipeline("Tez bukhar hai 3 din se, kamzori bhi hai", [])
        st.rerun()
    elif preset_choice.startswith("🟢"):
        st.session_state["tts_audio"] = None
        _run_pipeline("I have a mild headache since morning", [])
        st.rerun()

    st.markdown("---")
    st.markdown(f"### {_t('Describe your emergency', 'अपनी आपातकाल बताएं')}")
    st.markdown(_t(
        "Type or speak what's happening. Hindi or English.",
        "क्या हो रहा है टाइप करें या बोलें। हिन्दी या English।",
    ))

    # Text input
    user_text = st.text_area(
        label=_t("What's happening?", "क्या हो रहा है?"),
        value=st.session_state.user_text,
        placeholder=_t(
            "e.g. My father is having chest pain and difficulty breathing...",
            "जैसे: मेरे पिताजी को सीने में दर्द हो रहा है और सांस लेने में तकलीफ है...",
        ),
        height=100,
        key="text_input_area",
    )

    # Voice capture note (browser SpeechRecognition handled client-side)
    with st.expander(_t("🎙️ Use voice input", "🎙️ आवाज़ से बोलें")):
        st.info(_t(
            "On mobile: tap the microphone icon in your keyboard. "
            "Voice input works best in Chrome/Edge on Android.",
            "मोबाइल पर: कीबोर्ड में माइक्रोफ़ोन आइकॉन टैप करें। "
            "Voice इनपुट Chrome/Edge Android पर सबसे अच्छा काम करता है।",
        ))

    st.markdown(f"**{_t('Or tap a quick option:', 'या एक विकल्प चुनें:')}**")

    # Quick chips
    selected_chips = list(st.session_state.chip_ids)
    chip_cols = st.columns(3)
    for i, chip in enumerate(QUICK_CHIPS):
        col = chip_cols[i % 3]
        label = chip["label_hi"] if st.session_state.lang == "hi" else chip["label_en"]
        is_red = chip["urgency_hint"] == "RED"
        css_class = "chip-btn-red" if is_red else "chip-btn"
        selected = chip["id"] in selected_chips
        btn_label = f"{'✅ ' if selected else ''}{label}"
        with col:
            container = st.container()
            container.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if container.button(btn_label, key=f"chip_{chip['id']}"):
                if chip["id"] in selected_chips:
                    selected_chips.remove(chip["id"])
                else:
                    selected_chips.append(chip["id"])
                st.session_state.chip_ids = selected_chips
                st.rerun()
            container.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # Location input (Indore focus with custom option)
    with st.expander(_t("📍 Your Location (Indore Focus)", "📍 आपकी लोकेशन (इंदौर फोकस)")):
        area_names = list(INDORE_AREAS.keys())
        default_idx = area_names.index("Rajwada / Central Indore") if "Rajwada / Central Indore" in area_names else 0
        selected_area = st.selectbox(
            _t("Select your area in Indore:", "इंदौर में अपना क्षेत्र चुनें:"),
            area_names,
            index=default_idx,
            key="area_selector",
        )
        if selected_area in INDORE_AREAS:
            st.session_state.user_lat, st.session_state.user_lng = INDORE_AREAS[selected_area]
            st.session_state.user_area = selected_area

        with st.popover(_t("⚙️ Custom GPS Coordinates", "⚙️ कस्टम GPS निर्देशांक")):
            col_lat, col_lng = st.columns(2)
            with col_lat:
                lat_val = st.number_input("Latitude", value=float(st.session_state.user_lat), format="%.4f", key="lat_input")
            with col_lng:
                lng_val = st.number_input("Longitude", value=float(st.session_state.user_lng), format="%.4f", key="lng_input")
            if st.button(_t("Apply Custom GPS", "कस्टम GPS लागू करें")):
                st.session_state.user_lat = lat_val
                st.session_state.user_lng = lng_val
                st.session_state.user_area = "Custom GPS"
                st.success(_t("Location updated.", "लोकेशन अपडेट हुई।"))

        st.caption(f"📍 Active: **{st.session_state.user_area}** ({st.session_state.user_lat:.4f}, {st.session_state.user_lng:.4f})")

    # AI Model & Parsing Options
    with st.expander(_t("🤖 AI & Model Settings (Optional)", "🤖 AI और मॉडल सेटिंग्स (वैकल्पिक)")):
        st.session_state.use_llm = st.checkbox(
            _t("Enable BioMistral-7B Medical LLM (with instant rule fallback)", "बायोमिस्ट्राल-7B मेडिकल LLM सक्षम करें (तत्काल फ़ॉलबैक सहित)"),
            value=st.session_state.use_llm,
            help=_t(
                "Extracts clinical entities from conversational Hinglish. Guaranteed fail-safe fallback to deterministic rules if offline.",
                "हिंग्लिश से नैदानिक इकाइयां निकालता है। ऑफलाइन होने पर तत्काल नियमों पर स्विच करता है।"
            )
        )

    # Emergency contact
    with st.expander(_t("📞 Emergency contact number (for SOS)", "📞 आपातकालीन संपर्क नंबर (SOS के लिए)")):
        ec = st.text_input(
            _t("Contact number (with country code)", "संपर्क नंबर (देश कोड सहित)"),
            value=st.session_state.emergency_contact,
            placeholder="+919876543210",
            key="ec_input",
        )
        st.session_state.emergency_contact = ec

    # Submit
    st.markdown("")
    can_submit = bool(user_text.strip() or selected_chips)
    submit_label = _t("🔍 Check Urgency & Find Help", "🔍 तात्कालिकता जांचें और मदद खोजें")
    if st.button(submit_label, disabled=not can_submit, type="primary", use_container_width=True):
        st.session_state.user_text = user_text
        _run_pipeline(user_text, selected_chips)
        st.rerun()

    if not can_submit:
        st.caption(_t(
            "Please type your situation or select at least one option above.",
            "कृपया अपनी स्थिति टाइप करें या ऊपर कोई विकल्प चुनें।",
        ))


# ---------------------------------------------------------------------------
# UI: Result screen (Step 2)
# ---------------------------------------------------------------------------

def _render_urgency_banner(result: UrgencyResult):
    level = result.level
    label = result.label_hi if st.session_state.lang == "hi" else result.label_en
    guidance = result.guidance_hi if st.session_state.lang == "hi" else result.guidance_en
    css = {"RED": "banner-red", "YELLOW": "banner-yellow", "GREEN": "banner-green"}[level]

    st.markdown(f'<div class="{css}">{label}</div>', unsafe_allow_html=True)
    st.markdown(f"**{guidance}**")

    if result.must_call_108:
        col1, col2 = st.columns(2)
        with col1:
            st.link_button(
                "🚨 Call 108 NOW / 108 डायल करें",
                "tel:108",
                use_container_width=True,
                type="primary",
            )
        with col2:
            st.link_button(
                "🚔 Call 100 (Police)",
                "tel:100",
                use_container_width=True,
            )

    # ── Hindi Voice TTS Playback ──────────────────────────────────────────────
    col_tts, col_pad = st.columns([2, 3])
    with col_tts:
        btn_label = "🔊 " + _t("Listen in Hindi", "आवाज में सुनें")
        if st.button(btn_label, key="tts_play_btn", use_container_width=True):
            with st.spinner(_t("Generating audio...", "ऑडियो तैयार हो रहा है...")):
                tts_text = f"चेतावनी। {result.label_hi}। {result.guidance_hi}"
                audio_bytes = generate_audio_guidance(tts_text, lang="hi")
                if audio_bytes:
                    st.session_state["tts_audio"] = audio_bytes
                else:
                    st.warning(_t("Audio generation unavailable.", "ऑडियो उपलब्ध नहीं है।"))

    if st.session_state.get("tts_audio"):
        st.audio(st.session_state["tts_audio"], format="audio/mp3", autoplay=True)


def _render_facility_cards(facilities: list[Facility]):
    for fac in facilities:
        name = fac.name_hi if st.session_state.lang == "hi" else fac.name
        dist = f"{fac.distance_km:.1f} km" if fac.distance_km is not None else "? km"
        nav_url = get_google_maps_directions_url(fac.lat, fac.lng, fac.name)
        call_url = get_call_url(fac.emergency_number or fac.phone)

        with st.container():
            st.markdown(f"""
<div class="facility-card">
  <div class="facility-name">{name}</div>
  <div class="facility-sub">{fac.name_hi if st.session_state.lang == 'en' else fac.name}</div>
  <div class="facility-sub">📍 {dist} &nbsp;|&nbsp; 🏥 ICU: {fac.icu_display} &nbsp;|&nbsp; ⏰ {fac.open_display}</div>
  <div class="facility-sub">📞 {fac.emergency_number or fac.phone}</div>
</div>
""", unsafe_allow_html=True)
            col_nav, col_call = st.columns(2)
            with col_nav:
                st.link_button(
                    f"🗺️ {_t('Navigate', 'नेविगेट करें')}",
                    nav_url,
                    use_container_width=True,
                )
            with col_call:
                st.link_button(
                    f"📞 {_t('Call', 'कॉल करें')}",
                    call_url,
                    use_container_width=True,
                )


def _render_map(facilities: list[Facility], urgency_level: str):
    lat = st.session_state.user_lat or DEFAULT_INDORE_LAT
    lng = st.session_state.user_lng or DEFAULT_INDORE_LNG

    if _FOLIUM_AVAILABLE:
        try:
            from streamlit_folium import st_folium
            m = build_facility_map(facilities, lat, lng, urgency_level)
            if m:
                # returned_objects=[] locks the map and prevents full page re-runs on zoom/pan
                st_folium(m, width=700, height=400, returned_objects=[])
                return
        except ImportError:
            pass

    # Fallback: OSM iframe
    iframe_html = get_map_embed_iframe(lat, lng)
    st.markdown(iframe_html, unsafe_allow_html=True)


def _render_sos_section(result: UrgencyResult, facilities: list[Facility]):
    st.markdown(f"#### {_t('🆘 SOS Actions', '🆘 SOS क्रियाएं')}")
    lat = st.session_state.user_lat
    lng = st.session_state.user_lng
    nearest = facilities[0].name if facilities else None
    ec = st.session_state.emergency_contact or None

    sos = build_sos_actions(result.level, lat, lng, ec, nearest, st.session_state.lang)

    col1, col2 = st.columns(2)
    with col1:
        st.link_button(
            "🚑 " + _t("Call Ambulance (108)", "एम्बुलेंस बुलाएं (108)"),
            sos.call_108_url,
            use_container_width=True,
            type="primary" if result.level == "RED" else "secondary",
        )
    with col2:
        if sos.whatsapp_sos_url:
            st.link_button(
                "💬 " + _t("WhatsApp SOS", "WhatsApp SOS"),
                sos.whatsapp_sos_url,
                use_container_width=True,
            )
        else:
            st.info(_t(
                "Add emergency contact above to enable WhatsApp SOS.",
                "WhatsApp SOS के लिए ऊपर संपर्क नंबर डालें।",
            ))

    with st.expander(_t("SOS message preview", "SOS संदेश पूर्वावलोकन")):
        st.code(sos.sos_message, language=None)


def _render_result_screen():
    result: UrgencyResult = st.session_state.urgency_result
    facilities_dict: dict = st.session_state.facilities
    all_facilities: list[Facility] = []
    for v in facilities_dict.values():
        all_facilities.extend(v)

    # Back button
    if st.button(_t("← Back / नया प्रश्न", "← वापस / नया प्रश्न")):
        st.session_state.step = "input"
        st.session_state.urgency_result = None
        st.session_state.facilities = {}
        st.session_state["tts_audio"] = None
        st.rerun()

    st.divider()

    # Urgency banner (always first)
    _render_urgency_banner(result)

    # Show BioMistral extracted entities if enabled
    if st.session_state.get("extracted_symptoms"):
        ext = st.session_state.extracted_symptoms
        symp_display = ", ".join(ext.symptoms) if ext.symptoms else "None"
        dur_display = ext.duration or "Not specified"
        st.info(
            f"🤖 **BioMistral-7B Clinical Parser:** Symptoms: `{symp_display}` | "
            f"Duration: `{dur_display}` | Engine: `{ext.adapter_used}` ({ext.latency_ms} ms)"
        )

    # Performance latency (TRD §9 debug)
    with st.expander("⏱ Stage Latencies & TRD §9 Budget", expanded=False):
        st.json(st.session_state.latency_log)

    st.divider()

    # Layout: Map | Facility cards
    col_map, col_list = st.columns([3, 2])

    hospitals = facilities_dict.get("hospitals", [])
    blood_banks = facilities_dict.get("blood_banks", [])

    with col_map:
        st.markdown(f"#### {_t('Nearby Facilities', 'नज़दीकी सुविधाएं')}")
        _render_map(all_facilities, result.level)

    with col_list:
        st.markdown(f"**{_t('Hospitals / Emergency Centres', 'अस्पताल / आपातकालीन केंद्र')}**")
        if hospitals:
            _render_facility_cards(hospitals[:3])
        else:
            st.warning(_t(
                "No facilities found in cached data. Searching live OSM...",
                "कैश डेटा में कोई सुविधा नहीं मिली। OSM से खोज रहे हैं...",
            ))

        if blood_banks:
            st.markdown(f"**{_t('Blood Banks', 'ब्लड बैंक')}**")
            _render_facility_cards(blood_banks[:2])

    st.divider()

    # SOS section
    _render_sos_section(result, all_facilities)

    st.divider()
    _disclaimer_strip()


# ---------------------------------------------------------------------------
# Main render loop
# ---------------------------------------------------------------------------

def main():
    _render_header()

    if st.session_state.step == "input":
        _render_input_screen()
    else:
        _render_result_screen()


if __name__ == "__main__":
    main()
