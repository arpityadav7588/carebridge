"""
CareBridge — Text-to-Speech (TTS) Adapter
=========================================
Bilingual audio guidance generation (Hindi & English).
Gracefully falls back to silent visual display if offline/audio fails.
"""

from __future__ import annotations

import io
from typing import Optional

try:
    from gtts import gTTS
    _GTTS_AVAILABLE = True
except ImportError:
    _GTTS_AVAILABLE = False


def generate_audio_guidance(text: str, lang: str = "en") -> Optional[bytes]:
    """
    Generates MP3 audio bytes for emergency guidance.
    Returns None if TTS library is missing or fails (graceful visual fallback).
    """
    if not _GTTS_AVAILABLE or not text.strip():
        return None

    try:
        tts_lang = "hi" if lang == "hi" else "en"
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception:
        # Never break the demo on TTS failure
        return None
