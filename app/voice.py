"""
CareBridge — Voice Input Re-export
===================================
ponytail: thin alias to adapters.voice.asr.
"""

from adapters.voice.asr import (
    CHIP_ID_TO_TEXT,
    CHIP_ID_TO_TEXT_HI,
    QUICK_CHIPS,
    VoiceInputResult,
    detect_language,
    normalize_hinglish,
    process_input,
)

# Standard Indic language codes for client-side SpeechRecognition
SPEECH_RECOGNITION_LANGS = {
    "hi": "hi-IN",
    "en": "en-IN",
}

__all__ = [
    "QUICK_CHIPS",
    "CHIP_ID_TO_TEXT",
    "CHIP_ID_TO_TEXT_HI",
    "SPEECH_RECOGNITION_LANGS",
    "VoiceInputResult",
    "detect_language",
    "normalize_hinglish",
    "process_input",
]
