/**
 * Shawarar Lafiya — Client Logic v2
 * Clean · Minimal · WHO IMCI + NPHCDA
 */

const STATE = {
  theme: localStorage.getItem('lafiya_theme') || 'light',
  language: 'ha',
  tab: 'triage',
  isRecording: false,
  recognition: null,
  currentResult: null
};

// ---------------------------------------------------------------------------
// i18n strings
// ---------------------------------------------------------------------------
const I18N = {
  ha: {
    brandTagline:   "Jagorar Kiwon Lafiya",
    tabTriage:      "Tantance Alamomi",
    tabMrdt:        "Gwajin mRDT",
    tabReferral:    "Nemi PHC",
    tabImm:         "Rigakafi",
    voiceTitle:     "Auna Alamomin Mara Lafiya",
    voiceSub:       "Fadi ko rubuta abin da ke damun mai lafiya",
    placeholder:    "Bayyana alamomin ciwo a nan...",
    btnClear:       "Goge",
    btnSubmit:      "Auna Yanzu",
    statusReady:    "A shirye",
    statusListening:"Yana sauraro...",
    loading:        "Ana tantancewa bisa tsarin WHO IMCI...",
    lblSummary:     "Bayanin Likita",
    lblActions:     "Matakan Dauka",
    rfHeading:      "Alamun Hadari",
    safetyTitle:    "Tsaron Magunguna:",
    safetyDesc:     "Wannan manhaja ba ta bayar da magungunan rigakafi (antibiotics) kai tsaye ba. Ziyarci PHC domin gwajin jini na mRDT kafin a sha magani.",
    btnListen:      "Saurara",
    btnCall:        "Kira Sufurin Gaggawa (112)",
    firstAid:       "Kwantar da mara lafiyar a gefe (recovery position). Kada ka tura wani abu a bakinsa.",
    disclaimer:     "Jagorar kiwon lafiya ta farko ce kawai; ba madadin ganin likita ba ne.",
    lblNewAssessment: "+ Sabon Triage",
    lblNavModules:  "MODULIN AI",
    lblSidebarLibrary: "GIRKIN MISALAI",
    btnFindPhcShortcut: "Nemi PHC Mafi Kusa",
    btnScanMrdtShortcut: "Gwajin mRDT ta Hoto",
    mrdtTitle:      "Fassarar Gwajin mRDT ta AI",
    mrdtSub:        "Dauki hoton gwajin malaria (mRDT) don AI ta tantance layi da sakamako",
    lblUploadCta:   "Dauki Hoto ko Zaɓi daga Na'ura",
    lblUploadHint:  "Hoton yana bukatar ya nuna layin C da T a sarari",
    lblDemoSamples: "Misalai don Gwaji:",
    btnAnalyzeMrdt: "Auna Hoton Gwaji Yanzu",
    mrdtLoading:    "Ana duba layukan gwajin mRDT ta Gemini Vision...",
    lblMrdtMeaning: "Ma'anar Sakamako",
    lblMrdtAction:  "Matakin Da Za A Dauka",
    btnMrdtGotoPhc: "Nemi PHC Mafi Kusa don Magani",
    referralTitle:  "Nemi Cibiyar Kiwon Lafiya (PHC)",
    referralSub:    "Gano asibitoci da PHC mafi kusa ta hanyar tsarin DHIS2 na Najeriya",
    lblUseLocation: "Yi Amfani da Wuri na (GPS)",
    referralLoading:"Ana bincika cibiyoyin PHC mafi kusa...",
    immTitle:       "Allurar Rigakafi ta NPHCDA",
    immSub:         "Zabi shekarun jariri don ganin alluran da suka cancanta (Kyauta a PHC)",
    vaccineProtects:"Kariya daga:",
    noVaccines:     "Babu alluran da suka wajaba a wannan lokaci.",
    faqQ:           "Shin allurar rigakafi na da hadari?",
    faqA:           "A'a, allurar rigakafi tana da aminci da inganci sosai. Dan zazzabi kadan alama ce mai kyau ta garkuwar jiki.",
    btnFaqAudio:    "Saurara",
    tierRedBadge:   "GAGGAWA",
    tierRedTitle:   "Ana Bukatar Gaggauta Zuwa Asibiti",
    tierYellowBadge:"GANI LIKITA (24H)",
    tierYellowTitle:"Ziyarci PHC Domin Gwajin Jini",
    tierGreenBadge: "KULA A GIDA",
    tierGreenTitle: "Kula a Gida Tare Da Mayar Da Ruwan Jiki",
    btnScenarios:   "Zaɓi Yanayin Ciwo",
    dialogTitle:    "Zaɓi Yanayin Ciwo",
    dialogSubtitle: "Zabi misalin yanayin ciwo don gwajin tsarin triage",
    dialogFooter:   "Zaɓin zai cika filin rubutu da gudanar da bincike nan take",
    tierLabel: { red: "Gaggawa", amber: "Gani Likita", green: "Kula a Gida" }
  },
  en: {
    brandTagline:   "Voice-First Primary Health AI",
    tabTriage:      "Symptom Triage",
    tabMrdt:        "mRDT Reader",
    tabReferral:    "Find PHC",
    tabImm:         "Immunization",
    voiceTitle:     "Assess Patient Symptoms",
    voiceSub:       "Speak or type the patient's presenting complaint",
    placeholder:    "Describe symptoms here...",
    btnClear:       "Clear",
    btnSubmit:      "Run Triage",
    statusReady:    "Ready",
    statusListening:"Listening...",
    loading:        "Analysing against WHO IMCI clinical protocols...",
    lblSummary:     "Clinical Assessment",
    lblActions:     "Recommended Steps",
    rfHeading:      "Danger Signs Detected",
    safetyTitle:    "Clinical Safety Guardrail:",
    safetyDesc:     "This system does not autonomously prescribe antibiotics or antimalarials. Visit a PHC for an mRDT test before taking any medication.",
    btnListen:      "Listen",
    btnCall:        "Call Emergency / PHC (112)",
    firstAid:       "Lay patient on side (recovery position). Keep airway clear — do NOT insert anything into mouth.",
    disclaimer:     "Primary health triage guidance only; not a substitute for clinical examination.",
    lblNewAssessment: "+ New Assessment",
    lblNavModules:  "AI MODULES",
    lblSidebarLibrary: "SCENARIO LIBRARY",
    btnFindPhcShortcut: "Find Nearest PHC",
    btnScanMrdtShortcut: "Read mRDT Strip via Photo",
    mrdtTitle:      "AI mRDT Strip Interpretation",
    mrdtSub:        "Capture or upload a malaria RDT cassette photo for computer vision reading",
    lblUploadCta:   "Take Photo or Upload Image",
    lblUploadHint:  "Ensure both Control (C) and Test (T) lines are well-lit and clear",
    lblDemoSamples: "Quick Test Samples:",
    btnAnalyzeMrdt: "Interpret Test Strip Now",
    mrdtLoading:    "Analyzing test strip bands with Gemini Vision...",
    lblMrdtMeaning: "Clinical Interpretation",
    lblMrdtAction:  "Recommended Clinical Action",
    btnMrdtGotoPhc: "Locate Nearest PHC for Medication",
    referralTitle:  "Find Nearest Health Facility (PHC)",
    referralSub:    "Locate nearby clinics and hospitals via Nigeria DHIS2 integration",
    lblUseLocation: "Use My GPS Location",
    referralLoading:"Searching nearest health facilities via DHIS2...",
    immTitle:       "NPHCDA Routine Immunization Schedule",
    immSub:         "Select your child's age to view due vaccines — all 100% free at every PHC",
    vaccineProtects:"Protects against:",
    noVaccines:     "No routine vaccines scheduled for this milestone.",
    faqQ:           "Are vaccines safe?",
    faqA:           "Yes — all routine vaccines are completely safe and free. A mild fever after the jab is normal and shows the immune system is responding.",
    btnFaqAudio:    "Listen",
    tierRedBadge:   "EMERGENCY",
    tierRedTitle:   "Immediate Hospital Transfer Required",
    tierYellowBadge:"CLINICAL VISIT (24H)",
    tierYellowTitle:"Visit Nearest PHC for mRDT Test",
    tierGreenBadge: "HOME CARE",
    tierGreenTitle: "Home Rehydration & Monitoring",
    btnScenarios:   "Browse Clinical Scenarios",
    dialogTitle:    "Clinical Scenario Library",
    dialogSubtitle: "Select a scenario to auto-fill the triage input and run assessment",
    dialogFooter:   "Selecting a scenario will pre-fill the input and run triage immediately",
    tierLabel: { red: "Emergency", amber: "Clinical Visit", green: "Home Care" }
  }
};

// ---------------------------------------------------------------------------
// Clinical Scenario Presets — Extended
// ---------------------------------------------------------------------------
const SCENARIOS = {
  farfadiya: {
    tier: 'red',
    ha: "Yaro na yana karkarwa da farfadiya, ya daina shan nono.",
    en: "My child is convulsing and shaking uncontrollably, and has completely stopped breastfeeding.",
    label_ha: "Farfadiya / Convulsions",
    label_en: "Farfadiya / Convulsions",
    desc_ha: "Yaro yana karkarwa, ya daina nono",
    desc_en: "Child convulsing, stopped breastfeeding"
  },
  zazzabi: {
    tier: 'amber',
    ha: "Yaro na yana da zazzabi da zafin jiki tun kwana biyu, amma yana cin abinci.",
    en: "My child has had a fever for two days, but is active and eating normally.",
    label_ha: "Zazzabi / Fever (Kwana 2)",
    label_en: "Zazzabi / Fever (2 Days)",
    desc_ha: "Zazzabi kwana 2, yana cin abinci",
    desc_en: "2-day fever, still eating normally"
  },
  zawo: {
    tier: 'green',
    ha: "Yaro na ya yi zawo sau biyu yau, amma yana wasa kuma ba zazzabi ko amai.",
    en: "My child had loose stool twice today but is playing normally with no fever or vomiting.",
    label_ha: "Dan Zawo / Mild Diarrhea",
    label_en: "Dan Zawo / Mild Diarrhea",
    desc_ha: "Zawo sau 2, babu zazzabi ko amai",
    desc_en: "Loose stool x2, no fever or vomiting"
  },
  ciki_jini: {
    tier: 'red',
    ha: "Ina da ciki wata 7 kuma ga zubar jini a lokacin ciki tare da matsanancin ciwon kai da kumburin fuska.",
    en: "I am 7 months pregnant with heavy bleeding, severe headache, and facial swelling.",
    label_ha: "Mai Ciki da Zubar Jini",
    label_en: "Mai Ciki da Zubar Jini",
    desc_ha: "Ciki wata 7, zubar jini + ciwon kai + kumburin fuska",
    desc_en: "7 months pregnant, bleeding + headache + facial swelling"
  },
  amai_yaro: {
    tier: 'amber',
    ha: "Yaro yana amai sosai tun jiya dare, kuma baya iya sha ruwa.",
    en: "My child has been vomiting severely since last night and cannot keep any fluids down.",
    label_ha: "Amai Mai Tsanani / Severe Vomiting",
    label_en: "Amai Mai Tsanani / Severe Vomiting",
    desc_ha: "Amai tun jiya dare, baya iya sha ruwa",
    desc_en: "Vomiting since last night, unable to retain fluids"
  },
  numfashi: {
    tier: 'red',
    ha: "Jaririna yana numfashi da sauri sosai kuma kirjinsa yana shiga ciki lokacin da yake numfashi.",
    en: "My baby is breathing very fast and I can see the chest wall drawing in with each breath.",
    label_ha: "Matsalar Numfashi / Breathing Difficulty",
    label_en: "Matsalar Numfashi / Breathing Difficulty",
    desc_ha: "Numfashi da sauri, kirji yana shiga ciki",
    desc_en: "Fast breathing, chest indrawing visible"
  },
  ciwo_kunnen: {
    tier: 'amber',
    ha: "Yarana yana kuka kuma yana kama kunnensa. Wani ruwa yana fita daga kunnensa.",
    en: "My child is crying and pulling at his ear. There is some fluid draining from the ear.",
    label_ha: "Ciwo Kunnen / Ear Pain & Discharge",
    label_en: "Ciwo Kunnen / Ear Pain & Discharge",
    desc_ha: "Kama kunnen, ruwa yana fita — mai yiwuwa kamuwa",
    desc_en: "Ear pulling, discharge — possible otitis media"
  },
  rashin_abinci: {
    tier: 'red',
    ha: "Yaro na yana da rashin abinci mai tsanani, kafafunsa sun kumbura kuma fata tana ficewa.",
    en: "My child has severe malnutrition, swollen legs and feet, and skin peeling off.",
    label_ha: "Rashin Abinci Mai Tsanani / Severe Malnutrition",
    label_en: "Rashin Abinci Mai Tsanani / Severe Malnutrition",
    desc_ha: "Kumburin kafa, fatar jikin tana ficewa — SAM",
    desc_en: "Leg oedema, skin peeling — Severe Acute Malnutrition"
  },
  zazzabi_cizon_sauro: {
    tier: 'amber',
    ha: "Dan uwana yana da zazzabi, sanyi mai tsanani da rawar jiki, da ciwon kai. Muna zaune kusa da fadama.",
    en: "My family member has fever, severe chills and shaking, and a headache. We live near a swamp.",
    label_ha: "Zazzabin Cizon Sauro / Suspected Malaria",
    label_en: "Zazzabin Cizon Sauro / Suspected Malaria",
    desc_ha: "Zazzabi + sanyi + rawar jiki kusa da fadama — Zazzabin cizon sauro",
    desc_en: "Fever + chills + rigors near wetlands — Suspected malaria"
  },
  jariri_sabo: {
    tier: 'red',
    ha: "Jarirna na wata 3 baya motsi kamar yadda ya saba, baya shan nono kuma idanunsa sun zama rawaya.",
    en: "My 3-week-old baby is not moving normally, is not feeding, and her eyes have turned yellow.",
    label_ha: "Jariri Mai Zazzabi / Sick Neonate",
    label_en: "Jariri Mai Zazzabi / Sick Neonate",
    desc_ha: "Jariri wata 3, baya motsi, baya nono, idanu rawaya",
    desc_en: "3-week neonate, lethargic, not feeding, jaundiced"
  }
};

// ---------------------------------------------------------------------------
// Theme
// ---------------------------------------------------------------------------
function applyTheme(theme) {
  STATE.theme = theme;
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('lafiya_theme', theme);
  document.getElementById('theme-icon-sun').classList.toggle('hidden', theme === 'dark');
  document.getElementById('theme-icon-moon').classList.toggle('hidden', theme === 'light');
}

function toggleTheme() {
  applyTheme(STATE.theme === 'dark' ? 'light' : 'dark');
}

// ---------------------------------------------------------------------------
// Language
// ---------------------------------------------------------------------------
function setLanguage(lang) {
  STATE.language = lang;
  document.getElementById('btn-lang-ha').classList.toggle('active', lang === 'ha');
  document.getElementById('btn-lang-en').classList.toggle('active', lang === 'en');
  applyI18n();
  if (STATE.currentResult) renderResult(STATE.currentResult);
}

function applyI18n() {
  const t = I18N[STATE.language];
  const $ = id => document.getElementById(id);

  $('brand-tagline').innerText      = t.brandTagline;
  $('tab-label-triage').innerText   = t.tabTriage;
  $('tab-label-mrdt').innerText     = t.tabMrdt;
  $('tab-label-referral').innerText = t.tabReferral;
  $('tab-label-imm').innerText      = t.tabImm;
  $('voice-prompt-title').innerText = t.voiceTitle;
  $('voice-prompt-sub').innerText   = t.voiceSub;
  $('symptom-text').placeholder     = t.placeholder;
  $('btn-clear').innerText          = t.btnClear;
  $('btn-submit-label').innerText   = t.btnSubmit;
  $('voice-status-indicator').innerText = t.statusReady;
  $('loading-label').innerText      = t.loading;
  $('lbl-summary-title').innerText  = t.lblSummary;
  $('lbl-actions-title').innerText  = t.lblActions;
  $('rf-heading').innerText         = t.rfHeading;
  $('btn-listen-text').innerText    = t.btnListen;
  $('res-disclaimer').innerText     = t.disclaimer;
  $('res-first-aid-note').innerText = t.firstAid;
  $('btn-call-label').innerText     = t.btnCall;
  if ($('btn-find-phc-shortcut')) $('btn-find-phc-shortcut').innerText = t.btnFindPhcShortcut;
  if ($('btn-scan-mrdt-shortcut')) $('btn-scan-mrdt-shortcut').innerText = t.btnScanMrdtShortcut;

  // mRDT i18n
  if ($('mrdt-title')) $('mrdt-title').innerText = t.mrdtTitle;
  if ($('mrdt-sub')) $('mrdt-sub').innerText = t.mrdtSub;
  if ($('lbl-upload-cta')) $('lbl-upload-cta').innerText = t.lblUploadCta;
  if ($('lbl-upload-hint')) $('lbl-upload-hint').innerText = t.lblUploadHint;
  if ($('lbl-demo-samples')) $('lbl-demo-samples').innerText = t.lblDemoSamples;
  if ($('btn-analyze-mrdt-label')) $('btn-analyze-mrdt-label').innerText = t.btnAnalyzeMrdt;
  if ($('mrdt-loading-label')) $('mrdt-loading-label').innerText = t.mrdtLoading;
  if ($('lbl-mrdt-meaning')) $('lbl-mrdt-meaning').innerText = t.lblMrdtMeaning;
  if ($('lbl-mrdt-action')) $('lbl-mrdt-action').innerText = t.lblMrdtAction;
  if ($('btn-mrdt-goto-phc')) $('btn-mrdt-goto-phc').innerText = t.btnMrdtGotoPhc;

  // Referral i18n
  if ($('referral-title')) $('referral-title').innerText = t.referralTitle;
  if ($('referral-sub')) $('referral-sub').innerText = t.referralSub;
  if ($('lbl-use-location')) $('lbl-use-location').innerText = t.lblUseLocation;
  if ($('referral-loading-label')) $('referral-loading-label').innerText = t.referralLoading;

  $('imm-section-title').innerText  = t.immTitle;
  $('imm-section-sub').innerText    = t.immSub;
  $('faq-title').innerText          = t.faqQ;
  $('faq-text').innerText           = t.faqA;
  $('btn-faq-audio').innerText      = t.btnFaqAudio;

  // Sidebar labels
  if ($('lbl-new-assessment')) $('lbl-new-assessment').innerText = t.lblNewAssessment;
  if ($('lbl-nav-modules')) $('lbl-nav-modules').innerText = t.lblNavModules;
  if ($('lbl-sidebar-library')) $('lbl-sidebar-library').innerText = t.lblSidebarLibrary;
  if ($('btn-scenarios-label-inner')) $('btn-scenarios-label-inner').innerText = t.btnScenarios;

  // Scenario trigger button label
  if ($('btn-scenarios-label')) $('btn-scenarios-label').innerText = t.btnScenarios;

  // Update workspace topbar title
  updateTopbarTitle();

  // Re-render dialog list labels if dialog is open
  const overlay = $('scenario-dialog-overlay');
  if (overlay && !overlay.classList.contains('hidden')) renderScenarioList();
}

const TOPBAR_TITLES = {
  ha: {
    triage: "Tantance Alamomi",
    mrdt: "Fassarar Gwajin mRDT",
    referral: "Nemi Cibiyar PHC",
    imm: "Allurar Rigakafi"
  },
  en: {
    triage: "Symptom Triage",
    mrdt: "mRDT Strip Reader",
    referral: "Find Nearest PHC",
    imm: "Immunization Schedule"
  }
};

function updateTopbarTitle() {
  const el = document.getElementById('topbar-view-title');
  if (el) {
    const titles = TOPBAR_TITLES[STATE.language] || TOPBAR_TITLES.ha;
    el.innerText = titles[STATE.tab] || titles.triage;
  }
}

// ---------------------------------------------------------------------------
// Dashboard Sidebar Navigation Controls
// ---------------------------------------------------------------------------
function toggleSidebar() {
  const sb = document.getElementById('dashboard-sidebar');
  const bd = document.getElementById('sidebar-backdrop');
  if (sb) sb.classList.toggle('open');
  if (bd) bd.classList.toggle('active');
}

function closeSidebar() {
  const sb = document.getElementById('dashboard-sidebar');
  const bd = document.getElementById('sidebar-backdrop');
  if (sb) sb.classList.remove('open');
  if (bd) bd.classList.remove('active');
}

function startNewTriage() {
  switchTab('triage');
  clearInput();
  closeSidebar();
  const textarea = document.getElementById('symptom-text');
  if (textarea) textarea.focus();
}

// ---------------------------------------------------------------------------
// Tab Switching
// ---------------------------------------------------------------------------
function switchTab(tab) {
  STATE.tab = tab;
  ['triage', 'mrdt', 'referral', 'imm'].forEach(t => {
    const tabBtn = document.getElementById('tab-' + t);
    const viewSec = document.getElementById('view-' + t);
    if (tabBtn) tabBtn.classList.toggle('active', t === tab);
    if (viewSec) viewSec.classList.toggle('active', t === tab);
  });
  updateTopbarTitle();
  closeSidebar();
  if (tab === 'imm') loadVaccines(0);
  if (tab === 'referral') {
    const select = document.getElementById('referral-state-select');
    if (select && !STATE.referralLoaded) {
      searchReferralByState();
    }
  }
}

// ---------------------------------------------------------------------------
// Voice Input
// ---------------------------------------------------------------------------
function setupSpeechRecognition() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return;
  STATE.recognition = new SR();
  STATE.recognition.continuous = false;
  STATE.recognition.interimResults = false;

  STATE.recognition.onstart = () => {
    STATE.isRecording = true;
    document.getElementById('btn-voice-orb').classList.add('recording');
    document.getElementById('voice-status-indicator').innerText =
      I18N[STATE.language].statusListening;
  };

  STATE.recognition.onresult = (e) => {
    document.getElementById('symptom-text').value = e.results[0][0].transcript;
  };

  STATE.recognition.onerror = () => {
    document.getElementById('voice-status-indicator').innerText = I18N[STATE.language].statusReady;
  };

  STATE.recognition.onend = () => {
    STATE.isRecording = false;
    document.getElementById('btn-voice-orb').classList.remove('recording');
    document.getElementById('voice-status-indicator').innerText = I18N[STATE.language].statusReady;
  };
}

function toggleVoiceInput() {
  if (!STATE.recognition) setupSpeechRecognition();
  if (!STATE.recognition) return;
  if (STATE.isRecording) {
    STATE.recognition.stop();
  } else {
    STATE.recognition.lang = STATE.language === 'ha' ? 'ha-NG' : 'en-US';
    STATE.recognition.start();
  }
}

// ---------------------------------------------------------------------------
// Scenario Dialog
// ---------------------------------------------------------------------------
function openScenarioDialog() {
  const overlay = document.getElementById('scenario-dialog-overlay');
  const t = I18N[STATE.language];
  document.getElementById('dialog-title').innerText    = t.dialogTitle;
  document.getElementById('dialog-subtitle').innerText = t.dialogSubtitle;
  document.getElementById('dialog-footer-note').innerText = t.dialogFooter;
  renderScenarioList();
  overlay.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeScenarioDialog(e) {
  // Close only when clicking the backdrop directly (not inside the dialog box)
  if (e && e.target !== document.getElementById('scenario-dialog-overlay')) return;
  document.getElementById('scenario-dialog-overlay').classList.add('hidden');
  document.body.style.overflow = '';
}

function renderScenarioList() {
  const isHa = STATE.language === 'ha';
  const t     = I18N[STATE.language];
  const list  = document.getElementById('scenario-list');

  const tierColors = {
    red:   { dot: 'var(--red)',   bg: '#fff1f1', label: t.tierLabel.red },
    amber: { dot: 'var(--amber)', bg: '#fffbeb', label: t.tierLabel.amber },
    green: { dot: 'var(--green)', bg: '#f0fdf4', label: t.tierLabel.green }
  };

  list.innerHTML = Object.entries(SCENARIOS).map(([key, s]) => {
    const c = tierColors[s.tier] || tierColors.green;
    return `
      <li class="scenario-list-item" onclick="pickScenario('${key}')">
        <div class="scenario-item-left">
          <span class="scenario-tier-dot" style="background:${c.dot}"></span>
          <div class="scenario-item-body">
            <strong class="scenario-item-title">${isHa ? s.label_ha : s.label_en}</strong>
            <span class="scenario-item-desc">${isHa ? s.desc_ha : s.desc_en}</span>
          </div>
        </div>
        <span class="scenario-tier-badge" style="background:${c.bg};color:${c.dot}">${c.label}</span>
      </li>`;
  }).join('');
}

function pickScenario(key) {
  document.getElementById('scenario-dialog-overlay').classList.add('hidden');
  document.body.style.overflow = '';
  loadScenario(key);
}

// ---------------------------------------------------------------------------
// Scenario Chips / Input
// ---------------------------------------------------------------------------
function loadScenario(key) {
  const s = SCENARIOS[key];
  if (!s) return;
  document.getElementById('symptom-text').value = s[STATE.language] || s.ha;
  submitTriage();
}

function clearInput() {
  document.getElementById('symptom-text').value = '';
  document.getElementById('results-state').classList.add('hidden');
  STATE.currentResult = null;
}

// ---------------------------------------------------------------------------
// Triage API
// ---------------------------------------------------------------------------
async function submitTriage() {
  const text = document.getElementById('symptom-text').value.trim();
  if (!text) return;

  const btn = document.getElementById('btn-submit');
  btn.disabled = true;

  document.getElementById('loading-state').classList.remove('hidden');
  document.getElementById('results-state').classList.add('hidden');

  try {
    const res = await fetch('/api/v1/triage/text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symptoms_text: text, language: STATE.language })
    });
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    STATE.currentResult = data;
    renderResult(data);
  } catch (err) {
    alert(STATE.language === 'ha'
      ? "An samu matsala wajen sadarwa da sabar."
      : "Failed to connect to the triage server.");
  } finally {
    document.getElementById('loading-state').classList.add('hidden');
    btn.disabled = false;
  }
}

// ---------------------------------------------------------------------------
// Render Result
// ---------------------------------------------------------------------------
function renderResult(data) {
  const t    = I18N[STATE.language];
  const isHa = STATE.language === 'ha';

  const statusCard   = document.getElementById('result-status-card');
  const badge        = document.getElementById('res-badge');
  const headline     = document.getElementById('res-headline');
  const rfBox        = document.getElementById('res-red-flags-box');
  const rfGrid       = document.getElementById('res-red-flags-list');
  const summary      = document.getElementById('res-summary-text');
  const actionsList  = document.getElementById('res-actions-list');
  const emergencyCta = document.getElementById('res-emergency-cta');
  const panel        = document.getElementById('results-state');

  // Severity
  statusCard.className = 'report-header';
  if (data.tier === 'RED') {
    statusCard.classList.add('red');
    badge.innerText = t.tierRedBadge;
    headline.innerText = t.tierRedTitle;
    emergencyCta.classList.remove('hidden');
  } else if (data.tier === 'YELLOW') {
    statusCard.classList.add('yellow');
    badge.innerText = t.tierYellowBadge;
    headline.innerText = t.tierYellowTitle;
    emergencyCta.classList.add('hidden');
  } else {
    statusCard.classList.add('green');
    badge.innerText = t.tierGreenBadge;
    headline.innerText = t.tierGreenTitle;
    emergencyCta.classList.add('hidden');
  }

  // Danger Signs — compact pill badges
  if (data.red_flags_detected && data.red_flags_detected.length > 0) {
    rfBox.classList.remove('hidden');
    rfGrid.innerHTML = data.red_flags_detected.map(rf =>
      `<span class="flag-badge">${isHa ? rf.description_ha : rf.description_en}</span>`
    ).join('');
  } else {
    rfBox.classList.add('hidden');
  }

  // Summary
  summary.innerText = isHa ? data.summary_ha : data.summary_en;

  // Actions
  const actions = isHa ? data.primary_actions_ha : data.primary_actions_en;
  actionsList.innerHTML = actions.map((act, i) => `
    <div class="directive-row">
      <div class="directive-num">${i + 1}</div>
      <div class="directive-text">${act}</div>
    </div>
  `).join('');

  panel.classList.remove('hidden');
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ---------------------------------------------------------------------------
// TTS Audio
// ---------------------------------------------------------------------------
function playAudioGuidance() {
  if (!STATE.currentResult) return;
  const text = STATE.language === 'ha'
    ? STATE.currentResult.summary_ha
    : STATE.currentResult.summary_en;
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = STATE.language === 'ha' ? 'ha' : 'en-US';
    u.rate = 0.95;
    window.speechSynthesis.speak(u);
  }
}

function playMythAudio() {
  const text = STATE.language === 'ha'
    ? "Allurar rigakafi kyauta ce kuma tana da cikakkiyar aminci. Tana gina garkuwar jikin yaro daga cututtuka masu kisa."
    : "Routine vaccines are completely free and safe. They protect your child from preventable killer diseases.";
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = STATE.language === 'ha' ? 'ha' : 'en-US';
    window.speechSynthesis.speak(u);
  }
}

// ---------------------------------------------------------------------------
// Immunization Schedule
// ---------------------------------------------------------------------------
async function loadVaccines(weeks) {
  document.querySelectorAll('.milestone-pill').forEach(b => b.classList.remove('active'));
  if (event && event.target && event.target.classList.contains('milestone-pill')) {
    event.target.classList.add('active');
  }

  const container = document.getElementById('vaccines-list');
  container.innerHTML = `<div style="text-align:center;padding:24px;color:var(--text-muted);font-size:0.84rem;">Loading...</div>`;

  try {
    const res = await fetch('/api/v1/immunization/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ child_age_weeks: weeks, language: STATE.language })
    });
    const data = await res.json();
    const isHa    = STATE.language === 'ha';
    const vaccines = data.vaccines_due_now.length > 0
      ? data.vaccines_due_now
      : data.upcoming_milestones;

    if (!vaccines || !vaccines.length) {
      container.innerHTML = `<p style="color:var(--text-muted);font-size:0.88rem;padding:8px 0;">${I18N[STATE.language].noVaccines}</p>`;
      return;
    }

    container.innerHTML = vaccines.map(v => `
      <div class="vaccine-item">
        <div class="vaccine-icon-col">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2"><path d="m18 2 4 4"></path><path d="m17 7 3-3"></path><path d="M19 9 8.7 19.3c-1 1-2.5 1-3.4 0l-.6-.6c-1-1-1-2.5 0-3.4L15 5"></path></svg>
        </div>
        <div>
          <div class="v-item-name">${v.vaccine_name}</div>
          <div class="v-item-protects"><strong>${I18N[STATE.language].vaccineProtects}</strong> ${isHa ? v.disease_prevented_ha : v.disease_prevented_en}</div>
        </div>
      </div>
    `).join('');
  } catch {
    container.innerHTML = `<p style="color:var(--red);font-size:0.84rem;">Failed to load schedule.</p>`;
  }
}

// ---------------------------------------------------------------------------
// Auto mRDT Strip Interpretation Logic
// ---------------------------------------------------------------------------
let currentMRDTFile = null;

function handleMRDTFile(e) {
  const file = e.target.files && e.target.files[0];
  if (!file) return;
  currentMRDTFile = file;

  const reader = new FileReader();
  reader.onload = function(evt) {
    document.getElementById('mrdt-preview-img').src = evt.target.result;
    document.getElementById('mrdt-upload-prompt').classList.add('hidden');
    document.getElementById('mrdt-preview-wrap').classList.remove('hidden');
  };
  reader.readAsDataURL(file);
}

function clearMRDTUpload(e) {
  if (e) e.stopPropagation();
  currentMRDTFile = null;
  document.getElementById('mrdt-file-input').value = '';
  document.getElementById('mrdt-preview-wrap').classList.add('hidden');
  document.getElementById('mrdt-upload-prompt').classList.remove('hidden');
  document.getElementById('mrdt-result-card').classList.add('hidden');
}

// Generate SVG dataURL for demo strips
function generateDemoStripSVG(type) {
  const isPos = type === 'positive';
  const isNeg = type === 'negative';
  const isInv = type === 'invalid';

  const ctrlColor = isInv ? '#f1f4f9' : '#b91c1c';
  const testColor = isPos ? '#b91c1c' : '#f1f4f9';

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="360" height="120" viewBox="0 0 360 120">
    <rect width="360" height="120" rx="16" fill="#f8fafc" stroke="#cbd5e1" stroke-width="3"/>
    <rect x="20" y="24" width="70" height="72" rx="8" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>
    <circle cx="55" cy="60" r="14" fill="#94a3b8"/>
    <text x="55" y="65" font-family="sans-serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">S</text>
    <rect x="120" y="32" width="210" height="56" rx="8" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
    <rect x="180" y="36" width="10" height="48" rx="2" fill="${testColor}"/>
    <text x="185" y="102" font-family="sans-serif" font-size="13" font-weight="bold" fill="#64748b" text-anchor="middle">T</text>
    <rect x="260" y="36" width="10" height="48" rx="2" fill="${ctrlColor}"/>
    <text x="265" y="102" font-family="sans-serif" font-size="13" font-weight="bold" fill="#64748b" text-anchor="middle">C</text>
    <text x="180" y="22" font-family="sans-serif" font-size="11" font-weight="bold" fill="#475569">Malaria Pf / Pv RDT</text>
  </svg>`;
  return 'data:image/svg+xml;base64,' + btoa(svg);
}

async function loadSampleMRDT(type) {
  const dataUrl = generateDemoStripSVG(type);
  document.getElementById('mrdt-preview-img').src = dataUrl;
  document.getElementById('mrdt-upload-prompt').classList.add('hidden');
  document.getElementById('mrdt-preview-wrap').classList.remove('hidden');

  // Convert dataURL to Blob for submission
  const res = await fetch(dataUrl);
  const blob = await res.blob();
  currentMRDTFile = new File([blob], `sample_${type}_mrdt.svg`, { type: 'image/svg+xml' });

  submitMRDTAnalysis();
}

async function submitMRDTAnalysis() {
  if (!currentMRDTFile) {
    alert(STATE.language === 'ha' ? "Da fatan a fara daukar hoto ko zabi daga waya." : "Please take a photo or select an image first.");
    return;
  }

  const btn = document.getElementById('btn-analyze-mrdt');
  btn.disabled = true;
  document.getElementById('mrdt-loading').classList.remove('hidden');
  document.getElementById('mrdt-result-card').classList.add('hidden');

  const formData = new FormData();
  formData.append('image_file', currentMRDTFile);
  formData.append('language', STATE.language);

  try {
    const res = await fetch('/api/v1/mrdt/interpret', {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error('mRDT API error');
    const data = await res.json();
    renderMRDTResult(data);
  } catch (err) {
    alert(STATE.language === 'ha' ? "An samu matsala wajen fassara hoton mRDT." : "Failed to interpret mRDT image.");
  } finally {
    document.getElementById('mrdt-loading').classList.add('hidden');
    btn.disabled = false;
  }
}

function renderMRDTResult(data) {
  const isHa = STATE.language === 'ha';
  const card = document.getElementById('mrdt-result-card');
  const badge = document.getElementById('mrdt-status-badge');
  const typeLabel = document.getElementById('mrdt-test-type');

  badge.className = 'mrdt-status-pill ' + (data.result.toLowerCase());
  badge.innerText = data.result;
  typeLabel.innerText = data.test_type_detected ? data.test_type_detected.replace('_', ' ').toUpperCase() : 'mRDT Rapid Test';

  const ctrlVisible = data.bands_visible && data.bands_visible.control_band;
  const testVisible = data.bands_visible && (data.bands_visible.test_band_1 || data.bands_visible.test_band_2);

  document.getElementById('band-ctrl-text').innerText = (isHa ? "Layin Kula (C): " : "Control Line (C): ") + (ctrlVisible ? "Akwai ✓" : "Babu ✕");
  document.getElementById('band-test-text').innerText = (isHa ? "Layin Gwaji (T): " : "Test Line (T): ") + (testVisible ? "Akwai ✓" : "Babu ✕");

  document.getElementById('mrdt-interpretation').innerText = isHa ? data.interpretation_ha : data.interpretation_en;
  document.getElementById('mrdt-action').innerText = isHa ? data.clinical_action_ha : data.clinical_action_en;
  document.getElementById('mrdt-safety-note').innerText = isHa ? data.safety_note_ha : data.safety_note_en;

  card.classList.remove('hidden');
  card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ---------------------------------------------------------------------------
// DHIS2 PHC Referral Routing Logic
// ---------------------------------------------------------------------------
const STATE_COORDINATES = {
  Kano:    { lat: 12.0022, lon: 8.5920 },
  Kaduna:  { lat: 10.5296, lon: 7.4381 },
  Katsina: { lat: 12.9897, lon: 7.6006 },
  Sokoto:  { lat: 13.0622, lon: 5.2340 },
  Zamfara: { lat: 12.1702, lon: 6.6632 },
  Jigawa:  { lat: 11.6873, lon: 9.3414 },
  Bauchi:  { lat: 10.3100, lon: 9.8445 },
  Gombe:   { lat: 10.2900, lon: 11.1670 },
  Niger:   { lat: 9.6139, lon: 6.5570 },
  FCT:     { lat: 9.0579, lon: 7.5137 }
};

function openReferralFromTriage() {
  switchTab('referral');
  getUserLocationAndSearch();
}

function getUserLocationAndSearch() {
  if (!navigator.geolocation) {
    searchReferralByState();
    return;
  }
  document.getElementById('referral-loading').classList.remove('hidden');
  navigator.geolocation.getCurrentPosition(
    pos => {
      fetchAndRenderReferral(pos.coords.latitude, pos.coords.longitude, null);
    },
    err => {
      // Fallback to selected state
      searchReferralByState();
    },
    { timeout: 7000 }
  );
}

function searchReferralByState() {
  const select = document.getElementById('referral-state-select');
  const state = select ? select.value : 'Kano';
  const coords = STATE_COORDINATES[state] || STATE_COORDINATES.Kano;
  fetchAndRenderReferral(coords.lat, coords.lon, state);
}

async function fetchAndRenderReferral(lat, lon, stateFilter) {
  document.getElementById('referral-loading').classList.remove('hidden');
  const container = document.getElementById('referral-results-list');
  container.innerHTML = '';

  try {
    const res = await fetch('/api/v1/referral/nearest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lat: lat,
        lon: lon,
        state_filter: stateFilter || null,
        language: STATE.language,
        max_results: 5
      })
    });
    if (!res.ok) throw new Error('Referral API error');
    const data = await res.json();
    STATE.referralLoaded = true;
    renderReferralList(data);
  } catch (err) {
    container.innerHTML = `<p style="color:var(--red); font-size:0.85rem; padding:12px 0;">Failed to load nearby health facilities.</p>`;
  } finally {
    document.getElementById('referral-loading').classList.add('hidden');
  }
}

function renderReferralList(data) {
  const container = document.getElementById('referral-results-list');
  const isHa = STATE.language === 'ha';

  if (!data.facilities || data.facilities.length === 0) {
    container.innerHTML = `<p style="color:var(--text-muted); font-size:0.88rem; padding:12px 0;">${isHa ? "Babu cibiyar da aka samu a wannan yankin." : "No health facilities found in this area."}</p>`;
    return;
  }

  container.innerHTML = data.facilities.map(f => `
    <div class="facility-card">
      <div class="facility-left">
        <span class="facility-distance-badge">${f.distance_km} km</span>
        <div class="facility-info">
          <strong class="facility-name">${f.name}</strong>
          <span class="facility-location">${f.lga} LGA &bull; ${f.state} (${f.level})</span>
        </div>
      </div>
      <div class="facility-actions">
        ${f.phone ? `<a href="tel:${f.phone}" class="btn-facility-call" title="Call PHC">
          <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          <span>Kira</span>
        </a>` : ''}
        <a href="${f.maps_url}" target="_blank" rel="noopener noreferrer" class="btn-facility-dir">
          <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.2"><polygon points="3 11 22 2 13 21 11 13 3 11"></polygon></svg>
          <span>${isHa ? "Taswira" : "Directions"}</span>
        </a>
      </div>
    </div>
  `).join('');
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
window.addEventListener('DOMContentLoaded', () => {
  applyTheme(STATE.theme);
  setupSpeechRecognition();
  applyI18n();
  loadVaccines(0);
});


// Close scenario dialog with Escape key
window.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    const overlay = document.getElementById('scenario-dialog-overlay');
    if (overlay && !overlay.classList.contains('hidden')) {
      overlay.classList.add('hidden');
      document.body.style.overflow = '';
    }
  }
});
