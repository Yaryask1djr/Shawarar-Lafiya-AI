"""
Twilio WhatsApp & IVR (Voice) Webhook Router for Shawarar Lafiya.

Endpoints:
  POST /webhook/whatsapp   — Twilio WhatsApp Business message handler
  POST /webhook/ivr/greet  — Twilio Programmable Voice: initial IVR greeting (TwiML)
  POST /webhook/ivr/input  — Twilio IVR: captures <Gather> digits / speech transcription
  POST /webhook/ivr/status — Twilio call status callback (logging)

Flow (WhatsApp):
  Caregiver sends a text or voice note →
  Twilio delivers to /webhook/whatsapp →
  Guardrail scan → Gemini or deterministic triage →
  Reply with bilingual triage result + emergency 112 deeplink (if RED)

Flow (IVR / Feature Phone):
  Incoming call → TwiML greet in Hausa →
  <Gather> speech (or keypad digits for menu) →
  POST to /webhook/ivr/input →
  Triage → TwiML <Say> response in Hausa

Safety invariants honoured regardless of channel:
  - WHO IMCI RED bypass is always first
  - Prescription guardrail always runs on output
  - Clinical disclaimer always appended
"""

import logging
from typing import Optional

from fastapi import APIRouter, Form, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse

from app.schemas import SymptomTriageRequest, PatientContext
from app.services.triage_service import triage_service
from app.services.guardrail_service import guardrail_service
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["Twilio Webhooks"])


# ---------------------------------------------------------------------------
# Twilio signature validation helper (non-fatal in dev mode)
# ---------------------------------------------------------------------------
def _verify_twilio_signature(request: Request, params: Optional[dict] = None) -> bool:
    """
    Validate Twilio's X-Twilio-Signature header.
    Returns True in development (no auth token configured) so dev testing works.
    Returns True if validation passes, False if it fails in production.
    """
    auth_token = settings.TWILIO_AUTH_TOKEN
    if not auth_token:
        # Dev mode — skip validation
        return True
    try:
        from twilio.request_validator import RequestValidator  # type: ignore
        validator = RequestValidator(auth_token)
        signature = request.headers.get("X-Twilio-Signature", "")
        url = str(request.url)
        return validator.validate(url, params or {}, signature)
    except Exception as exc:
        logger.warning(f"Twilio signature validation error: {exc}")
        return False


# ---------------------------------------------------------------------------
# TwiML helpers
# ---------------------------------------------------------------------------
def _twiml_response(twiml_body: str) -> Response:
    """Return a Twilio-compatible XML response."""
    return Response(
        content=f'<?xml version="1.0" encoding="UTF-8"?>\n<Response>{twiml_body}</Response>',
        media_type="application/xml"
    )


def _say(text: str, language: str = "ha") -> str:
    """
    Generate a TwiML <Say> verb.
    Hausa voice: Alice (en-NG is the closest available; production would use
    a custom Hausa voice or Polly).
    """
    voice = "Polly.Ayanda" if language == "ha" else "Polly.Joanna"
    lang_code = "en-NG" if language == "ha" else "en-US"
    # Escape XML special chars
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<Say voice="{voice}" language="{lang_code}">{safe}</Say>'


# ---------------------------------------------------------------------------
# Format triage result for SMS/WhatsApp character budget (~1600 chars)
# ---------------------------------------------------------------------------
def _format_whatsapp_reply(result, language: str = "ha") -> str:
    is_ha = language == "ha"
    tier = result.tier.value

    # Emoji tier indicator
    tier_emoji = {"RED": "🚨", "YELLOW": "⚠️", "GREEN": "✅"}.get(tier, "ℹ️")
    tier_label = result.tier_label_ha if is_ha else result.tier_label_en
    summary = result.summary_ha if is_ha else result.summary_en
    actions = result.primary_actions_ha if is_ha else result.primary_actions_en
    disclaimer = result.clinical_disclaimer_ha if is_ha else result.clinical_disclaimer_en

    action_lines = "\n".join(f"  {i+1}. {a}" for i, a in enumerate(actions[:3]))

    reply = (
        f"{tier_emoji} *SHAWARAR LAFIYA — {tier_label.upper()}*\n\n"
        f"{summary}\n\n"
        f"{'Matakan Da Ya Kamata:' if is_ha else 'Recommended Steps:'}\n"
        f"{action_lines}\n"
    )

    # Emergency: add 112 deep-link and first aid note
    if tier == "RED":
        if is_ha:
            reply += "\n🆘 *Ana bukatar gaggauta zuwa asibiti nan take!*\nKira: *tel:112* (Sufurin Gaggawa)\n"
            reply += "⚕️ Kwantar da mara lafiyar a gefe (recovery position). Kada ka tura wani abu a bakinsa.\n"
        else:
            reply += "\n🆘 *Immediate hospital transfer required!*\nCall: *tel:112* (Emergency Services)\n"
            reply += "⚕️ Lay patient on side (recovery position). Keep airway clear.\n"

    reply += f"\n_{'Shawarar Lafiya ba madadin likita ba ne.' if is_ha else disclaimer}_"
    return reply


# ===========================================================================
# WHATSAPP ENDPOINT
# ===========================================================================
@router.post("/whatsapp", response_class=PlainTextResponse)
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(default=""),
    From: str = Form(default=""),
    To: str = Form(default=""),
    MediaUrl0: Optional[str] = Form(default=None),
    NumMedia: str = Form(default="0"),
):
    """
    Twilio WhatsApp Business webhook.

    Receives inbound WhatsApp messages and responds with bilingual triage guidance.
    Voice memos (MediaUrl0) are handled via the audio triage pipeline (stub in dev).
    """
    if settings.TWILIO_AUTH_TOKEN:
        params = {"Body": Body, "From": From, "To": To, "NumMedia": NumMedia}
        if MediaUrl0:
            params["MediaUrl0"] = MediaUrl0
        if not _verify_twilio_signature(request, params):
            raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    # Determine language from sender number prefix (+234 → Nigeria → Hausa default)
    language = "ha" if From.startswith("+234") or From.startswith("whatsapp:+234") else "en"

    logger.info(f"WhatsApp inbound | from={From} | media={NumMedia} | lang={language}")

    # Handle voice memo (audio attachment)
    if int(NumMedia) > 0 and MediaUrl0:
        # In production: download MediaUrl0 → pass to asr_service → triage
        # For now, acknowledge and prompt for text re-send
        if language == "ha":
            reply = (
                "🎤 *An karbi muryarka.* "
                "Don fara aiki, rubuta alamomin mara lafiya cikin rubutu. "
                "Misali: 'Yaro na yana da zazzabi tun kwana biyu, yana amai.'"
            )
        else:
            reply = (
                "🎤 *Voice note received.* "
                "Please type out the symptoms as text to begin triage. "
                "Example: 'Child has had a fever for two days with vomiting.'"
            )
        return _twiml_to_wa_reply(reply)

    symptoms = Body.strip()
    if not symptoms or len(symptoms) < 3:
        greeting = (
            "Sannu! Ni ne *Shawarar Lafiya*, Jagora na Kiwon Lafiya ta Farko. "
            "Fada mini alamomin mara lafiya don in taimaka.\n"
            "_(Rubuta cikin Hausa ko Turanci)_"
        ) if language == "ha" else (
            "Hello! I am *Shawarar Lafiya*, your Primary Health Triage Guide. "
            "Please describe the patient's symptoms and I'll help assess urgency.\n"
            "_(Type in Hausa or English)_"
        )
        return PlainTextResponse(greeting)

    # Triage pipeline
    try:
        triage_req = SymptomTriageRequest(
            symptoms_text=symptoms,
            language=language,
            channel="whatsapp",
        )
        result = await triage_service.triage_symptoms(triage_req)
        reply = _format_whatsapp_reply(result, language=language)
    except Exception as exc:
        logger.error(f"WhatsApp triage error: {exc}")
        reply = (
            "⚠️ An samu matsala ta fasaha. Da fatan za a sake aika sakon.\n"
            "_(Technical error. Please resend your message.)_"
        )

    return PlainTextResponse(reply)


def _twiml_to_wa_reply(text: str) -> PlainTextResponse:
    """WhatsApp replies are plain text (not TwiML XML)."""
    return PlainTextResponse(text)


# ===========================================================================
# IVR — INITIAL GREETING
# ===========================================================================
@router.post("/ivr/greet")
async def ivr_greet(
    request: Request,
    From: str = Form(default=""),
    CallSid: str = Form(default=""),
):
    """
    TwiML: Greet caller in Hausa and open a <Gather> for speech or keypad input.
    """
    logger.info(f"IVR inbound call | CallSid={CallSid} | from={From}")
    twiml = (
        _say(
            "Sannu da zuwa Shawarar Lafiya. "
            "Ni ne jagoran kiwon lafiya na farko. "
            "Bayan kararrawa, fada min alamomin mara lafiya cikin Hausa ko Turanci. "
            "Idan kana da gaggawa kuma mara lafiyar yana mutuwa, danna kafi biyu yanzu.",
            language="ha"
        )
        + '<Gather input="speech dtmf" timeout="8" speechTimeout="auto" '
          'action="/webhook/ivr/input" method="POST" language="en-NG" hints="zazzabi,farfadiya,amai,zawo,fever,convulsion,emergency">'
        + _say("Fada min alamomin yanzu.", language="ha")
        + "</Gather>"
        + _say(
            "Ba mu ji komai ba. Za ka iya kiran lamba dari da goma sha biyu — 112 — domin gaggawa.",
            language="ha"
        )
        + "<Hangup/>"
    )
    return _twiml_response(twiml)


# ===========================================================================
# IVR — GATHER INPUT (speech transcription → triage → <Say> response)
# ===========================================================================
@router.post("/ivr/input")
async def ivr_input(
    request: Request,
    SpeechResult: Optional[str] = Form(default=None),
    Digits: Optional[str] = Form(default=None),
    Confidence: Optional[str] = Form(default=None),
    CallSid: str = Form(default=""),
    From: str = Form(default=""),
):
    """
    TwiML: Processes gathered speech or DTMF digits.
    '2' → emergency shortcut (immediately instructs caller to dial 112).
    Speech text → full triage pipeline → <Say> bilingual result.
    """
    logger.info(
        f"IVR input | CallSid={CallSid} | digits={Digits!r} | speech={SpeechResult!r} | conf={Confidence}"
    )

    # DTMF 2 = emergency fast path
    if Digits == "2":
        twiml = (
            _say(
                "Gaggawa! Rufe wannan kira kuma kira ɗari da goma sha biyu — 112 — nan take. "
                "Kwantar da mara lafiyar a gefe idan yana kwance. Allah ya kare ku.",
                language="ha",
            )
            + "<Hangup/>"
        )
        return _twiml_response(twiml)

    symptoms = (SpeechResult or "").strip()
    if not symptoms:
        twiml = (
            _say("Ba mu ji komai ba, don Allah sake fada.", language="ha")
            + '<Gather input="speech" timeout="8" speechTimeout="auto" '
              'action="/webhook/ivr/input" method="POST" language="en-NG">'
            + _say("Fada min alamomin mara lafiya.", language="ha")
            + "</Gather>"
            + "<Hangup/>"
        )
        return _twiml_response(twiml)

    # Language detection: simple heuristic (Hausa-dominant terms)
    hausa_markers = ["yaro", "yana", "tana", "zazzabi", "amai", "zawo", "nono", "ciki"]
    language = "ha" if any(m in symptoms.lower() for m in hausa_markers) else "en"

    try:
        triage_req = SymptomTriageRequest(
            symptoms_text=symptoms,
            language=language,
            channel="ivr",
        )
        result = await triage_service.triage_symptoms(triage_req)
        tier = result.tier.value

        # Build IVR spoken response (keep under ~30 seconds of speech)
        summary = result.summary_ha if language == "ha" else result.summary_en
        actions = result.primary_actions_ha if language == "ha" else result.primary_actions_en
        first_two = ". ".join(actions[:2])

        if tier == "RED":
            spoken = (
                f"GAGGAWA! {summary} "
                f"Ka kai mara lafiyar asibiti ko PHC nan take. {first_two}. "
                f"Idan ba zaka iya ba, kira ɗari da goma sha biyu — 112."
            )
        elif tier == "YELLOW":
            spoken = (
                f"Ana bukatar ziyartar PHC a cikin awowi ashirin da hudu. "
                f"{summary} {first_two}."
            )
        else:
            spoken = (
                f"Za ka iya kula da mara lafiyar a gida. "
                f"{summary} {first_two}. "
                f"Idan yanayin ya tsananta, kai zuwa PHC."
            )

        # Always append disclaimer
        spoken += " Shawarar Lafiya ba madadin likita ba ne."

        twiml = (
            _say(spoken, language=language)
            + _say(
                "Don sake tambaya, danna tauraron dan adam ko kira mu da wuri.",
                language="ha"
            )
            + "<Hangup/>"
        )

    except Exception as exc:
        logger.error(f"IVR triage error: {exc}")
        twiml = (
            _say(
                "An samu matsala ta fasaha. Da fatan za a sake kira ko je asibiti mafi kusa.",
                language="ha",
            )
            + "<Hangup/>"
        )

    return _twiml_response(twiml)


# ===========================================================================
# IVR STATUS CALLBACK (Twilio posts call lifecycle events here)
# ===========================================================================
@router.post("/ivr/status")
async def ivr_status_callback(
    CallSid: str = Form(default=""),
    CallStatus: str = Form(default=""),
    From: str = Form(default=""),
    Duration: Optional[str] = Form(default=None),
):
    """
    Twilio call status callback endpoint (logging only).
    """
    logger.info(
        f"IVR status | CallSid={CallSid} | status={CallStatus} | "
        f"from={From} | duration={Duration}s"
    )
    return {"received": True}
