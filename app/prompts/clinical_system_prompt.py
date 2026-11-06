"""
Clinical System Prompts, IMCI decision rules, and NPHCDA Immunization schedules
for Shawarar Lafiya.
"""

from typing import Dict, Any, List

SHAWARAR_LAFIYA_SYSTEM_PROMPT = """
You are "Shawarar Lafiya" (Health Advice), a clinical primary healthcare triage and health guidance AI assistant serving Hausa-speaking rural families and Community Health Extension Workers (CHEWs) in Nigeria and West Africa.

CORE MISSION & ETHICAL ROLE:
- You are a TRIAGE DECISION-SUPPORT TOOL, NOT A DIAGNOSTIC DOCTOR.
- Your role is to assess symptoms, identify emergency danger signs, provide supportive home care when safe, and guide patients to Primary Healthcare Centres (PHCs) or General Hospitals at the right time.
- You must always communicate with warm cultural empathy, respect, and utmost clinical caution.

CLINICAL TRIAGE TIERS (WHO IMCI & NPHCDA STANDARDS):
1. RED (GAGGAWA / EMERGENCY):
   - Triggers: Any IMCI General Danger Sign (Convulsions/Farfadiya, Unconsciousness/Lethargy/Sumamme, Inability to drink or breastfeed, Vomiting everything), Respiratory Distress (chest indrawing/shanyewar kirji, stridor), Severe Dehydration (skin pinch >2s, sunken eyes), or Maternal Danger Signs (heavy bleeding/zubar jini, eclampsia, blurred vision with high blood pressure).
   - Mandatory Directive: Instantly instruct the caregiver/patient to proceed to the nearest PHC or General Hospital. Do not delay with home remedies.

2. YELLOW (GANI LIKITA CIKIN SA'O'I 24 / CLINICAL ASSESSMENT):
   - Triggers: Fever lasting > 24-48 hours without general danger signs, persistent cough without chest indrawing, diarrhea with mild thirst/fluid loss, localized skin rash or ear discharge.
   - Mandatory Directive: Instruct patient/caregiver to visit the PHC for testing (e.g., malaria Rapid Diagnostic Test - mRDT) within 24 hours. Advise on hydration and comfort in the interim.

3. GREEN (KULA A GIDA / SUPPORTIVE HOME CARE):
   - Triggers: Mild, self-limiting symptoms (early mild cold, teething irritability, simple loose stool with alert active child drinking normally).
   - Mandatory Directive: Provide safe supportive home care (ORS for hydration, zinc for under-5 diarrhea, continued breastfeeding/feeding, tepid sponging for fever). List clear WORSENING SIGNS that require immediate upgrade to RED/YELLOW.

CRITICAL GUARDRAIL RESTRICTIONS (NEVER VIOLATE):
- NEVER prescribe or recommend systemic prescription antibiotics (e.g., Amoxicillin, Ciprofloxacin, Metronidazole, Augmentin).
- NEVER autonomously diagnose malaria and prescribe Artemisinin-based Combination Therapy (ACT/Coartem) without clinical testing; always direct to PHC for an mRDT test first.
- Only supportive care is permitted: ORS (Ruwan gishiri da sukari), Zinc tablets (Sin) for diarrhea, and Paracetamol for fever relief.
- NEVER tell a parent or patient that their condition is "100% fine" or "nothing to worry about". Maintain professional vigilance.

OUTPUT FORMAT:
Your final output must strictly be valid JSON matching the following schema:
{
  "tier": "RED" | "YELLOW" | "GREEN",
  "tier_label_ha": "Gaggawa (Emergency) | Gani Likita (Clinical Visit) | Kula a Gida (Home Care)",
  "tier_label_en": "Emergency | Clinical Assessment | Home Care",
  "is_emergency": true | false,
  "summary_ha": "Clear Hausa explanation of the clinical assessment.",
  "summary_en": "Clear English translation of the assessment.",
  "primary_actions_ha": ["Action 1 in Hausa", "Action 2 in Hausa"],
  "primary_actions_en": ["Action 1 in English", "Action 2 in English"],
  "clinical_disclaimer_ha": "Shawarar Lafiya na taimakawa ne kawai da bayanan kiwon lafiya na farko; ba madadin ganin likita ko ma'aikacin asibitin PHC ba ne.",
  "clinical_disclaimer_en": "Shawarar Lafiya provides primary health triage guidance only; it is not a substitute for clinical examination by a qualified doctor or healthcare provider.",
  "nearest_care_guidance_ha": "Idan alamomin suka tsananta, gaggauta zuwa Cibiyar Lafiya ta Matakin Farko (PHC) mafi kusa.",
  "nearest_care_guidance_en": "If symptoms worsen, proceed immediately to your nearest Primary Healthcare Centre (PHC)."
}
"""

# Nigeria NPHCDA Routine Immunization Schedule
NIGERIA_ROUTINE_IMMUNIZATION_SCHEDULE: List[Dict[str, Any]] = [
    {
        "age_weeks": 0,
        "age_label": "At Birth (Haihuwa)",
        "vaccines": [
            {
                "vaccine_name": "BCG",
                "disease_prevented_ha": "Ciwon Fuka da Tarin Fuka (Tuberculosis)",
                "disease_prevented_en": "Tuberculosis",
                "urgency": "High"
            },
            {
                "vaccine_name": "OPV 0",
                "disease_prevented_ha": "Cutar Shan-Inna (Polio)",
                "disease_prevented_en": "Polio (Birth dose)",
                "urgency": "High"
            },
            {
                "vaccine_name": "Hepatitis B 0",
                "disease_prevented_ha": "Ciwon Hanta (Hepatitis B)",
                "disease_prevented_en": "Hepatitis B birth dose",
                "urgency": "High"
            }
        ]
    },
    {
        "age_weeks": 6,
        "age_label": "6 Weeks (Makonni 6)",
        "vaccines": [
            {
                "vaccine_name": "Penta 1",
                "disease_prevented_ha": "Ciwon Hanta, Tarin Shika, Makoko, Tsananin zazzabi da Ciwon Kwayar Ido (5-in-1)",
                "disease_prevented_en": "Diphtheria, Pertussis, Tetanus, Hep B, Hib (Pentavalent)",
                "urgency": "High"
            },
            {
                "vaccine_name": "OPV 1",
                "disease_prevented_ha": "Cutar Shan-Inna (Polio dose 1)",
                "disease_prevented_en": "Polio dose 1",
                "urgency": "High"
            },
            {
                "vaccine_name": "PCV 1",
                "disease_prevented_ha": "Ciwon Huhu (Pneumonia) da Ciwon Kunne",
                "disease_prevented_en": "Pneumococcal Conjugate Vaccine 1",
                "urgency": "High"
            },
            {
                "vaccine_name": "Rotavirus 1",
                "disease_prevented_ha": "Zawo mai zafi mai sanadin kwayar cutar Rota (Rotavirus diarrhea)",
                "disease_prevented_en": "Rotavirus Diarrhea dose 1",
                "urgency": "High"
            }
        ]
    },
    {
        "age_weeks": 10,
        "age_label": "10 Weeks (Makonni 10)",
        "vaccines": [
            {
                "vaccine_name": "Penta 2",
                "disease_prevented_ha": "Kariyar Pentavalent karo na biyu",
                "disease_prevented_en": "Pentavalent dose 2",
                "urgency": "High"
            },
            {
                "vaccine_name": "OPV 2",
                "disease_prevented_ha": "Cutar Shan-Inna (Polio dose 2)",
                "disease_prevented_en": "Polio dose 2",
                "urgency": "High"
            },
            {
                "vaccine_name": "PCV 2",
                "disease_prevented_ha": "Ciwon Huhu (Pneumonia dose 2)",
                "disease_prevented_en": "Pneumococcal dose 2",
                "urgency": "High"
            },
            {
                "vaccine_name": "Rotavirus 2",
                "disease_prevented_ha": "Rotavirus zawo karo na biyu",
                "disease_prevented_en": "Rotavirus dose 2",
                "urgency": "High"
            }
        ]
    },
    {
        "age_weeks": 14,
        "age_label": "14 Weeks (Makonni 14)",
        "vaccines": [
            {
                "vaccine_name": "Penta 3",
                "disease_prevented_ha": "Kariyar Pentavalent karo na uku",
                "disease_prevented_en": "Pentavalent dose 3",
                "urgency": "High"
            },
            {
                "vaccine_name": "OPV 3 & IPV 1",
                "disease_prevented_ha": "Cutar Shan-Inna (Polio dose 3 + Allurar rigakafin Polio)",
                "disease_prevented_en": "Oral & Inactivated Polio Vaccine",
                "urgency": "High"
            },
            {
                "vaccine_name": "PCV 3",
                "disease_prevented_ha": "Ciwon Huhu (Pneumonia dose 3)",
                "disease_prevented_en": "Pneumococcal dose 3",
                "urgency": "High"
            },
            {
                "vaccine_name": "Rotavirus 3",
                "disease_prevented_ha": "Rotavirus zawo karo na uku",
                "disease_prevented_en": "Rotavirus dose 3",
                "urgency": "High"
            }
        ]
    },
    {
        "age_weeks": 36,  # 9 months
        "age_label": "9 Months (Watan 9)",
        "vaccines": [
            {
                "vaccine_name": "Measles 1 (Kyanda)",
                "disease_prevented_ha": "Ciwon Kyanda (Measles)",
                "disease_prevented_en": "Measles dose 1",
                "urgency": "Critical"
            },
            {
                "vaccine_name": "Yellow Fever (Zazzabin Rawaya)",
                "disease_prevented_ha": "Zazzabin Rawaya",
                "disease_prevented_en": "Yellow Fever",
                "urgency": "Critical"
            },
            {
                "vaccine_name": "Meningitis A (Sankarau)",
                "disease_prevented_ha": "Ciwon Sankarau",
                "disease_prevented_en": "Meningococcal A Conjugate",
                "urgency": "Critical"
            }
        ]
    },
    {
        "age_weeks": 60,  # 15 months
        "age_label": "15 Months (Watan 15)",
        "vaccines": [
            {
                "vaccine_name": "Measles 2 (Kyanda karo na 2)",
                "disease_prevented_ha": "Kyanda kashi na biyu domin cikakkiyar kariya",
                "disease_prevented_en": "Measles second dose",
                "urgency": "High"
            }
        ]
    }
]
