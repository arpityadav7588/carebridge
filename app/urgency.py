"""
CareBridge — Urgency Classifier Re-export
=========================================
ponytail: thin alias to core.urgency to eliminate duplicate triage logic.
"""

from core.models import UrgencyResult
from core.urgency import (
    FIRST_AID_WHITELIST,
    URGENCY_LEVELS,
    classify_urgency,
)

__all__ = [
    "URGENCY_LEVELS",
    "FIRST_AID_WHITELIST",
    "UrgencyResult",
    "classify_urgency",
]
