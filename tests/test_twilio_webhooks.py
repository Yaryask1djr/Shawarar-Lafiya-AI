"""
Tests for Twilio WhatsApp and IVR Webhooks.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_whatsapp_empty_message_returns_greeting():
    response = client.post(
        "/webhook/whatsapp",
        data={"Body": "", "From": "+2348012345678", "To": "whatsapp:+14155238886"}
    )
    assert response.status_code == 200
    assert "Shawarar Lafiya" in response.text
    assert "Fada mini alamomin" in response.text

def test_whatsapp_red_flag_emergency_response():
    response = client.post(
        "/webhook/whatsapp",
        data={
            "Body": "Yaro na yana karkarwa da farfadiya, ya daina shan nono.",
            "From": "+2348012345678",
            "To": "whatsapp:+14155238886"
        }
    )
    assert response.status_code == 200
    text = response.text
    assert "🚨" in text
    assert "GAGGAWA" in text
    assert "112" in text
    assert "recovery position" in text.lower() or "gefe" in text.lower()

def test_whatsapp_yellow_fever_response():
    response = client.post(
        "/webhook/whatsapp",
        data={
            "Body": "Yaro na yana da zazzabi da zafin jiki tun kwana biyu, amma yana cin abinci.",
            "From": "+2348012345678",
            "To": "whatsapp:+14155238886"
        }
    )
    assert response.status_code == 200
    text = response.text
    assert "⚠️" in text
    assert "PHC" in text

def test_whatsapp_voice_note_received_prompt():
    response = client.post(
        "/webhook/whatsapp",
        data={
            "Body": "",
            "From": "+2348012345678",
            "To": "whatsapp:+14155238886",
            "NumMedia": "1",
            "MediaUrl0": "https://api.twilio.com/mock_audio.ogg"
        }
    )
    assert response.status_code == 200
    assert "An karbi muryarka" in response.text or "Voice note received" in response.text

def test_ivr_greet_endpoint():
    response = client.post(
        "/webhook/ivr/greet",
        data={"CallSid": "CA123456789", "From": "+2348012345678"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml"
    content = response.text
    assert "<Response>" in content
    assert "<Gather" in content
    assert 'action="/webhook/ivr/input"' in content
    assert "<Say" in content

def test_ivr_input_dtmf_emergency_shortcut():
    response = client.post(
        "/webhook/ivr/input",
        data={"Digits": "2", "CallSid": "CA123456789", "From": "+2348012345678"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml"
    content = response.text
    assert "112" in content
    assert "<Hangup/>" in content

def test_ivr_input_speech_triage():
    response = client.post(
        "/webhook/ivr/input",
        data={
            "SpeechResult": "Yaro yana da zazzabi da zafin jiki tun kwana biyu",
            "CallSid": "CA123456789",
            "From": "+2348012345678"
        }
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml"
    content = response.text
    assert "<Say" in content
    assert ("PHC" in content) or ("likita" in content.lower())

def test_ivr_status_callback():
    response = client.post(
        "/webhook/ivr/status",
        data={"CallSid": "CA123456789", "CallStatus": "completed", "From": "+2348012345678", "Duration": "45"}
    )
    assert response.status_code == 200
    assert response.json() == {"received": True}
