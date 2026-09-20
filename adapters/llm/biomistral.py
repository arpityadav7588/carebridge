"""
CareBridge — BioMistral-7B Medical LLM Adapter
===============================================
Adapter for BioMistral-7B (or similar medical open-source LLMs).
Used strictly for multilingual symptom extraction from Hinglish/Hindi.

Fail-safe design:
- If API key is missing -> returns RuleBasedLLMAdapter output.
- If network request fails or times out (> 2.0s) -> returns RuleBasedLLMAdapter output.
- NEVER throws unhandled exceptions to the caller.
"""

from __future__ import annotations

import json
import os
import time
from typing import Optional

import requests

from adapters.llm.base import BaseLLMAdapter, ExtractedSymptoms
from adapters.llm.fallback_rules import RuleBasedLLMAdapter

_DEFAULT_HF_MODEL = "BioMistral/BioMistral-7B"
_DEFAULT_TIMEOUT_SEC = 2.0


class BioMistralAdapter(BaseLLMAdapter):
    """
    BioMistral-7B adapter with strict fallback to RuleBasedLLMAdapter.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = _DEFAULT_HF_MODEL,
        timeout_sec: float = _DEFAULT_TIMEOUT_SEC,
    ):
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
        self.model_name = model_name
        self.timeout_sec = timeout_sec
        self.fallback = RuleBasedLLMAdapter()
        self.endpoint = f"https://api-inference.huggingface.co/models/{self.model_name}"

    def extract_symptoms(self, text: str) -> ExtractedSymptoms:
        """
        Extract symptoms using BioMistral if available, otherwise fallback.
        """
        if not self.api_key:
            # Silent fallback if no API key is configured
            return self.fallback.extract_symptoms(text)

        start_time = time.perf_counter()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        system_prompt = (
            "You are a medical assistant extracting symptoms from user distress descriptions. "
            "Never diagnose diseases. Extract ONLY observed symptoms in a JSON list format.\n"
            "Output format: {\"symptoms\": [\"symptom1\"], \"duration\": \"time\"}\n"
            f"Input: {text}\nOutput:"
        )

        payload = {
            "inputs": system_prompt,
            "parameters": {
                "max_new_tokens": 60,
                "temperature": 0.1,
                "return_full_text": False,
            },
        }

        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=self.timeout_sec,
            )

            if response.status_code == 200:
                data = response.json()
                generated_text = ""
                if isinstance(data, list) and len(data) > 0:
                    generated_text = data[0].get("generated_text", "")

                latency_ms = (time.perf_counter() - start_time) * 1000.0

                # Try to parse json if LLM returned structured text
                try:
                    parsed = json.loads(generated_text)
                    return ExtractedSymptoms(
                        raw_text=text,
                        detected_language="hi" if any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in text) else "en",
                        symptoms=parsed.get("symptoms", ["unspecified"]),
                        duration=parsed.get("duration"),
                        latency_ms=round(latency_ms, 2),
                        adapter_used=f"BioMistral-7B",
                        is_fallback=False,
                    )
                except Exception:
                    pass

        except Exception:
            # On timeout, connection reset, or HTTP error, fallback cleanly
            pass

        # Return fast rule-based fallback
        fallback_res = self.fallback.extract_symptoms(text)
        fallback_res.adapter_used = "BioMistral-fallback (rules)"
        return fallback_res
