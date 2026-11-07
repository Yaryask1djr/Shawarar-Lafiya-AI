"""
FastAPI Entrypoint for Shawarar Lafiya.
Primary Health & Symptom Triage Voicebot Backend.
"""

import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.schemas import (
    SymptomTriageRequest,
    TriageResponse,
    ImmunizationQueryRequest,
    ImmunizationQueryResponse,
    AudioProcessResponse,
    RedFlagDetection,
    MRDTInterpretationResponse,
    ReferralQueryRequest,
    ReferralQueryResponse
)
from app.services.triage_service import triage_service
from app.services.guardrail_service import guardrail_service
from app.services.asr_service import asr_service
from app.services.tts_service import tts_service
from app.services.gemini_service import gemini_service
from app.services.mrdt_service import mrdt_service
from app.services.referral_service import referral_service
from app.webhooks.twilio_webhook import router as twilio_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Primary Healthcare & Symptom Triage Voicebot serving Hausa-speaking rural communities and CHEWs."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.AUDIO_UPLOAD_DIR, exist_ok=True)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Register Twilio WhatsApp + IVR webhook routes
app.include_router(twilio_router)

@app.get("/ui", include_in_schema=False)
@app.get("/app", include_in_schema=False)
def serve_ui():
    index_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "UI under development"}

@app.get("/favicon.ico", include_in_schema=False)
def serve_favicon():
    favicon_file = os.path.join(os.path.dirname(__file__), "static", "favicon.ico")
    if os.path.exists(favicon_file):
        return FileResponse(favicon_file, media_type="image/x-icon")
    return Response(status_code=404)

@app.get("/")
def read_root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "description": "Shawarar Lafiya Voicebot API (Hausa / English Primary Health Triage)",
        "web_ui": "/ui",
        "llm_engine": "gemini_2.5_flash" if gemini_service.is_available else "imci_deterministic",
        "endpoints": {
            "web_ui": "/ui",
            "triage_text": f"{settings.API_PREFIX}/triage/text",
            "triage_audio": f"{settings.API_PREFIX}/triage/audio",
            "immunization": f"{settings.API_PREFIX}/immunization/query",
            "guardrail_check": f"{settings.API_PREFIX}/guardrails/check-redflags",
            "mrdt_interpret": f"{settings.API_PREFIX}/mrdt/interpret",
            "referral_nearest": f"{settings.API_PREFIX}/referral/nearest",
            "whatsapp_webhook": "/webhook/whatsapp",
            "ivr_greet": "/webhook/ivr/greet",
            "ivr_input": "/webhook/ivr/input",
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "env": settings.ENV,
        "guardrails_active": True,
        "default_language": settings.DEFAULT_LANGUAGE,
        "llm_engine": "gemini_2.5_flash" if gemini_service.is_available else "imci_deterministic",
        "llm_active": gemini_service.is_available,
        "twilio_whatsapp_configured": bool(settings.TWILIO_AUTH_TOKEN),
        "version": settings.VERSION,
    }

@app.post(f"{settings.API_PREFIX}/triage/text", response_model=TriageResponse)
async def triage_text_endpoint(request: SymptomTriageRequest):
    """
    Receives symptom descriptions in Hausa or English, applies safety guardrails,
    and returns tiered WHO IMCI clinical triage guidance.
    """
    try:
        response = await triage_service.triage_symptoms(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage processing error: {str(e)}")

@app.post(f"{settings.API_PREFIX}/triage/audio", response_model=AudioProcessResponse)
async def triage_audio_endpoint(
    audio_file: UploadFile = File(...),
    language: str = Form("ha"),
    channel: str = Form("voicebot"),
    is_pregnant: bool = Form(False)
):
    """
    Handles audio note upload (IVR/WhatsApp voice memo), transcribes using ASR,
    and executes clinical symptom triage.
    """
    # Secure unique temporary file path preventing directory traversal
    safe_filename = os.path.basename(audio_file.filename or "temp_audio.wav")
    temp_filename = f"{uuid.uuid4().hex}_{safe_filename}"
    temp_path = os.path.join(settings.AUDIO_UPLOAD_DIR, temp_filename)
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        transcription, detected_lang, duration = await asr_service.transcribe_audio_file(
            file_path=temp_path,
            hint_language=language
        )

        if not transcription or len(transcription.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail="Audio transcription was empty or too brief to evaluate. Please record a clearer voice message."
            )

        request = SymptomTriageRequest(
            symptoms_text=transcription,
            language=detected_lang,
            channel=channel
        )
        request.patient_context.is_pregnant = is_pregnant

        triage_result = await triage_service.triage_symptoms(request)

        return AudioProcessResponse(
            success=True,
            transcription=transcription,
            detected_language=detected_lang,
            audio_duration_seconds=duration,
            triage_result=triage_result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

@app.post(f"{settings.API_PREFIX}/immunization/query", response_model=ImmunizationQueryResponse)
def query_immunization_endpoint(request: ImmunizationQueryRequest):
    """
    Returns Nigeria NPHCDA routine childhood immunization milestones
    and culturally grounded vaccine education in Hausa.
    """
    return triage_service.query_immunization(request)

@app.post(f"{settings.API_PREFIX}/guardrails/check-redflags", response_model=list[RedFlagDetection])
def check_redflags_endpoint(text: str = Form(...), language: str = Form("ha")):
    """
    Standalone guardrail endpoint to test emergency token and danger sign detection.
    """
    return guardrail_service.scan_for_red_flags(text, language=language)

@app.get(f"{settings.API_PREFIX}/voice/stream")
def stream_voice_audio(text_hash: str = Query(...), lang: str = Query("ha")):
    """
    Voice stream endpoint for IVR / WhatsApp audio response playback.
    """
    # Return minimal WAV header as a mock audio byte payload for audio player clients
    wav_header = (
        b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
        b"D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    )
    return Response(content=wav_header, media_type="audio/wav")

@app.post(f"{settings.API_PREFIX}/mrdt/interpret", response_model=MRDTInterpretationResponse)
async def interpret_mrdt_endpoint(
    image_file: UploadFile = File(...),
    language: str = Form("ha")
):
    """
    Interprets Rapid Diagnostic Test (mRDT) strip photos using computer vision.
    Provides bilingual clinical reading, band identification, and safety directives.
    """
    try:
        MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit
        image_bytes = await image_file.read()
        if not image_bytes or len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded image file is empty.")
        if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="Image file exceeds maximum permitted size of 10MB.")

        mime_type = image_file.content_type or "image/jpeg"
        result = await mrdt_service.interpret_image(
            image_bytes=image_bytes,
            mime_type=mime_type,
            language=language
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"mRDT interpretation failed: {str(e)}")

@app.post(f"{settings.API_PREFIX}/referral/nearest", response_model=ReferralQueryResponse)
async def nearest_referral_endpoint(request: ReferralQueryRequest):
    """
    Finds nearest open PHC health facilities using Nigeria DHIS2 live API or offline curated database.
    """
    try:
        result = await referral_service.find_nearest(
            lat=request.lat,
            lon=request.lon,
            state_filter=request.state_filter,
            level_filter=request.level_filter,
            language=request.language,
            max_results=request.max_results
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Referral routing failed: {str(e)}")
