import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Shawarar Lafiya - Hausa Primary Health & Symptom Triage Voicebot"
    VERSION: str = "1.1.0"
    API_PREFIX: str = "/api/v1"

    # Environment
    ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # ── Gemini LLM ────────────────────────────────────────────────────────────
    # Set GEMINI_API_KEY to enable Gemini 2.5 Flash triage.
    # Leave blank to use the deterministic WHO IMCI rule engine (safe offline mode).
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "gemini-2.5-flash")

    # ── Twilio ────────────────────────────────────────────────────────────────
    # Set these to enable WhatsApp Business + IVR voice webhooks.
    # Leave blank in development — signature validation is bypassed automatically.
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "")  # e.g. whatsapp:+14155238886
    TWILIO_VOICE_NUMBER: str = os.getenv("TWILIO_VOICE_NUMBER", "")

    # ── Audio & Speech ────────────────────────────────────────────────────────
    AUDIO_UPLOAD_DIR: str = os.getenv("AUDIO_UPLOAD_DIR", "uploads")
    DEFAULT_LANGUAGE: str = "ha"  # Hausa ISO code
    SUPPORTED_LANGUAGES: list[str] = ["ha", "en"]

    # ── Referral & DHIS2 ──────────────────────────────────────────────────────
    DHIS2_USERNAME: str = os.getenv("DHIS2_USERNAME", "")
    DHIS2_PASSWORD: str = os.getenv("DHIS2_PASSWORD", "")

    # ── Clinical Safety ───────────────────────────────────────────────────────
    MAX_SYMPTOM_DESCRIPTION_CHARS: int = 1500
    ENABLE_STRICT_PRESCRIPTION_FILTER: bool = True
    ALLOW_SUPPORTIVE_MEDICATIONS: list[str] = [
        "ors", "ruwan gishiri da sukari", "oral rehydration salts",
        "zinc", "zinc sulphate", "sin",
        "paracetamol", "fannas"
    ]

settings = Settings()
