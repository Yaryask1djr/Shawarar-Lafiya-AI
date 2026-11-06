# 🩺 Shawarar Lafiya (*"Health Advice"*)
### Primary Health & Symptom Triage Voicebot in Hausa — v1.1.0

An AI-driven, voice-first primary health symptom triage and immunization guidance platform designed for **rural caregivers, pregnant mothers, and frontline Community Health Extension Workers (CHEWs)** across Northern Nigeria and the Hausa-speaking Sahel (50M+ speakers).

---

## 🌟 Key Highlights

- **Voice-First in Hausa:** Supports oral descriptions of pediatric and maternal symptoms via WhatsApp Audio notes and IVR Telephony for non-literate and rural feature-phone users.
- **Strict Clinical Guardrails:** Hard-coded detection of **WHO IMCI (Integrated Management of Childhood Illness)** General Danger Signs and obstetric emergencies. Bypasses all generative delays during life-threatening red flags.
- **Autonomous Prescription Blocker:** Strictly prohibits autonomous prescription of systemic antibiotics (e.g., Amoxicillin, Ciprofloxacin) or ungrounded antimalarials — directing patients to PHCs for mRDT testing.
- **Dual Triage Engine:** Uses **Gemini 2.5 Flash** (when `GEMINI_API_KEY` is set) for richly contextual bilingual reasoning, with deterministic WHO IMCI rules as a fully self-contained offline fallback.
- **WhatsApp & IVR Webhooks:** Twilio-compatible endpoints for WhatsApp Business and feature-phone IVR voice calls — including TwiML `<Gather>` speech recognition and DTMF emergency shortcut (press 2 → 112).
- **Routine Immunization Tracker:** NPHCDA-aligned milestone calculations from birth to 15 months, with culturally empathetic Hausa myth-busting.
- **33 Tests Passing:** Full automated clinical benchmark suite covering guardrails, triage tiers, Gemini mock integration, Twilio webhooks, and IVR flows.

---

## 🏗️ System Architecture

```
   [ 📱 WhatsApp Business ]  [ 📞 IVR Feature Phone ]  [ 🌐 Web UI ]
              │                        │                      │
              ▼                        ▼                      ▼
   POST /webhook/whatsapp    POST /webhook/ivr/greet    GET /ui
              │               → <Gather> speech/DTMF        │
              └────────────────────────┬────────────────────-┘
                                       ▼
                        [ ASR: Hausa Speech-to-Text ]
                              (stub / Google STT)
                                       │
                                       ▼
              ┌────────────────────────────────────────────────────────┐
              │       STAGE 1: Pre-Execution Red Flag Classifier        │
              │   (Convulsions · Stridor · Unconsciousness · Maternal  │
              │    Hemorrhage · Severe Dehydration · Cannot drink)     │
              └────────────────────────┬───────────────────────────────┘
                                       │
                 ┌─────────────────────┴──────────────────────┐
                 │                                             │
      [ Red Flag Detected ]                        [ Non-Emergency Query ]
                 │                                             │
                 ▼                                             ▼
    ┌─────────────────────────┐             ┌──────────────────────────────────┐
    │    EMERGENCY OVERRIDE   │             │  STAGE 2a: Gemini 2.5 Flash LLM  │
    │  Instant RED directive  │             │  (bilingual, contextual triage)   │
    │  to PHC/Hospital. FAST  │             │  — or —                           │
    └─────────────────────────┘             │  STAGE 2b: Deterministic IMCI    │
                                            │  (offline fallback, always works) │
                                            └─────────────┬────────────────────┘
                                                          │
                                                          ▼
                                            ┌─────────────────────────────┐
                                            │  STAGE 3: Prescription      │
                                            │  Guardrail — blocks all     │
                                            │  antibiotics & antimalarials│
                                            └─────────────┬───────────────┘
                                                          │
                                                          ▼
                                            🔴 RED / 🟡 YELLOW / 🟢 GREEN
                                                          │
                                            ┌─────────────┴───────────────┐
                                            │  TTS <Say> (IVR TwiML)      │
                                            │  or WhatsApp text reply      │
                                            │  or Web UI render            │
                                            └─────────────────────────────┘
```

---

## 🚦 Triage Classification Tiers

| Tier | Label (Hausa / English) | Clinical Criteria | Recommended Action |
| :--- | :--- | :--- | :--- |
| **🔴 RED** | **Gaggawa** *(Emergency)* | Any WHO IMCI General Danger Sign (convulsions, unconsciousness, unable to drink/breastfeed, vomiting everything), chest indrawing, maternal hemorrhage. | Immediate transfer to nearest General Hospital or 24/7 PHC. Call 112. |
| **🟡 YELLOW** | **Gani Likita** *(Clinical Visit)* | Fever > 24–48 hours, prolonged diarrhea, suspected malaria or pneumonia without acute chest indrawing. | Visit Primary Healthcare Centre within 24 hours for mRDT blood test. |
| **🟢 GREEN** | **Kula a Gida** *(Home Care)* | Mild loose stool with alert, well-hydrated child; mild common cold without respiratory distress. | ORS + Zinc; home comfort; watch for worsening signs. |

---

## 🚀 Getting Started

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Configure (optional — system works without any keys)
```bash
# .env  (copy to environment variables or set directly)
GEMINI_API_KEY=AIza...        # Enables Gemini 2.5 Flash LLM triage
TWILIO_ACCOUNT_SID=AC...      # Enables Twilio webhook signature validation
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
TWILIO_VOICE_NUMBER=+1234567890
```

### 3. Run Development Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Web UI:** http://localhost:8000/ui
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

---

## 📡 API Endpoints

### Core Triage

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/triage/text` | Symptom triage from text (Hausa or English) |
| `POST` | `/api/v1/triage/audio` | Symptom triage from audio file upload |
| `POST` | `/api/v1/immunization/query` | NPHCDA child vaccine schedule lookup |
| `POST` | `/api/v1/guardrails/check-redflags` | Standalone danger sign scanner |

### Twilio Webhooks

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/webhook/whatsapp` | Twilio WhatsApp Business inbound handler |
| `POST` | `/webhook/ivr/greet` | TwiML IVR greeting + `<Gather>` voice/DTMF |
| `POST` | `/webhook/ivr/input` | TwiML IVR speech result → triage → `<Say>` |
| `POST` | `/webhook/ivr/status` | Twilio call status callback (logging) |

### IVR DTMF Shortcuts
- **Press `2`** → Instant emergency fast-path: "Rufe wannan kira kuma kira 112 nan take"

---

## 📱 Connecting Twilio

### WhatsApp Business
1. Set your Twilio sandbox/prod number webhook URL to:
   `https://your-domain.com/webhook/whatsapp`
2. Set `TWILIO_AUTH_TOKEN` env var to enable signature validation.

### IVR Voice Calls
1. Set your Twilio Voice number's **A CALL COMES IN** webhook to:
   `https://your-domain.com/webhook/ivr/greet` (HTTP POST)
2. Set call **Status Callback** to:
   `https://your-domain.com/webhook/ivr/status`

> **Local testing with ngrok:**
> ```bash
> ngrok http 8000
> # then set your Twilio webhook to the ngrok HTTPS URL
> ```

---

## 🔌 Connecting Gemini 2.5 Flash

```bash
export GEMINI_API_KEY="AIzaSy..."
python -m uvicorn app.main:app --reload
```

Verify the engine is active:
```bash
curl http://localhost:8000/health
# "llm_engine": "gemini_2.5_flash", "llm_active": true
```

**Safety architecture with Gemini active:**
- Stage 1 (red flag bypass) still runs FIRST — Gemini is never called for emergencies
- Stage 3 (prescription guardrail) still runs LAST — Gemini output is sanitized
- If Gemini times out or returns malformed JSON, the deterministic IMCI engine takes over silently
- `metadata.triage_source` in every response tells you which engine was used

---

## 🧪 Testing

```bash
python -m pytest -v
# 33 passed in ~2s
```

| Test File | Coverage |
|-----------|----------|
| `test_guardrails.py` | Red flag detection, prescription sanitization, emergency overrides |
| `test_triage_api.py` | Full API endpoint integration (RED, YELLOW, GREEN, immunization) |
| `test_gemini_service.py` | Gemini mock, fallback on bad JSON, guardrail bypass invariant |
| `test_twilio_webhooks.py` | WhatsApp handler, IVR greet/input/DTMF/status |
| `test_benchmark_dataset.py` | 10-case clinical dataset benchmark |

---

## 🛡️ Clinical Safety Commitments

> These are non-negotiable invariants enforced at the code level, not via prompt instructions.

1. **WHO IMCI emergency bypass is always first** — no generative model is invoked for danger signs
2. **No autonomous antibiotic prescription** — Amoxicillin, Ciprofloxacin, Metronidazole etc. are regex-blocked in all outputs
3. **No autonomous antimalarial prescription** — Coartem, Artesunate etc. always require PHC mRDT confirmation
4. **Clinical disclaimer on every output** — in both Hausa and English
5. **Decision-support only** — always instructs visit to PHC or hospital; never claims to diagnose

---

## 📄 License & Attribution

Built for community health impact. Clinical protocols aligned with WHO IMCI (2024), Nigeria NPHCDA Routine Immunization Schedule, and Federal Ministry of Health guidelines.

*Shawarar Lafiya — ba madadin likita ba ne. (Shawarar Lafiya is not a substitute for a doctor.)*
