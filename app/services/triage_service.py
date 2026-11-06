"""
Clinical Triage Orchestration Engine.
Coordinates Guardrails, WHO IMCI logic, NPHCDA Immunization schedules,
and LLM/Deterministic triage execution.

Pipeline priority:
  1. Pre-execution red-flag scan (always — bypasses everything if RED)
  2. Gemini 2.5 Flash LLM triage (if GEMINI_API_KEY is set and call succeeds)
  3. Deterministic WHO IMCI rule engine (fallback, always available offline)
  4. Post-execution prescription guardrail (always)
"""

import re
import logging
from typing import Dict, Any, List
from app.config import settings
from app.schemas import (
    SymptomTriageRequest,
    TriageResponse,
    TriageTier,
    ImmunizationQueryRequest,
    ImmunizationQueryResponse,
    VaccineMilestone
)
from app.services.guardrail_service import guardrail_service
from app.services.gemini_service import gemini_service
from app.prompts.clinical_system_prompt import (
    SHAWARAR_LAFIYA_SYSTEM_PROMPT,
    NIGERIA_ROUTINE_IMMUNIZATION_SCHEDULE
)

logger = logging.getLogger(__name__)

class TriageService:
    def __init__(self):
        self.schedule = NIGERIA_ROUTINE_IMMUNIZATION_SCHEDULE

    def _has_symptom(self, text: str, keywords: List[str]) -> bool:
        """
        Detects if symptom keywords are present, properly accounting for negation
        in both Hausa ('ba zazzabi', 'babu zazzabi') and English ('no fever').
        """
        negation_prefix = r'\b(?:ba|babu|ba\s+ya\s+da|ba\s+ta\s+da|ba\s+wata|babu\s+wani|babu\s+alamar|no|without|not|denies)\s+(?:\w+\s+)?'
        for kw in keywords:
            pattern = r'\b' + re.escape(kw) + r'\b'
            for match in re.finditer(pattern, text):
                start = max(0, match.start() - 30)
                window = text[start:match.end()]
                if not re.search(negation_prefix + re.escape(kw), window):
                    return True
        return False

    async def triage_symptoms(self, request: SymptomTriageRequest) -> TriageResponse:
        """
        Main clinical triage pipeline:
        Step 1: Check Pre-execution Red Flags (Emergency Bypass — always first)
        Step 2a: Gemini 2.5 Flash LLM triage (if API key configured)
        Step 2b: Deterministic WHO IMCI rule engine (offline fallback)
        Step 3: Post-execution prescription filter & output sanitization
        """
        text = request.symptoms_text
        lang = request.language

        # -------------------------------------------------------------
        # STEP 1: PRE-EXECUTION RED FLAG SCAN (non-negotiable bypass)
        # -------------------------------------------------------------
        red_flags = guardrail_service.scan_for_red_flags(text, language=lang)
        if red_flags:
            override_data = guardrail_service.build_emergency_override_response(red_flags, language=lang)
            return TriageResponse(**override_data)

        # -------------------------------------------------------------
        # STEP 2a: GEMINI 2.5 FLASH LLM (if available)
        # -------------------------------------------------------------
        triage_dict = None
        triage_source = "imci_deterministic"

        if gemini_service.is_available:
            context_dict = None
            if request.patient_context:
                context_dict = request.patient_context.model_dump()
            llm_result = await gemini_service.run_triage(
                symptoms_text=text,
                language=lang,
                patient_context=context_dict,
            )
            if llm_result is not None:
                # Inject defaults for optional schema fields Gemini may omit
                llm_result.setdefault("red_flags_detected", [])
                llm_result.setdefault("blocked_prescriptions_found", [])
                # Coerce tier to enum
                llm_result["tier"] = TriageTier(llm_result["tier"])
                triage_dict = llm_result
                triage_source = "gemini_2.5_flash"
                logger.info("Using Gemini 2.5 Flash triage result.")

        # -------------------------------------------------------------
        # STEP 2b: DETERMINISTIC IMCI FALLBACK
        # -------------------------------------------------------------
        if triage_dict is None:
            triage_dict = self._evaluate_imci_rules(request)
            logger.info("Using deterministic IMCI rule engine (Gemini unavailable or failed).")

        # Tag the source in metadata
        triage_dict["metadata"] = {"triage_source": triage_source}

        # -------------------------------------------------------------
        # STEP 3: POST-EXECUTION PRESCRIPTION GUARDRAIL
        # -------------------------------------------------------------
        raw_summary = triage_dict.get("summary_ha", "") + " " + triage_dict.get("summary_en", "")
        for act in triage_dict.get("primary_actions_ha", []) + triage_dict.get("primary_actions_en", []):
            raw_summary += " " + act

        _, blocked_drugs = guardrail_service.sanitize_and_check_prescriptions(raw_summary)

        cleaned_actions_ha = [
            guardrail_service.sanitize_and_check_prescriptions(act)[0]
            for act in triage_dict.get("primary_actions_ha", [])
        ]
        cleaned_actions_en = [
            guardrail_service.sanitize_and_check_prescriptions(act)[0]
            for act in triage_dict.get("primary_actions_en", [])
        ]

        triage_dict["primary_actions_ha"] = cleaned_actions_ha
        triage_dict["primary_actions_en"] = cleaned_actions_en
        triage_dict["blocked_prescriptions_found"] = blocked_drugs

        return TriageResponse(**triage_dict)

    def _evaluate_imci_rules(self, request: SymptomTriageRequest) -> Dict[str, Any]:
        """
        High-fidelity deterministic WHO IMCI & primary care rule engine.
        Evaluates fever, diarrhea, respiratory complaints, and general discomfort.
        """
        text = request.symptoms_text.lower()
        context = request.patient_context

        # Diarrhea / Loose stool check
        has_diarrhea = self._has_symptom(text, ["zawo", "diarrhea", "loose stool", "gudawa", "bakin ciki"])
        # Fever check
        has_fever = self._has_symptom(text, ["zazzabi", "fever", "zafin jiki", "temperature", "hot body", "jiki da zafi"])
        # Cough / Respiratory check
        has_cough = self._has_symptom(text, ["tari", "cough", "mura", "catarrh", "majina"])
        # Duration indicators
        is_prolonged = any(w in text for w in ["kwanaki", "kwana uku", "kwana biyu", "three days", "two days", "days", "mako"])

        # Category: Urgent Clinical Assessment (YELLOW)
        if has_fever or (has_diarrhea and is_prolonged) or is_prolonged:
            return {
                "tier": TriageTier.YELLOW,
                "tier_label_ha": "Gani Likita Cikin Sa'o'i 24 (Clinical Assessment)",
                "tier_label_en": "Urgent Clinical Visit (Within 24 Hours)",
                "is_emergency": False,
                "summary_ha": "Akwai bukatar ganin ma'aikacin lafiya a PHC domin auna zazzabi da kuma yin gwajin jini na cutar cizon sauro (mRDT).",
                "summary_en": "Clinical assessment required at a Primary Healthcare Centre within 24 hours to test for malaria (mRDT) and evaluate the infection.",
                "primary_actions_ha": [
                    "Kai mara lafiyar cibiyar PHC mafi kusa domin gwajin mRDT kafin a fara kowane magani.",
                    "Ci gaba da ba shi ruwan sha da abinci akai-akai domin karfin jiki.",
                    "Idan zafin jiki ya yi yawa, shafa masa ruwa mai dumi-dumi a jiki (tepid sponging) da amfani da Paracetamol daidai da ka'ida."
                ],
                "primary_actions_en": [
                    "Visit the nearest PHC for a rapid diagnostic test (mRDT) before giving any antimalarial medications.",
                    "Maintain continuous hydration, breastfeeding, and frequent light meals.",
                    "Apply lukewarm water sponging for fever comfort, and administer safe age-appropriate Paracetamol as directed by PHC staff."
                ],
                "red_flags_detected": [],
                "blocked_prescriptions_found": [],
                "clinical_disclaimer_ha": "Shawarar Lafiya na taimakawa ne kawai da jagorar kiwon lafiya; ba zai maye gurbin gwajin asibiti ba.",
                "clinical_disclaimer_en": "Shawarar Lafiya is an informational triage aid and does not replace medical laboratory testing or physician examination.",
                "nearest_care_guidance_ha": "Ziyarci cibiyar lafiya ta PHC mafi kusa da kai a yau.",
                "nearest_care_guidance_en": "Visit your nearest local Primary Healthcare Centre today."
            }

        # Category: Diarrhea without severe dehydration (GREEN or YELLOW)
        if has_diarrhea:
            return {
                "tier": TriageTier.GREEN,
                "tier_label_ha": "Kula a Gida (Supportive Home Care)",
                "tier_label_en": "Supportive Home Care & Monitoring",
                "is_emergency": False,
                "summary_ha": "Alamun zawo ne mai sauki ba tare da alamun matsanancin hadari ba. Babban aikin shine mayar da ruwan da aka rasa.",
                "summary_en": "Mild diarrhea without acute general danger signs. Primary goal is fluid replacement to prevent dehydration.",
                "primary_actions_ha": [
                    "Hada ruwan gishiri da sukari (ORS) a litar ruwa mai tsabta, a rika ba shi bayan kowane zawo.",
                    "Ba yaro kwayoyin Zinc (Sin) na tsawon kwanaki 10-14 domin gina 'ya'yan hanji.",
                    "Kada ka dakatar da nono ko abinci. Idan ya fara amai da komai ko ya kasa shan ruwa, je asibiti nan take."
                ],
                "primary_actions_en": [
                    "Prepare and administer Oral Rehydration Salts (ORS) solution after every loose bowel movement.",
                    "Give Zinc supplementation daily for 10-14 days to rebuild the intestinal lining (for under-5s).",
                    "Do NOT stop breastfeeding or feeding. Escalate immediately to hospital if child vomits everything or stops drinking."
                ],
                "red_flags_detected": [],
                "blocked_prescriptions_found": [],
                "clinical_disclaimer_ha": "Wannan shawarar gida ce ta farko. Idan an ga alamun kasala ko idanu sun fada, a garzaya asibiti.",
                "clinical_disclaimer_en": "Supportive guidance only. Seek urgent clinical care if sunken eyes, lethargy, or extreme thirst develop.",
                "nearest_care_guidance_ha": "Kula da yaro a gida, amma ka san inda PHC take idan yanayin ya canza.",
                "nearest_care_guidance_en": "Monitor at home and remain prepared to visit the PHC if worsening signs appear."
            }

        # Default Mild / Common Cold (GREEN)
        return {
            "tier": TriageTier.GREEN,
            "tier_label_ha": "Kula a Gida (Supportive Home Care)",
            "tier_label_en": "Supportive Home Care",
            "is_emergency": False,
            "summary_ha": "Alamomin sun nuna mura ce mai sauki ko gajiya wadda ba ta bukatar kwayoyin rigakafi (antibiotics).",
            "summary_en": "Symptoms suggest a mild self-limiting upper respiratory infection or discomfort not requiring antibiotics.",
            "primary_actions_ha": [
                "Samar da isasshen hutu da ruwa ko romo mai dumi.",
                "Ci gaba da shayar da nonon uwa idan jariri ne.",
                "Kula da alamun tsanani: idan numfashi ya yi sauri sosai ko kirji na faduwa, a je asibiti nan take."
            ],
            "primary_actions_en": [
                "Ensure plenty of rest and warm fluids/hydration.",
                "Continue frequent breastfeeding if patient is an infant.",
                "Watch vigilantly for danger signs: if rapid breathing or chest indrawing occurs, seek hospital care immediately."
            ],
            "red_flags_detected": [],
            "blocked_prescriptions_found": [],
            "clinical_disclaimer_ha": "Shawarar Lafiya jagora ce ta farko; ba madadin likita ba ne.",
            "clinical_disclaimer_en": "Primary triage guide only; not a formal medical diagnosis.",
            "nearest_care_guidance_ha": "Za a iya tuntubar ma'aikacin lafiya (CHEW) na unguwa idan akwai tambaya.",
            "nearest_care_guidance_en": "Contact your local Community Health Extension Worker (CHEW) if symptoms persist."
        }

    def query_immunization(self, request: ImmunizationQueryRequest) -> ImmunizationQueryResponse:
        """
        Determines current and upcoming routine vaccines based on child's age in weeks.
        """
        child_weeks = request.child_age_weeks
        due_now: List[VaccineMilestone] = []
        upcoming: List[VaccineMilestone] = []

        for milestone in self.schedule:
            m_weeks = milestone["age_weeks"]
            for v in milestone["vaccines"]:
                vm = VaccineMilestone(
                    age_label=milestone["age_label"],
                    vaccine_name=v["vaccine_name"],
                    disease_prevented_ha=v["disease_prevented_ha"],
                    disease_prevented_en=v["disease_prevented_en"],
                    urgency=v["urgency"]
                )
                # Check if due now (+/- 2 weeks window)
                if abs(child_weeks - m_weeks) <= 2 or (child_weeks >= m_weeks and v["vaccine_name"] not in request.known_vaccines_received and child_weeks < m_weeks + 6):
                    due_now.append(vm)
                elif m_weeks > child_weeks:
                    upcoming.append(vm)

        guidance_ha = (
            f"Allurar rigakafi kyauta ce a kowace cibiyar PHC a fadin Najeriya. "
            f"Tana kare yaro daga cututtuka masu kisa kamar Polio, Ciwon Huhu, da Kyanda."
        )
        guidance_en = (
            f"Routine vaccines are free at all Primary Healthcare Centres in Nigeria. "
            f"They build robust immunity against polio, measles, pneumonia, and hepatitis."
        )

        return ImmunizationQueryResponse(
            child_age_weeks=child_weeks,
            vaccines_due_now=due_now,
            upcoming_milestones=upcoming[:3],
            guidance_ha=guidance_ha,
            guidance_en=guidance_en,
            faq_answer_ha="Allurar rigakafi tana da aminci sosai. Dan zazzabi ko kukan yaro bayan allura alama ce da ke nuna garkuwar jikinsa na aiki."
        )

triage_service = TriageService()
