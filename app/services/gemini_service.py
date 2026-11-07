"""
Gemini 2.5 Flash LLM Service for Shawarar Lafiya.

Wraps Google Generative AI SDK with:
 - Structured JSON output enforcement
 - WHO IMCI system prompt injection
 - Hard timeout + retry logic
 - Graceful fallback to deterministic IMCI engine if API key missing or quota exceeded
"""

import json
import re
import logging
import asyncio
from typing import Optional, Dict, Any

from app.config import settings
from app.prompts.clinical_system_prompt import SHAWARAR_LAFIYA_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Thin async wrapper around google-generativeai for clinical triage.
    Falls back silently to None so the triage service can use deterministic rules.
    """

    MODEL_NAME = "gemini-2.5-flash"
    TIMEOUT_SECONDS = 18
    MAX_RETRIES = 2

    def __init__(self):
        self._client = None
        self._model = None
        self._available = False
        self._init_client()

    def _init_client(self):
        """Lazy initialise the Gemini SDK. Safe to call even without an API key."""
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.info("GEMINI_API_KEY not set — LLM triage disabled; deterministic IMCI engine active.")
            return
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(
                model_name=self.MODEL_NAME,
                system_instruction=SHAWARAR_LAFIYA_SYSTEM_PROMPT,
                generation_config={
                    "temperature": 0.2,          # Low temp for clinical consistency
                    "top_p": 0.85,
                    "max_output_tokens": 1200,
                    "response_mime_type": "application/json",
                },
            )
            self._available = True
            logger.info(f"Gemini LLM initialised: {self.MODEL_NAME}")
        except ImportError:
            logger.warning("google-generativeai not installed. Run: pip install google-generativeai")
        except Exception as exc:
            logger.error(f"Gemini init failed: {exc}")

    @property
    def is_available(self) -> bool:
        return self._available and self._model is not None

    async def run_triage(
        self,
        symptoms_text: str,
        language: str = "ha",
        patient_context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Send a triage prompt to Gemini 2.5 Flash and return parsed JSON dict.
        Returns None on any failure so the caller falls back gracefully.
        """
        if not self.is_available:
            return None

        context_str = ""
        if patient_context:
            age_m = patient_context.get("age_months")
            age_g = patient_context.get("age_group", "unknown")
            preg = patient_context.get("is_pregnant", False)
            context_str = f"\n[Patient Context] Age group: {age_g}"
            if age_m is not None:
                context_str += f", {age_m} months old"
            if preg:
                context_str += ", PREGNANT"

        user_prompt = f"""
Clinical Triage Request — Language: {language.upper()}
{context_str}

Symptom Description:
\"\"\"{symptoms_text}\"\"\"

Instructions:
1. Assess using WHO IMCI General Danger Signs FIRST.
2. If ANY danger sign is present → tier MUST be "RED".
3. Provide bilingual response (Hausa + English) in the JSON schema specified.
4. Recommend only ORS, Zinc, or Paracetamol as supportive medications — NEVER antibiotics or antimalarials.
5. Output ONLY valid JSON — no markdown fences, no preamble.
"""
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(self._model.generate_content, user_prompt),
                    timeout=self.TIMEOUT_SECONDS,
                )
                raw = response.text.strip()

                # Strip markdown fences if model forgets response_mime_type
                raw = re.sub(r"^```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)

                data = json.loads(raw)
                self._validate_triage_json(data)
                logger.info(f"Gemini triage OK (attempt {attempt}): tier={data.get('tier')}")
                return data

            except asyncio.TimeoutError:
                logger.warning(f"Gemini timeout (attempt {attempt}/{self.MAX_RETRIES})")
            except json.JSONDecodeError as exc:
                logger.warning(f"Gemini JSON parse error (attempt {attempt}): {exc}")
            except Exception as exc:
                logger.warning(f"Gemini call error (attempt {attempt}): {exc}")
                # Quota / 429 — no point retrying immediately
                if "429" in str(exc) or "quota" in str(exc).lower():
                    break

        logger.error("Gemini: all attempts failed — falling back to deterministic IMCI engine.")
        return None

    # ------------------------------------------------------------------
    # Structural validation — prevents hallucinated schema from reaching users
    # ------------------------------------------------------------------
    REQUIRED_KEYS = {
        "tier", "tier_label_ha", "tier_label_en", "is_emergency",
        "summary_ha", "summary_en",
        "primary_actions_ha", "primary_actions_en",
        "clinical_disclaimer_ha", "clinical_disclaimer_en",
        "nearest_care_guidance_ha", "nearest_care_guidance_en",
    }
    VALID_TIERS = {"RED", "YELLOW", "GREEN"}

    def _validate_triage_json(self, data: Dict[str, Any]):
        missing = self.REQUIRED_KEYS - set(data.keys())
        if missing:
            raise ValueError(f"Gemini response missing required keys: {missing}")
        tier_val = str(data.get("tier", "")).strip().upper()
        if tier_val not in self.VALID_TIERS:
            raise ValueError(f"Invalid tier value: {data.get('tier')}")
        data["tier"] = tier_val
        for field in ("primary_actions_ha", "primary_actions_en"):
            if not isinstance(data.get(field), list) or len(data[field]) == 0:
                raise ValueError(f"Field '{field}' must be a non-empty list")


gemini_service = GeminiService()
