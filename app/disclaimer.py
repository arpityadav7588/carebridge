"""
CareBridge — Disclaimer Re-export
=================================
ponytail: thin alias to core.disclaimer.
"""

from core.disclaimer import (
    DISCLAIMER_EN,
    DISCLAIMER_HI,
    DISCLAIMER_SHORT_EN,
    DISCLAIMER_SHORT_HI,
    get_both_disclaimers,
    get_disclaimer,
)

__all__ = [
    "DISCLAIMER_EN",
    "DISCLAIMER_HI",
    "DISCLAIMER_SHORT_EN",
    "DISCLAIMER_SHORT_HI",
    "get_disclaimer",
    "get_both_disclaimers",
]
