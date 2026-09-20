"""CareBridge Voice Package."""

from adapters.voice.asr import (
    CHIP_ID_TO_TEXT,
    CHIP_ID_TO_TEXT_HI,
    QUICK_CHIPS,
    VoiceInputResult,
    detect_language,
    normalize_hinglish,
    process_input,
)
from adapters.voice.tts import generate_audio_guidance

__all__ = [
    "QUICK_CHIPS",
    "CHIP_ID_TO_TEXT",
    "CHIP_ID_TO_TEXT_HI",
    "VoiceInputResult",
    "detect_language",
    "normalize_hinglish",
    "process_input",
    "generate_audio_guidance",
]
