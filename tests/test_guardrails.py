"""
Unit tests for Shawarar Lafiya Clinical Guardrail Service.
"""

import pytest
from app.services.guardrail_service import guardrail_service
from app.schemas import TriageTier

def test_convulsion_red_flag_detection_hausa():
    text = "Yaro na yana ta farfadiya da karkarwa a jiki."
    detections = guardrail_service.scan_for_red_flags(text, language="ha")
    assert len(detections) >= 1
    flag_ids = [d.flag_id for d in detections]
    assert "RF_CONVULSION_SEIZURE" in flag_ids
    assert detections[0].severity == "CRITICAL"

def test_unconscious_red_flag_detection_english():
    text = "The patient is completely unconscious and cannot wake up."
    detections = guardrail_service.scan_for_red_flags(text, language="en")
    assert len(detections) >= 1
    flag_ids = [d.flag_id for d in detections]
    assert "RF_UNCONSCIOUS_LETHARGIC" in flag_ids

def test_chest_indrawing_pneumonia_detection():
    text = "Yarinya ta tana da shanyewar kirji kuma numfashi da kyar take yi."
    detections = guardrail_service.scan_for_red_flags(text, language="ha")
    flag_ids = [d.flag_id for d in detections]
    assert "RF_RESPIRATORY_DISTRESS" in flag_ids

def test_cannot_drink_or_breastfeed_danger_sign():
    text = "Jariri ya daina shan nono gaba daya."
    detections = guardrail_service.scan_for_red_flags(text, language="ha")
    flag_ids = [d.flag_id for d in detections]
    assert "RF_CANNOT_DRINK_BREASTFEED" in flag_ids

def test_maternal_hemorrhage_detection():
    text = "Ina da ciki kuma ga zubar jini a lokacin ciki tare da matsanancin ciwon kai."
    detections = guardrail_service.scan_for_red_flags(text, language="ha")
    flag_ids = [d.flag_id for d in detections]
    assert "RF_MATERNAL_HEMORRHAGE" in flag_ids

def test_safe_non_emergency_text_has_no_red_flags():
    text = "Ina da dan mura da atishawa amma ba zazzabi."
    detections = guardrail_service.scan_for_red_flags(text, language="ha")
    assert len(detections) == 0

def test_prohibited_antibiotic_prescription_sanitization():
    unsafe_text = "Ka sha amoxicillin 500mg ko ciprofloxacin sau biyu a rana."
    sanitized, blocked = guardrail_service.sanitize_and_check_prescriptions(unsafe_text)
    assert "amoxicillin" in blocked
    assert "ciprofloxacin" in blocked
    assert "amoxicillin" not in sanitized.lower()
    assert "ciprofloxacin" not in sanitized.lower()
    assert "MAGANI: Ana bukatar gwajin jini" in sanitized

def test_prohibited_antimalarial_prescription_sanitization():
    unsafe_text = "Je kemis ka sayi coartem ko lonart ka sha."
    sanitized, blocked = guardrail_service.sanitize_and_check_prescriptions(unsafe_text)
    assert "coartem" in blocked
    assert "lonart" in blocked

def test_emergency_override_response_structure():
    detections = guardrail_service.scan_for_red_flags("Yaro yana farfadiya", language="ha")
    override = guardrail_service.build_emergency_override_response(detections, language="ha")
    assert override["tier"] == TriageTier.RED
    assert override["is_emergency"] is True
    assert "Gaggawa" in override["tier_label_ha"]
    assert len(override["primary_actions_ha"]) > 0
