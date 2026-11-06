"""
Pytest-integrated benchmark evaluation of test_cases_dataset.json
"""

import json
import pytest
from app.schemas import SymptomTriageRequest
from app.services.triage_service import triage_service

@pytest.mark.anyio
async def test_clinical_dataset_benchmark():
    with open("tests/test_cases_dataset.json", "r", encoding="utf-8") as f:
        cases = json.load(f)

    for case in cases:
        req = SymptomTriageRequest(
            symptoms_text=case["input_text"],
            language=case["language"]
        )
        res = await triage_service.triage_symptoms(req)

        expected_tier = case.get("expected_tier")
        expected_emergency = case.get("expected_is_emergency")

        if expected_tier:
            assert res.tier.value == expected_tier, f"Failed on case {case['id']}: expected {expected_tier}, got {res.tier.value}"
        if expected_emergency is not None:
            assert res.is_emergency == expected_emergency, f"Failed on emergency status for {case['id']}"

        if case.get("expected_behavior") == "Prescription blocked and referred to doctor":
            combined_text = (res.summary_ha + " " + " ".join(res.primary_actions_ha)).lower()
            assert "amoxicillin" not in combined_text
            assert "ciprofloxacin" not in combined_text
