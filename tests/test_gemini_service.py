"""
Tests for Gemini LLM Service and Integration with Triage Pipeline.
"""

import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.gemini_service import GeminiService
from app.services.triage_service import triage_service
from app.schemas import SymptomTriageRequest, TriageTier

@pytest.mark.anyio
async def test_gemini_service_unavailable_by_default():
    service = GeminiService()
    # In test environment, GEMINI_API_KEY is unset or empty
    if not service.is_available:
        result = await service.run_triage("Yaro na yana tari")
        assert result is None

@pytest.mark.anyio
async def test_gemini_service_successful_mock_response():
    service = GeminiService()
    service._available = True
    
    mock_payload = {
        "tier": "YELLOW",
        "tier_label_ha": "Gani Likita Cikin Sa'o'i 24",
        "tier_label_en": "Urgent Clinical Visit (Within 24 Hours)",
        "is_emergency": False,
        "summary_ha": "Akwai bukatar ganin likita a PHC don auna zazzabi da gwajin mRDT.",
        "summary_en": "Needs clinical review at PHC for fever evaluation and mRDT test.",
        "primary_actions_ha": ["Kai mara lafiyar PHC don gwajin mRDT", "Shafa masa ruwan dumi"],
        "primary_actions_en": ["Visit PHC for mRDT malaria test", "Tepid sponging"],
        "clinical_disclaimer_ha": "Shawarar Lafiya ba madadin likita ba ne.",
        "clinical_disclaimer_en": "Shawarar Lafiya is not a doctor.",
        "nearest_care_guidance_ha": "Ziyarci cibiyar PHC mafi kusa.",
        "nearest_care_guidance_en": "Visit nearest PHC."
    }
    
    mock_response = MagicMock()
    mock_response.text = json.dumps(mock_payload)
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    service._model = mock_model

    result = await service.run_triage("Child has high fever for two days", language="en")
    assert result is not None
    assert result["tier"] == "YELLOW"
    assert "PHC" in result["primary_actions_en"][0]

@pytest.mark.anyio
async def test_gemini_service_fallback_on_invalid_json():
    service = GeminiService()
    service._available = True
    
    mock_response = MagicMock()
    mock_response.text = "Sorry, I cannot diagnose this patient. Please consult a doctor."
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    service._model = mock_model

    result = await service.run_triage("Child is sick")
    assert result is None

@pytest.mark.anyio
async def test_gemini_service_fallback_on_missing_required_fields():
    service = GeminiService()
    service._available = True
    
    # Missing tier and primary actions
    mock_response = MagicMock()
    mock_response.text = json.dumps({"summary_ha": "Lafiya kalau"})
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    service._model = mock_model

    result = await service.run_triage("Child is sick")
    assert result is None

@pytest.mark.anyio
async def test_red_flag_guardrail_bypasses_gemini_completely():
    """
    Critical Clinical Safety Invariant:
    If a general danger sign is detected, the emergency override must fire
    INSTANTLY without invoking Gemini or any generative model.
    """
    mock_gemini = MagicMock()
    mock_gemini.is_available = True
    mock_gemini.run_triage = AsyncMock()

    with patch("app.services.triage_service.gemini_service", mock_gemini):
        req = SymptomTriageRequest(
            symptoms_text="Yaro na yana karkarwa da farfadiya, ya daina shan nono.",
            language="ha"
        )
        response = await triage_service.triage_symptoms(req)
        
        # Verify emergency tier
        assert response.tier == TriageTier.RED
        assert response.is_emergency is True
        assert len(response.red_flags_detected) > 0
        
        # Confirm Gemini was NEVER called because pre-execution red flag intercepted
        mock_gemini.run_triage.assert_not_called()

@pytest.mark.anyio
async def test_triage_service_uses_gemini_when_available():
    """
    When Gemini is available and no red flags, triage_service should use Gemini's result
    and stamp metadata['triage_source'] = 'gemini_2.5_flash'.
    """
    mock_gemini = MagicMock()
    mock_gemini.is_available = True
    mock_gemini.run_triage = AsyncMock(return_value={
        "tier": "YELLOW",
        "tier_label_ha": "Gani Likita Cikin Sa'o'i 24",
        "tier_label_en": "Urgent Clinical Visit",
        "is_emergency": False,
        "summary_ha": "Bayani daga Gemini",
        "summary_en": "Explanation from Gemini",
        "primary_actions_ha": ["Mataki na daya"],
        "primary_actions_en": ["Step one"],
        "clinical_disclaimer_ha": "Shawarar Lafiya jagora ce.",
        "clinical_disclaimer_en": "Shawarar Lafiya is an aid.",
        "nearest_care_guidance_ha": "Je PHC",
        "nearest_care_guidance_en": "Visit PHC"
    })

    with patch("app.services.triage_service.gemini_service", mock_gemini):
        req = SymptomTriageRequest(
            symptoms_text="Yaro na yana da zazzabi da zafin jiki tun kwana biyu",
            language="ha"
        )
        response = await triage_service.triage_symptoms(req)
        assert response.tier == TriageTier.YELLOW
        assert response.metadata.get("triage_source") == "gemini_2.5_flash"
        mock_gemini.run_triage.assert_called_once()
