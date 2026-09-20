"""
CareBridge — LLM Adapter Base Interface
========================================
Defines the contract for plug-and-play symptom extraction adapters.
Any LLM (BioMistral, HuggingFace, Ollama, Mock) must adhere to this.
CRITICAL: LLM is strictly non-diagnostic; it only extracts symptom keywords/tags.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExtractedSymptoms:
    """Structured symptoms extracted from raw Hinglish/Hindi/English input."""
    raw_text: str
    detected_language: str
    symptoms: list[str] = field(default_factory=list)
    duration: Optional[str] = None
    severity_keywords: list[str] = field(default_factory=list)
    latency_ms: float = 0.0
    adapter_used: str = "unknown"
    is_fallback: bool = False

    def to_dict(self) -> dict:
        return {
            "raw_text": self.raw_text,
            "detected_language": self.detected_language,
            "symptoms": self.symptoms,
            "duration": self.duration,
            "severity_keywords": self.severity_keywords,
            "latency_ms": self.latency_ms,
            "adapter_used": self.adapter_used,
            "is_fallback": self.is_fallback,
        }


class BaseLLMAdapter(ABC):
    """Abstract base class for symptom extraction adapters."""

    @abstractmethod
    def extract_symptoms(self, text: str) -> ExtractedSymptoms:
        """
        Extract structured symptom entities from freeform text.
        Must gracefully catch all exceptions and return a fallback result.
        """
        pass
