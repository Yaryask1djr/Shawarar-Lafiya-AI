"""
Medical Red Flag definitions, IMCI danger signs, and forbidden drug lexicons
for Hausa & English clinical triage safety guardrails.
"""

from typing import Dict, List, Any

# WHO IMCI & Maternal Emergency Red Flag Rules
RED_FLAG_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "flag_id": "RF_CONVULSION_SEIZURE",
        "category": "Neurological / Emergency",
        "severity": "CRITICAL",
        "trigger_tokens_ha": [
            "farfadiya", "farfadiyar", "karkarwa", "fita a hayyaci", "kikewa",
            "jiki yana karkarwa", "farfadiya yake yi", "farfadiya take yi", "kumbura idanu"
        ],
        "trigger_tokens_en": [
            "convulsion", "convulsing", "seizure", "seizures", "fit", "fits",
            "shaking uncontrollably", "eyes rolling back"
        ],
        "description_ha": "Alamomin farfadiya ko jijjiga a cikin yaro ko babba - alama ce mai hadarin gaske da ke bukatar kulawar gaggawa.",
        "description_en": "Presence of convulsions or seizures indicating severe cerebral malaria, meningitis, or febrile status.",
        "immediate_instruction_ha": "Gaggauta zuwa babban asibiti ko PHC mafi kusa yanzu. Kwantar da mara lafiyar a gefe (recovery position), kada ka sanya wani abu a bakinsa.",
        "immediate_instruction_en": "Go immediately to the nearest health facility. Lay patient on their side, keep airway clear, do NOT insert anything into mouth."
    },
    {
        "flag_id": "RF_UNCONSCIOUS_LETHARGIC",
        "category": "Neurological / General Danger Sign",
        "severity": "CRITICAL",
        "trigger_tokens_ha": [
            "sumamme", "sume", "rashin sanin kansa", "rashin sanin inda kansa yake",
            "ba ya motsi", "ba ta motsi", "nannauyan barci", "farka da kyar",
            "ba ya iya farkawa", "ba ta iya farkawa", "jiki ya mutu"
        ],
        "trigger_tokens_en": [
            "unconscious", "cannot wake up", "unresponsive", "lethargic", "coma",
            "floppy baby", "barely breathing", "not responding"
        ],
        "description_ha": "Mara lafiya ya suma ko yana cikin matsanancin nannauyan barci da ba ya iya farkawa.",
        "description_en": "Patient is unconscious, unresponsive, or abnormally lethargic (WHO General Danger Sign).",
        "immediate_instruction_ha": "Wannan matsanancin yanayi ne na gaggawa. Kai mara lafiyar cibiyar lafiya (PHC/Hospital) cikin hanzari.",
        "immediate_instruction_en": "Emergency danger sign. Seek immediate emergency transportation to the nearest primary healthcare clinic or hospital."
    },
    {
        "flag_id": "RF_CANNOT_DRINK_BREASTFEED",
        "category": "Pediatric / General Danger Sign",
        "severity": "CRITICAL",
        "trigger_tokens_ha": [
            "ba ya shan nono", "ba ta shan nono", "ya daina shan nono", "ta daina shan nono",
            "kasawar shan ruwa", "ba ya iya shan ruwa", "ba ta iya shan ruwa", "ya kasa shan komai"
        ],
        "trigger_tokens_en": [
            "unable to drink", "cannot breastfeed", "stopped suckling", "cannot swallow",
            "not feeding at all", "refuses all fluid"
        ],
        "description_ha": "Yaro ya kasa shan nono ko shan ruwa gaba daya - wannan babbar alamar hadari ce ta IMCI.",
        "description_en": "Child completely unable to drink or breastfeed, risking rapid severe dehydration and hypoglycemia.",
        "immediate_instruction_ha": "Kada ka tilasta zuba masa ruwa da karfi. Tafi da yaron zuwa asibiti nan take.",
        "immediate_instruction_en": "Do not force fluid down the throat. Take child to hospital immediately for medical evaluation."
    },
    {
        "flag_id": "RF_VOMITING_EVERYTHING",
        "category": "Pediatric / Gastrointestinal Danger Sign",
        "severity": "CRITICAL",
        "trigger_tokens_ha": [
            "amai da duk abin da", "amai da komai", "duk abin da ya ci sai ya amayar",
            "ba ya rike komai a ciki", "amai ba kakkautawa", "amai mai jini"
        ],
        "trigger_tokens_en": [
            "vomiting everything", "vomits all food and water", "cannot retain anything",
            "persistent vomiting", "vomiting blood"
        ],
        "description_ha": "Yaro yana amayar da dukkan abinci da ruwa da aka ba shi, ko yana amai mai jini.",
        "description_en": "Vomiting everything consumed (WHO IMCI danger sign) preventing oral rehydration.",
        "immediate_instruction_ha": "Kai yaron asibiti domin a duba shi a kuma ba shi ruwan leda (IV fluids) idan ya cancanta.",
        "immediate_instruction_en": "Seek immediate clinical care for potential IV fluid rehydration and medical stabilization."
    },
    {
        "flag_id": "RF_RESPIRATORY_DISTRESS",
        "category": "Respiratory / Pneumonia Danger Sign",
        "severity": "CRITICAL",
        "trigger_tokens_ha": [
            "shanyewar kirji", "faduwar kirji", "kirji na faduwa", "numfashi da kyar",
            "kugin kirji", "kugi a kirji", "shaƙuwa", "numfashi da sauri sosai",
            "lebe ya yi baki", "lebe ya canza launi"
        ],
        "trigger_tokens_en": [
            "chest indrawing", "stridor", "grunting", "gasping for air", "severe fast breathing",
            "blue lips", "cyanosis", "flaring nostrils"
        ],
        "description_ha": "Alamomin matsanancin ciwon huhu (Pneumonia) ko shanyewar kirji da wahalar numfashi.",
        "description_en": "Subcostal chest indrawing, stridor, or severe respiratory distress in pediatric patients.",
        "immediate_instruction_ha": "A tabbatar yaron yana samun isasshen iska (kada a rufe masa fuska). Gaggauta kai shi asibiti.",
        "immediate_instruction_en": "Keep airway open, do not constrict clothing or swaddle tightly. Transport urgently to clinic."
    },
    {
        "flag_id": "RF_MATERNAL_HEMORRHAGE",
        "category": "Maternal / Obstetric Emergency",
        "severity": "CRITICAL",
        "trigger_tokens_ha": [
            "zubar jini mai ciki", "zubar jini a lokacin ciki", "zubar jini bayan haihuwa",
            "jini yana zuba sosai", "bakin ciki da zubar jini", "kumburin fuska da ciwon kai mai tsanani"
        ],
        "trigger_tokens_en": [
            "bleeding in pregnancy", "postpartum bleeding", "heavy vaginal bleeding",
            "severe bleeding after delivery", "severe headache with blurry vision pregnant"
        ],
        "description_ha": "Zubar jini mai yawa ga mace mai ciki ko bayan haihuwa, ko alamomin cutar hawan jinin ciki (Pre-eclampsia/Eclampsia).",
        "description_en": "Antepartum/postpartum hemorrhage or signs of severe pre-eclampsia in pregnant/postpartum women.",
        "immediate_instruction_ha": "Wannan hadari ne ga rayuwar uwa da jariri! Gaggauta kaita babban asibiti ko PHC mai sashen haihuwa yanzu.",
        "immediate_instruction_en": "Life-threatening maternal obstetric emergency. Move immediately to a comprehensive emergency obstetric hospital."
    },
    {
        "flag_id": "RF_SEVERE_DEHYDRATION",
        "category": "Pediatric / Dehydration",
        "severity": "CRITICAL",
        "trigger_tokens_ha": [
            "idanu sun fada sosai", "fatar ciki bata komawa", "zawo ba kakkautawa",
            "babu hawaye idan yana kuka", "bakin ya bushe qeƙas"
        ],
        "trigger_tokens_en": [
            "sunken eyes severe", "skin pinch goes back very slowly", "no tears when crying",
            "mouth extremely dry", "cholera like diarrhea"
        ],
        "description_ha": "Alamomin matsananciyar asarar ruwan jiki sakamakon zawo da amai.",
        "description_en": "Severe dehydration signs: lethargic, sunken eyes, skin pinch retracts > 2 seconds.",
        "immediate_instruction_ha": "Idan yana iya shan ruwa, ci gaba da ba shi ruwan ORS (gishiri da sukari) a hanya yayin da ake kai shi asibiti.",
        "immediate_instruction_en": "If conscious and able to swallow, give frequent sips of ORS during immediate transit to PHC."
    }
]

# Prohibited Prescription Medications that the AI MUST NEVER PRESCRIBE autonomously
PROHIBITED_PRESCRIPTION_DRUGS: List[str] = [
    # Systemic Antibiotics
    "amoxicillin", "amoxil", "augmentin", "ampicillin", "tetracycline", "ciprofloxacin",
    "cipro", "metronidazole", "flagyl", "erythromycin", "azithromycin", "septrin",
    "co-trimoxazole", "chloramphenicol", "ceftriaxone", "gentamicin", "gentamycin",
    
    # Antimalarials (Must mandate RDT test first instead of autonomous diagnosis)
    "artemether", "lumefantrine", "coartem", "lonart", "artesunate", "maloxine",
    "quinine", "chloroquine",
    
    # Injections / Sedatives / High-risk Drugs
    "diclofenac injection", "promethazine", "diazepam", "tramadol", "codeine"
]

# Safe, Permitted Over-The-Counter Supportive Care Remedies
PERMITTED_SUPPORTIVE_CARE: Dict[str, Dict[str, str]] = {
    "ors": {
        "name_ha": "Ruwan Gishiri da Sukari (ORS)",
        "name_en": "Oral Rehydration Salts (ORS)",
        "purpose_ha": "Mayar da ruwan jiki da aka rasa sakamakon zawo ko amai.",
        "purpose_en": "Restores fluid and electrolytes lost through diarrhea or vomiting.",
        "preparation_ha": "Hada fakitin ORS daya a cikin litar ruwa mai tsabta guda daya. A sha a hankali bayan kowane zawo."
    },
    "zinc": {
        "name_ha": "Kwayoyin Zinc (Sin)",
        "name_en": "Zinc Sulfate Tablets (20mg for under-5)",
        "purpose_ha": "Taimaka wa 'ya'yan hanji su warke da kuma rage tsawon lokacin zawo a kananan yara.",
        "purpose_en": "Accelerates intestinal mucosa healing and shortens diarrheal episodes in children under 5.",
        "preparation_ha": "A narkar da kwaya 1 a cikin ruwan nono ko ruwa mai tsafta sau daya a rana tsawon kwanaki 10-14 (karkashin shawarar ma'aikacin lafiya)."
    },
    "paracetamol": {
        "name_ha": "Magungunan zazzabi na Paracetamol / Fannas",
        "name_en": "Paracetamol (Syrup/Drops for Children, Tablets for Adults)",
        "purpose_ha": "Rage radadin zazzabi da zafi na wucin gadi.",
        "purpose_en": "Symptomatic relief of fever and mild pain.",
        "preparation_ha": "Kada a wuce ka'ida; a bi bayanin da ke jikin marufin ko shawarar ma'aikacin PHC."
    }
}
