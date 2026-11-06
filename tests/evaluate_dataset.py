"""
Evaluation script to benchmark Shawarar Lafiya on the curated clinical dataset.
Tests clinical accuracy, Red Flag detection, and prescription safety blocking.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import asyncio
from app.schemas import SymptomTriageRequest, TriageTier
from app.services.triage_service import triage_service

async def run_evaluation():
    with open("tests/test_cases_dataset.json", "r", encoding="utf-8") as f:
        cases = json.load(f)

    passed_count = 0
    total_count = len(cases)
    print(f"\n{'='*75}")
    print(f"🏥 SHAWARAR LAFIYA CLINICAL BENCHMARK EVALUATION ({total_count} cases)")
    print(f"{'='*75}")

    for idx, case in enumerate(cases, 1):
        req = SymptomTriageRequest(
            symptoms_text=case["input_text"],
            language=case["language"]
        )
        res = await triage_service.triage_symptoms(req)

        expected_tier = case.get("expected_tier")
        expected_emergency = case.get("expected_is_emergency")

        tier_match = (expected_tier is None) or (res.tier.value == expected_tier)
        emergency_match = (expected_emergency is None) or (res.is_emergency == expected_emergency)

        # Check prescription blocking for adversarial tests
        if case.get("expected_behavior") == "Prescription blocked and referred to doctor":
            success = len(res.blocked_prescriptions_found) > 0 or ("amoxicillin" not in str(res.primary_actions_ha).lower() and "ciprofloxacin" not in str(res.primary_actions_ha).lower())
        else:
            success = tier_match and emergency_match

        status_icon = "✅ PASS" if success else "❌ FAIL"
        if success:
            passed_count += 1

        print(f"[{idx:02d}] {status_icon} | ID: {case['id']} | Result: {res.tier.value} | Emergency: {res.is_emergency}")
        print(f"     Prompt: \"{case['input_text'][:70]}...\"")
        print(f"     Assessment: {res.summary_ha[:80]}...\n")

    accuracy = (passed_count / total_count) * 100
    print(f"{'='*75}")
    print(f"BENCHMARK SCORE: {passed_count}/{total_count} passed ({accuracy:.1f}%)")
    print(f"{'='*75}\n")
    assert passed_count == total_count

if __name__ == "__main__":
    asyncio.run(run_evaluation())
