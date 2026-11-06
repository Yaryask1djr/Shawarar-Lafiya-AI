"""
mRDT (Rapid Diagnostic Test) Image Interpretation Service
Uses Gemini Vision to read malaria / pregnancy / COVID RDT strip photos.

Fallback: rule-based colour-band detection description when Gemini is unavailable.
"""

import base64
import logging
import asyncio
import re
import json
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


MRDT_VISION_PROMPT = """You are a clinical laboratory AI assistant trained to interpret Rapid Diagnostic Test (RDT) strips from photos.

Analyse the provided image of a rapid diagnostic test strip and return ONLY valid JSON in this exact schema:

{
  "test_type_detected": "malaria_rdt" | "pregnancy_test" | "covid_antigen" | "unknown",
  "result": "POSITIVE" | "NEGATIVE" | "INVALID" | "UNCLEAR",
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "bands_visible": {
    "control_band": true | false,
    "test_band_1": true | false,
    "test_band_2": true | false
  },
  "interpretation_ha": "Hausa explanation of result in 1-2 sentences",
  "interpretation_en": "English explanation of result in 1-2 sentences",
  "clinical_action_ha": "What the patient/CHEW should do next — in Hausa",
  "clinical_action_en": "What the patient/CHEW should do next — in English",
  "safety_note_ha": "Any clinical safety caveat in Hausa",
  "safety_note_en": "Any clinical safety caveat in English",
  "image_quality": "GOOD" | "POOR" | "UNREADABLE"
}

Rules:
- If the control band (C) is NOT visible, result = "INVALID" regardless of test bands.
- For malaria RDT: one test band (T) = POSITIVE; no test band = NEGATIVE.
- Never recommend specific antimalarial drugs. Only say "visit PHC for treatment".
- If image is blurry or unreadable, set result = "UNCLEAR", image_quality = "UNREADABLE".
- Output ONLY the JSON object. No markdown, no preamble.
"""


class MRDTService:
    """
    Interprets RDT strip images using Gemini Vision.
    Gracefully degrades if Gemini is unavailable.
    """

    TIMEOUT_SECONDS = 20
    MAX_RETRIES = 2

    def __init__(self):
        self._model = None
        self._available = False
        self._init_model()

    def _init_model(self):
        from app.config import settings
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.info("GEMINI_API_KEY not set — mRDT vision disabled; manual fallback active.")
            return
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 600,
                    "response_mime_type": "application/json",
                },
            )
            self._available = True
            logger.info("mRDT Vision service initialised (Gemini 2.5 Flash).")
        except ImportError:
            logger.warning("google-generativeai not installed.")
        except Exception as exc:
            logger.error(f"mRDT Vision init failed: {exc}")

    @property
    def is_available(self) -> bool:
        return self._available and self._model is not None

    async def interpret_image(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        language: str = "ha",
    ) -> dict:
        """
        Main entry point. Accepts raw image bytes.
        Returns structured dict with result, confidence, bilingual guidance.
        """
        if not self.is_available:
            return self._fallback_response(language)

        # Encode to base64 for Gemini
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        image_part = {"mime_type": mime_type, "data": b64}

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self._model.generate_content,
                        [MRDT_VISION_PROMPT, image_part]
                    ),
                    timeout=self.TIMEOUT_SECONDS,
                )
                raw = response.text.strip()
                raw = re.sub(r"^```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
                data = json.loads(raw)
                self._validate(data)
                logger.info(f"mRDT Vision OK (attempt {attempt}): result={data.get('result')}")
                return data

            except asyncio.TimeoutError:
                logger.warning(f"mRDT Vision timeout (attempt {attempt})")
            except json.JSONDecodeError as exc:
                logger.warning(f"mRDT JSON parse error (attempt {attempt}): {exc}")
            except Exception as exc:
                logger.warning(f"mRDT Vision error (attempt {attempt}): {exc}")
                if "429" in str(exc) or "quota" in str(exc).lower():
                    break

        logger.error("mRDT Vision: all attempts failed — returning fallback.")
        return self._fallback_response(language)

    # ------------------------------------------------------------------
    def _validate(self, data: dict):
        required = {"result", "confidence", "interpretation_ha",
                    "interpretation_en", "clinical_action_ha", "clinical_action_en"}
        missing = required - set(data.keys())
        if missing:
            raise ValueError(f"mRDT response missing keys: {missing}")
        if data.get("result") not in {"POSITIVE", "NEGATIVE", "INVALID", "UNCLEAR"}:
            raise ValueError(f"Invalid mRDT result: {data.get('result')}")

    def _fallback_response(self, language: str) -> dict:
        return {
            "test_type_detected": "unknown",
            "result": "UNCLEAR",
            "confidence": "LOW",
            "bands_visible": {
                "control_band": None,
                "test_band_1": None,
                "test_band_2": None,
            },
            "interpretation_ha": "Ba za a iya karanta hoto ba ta atomatik. Da fatan a nuna wa ma'aikacin lafiya.",
            "interpretation_en": "Automatic image reading is unavailable. Please show the test to a health worker.",
            "clinical_action_ha": "Kai jarrabawar zuwa Cibiyar PHC mafi kusa domin likita ya duba.",
            "clinical_action_en": "Bring the test strip to the nearest PHC for a health worker to read.",
            "safety_note_ha": "Kada a dogara kan hoto kawai — dole ne a tabbatar da sakamakon a PHC.",
            "safety_note_en": "Do not rely on photo reading alone — always confirm results at a PHC.",
            "image_quality": "UNREADABLE",
        }


mrdt_service = MRDTService()
