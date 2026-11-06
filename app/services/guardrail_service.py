"""
Clinical Guardrail Service for Shawarar Lafiya.
Enforces:
1. Pre-execution Red Flag Emergency Detection.
2. Post-execution Prescription Drug Filtering.
3. IMCI Danger Sign Override.
"""

import re
from typing import List, Tuple
from app.schemas import RedFlagDetection, TriageTier
from app.prompts.red_flag_definitions import (
    RED_FLAG_DEFINITIONS,
    PROHIBITED_PRESCRIPTION_DRUGS,
    PERMITTED_SUPPORTIVE_CARE
)

class GuardrailService:
    def __init__(self):
        self.red_flags = RED_FLAG_DEFINITIONS
        self.prohibited_drugs = set(d.lower() for d in PROHIBITED_PRESCRIPTION_DRUGS)

    def scan_for_red_flags(self, text: str, language: str = "ha") -> List[RedFlagDetection]:
        """
        Scans input clinical text for emergency danger signs across Hausa and English.
        """
        lowered_text = text.lower()
        detections: List[RedFlagDetection] = []

        for flag in self.red_flags:
            matched_tokens: List[str] = []
            
            # Check Hausa triggers
            for token in flag.get("trigger_tokens_ha", []):
                pattern = r'\b' + re.escape(token.lower()) + r'\b'
                if re.search(pattern, lowered_text):
                    matched_tokens.append(token)

            # Check English triggers
            for token in flag.get("trigger_tokens_en", []):
                pattern = r'\b' + re.escape(token.lower()) + r'\b'
                if re.search(pattern, lowered_text):
                    matched_tokens.append(token)

            if matched_tokens:
                detections.append(RedFlagDetection(
                    flag_id=flag["flag_id"],
                    category=flag["category"],
                    severity=flag["severity"],
                    trigger_tokens=list(set(matched_tokens)),
                    description_ha=flag["description_ha"],
                    description_en=flag["description_en"],
                    immediate_instruction_ha=flag["immediate_instruction_ha"],
                    immediate_instruction_en=flag["immediate_instruction_en"]
                ))

        return detections

    def sanitize_and_check_prescriptions(self, output_text: str) -> Tuple[str, List[str]]:
        """
        Verifies that no prohibited prescription medications (antibiotics, systemic antimalarials)
        are prescribed autonomously. Replaces forbidden references with safe clinic referral text.
        """
        detected_prescriptions: List[str] = []
        sanitized_text = output_text

        for drug in self.prohibited_drugs:
            pattern = r'\b' + re.escape(drug) + r'\b'
            if re.search(pattern, sanitized_text, flags=re.IGNORECASE):
                detected_prescriptions.append(drug)
                # Replace with guarded referral message
                replacement = f"[MAGANI: Ana bukatar gwajin jini a PHC kafin a bayar da wannan magani / Prescription blocked: Doctor evaluation required]"
                sanitized_text = re.sub(pattern, replacement, sanitized_text, flags=re.IGNORECASE)

        return sanitized_text, detected_prescriptions

    def build_emergency_override_response(self, red_flags: List[RedFlagDetection], language: str = "ha") -> dict:
        """
        Generates an instantaneous RED tier response bypassing any generative ambiguity.
        """
        flag_names_ha = "; ".join([f.description_ha for f in red_flags])
        flag_names_en = "; ".join([f.description_en for f in red_flags])
        
        actions_ha = [f.immediate_instruction_ha for f in red_flags]
        actions_ha.append("Gaggauta zuwa Cibiyar Lafiya ta Matakin Farko (PHC) ko Babban Asibiti mafi kusa yanzu.")
        
        actions_en = [f.immediate_instruction_en for f in red_flags]
        actions_en.append("Proceed immediately to the nearest Primary Healthcare Centre (PHC) or General Hospital.")

        return {
            "tier": TriageTier.RED,
            "tier_label_ha": "Gaggawa (Emergency)",
            "tier_label_en": "Emergency - Urgent Clinical Action",
            "is_emergency": True,
            "summary_ha": f"GARGADI NA GAGGAWA: An gano alamun hadari masu tsanani: {flag_names_ha}. Wannan yanayi na bukatar kulawar likita cikin gaggawa.",
            "summary_en": f"EMERGENCY WARNING: Severe danger signs detected: {flag_names_en}. This condition requires immediate clinical resuscitation or intervention.",
            "primary_actions_ha": actions_ha,
            "primary_actions_en": actions_en,
            "red_flags_detected": red_flags,
            "blocked_prescriptions_found": [],
            "clinical_disclaimer_ha": "Shawarar Lafiya na gano alamun hadari ne kawai; ba zai maye gurbin duba likita a dakin gaggawa ba.",
            "clinical_disclaimer_en": "Shawarar Lafiya identifies emergency triage indicators only; it is not a substitute for clinical emergency care.",
            "nearest_care_guidance_ha": "Kada ka bata lokaci a gida. Nemi sufurin gaggawa zuwa asibiti yanzu.",
            "nearest_care_guidance_en": "Do not delay with home care. Seek immediate transport to the nearest hospital."
        }

guardrail_service = GuardrailService()
