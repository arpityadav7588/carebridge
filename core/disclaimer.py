"""
CareBridge — Disclaimer Module
================================
Every screen MUST render this disclaimer strip.
TRD §5.3 / PRD Non-Diagnostic Constraint.
"""

DISCLAIMER_EN = (
    "⚠️ CareBridge is NOT a diagnostic tool. It does not identify diseases or replace "
    "professional medical advice. In a life-threatening emergency, call 108 immediately."
)

DISCLAIMER_HI = (
    "⚠️ CareBridge एक डायग्नोस्टिक टूल नहीं है। यह बीमारियों की पहचान नहीं करता और "
    "पेशेवर चिकित्सा सलाह का विकल्प नहीं है। जानलेवा आपातकाल में तुरंत 108 पर कॉल करें।"
)

DISCLAIMER_SHORT_EN = "Not a diagnostic tool. Emergencies: call 108."
DISCLAIMER_SHORT_HI = "डायग्नोस्टिक टूल नहीं। आपातकाल: 108 कॉल करें।"


def get_disclaimer(lang: str = "en", short: bool = False) -> str:
    """
    Returns the disclaimer string for the given language.

    Args:
        lang: 'en' for English, 'hi' for Hindi.
        short: If True, return abbreviated version.

    Returns:
        Disclaimer string.
    """
    if short:
        return DISCLAIMER_SHORT_HI if lang == "hi" else DISCLAIMER_SHORT_EN
    return DISCLAIMER_HI if lang == "hi" else DISCLAIMER_EN


def get_both_disclaimers(short: bool = False) -> dict:
    """Returns both language disclaimers as a dict."""
    return {
        "en": get_disclaimer("en", short),
        "hi": get_disclaimer("hi", short),
    }
