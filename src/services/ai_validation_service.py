"""
AI Validation service using GPTZero to assess AI-likeness of text content.
This service submits text to the detection provider and degrades gracefully if
configuration is missing or the provider is unavailable.
"""

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx


class APIConstants:
    """Environment variable names for API configuration."""
    ENV_GPTZERO_API_KEY = "GPTZERO_API_KEY"
    ENV_GPTZERO_API_URL = "GPTZERO_API_URL"


class GPTZeroConfig:
    """Default configuration values for GPTZero integration."""
    DEFAULT_API_KEY = "be0adeba517a4d2fa304f3ca468f322e"
    DEFAULT_API_URL = "https://api.gptzero.me/v2/predict/text"
    DEFAULT_TIMEOUT_SECONDS = 30
    CHUNK_SIZE_CHARS = 5000
    CHUNK_OVERLAP_CHARS = 500
    MAX_PARALLEL_REQUESTS = 3


class AIValidationService:
    """Service that integrates with GPTZero to score AI-likeness.

    Configuration is taken from environment variables:
      - GPTZERO_API_KEY
      - GPTZERO_API_URL
    """

    def __init__(self):
        self.api_key: Optional[str] = os.getenv(APIConstants.ENV_GPTZERO_API_KEY) or GPTZeroConfig.DEFAULT_API_KEY
        self.api_url: Optional[str] = os.getenv(APIConstants.ENV_GPTZERO_API_URL) or GPTZeroConfig.DEFAULT_API_URL
        self.timeout_seconds: int = GPTZeroConfig.DEFAULT_TIMEOUT_SECONDS
        self.chunk_size_chars: int = GPTZeroConfig.CHUNK_SIZE_CHARS
        self.chunk_overlap_chars: int = GPTZeroConfig.CHUNK_OVERLAP_CHARS
        self.max_parallel: int = GPTZeroConfig.MAX_PARALLEL_REQUESTS

        self.include_raw: bool = False

    def _split_into_chunks(self, text: str) -> List[Tuple[int, str]]:
        """Split text into overlapping chunks to respect provider size limits.
        Returns list of (index, chunk_text).
        """
        if not text:
            return []

        size = max(1000, self.chunk_size_chars)
        overlap = max(0, min(self.chunk_overlap_chars, size // 2))

        chunks: List[Tuple[int, str]] = []
        start = 0
        idx = 0
        text_len = len(text)
        while start < text_len:
            end = min(text_len, start + size)
            chunk = text[start:end]
            chunks.append((idx, chunk))
            idx += 1
            if end == text_len:
                break
            start = end - overlap
        return chunks

    async def _score_chunk(self, chunk_index: int, chunk_text: str) -> Dict[str, Any]:
        """Post a single chunk to GPTZero."""
        if not self.api_key or not self.api_url:
            return {
                "index": chunk_index,
                "status": "unavailable",
                "reason": "GPTZero configuration missing",
                "score": None,
                "chars": len(chunk_text),
            }

        headers = {
            "x-api-key": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        payload = {"document": chunk_text, "multilingual": False}

        try:
            resp = await httpx.AsyncClient().post(self.api_url, json=payload, headers=headers, timeout=self.timeout_seconds)
            resp.raise_for_status()
            data = resp.json()

            score = None
            label = None
            confidence_score = None
            confidence_category = None
            version = data.get("version") or data.get("neatVersion")

            doc = None
            if isinstance(data, dict) and isinstance(data.get("documents"), list) and data["documents"]:
                doc = data["documents"][0]
                score = doc.get("completely_generated_prob")
                label = doc.get("predicted_class")
                confidence_score = doc.get("confidence_score")
                confidence_category = doc.get("confidence_category")
                if score is None and isinstance(doc.get("class_probabilities"), dict):
                    score = doc["class_probabilities"].get("ai")

            if score is None:
                score = data.get("probability") or data.get("score")

            try:
                score = float(score) if score is not None else None
            except Exception:
                score = None

            if label is not None:
                label = str(label).lower()
                if label in ("ai", "pure_ai", "ai_only"):
                    label = "likely_ai"
                elif label in ("human", "human_only"):
                    label = "likely_human"
                elif label in ("mixed", "ai_paraphrased"):
                    label = "mixed"
            elif isinstance(score, (int, float)):
                label = "likely_ai" if score >= 0.5 else "likely_human"

            chunk_result = {
                "index": chunk_index,
                "status": "ok",
                "score": score,
                "label": label,
                "chars": len(chunk_text),
                "confidence_score": confidence_score,
                "confidence_category": confidence_category,
                "version": version,
            }
            if self.include_raw:
                chunk_result["raw"] = data
            return chunk_result
        except httpx.HTTPError as e:
            return {
                "index": chunk_index,
                "status": "error",
                "reason": str(e),
                "score": None,
                "chars": len(chunk_text),
            }

    @staticmethod
    def _aggregate_results(chunk_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        ok_chunks = [c for c in chunk_results if c.get("status") == "ok" and isinstance(c.get("score"), (int, float))]
        if not ok_chunks:
            status = "unavailable" if any(c.get("status") == "unavailable" for c in chunk_results) else "error"
            reason = ", ".join(sorted({c.get("reason", "") for c in chunk_results if c.get("reason")})) or None
            return {
                "provider": "gptzero",
                "status": status,
                "reason": reason,
            }

        total_chars = sum(c.get("chars", 0) for c in ok_chunks)
        if total_chars <= 0:
            overall_score = sum(c.get("score", 0.0) for c in ok_chunks) / max(1, len(ok_chunks))
        else:
            overall_score = sum((c.get("score", 0.0) * c.get("chars", 0)) for c in ok_chunks) / total_chars

        label = "likely_ai" if overall_score >= 0.5 else "likely_human"

        categories = [c.get("confidence_category") for c in ok_chunks if c.get("confidence_category")]
        overall_confidence_category = None
        if categories:
            counts: Dict[str, int] = {}
            for cat in categories:
                counts[cat] = counts.get(cat, 0) + 1
            overall_confidence_category = max(counts.items(), key=lambda kv: kv[1])[0]

        ai_prob_pct = round(float(overall_score) * 100, 2)
        verdict_text = (
            "Likely AI-generated" if label == "likely_ai" else
            "Likely Human-written" if label == "likely_human" else
            "Mixed signals"
        )

        return {
            "provider": "gptzero",
            "status": "ok",
            "overall_score": round(float(overall_score), 4),
            "label": label,
            "chunks": ok_chunks,
            "tokens_or_chars_analyzed": total_chars,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "verdict": verdict_text,
                "ai_probability_percent": ai_prob_pct,
                "confidence_category": overall_confidence_category,
                "chunks_analyzed": len(ok_chunks),
                "characters_analyzed": total_chars,
            },
        }
    async def detect_ai_from_text(self, text: str) -> Dict[str, Any]:
        """Detect AI-generated content from text input."""
        if not text:
            return {
                "provider": "gptzero",
                "status": "ok",
                "overall_score": 0.0,
                "label": "inconclusive",
                "chunks": [],
                "tokens_or_chars_analyzed": 0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


        result = await self._score_chunk(0, text)

        return self._aggregate_results([result])
