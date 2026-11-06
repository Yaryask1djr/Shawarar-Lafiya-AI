from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TriageTier(str, Enum):
    RED = "RED"       # Emergency / Gaggawa - Immediate referral to hospital/PHC
    YELLOW = "YELLOW" # Urgent / Gani Likita Cikin Sa'o'i 24 - Non-emergency clinical evaluation within 24h
    GREEN = "GREEN"   # Home Care / Kula a Gida - Supportive home care & monitoring

class AgeGroup(str, Enum):
    INFANT = "infant"           # 0 - 2 months (Special neonatal caution)
    YOUNG_CHILD = "young_child" # 2 months - 5 years (Standard WHO IMCI)
    CHILD = "child"             # 5 - 12 years
    ADOLESCENT = "adolescent"   # 12 - 18 years
    ADULT = "adult"             # 18+ years
    PREGNANT = "pregnant"       # Maternal health track

class PatientContext(BaseModel):
    age_group: Optional[AgeGroup] = AgeGroup.YOUNG_CHILD
    age_months: Optional[int] = Field(None, ge=0, le=1200, description="Patient age in months if known")
    is_pregnant: bool = False
    pregnancy_trimester: Optional[int] = Field(None, ge=1, le=3)
    user_location_lga: Optional[str] = Field(None, description="Local Government Area or State in Nigeria")

class SymptomTriageRequest(BaseModel):
    symptoms_text: str = Field(..., min_length=2, max_length=2000, description="Symptoms described in Hausa or English")
    language: str = Field(default="ha", description="'ha' for Hausa, 'en' for English")
    patient_context: Optional[PatientContext] = Field(default_factory=PatientContext)
    channel: str = Field(default="voicebot", description="Channel: 'ivr', 'whatsapp', 'web', 'chew_app'")

class RedFlagDetection(BaseModel):
    flag_id: str
    category: str
    severity: str = "CRITICAL"
    trigger_tokens: List[str]
    description_ha: str
    description_en: str
    immediate_instruction_ha: str
    immediate_instruction_en: str

class TriageResponse(BaseModel):
    tier: TriageTier
    tier_label_ha: str
    tier_label_en: str
    is_emergency: bool
    summary_ha: str
    summary_en: str
    primary_actions_ha: List[str]
    primary_actions_en: List[str]
    red_flags_detected: List[RedFlagDetection] = []
    blocked_prescriptions_found: List[str] = []
    clinical_disclaimer_ha: str
    clinical_disclaimer_en: str
    nearest_care_guidance_ha: str
    nearest_care_guidance_en: str
    metadata: Dict[str, Any] = {}

class ImmunizationQueryRequest(BaseModel):
    child_age_weeks: int = Field(..., ge=0, le=260, description="Child's age in weeks (0-5 years)")
    known_vaccines_received: List[str] = []
    language: str = "ha"

class VaccineMilestone(BaseModel):
    age_label: str
    vaccine_name: str
    disease_prevented_ha: str
    disease_prevented_en: str
    urgency: str

class ImmunizationQueryResponse(BaseModel):
    child_age_weeks: int
    vaccines_due_now: List[VaccineMilestone]
    upcoming_milestones: List[VaccineMilestone]
    guidance_ha: str
    guidance_en: str
    faq_answer_ha: Optional[str] = None

class AudioProcessResponse(BaseModel):
    success: bool
    transcription: str
    detected_language: str
    audio_duration_seconds: Optional[float] = None
    triage_result: Optional[TriageResponse] = None


# ---------------------------------------------------------------------------
# mRDT Image Interpretation
# ---------------------------------------------------------------------------
class MRDTBands(BaseModel):
    control_band: Optional[bool] = None
    test_band_1: Optional[bool] = None
    test_band_2: Optional[bool] = None

class MRDTInterpretationResponse(BaseModel):
    test_type_detected: str
    result: str                     # POSITIVE | NEGATIVE | INVALID | UNCLEAR
    confidence: str                 # HIGH | MEDIUM | LOW
    bands_visible: MRDTBands
    interpretation_ha: str
    interpretation_en: str
    clinical_action_ha: str
    clinical_action_en: str
    safety_note_ha: str
    safety_note_en: str
    image_quality: str              # GOOD | POOR | UNREADABLE


# ---------------------------------------------------------------------------
# Referral / PHC Routing
# ---------------------------------------------------------------------------
class ReferralQueryRequest(BaseModel):
    lat: float = Field(..., description="User latitude")
    lon: float = Field(..., description="User longitude")
    state_filter: Optional[str] = Field(None, description="Limit to a specific Nigerian state")
    level_filter: Optional[str] = Field(None, description="'PHC' | 'General Hospital' | 'Teaching Hospital'")
    language: str = Field(default="ha", description="'ha' | 'en'")
    max_results: int = Field(default=5, ge=1, le=20)

class PHCFacility(BaseModel):
    name: str
    lga: str
    state: str
    lat: float
    lon: float
    distance_km: float
    phone: Optional[str] = None
    level: str
    source: str
    maps_url: str

class ReferralQueryResponse(BaseModel):
    query_lat: float
    query_lon: float
    source: str
    facilities_found: int
    guidance_ha: str
    guidance_en: str
    facilities: List[PHCFacility]
