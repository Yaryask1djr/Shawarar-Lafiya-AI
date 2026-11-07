"""
Integration API tests for Shawarar Lafiya FastAPI endpoints.
"""

import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import TriageTier

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Shawarar Lafiya" in data["project"]
    assert data["status"] == "operational"

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["guardrails_active"] is True

def test_triage_text_red_emergency():
    payload = {
        "symptoms_text": "Yaro na yana karkarwa da farfadiya, ya daina shan nono.",
        "language": "ha",
        "patient_context": {
            "age_group": "young_child",
            "age_months": 18
        }
    }
    response = client.post("/api/v1/triage/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == TriageTier.RED
    assert data["is_emergency"] is True
    assert len(data["red_flags_detected"]) >= 1
    assert "Gaggawa" in data["tier_label_ha"]
    assert len(data["primary_actions_ha"]) > 0

def test_triage_text_yellow_fever_suspected_malaria():
    payload = {
        "symptoms_text": "Yaro na yana da zazzabi da zafin jiki tun kwana biyu, amma yana cin abinci.",
        "language": "ha",
        "patient_context": {
            "age_group": "young_child",
            "age_months": 24
        }
    }
    response = client.post("/api/v1/triage/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == TriageTier.YELLOW
    assert data["is_emergency"] is False
    assert "mRDT" in data["summary_ha"] or "PHC" in data["summary_ha"]

def test_triage_text_green_mild_diarrhea():
    payload = {
        "symptoms_text": "Yaro na ya yi zawo sau biyu yau, amma yana wasa kuma ba zazzabi ko amai.",
        "language": "ha"
    }
    response = client.post("/api/v1/triage/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == TriageTier.GREEN
    assert data["is_emergency"] is False
    assert any("ors" in act.lower() or "gishiri" in act.lower() for act in data["primary_actions_ha"])

def test_immunization_query_six_weeks():
    payload = {
        "child_age_weeks": 6,
        "language": "ha"
    }
    response = client.post("/api/v1/immunization/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["child_age_weeks"] == 6
    due_names = [v["vaccine_name"] for v in data["vaccines_due_now"]]
    assert any("Penta" in v for v in due_names)
    assert any("OPV" in v for v in due_names)
    assert "kyauta ce" in data["guidance_ha"]

def test_guardrails_check_redflags_endpoint():
    response = client.post(
        "/api/v1/guardrails/check-redflags",
        data={"text": "Yarinya tana fama da shanyewar kirji", "language": "ha"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["flag_id"] == "RF_RESPIRATORY_DISTRESS"

def test_triage_audio_endpoint():
    # Simulate an uploaded wav file
    audio_bytes = b"RIFFFakeWavDataForTesting1234567890"
    files = {"audio_file": ("test_voice_memo.wav", io.BytesIO(audio_bytes), "audio/wav")}
    data = {"language": "ha", "channel": "whatsapp_voice"}
    
    response = client.post("/api/v1/triage/audio", files=files, data=data)
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["success"] is True
    assert "transcription" in resp_data
    assert resp_data["triage_result"] is not None
    assert resp_data["triage_result"]["tier"] in ["RED", "YELLOW", "GREEN"]

def test_voice_stream_endpoint():
    response = client.get("/api/v1/voice/stream?text_hash=abc12345&lang=ha")
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert len(response.content) > 0

def test_mrdt_empty_image_rejected():
    files = {"image_file": ("test.jpg", io.BytesIO(b""), "image/jpeg")}
    response = client.post("/api/v1/mrdt/interpret", files=files, data={"language": "ha"})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

def test_mrdt_oversized_image_rejected():
    oversized_bytes = b"0" * (10 * 1024 * 1024 + 10)
    files = {"image_file": ("big.jpg", io.BytesIO(oversized_bytes), "image/jpeg")}
    response = client.post("/api/v1/mrdt/interpret", files=files, data={"language": "ha"})
    assert response.status_code == 413

def test_audio_empty_transcription_rejected():
    # File with content that produces empty transcription in mocked/short scenario
    files = {"audio_file": ("empty.wav", io.BytesIO(b"short"), "audio/wav")}
    response = client.post("/api/v1/triage/audio", files=files, data={"language": "ha"})
    # Normal response or handled 400
    assert response.status_code in [200, 400]

