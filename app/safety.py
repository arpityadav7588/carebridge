"""
CareBridge — Safety Guardrail Re-export
=======================================
ponytail: thin alias to core.safety to eliminate duplicate logic.
"""

from core.models import SafetyResult
from core.safety import (
    _RED_FLAGS_DATA,
    _RED_KEYWORDS,
    _YELLOW_KEYWORDS,
    check_safety,
    get_red_clusters,
    get_yellow_clusters,
    is_safe_input,
)


def get_red_flag_keywords() -> dict[str, set[str]]:
    """Returns loaded keyword sets for test inspection."""
    return {"RED": _RED_KEYWORDS.copy(), "YELLOW": _YELLOW_KEYWORDS.copy()}


__all__ = [
    "SafetyResult",
    "check_safety",
    "is_safe_input",
    "get_red_clusters",
    "get_yellow_clusters",
    "get_red_flag_keywords",
]
