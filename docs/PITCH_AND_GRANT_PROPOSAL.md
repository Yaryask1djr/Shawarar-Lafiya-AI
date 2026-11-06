# 📑 Project Proposal & Pitch: Shawarar Lafiya
### AI-Powered Primary Health & Routine Immunization Voice Triage for Hausa-Speaking Rural Communities

**Target Grant / Pitch Tracks:** 
- Bill & Melinda Gates Foundation (Grand Challenges: AI for Global Health)
- Wellcome Trust / USAID Digital Health Innovations
- National Primary Health Care Development Agency (NPHCDA) Innovation Challenge

---

## 1. Executive Summary

**The Challenge:** In Northern Nigeria and the wider Sahel region, over 50 million people speak Hausa as a primary language, with adult female literacy in rural regions frequently below 25%. Under-5 mortality remains among the highest globally (114 deaths per 1,000 live births in Nigeria), driven largely by preventable diseases: malaria, diarrhea with dehydration, pneumonia, and vaccine-preventable infections (measles, diphtheria, polio). Caregivers frequently face the "three delays" model of maternal/infant mortality: (1) delay in deciding to seek care due to low health literacy or inability to read clinic brochures, (2) delay in reaching care due to geographical distance and transport costs, and (3) delay in receiving adequate care.

**The Solution:** **Shawarar Lafiya** (*"Health Advice"*) is an intelligent, voice-first primary healthcare triage and routine immunization guidance system. Accessible via feature-phone telephony (IVR/toll-free GSM) and WhatsApp voice notes, it allows non-literate mothers and frontline Community Health Extension Workers (CHEWs) to describe symptoms verbally in natural, conversational Hausa.

**Clinical Safety Innovation:** Unlike generic conversational chatbots that risk medical hallucination, Shawarar Lafiya employs a multi-layered clinical guardrail architecture grounded in the **World Health Organization's Integrated Management of Childhood Illness (WHO IMCI)** protocols. It enforces hard-coded red-flag emergency bypasses for life-threatening conditions (e.g., convulsions, stridor, maternal hemorrhage) and strictly blocks the autonomous prescribing of systemic prescription medications, acting purely as an empathetic, safe triage decision-support tool.

---

## 2. Problem Statement & Ground Reality

### The Northern Nigerian Context
1. **The Literacy Gap:** Most existing digital health applications rely on SMS, mobile apps, or English chatbots. For a mother in rural Kano, Jigawa, Sokoto, or Katsina, text-based interfaces are inaccessible.
2. **Zero-Dose Children:** Nigeria accounts for approximately 2.2 million "zero-dose" children (children who have not received a single routine vaccine). Cultural misconceptions, vaccine hesitancy, and lack of schedule visibility represent major bottlenecks.
3. **Overburdened Primary Healthcare:** When rural families do visit Primary Healthcare Centres (PHCs), facilities are often staffed by solitary CHEWs managing long queues. A reliable triage copilot empowers CHEWs to quickly prioritize emergency cases.
4. **The Hazard of Unregulated Self-Medication:** Patent and Proprietary Medicine Vendors (PPMVs / "chemists") often dispense systemic antibiotics or inappropriate injections without diagnostic testing, exacerbating antimicrobial resistance (AMR).

---

## 3. Product Overview & Key Capabilities

```
+----------------------------------------------------------------------------+
|                              SHAWARAR LAFIYA                               |
+----------------------------------------------------------------------------+
|  [Channel 1: Toll-Free IVR / GSM]    |  [Channel 2: WhatsApp Voice Notes]  |
|  For low-cost feature phone owners   |  For smartphone users & rural CHEWs |
+--------------------------------------+-------------------------------------+
                                   │
                                   ▼
             [ HAUSA NATURAL SPEECH UNDERSTANDING (ASR) ]
                                   │
                                   ▼
        +─────────────────────────────────────────────────────────+
        |                 CLINICAL SAFETY ENGINE                  |
        |  1. WHO IMCI General Danger Sign Detector (Instant RED) |
        |  2. Prescription & Antibiotic Blocking Guardrail        |
        |  3. NPHCDA Routine Immunization Milestone Tracker       |
        +─────────────────────────────────────────────────────────+
                                   │
                                   ▼
          [ HAUSA VOICE RESPONSE (TTS) & LOCAL PHC REFERRAL ]
```

### Module 1: Pediatric & Maternal Symptom Triage
- **IMCI Danger Signs First:** Checks for convulsions (*farfadiya*), inability to drink/breastfeed (*kasawar shan nono*), persistent vomiting (*amai da komai*), and chest indrawing (*shanyewar kirji*).
- **Three-Tier Action Plans:**
  - 🔴 **Red (Gaggawa):** Immediate emergency transfer guidance.
  - 🟡 **Yellow (Gani Likita Cikin Sa'o'i 24):** Guidance to visit PHC for malaria mRDT blood tests and clinical diagnosis.
  - 🟢 **Green (Kula a Gida):** Safe home supportive care (ORS/Zinc, continued breastfeeding, tepid sponging).

### Module 2: Routine Immunization (RI) & Zero-Dose Elimination
- **Milestone Calculator:** Caregivers state their baby's age in weeks or months; Shawarar Lafiya outputs the exact free vaccines due according to the NPHCDA national calendar.
- **Cultural Myth Busting:** Addresses common rumors (e.g., vaccine safety, fever reactions) in culturally respectful Hausa idioms (*"Allurar rigakafi garkuwar rayuwa ce"*).

### Module 3: CHEW Copilot
- Frontline community workers use the voice assistant during household outreach to corroborate triage decisions and calculate catch-up immunization windows for missed doses.

---

## 4. Technical Architecture & Innovation

1. **Speech Recognition (ASR):** Utilizes fine-tuned acoustic models for Hausa (Google Cloud Speech-to-Text `ha-NG` and fine-tuned open-weight Whisper models) trained on accented Northern Nigerian dialectal variations.
2. **Deterministic-First Clinical Engine:** Prioritizes deterministic medical state machines for red flags before invoking generative models, eliminating latency during critical emergencies.
3. **Zero-Egress Data Protection:** Compliant with the Nigeria Data Protection Act (NDPA 2023) and clinical data privacy standards. Sensitive patient audio is transcribed in-memory without persistent recording of identifiable biometrics.

---

## 5. Implementation Roadmap & Milestones (12-Month Plan)

```
Month 1 - 3: Baseline & Dataset Hardening
├── Clinical validation of Hausa symptom lexicons with Northern Nigerian pediatricians
├── Deployment of toll-free IVR number pilot in 2 target LGAs (e.g., Kano and Kaduna)
└── Integration of SMS/WhatsApp gateway via Africa's Talking

Month 4 - 6: Controlled Community Pilot
├── Rollout to 150 Community Health Extension Workers (CHEWs)
├── Pilot cohort of 5,000 rural mothers/caregivers
└── Continuous auditing of triage safety with local Clinical Advisory Board

Month 7 - 9: Evaluation & Model Refinement
├── Rigorous comparison of AI triage recommendations against in-person PHC doctor reviews
├── Measurement of zero-dose vaccine uptake improvement in pilot communities
└── Optimization of offline-edge model for rural tablet deployment

Month 10 - 12: Scaling & Public Health Hand-off
├── Integration with NPHCDA and State Primary Health Care Development Agencies (SPHCDA)
└── Scaling to 50,000 active monthly callers across Northern Nigeria
```

---

## 6. Budget & Resource Allocation ($150,000 Grant Model)

| Category | Description | Amount (USD) |
| :--- | :--- | :--- |
| **Clinical Advisory & Validation** | Honoraria for Nigerian pediatricians, OB-GYNs, and CHEW trainers for protocol review | $25,000 |
| **Telephony & Cloud Infrastructure** | Toll-free GSM IVR lines (Africa's Talking / local telcos: MTN, Airtel), ASR & cloud servers | $35,000 |
| **Field Pilot & CHEW Training** | Training workshops, device stipends for 150 CHEWs across target local government areas | $40,000 |
| **Engineering & AI Alignment** | Speech pipeline optimization, safety red-teaming, guardrail engineering, mobile app UI | $35,000 |
| **Monitoring, Evaluation & Audit** | Independent public health impact assessment and clinical safety auditing | $15,000 |
| **Total** | | **$150,000** |

---

## 7. Anticipated Public Health Impact & Success Metrics

- **Zero-Dose Reduction:** 30%+ increase in on-time routine immunization completion among registered cohorts.
- **Triage Safety Rate:** >99.5% accuracy in flagging WHO IMCI General Danger Signs and obstetric emergencies during clinical validation.
- **Healthcare Cost Reduction:** Significant decrease in unnecessary out-of-pocket spending on unprescribed antibiotics and substandard patent medications.
- **Early Referral Rate:** 40% reduction in the first delay (delay in deciding to seek clinical care for severe pneumonia and cerebral malaria).

---

## 8. Conclusion & Pitch Deck Takeaway

> *"Shawarar Lafiya bridges the catastrophic divide between world-class clinical triage protocols and the rural mother who cannot read a medical poster. By transforming any basic mobile phone into an empathetic, safe, Hausa-speaking health triage voice assistant, we turn timely medical intervention from a privilege into an accessible fundamental right."*
