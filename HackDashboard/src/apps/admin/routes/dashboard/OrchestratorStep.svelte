<script>
  import { fly, fade } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";
  import ClinicalAssessmentHeader from "./ClinicalAssessmentHeader.svelte";
  import ClinicalAssessmentLiveStatus from "./ClinicalAssessmentLiveStatus.svelte";
  import OrchestratorCaseSelector from "./OrchestratorCaseSelector.svelte";
  import OrchestratorProblemCard from "./OrchestratorProblemCard.svelte";
  import OrchestratorEvidenceStep from "./OrchestratorEvidenceStep.svelte";
  import OrchestratorCalculationStep from "./OrchestratorCalculationStep.svelte";
  import OrchestratorRiskStep from "./OrchestratorRiskStep.svelte";
  import OrchestratorDirectivesStep from "./OrchestratorDirectivesStep.svelte";
  import OrchestratorGapsTab from "./OrchestratorGapsTab.svelte";
  import OrchestratorQueriesTab from "./OrchestratorQueriesTab.svelte";
  import { t } from "$lib";

  let {
    patient = $bindable(),
    orchestratorState = $bindable(),
    artifactsData = null,
    runStatus = "idle",
    runId = "",
    elapsedSeconds = 0,
    stepNodes = [],
    logsText = "",
    errorMessage = "",
    onNext,
    onBack,
    onOpenDagu,
  } = $props();

  let activeTab = $state("pipeline"); // 'pipeline' | 'gaps' | 'queries'
  let activeSubStep = $state("all"); // 'all' | 1 | 2 | 3 | 4

  const clinicalCases = [
    {
      id: "chocolate",
      name: "Dog · Dark Chocolate",
      icon: "🍫",
      specie: "Dog",
      razza: "Labrador Retriever",
      peso: 22.0,
      priorita: "critical",
      sintomi:
        "22 kg dog, ingested 150g of dark bitter chocolate about 1 hour ago (within the 2-hour window). Agitated, tachycardic with muscle tremors.",
    },
    {
      id: "lily",
      name: "Cat · Lily",
      icon: "🌺",
      specie: "Cat",
      razza: "European Shorthair",
      peso: 3.5,
      priorita: "critical",
      sintomi:
        "3.5 kg European Shorthair cat, chewed leaves of a cut flower received yesterday (Easter Lily / Lilium). Profuse hypersalivation (drooling) and vomiting x2.",
    },
    {
      id: "amlodipine",
      name: "Dog · Amlodipine 10mg",
      icon: "💊",
      specie: "Dog",
      razza: "Golden Retriever",
      peso: 28.0,
      priorita: "critical",
      sintomi:
        "28 kg Golden Retriever, ingested a blister pack of 4-6 tablets of Amlodipine 10 mg (grandpa's blood pressure medication) about 45 minutes ago. Risk of refractory hypotension and shock.",
    },
    {
      id: "rabbit",
      name: "Rabbit · GI Stasis",
      icon: "🐰",
      specie: "Rabbit",
      razza: "Holland Lop",
      peso: 1.2,
      priorita: "urgent",
      sintomi:
        "1.2 kg dwarf rabbit with gastrointestinal stasis: anorexia and no fecal production for 18 hours. Needs analgesia and prokinetics without drugs toxic to the cecum.",
    },
    {
      id: "vector",
      name: "Dog · Ticks / Lameness",
      icon: "🩺",
      specie: "Dog",
      razza: "German Shepherd",
      peso: 32.0,
      priorita: "urgent",
      sintomi:
        "4-year-old German Shepherd (32 kg), intermittent shifting lameness, lymphadenopathy, fever at 39.8°C and lethargy. Lives in the hills with frequent removed tick bites.",
    },
  ];

  // Detect which clinical use case matches the current patient
  let currentCaseKey = $derived.by(() => {
    const text = (
      (patient?.sintomi || "") +
      " " +
      (patient?.specie || "") +
      " " +
      (patient?.razza || "")
    ).toLowerCase();
    if (
      text.includes("amlodip") ||
      text.includes("calcium channel") ||
      text.includes("blister")
    ) {
      return "amlodipine";
    }
    if (
      text.includes("rabbit") ||
      text.includes("stasis") ||
      text.includes("lagomorph") ||
      text.includes("cecal")
    ) {
      return "rabbit";
    }
    if (
      text.includes("tick") ||
      text.includes("lameness") ||
      text.includes("lyme") ||
      text.includes("borrelia") ||
      text.includes("anaplasma")
    ) {
      return "vector";
    }
    if (
      text.includes("cat") ||
      text.includes("feline") ||
      text.includes("flower") ||
      text.includes("lily") ||
      text.includes("lilium")
    ) {
      return "lily";
    }
    return "chocolate";
  });

  function selectCasePreset(c) {
    patient = {
      specie: c.specie,
      razza: c.razza,
      peso: c.peso,
      priorita: c.priorita,
      sintomi: c.sintomi,
    };
  }

  // Reactive details for each case
  let caseData = $derived.by(() => {
    const key = currentCaseKey;
    const weight = patient?.peso > 0 ? patient.peso : 20.0;

    if (key === "lily") {
      const fluidRatePerHour = (weight * 7.0).toFixed(1);
      const fluidRatePerDay = (weight * 7.0 * 24).toFixed(0);
      return {
        key: "lily",
        title: "Case 1: The Unknown Houseplant (Feline Emergency)",
        problemTitle:
          "1. The Chemical & Pathophysiological Problem: Glucuronidation Deficiency & Nephrotoxins",
        problemTag: "Feline Nephrotoxicology",
        chemCards: [
          {
            tag: "Species-Specific Vulnerability",
            title: "Glucuronyltransferase Deficiency",
            desc: "Cats have a constitutive deficiency of the hepatic enzyme glucuronyltransferase, which prevents the conjugation and detoxification of the plant toxins of Lilium and Hemerocallis.",
          },
          {
            tag: "Mechanism of Action",
            title: "Acute Tubular Necrosis",
            desc: "The unidentified water-soluble toxins cause immediate lysis of the renal tubular epithelium. Even minimal traces (pollen licked from the coat or water from the cut-flower vase) are lethal.",
          },
          {
            tag: "Patient Parameters",
            title: `European cat · ${weight} kg`,
            desc: `Symptoms: profuse drooling, vomiting x2. Critical intervention window: before anuria sets in (within 18 hours).`,
          },
        ],
        step1: {
          title: "Evidence Search · Botanical Identification & Toxicity",
          badge: "Species-Specific Classification",
          desc: "The evidence search queries the ASPCA, Merck and BSAVA registries: it identifies the 'Easter Lily' as belonging to the Lilium genus and highlights the renal target exclusive to felines.",
          highlightLabel: "Botanical Identification:",
          highlightVal: "Lilium / Hemerocallis spp. (True Lily)",
          highlightSub: "Lethal nephrotoxin with rapid tubular action",
        },
        step2: {
          title:
            "AI Clinical Engine · Forced Diuresis & Infusion Target Calculation",
          badge: "Reasoning & Dosing Logic",
          desc: "The AI engine defines the continuous forced-diuresis protocol for 48-72 hours, calculating the volumetric rate at double/triple maintenance:",
          formula: `Infusion rate: ${weight} kg × 7.0 ml/kg/h = ${fluidRatePerHour} ml/h (${fluidRatePerDay} ml/day)`,
        },
        step3: {
          title: "Clinical Assessment & Therapeutic Window",
          badge: "Red Alert · 18-Hour Window",
          badgeClass: "badge-error text-white animate-pulse",
          thresholds: [
            {
              label: "< 2-4 Hours",
              badge: "Decontamination",
              text: "Guided emesis only if alert. Activated charcoal for adsorption.",
            },
            {
              label: "0 - 18 Hours",
              badge: "Life-Saving Window",
              text: "Prompt start of intravenous fluid therapy: favorable prognosis (>90%).",
            },
            {
              label: "> 18-24 Hours",
              badge: "Irreversible Anuria",
              text: "Established tubular necrosis, terminal uremia (mortality >70% without hemodialysis).",
            },
          ],
          alertBox: {
            title: "Red Alert: Risk of Fulminant Acute Renal Failure",
            desc: "Treatment delay beyond 18 hours leads to anuria and inevitable renal death.",
          },
        },
        step4: {
          badge: "Feline Intensive Care Protocol",
          directives: [
            {
              icon: "🚨",
              title: "Alert Status",
              color: "text-error",
              border: "border-error/30",
              heading: "Red Alert: Fatal Renal Toxicity",
              desc: "Immediate hospitalization in intensive care with hourly urine output monitoring.",
            },
            {
              icon: "⚡",
              title: "Immediate Action",
              color: "text-secondary",
              border: "border-secondary/30",
              heading: `Decontamination & Fluids (${fluidRatePerHour} ml/h)`,
              desc: `If alert: Dexmedetomidine (10-20 mcg/kg IM, NEVER apomorphine in cats). Activated charcoal 1-2 g/kg. Forced fluid therapy at ${fluidRatePerHour} ml/h.`,
            },
            {
              icon: "🧪",
              title: "Lab Monitoring",
              color: "text-primary",
              border: "border-primary/30",
              heading: "Creatinine, BUN & SDMA",
              desc: "Baseline sample at T0, then at 24h and 48h. Urinary catheter for a urine output target > 1.5-2.0 ml/kg/h.",
            },
          ],
        },
      };
    } else if (key === "amlodipine") {
      const pillsMax = 6;
      const mgTotal = pillsMax * 10;
      const dosePerKg = (mgTotal / weight).toFixed(2);
      const apomorphineMg = (weight * 0.035).toFixed(2);
      const apomorphineMl = ((weight * 0.035) / 10).toFixed(3);
      return {
        key: "amlodipine",
        title:
          "Case 2: Human Medication Taken from the Nightstand (Pharmacological Toxicology)",
        problemTitle:
          "1. The Chemical & Pharmacological Problem: Calcium Channel Blockade & Hypotension",
        problemTag: "Emergency Cardiotoxicology",
        chemCards: [
          {
            tag: "Ingested Molecule",
            title: "Amlodipine 10 mg",
            desc: "Long-acting dihydropyridine calcium antagonist for human hypertension. It blocks L-type voltage-gated Ca2+ channels in the vessels and myocardium.",
          },
          {
            tag: "Kinetics & Clinical Risk",
            title: "Refractory Hypotension & Shock",
            desc: "Massive systemic arteriolar vasodilation, collapse of peripheral vascular resistance (SVR), coronary hypoperfusion and cardiogenic/vasogenic shock.",
          },
          {
            tag: "Patient Parameters",
            title: `Golden Retriever · ${weight} kg`,
            desc: `Ingestion: 4-6 tablets of 10 mg (up to 60 mg) 45 minutes ago. Decontamination window still open (< 1 hour).`,
          },
        ],
        step1: {
          title: "Evidence Search · Canine Toxic Dose Retrieval",
          badge: "ASPCA / Merck Toxicology Data",
          desc: "The evidence search queries the toxicology databases: the therapeutic dose in dogs is 0.1 - 0.5 mg/kg; doses above 1.0 mg/kg trigger severe refractory hypotension and shock.",
          highlightLabel: "Canine Toxicology Thresholds:",
          highlightVal: "Toxic > 1.0 mg/kg · Therapeutic 0.1 - 0.5 mg/kg",
          highlightSub:
            "Risk of cardiovascular collapse and reflex brady/tachyarrhythmia",
        },
        step2: {
          title: "AI Clinical Engine · Worst-Case Scenario Calculation",
          badge: "Deterministic Risk Calculus",
          desc: "The AI engine estimates the risk assuming ingestion of the maximum number of tablets in the blister (6 tablets of 10 mg):",
          formula: `Worst case: (6 tabs × 10 mg) ÷ ${weight} kg = 60 mg ÷ ${weight} kg = ${dosePerKg} mg/kg (> 1.0 mg/kg: CRITICAL)`,
        },
        step3: {
          title: "Clinical Assessment of the Massive Overdose",
          badge: ">1 mg/kg Threshold Exceeded (2.14x)",
          badgeClass: "badge-error text-white animate-pulse",
          thresholds: [
            {
              label: "0.1 - 0.5 mg/kg",
              badge: "Therapeutic Dose",
              text: "Conventional pharmacological range for canine hypertension.",
            },
            {
              label: "0.5 - 1.0 mg/kg",
              badge: "Moderate Toxicity",
              text: "Marked hypotension, weakness, lethargy and reflex tachycardia.",
            },
            {
              label: "> 1.0 mg/kg",
              badge: "Refractory Shock",
              text: "Vascular collapse, fluid-unresponsive hypotensive shock, extreme bradycardia.",
            },
          ],
          alertBox: {
            title: `Critical Alert: Estimated dose ${dosePerKg} mg/kg (>200% of the toxic threshold)`,
            desc: "Avoid fluid overload with massive crystalloid boluses (risk of pulmonary edema from myocardial dysfunction).",
          },
        },
        step4: {
          badge: "Cardiovascular Emergency Protocol",
          directives: [
            {
              icon: "🚨",
              title: "Alert Status",
              color: "text-error",
              border: "border-error/30",
              heading: "Risk of Refractory Hypotensive Shock",
              desc: "Code Red. Invasive blood-pressure monitoring or continuous Doppler and ECG trace.",
            },
            {
              icon: "⚡",
              title: "Immediate Action",
              color: "text-secondary",
              border: "border-secondary/30",
              heading: `Emesis (< 1h) with Apomorphine (${apomorphineMg} mg / ${apomorphineMl} ml)`,
              desc: "Immediate emesis induction given the < 1h window. Then activated charcoal 1-2 g/kg in repeated doses.",
            },
            {
              icon: "🫀",
              title: "Hemodynamic Support",
              color: "text-primary",
              border: "border-primary/30",
              heading: "Vasopressors, Calcium Gluconate or ILE",
              desc: "No fluid overload! Calcium gluconate 10% (0.5-1.5 ml/kg slow IV), Norepinephrine or rescue Intravenous Lipid Emulsion (ILE).",
            },
          ],
        },
      };
    } else if (key === "rabbit") {
      const meloxicamDose = (weight * 0.75).toFixed(2);
      const meloxicamMl = ((weight * 0.75) / 5).toFixed(2);
      const metoclopramideDose = (weight * 0.5).toFixed(2);
      const metoclopramideMl = ((weight * 0.5) / 5).toFixed(2);
      return {
        key: "rabbit",
        title: "Case 3: The Exotic / Non-Conventional Animal (Orphan Species)",
        problemTitle:
          "1. The Pathophysiological Problem: Cecal Dysbiosis & Fast Metabolism in Lagomorphs",
        problemTag: "Emergency Medicine for Non-Conventional Animals",
        chemCards: [
          {
            tag: "Anatomy & Microbiome",
            title: "Cecotrophy & Fermentation",
            desc: "The rabbit relies entirely on cecal fermentation. Inappropriate use of antibiotics (penicillins, macrolides, cephalosporins) causes fatal Clostridium spiroforme dysbiosis.",
          },
          {
            tag: "Species-Specific Metabolism",
            title: "High Metabolic Rate",
            desc: "Rabbits have markedly higher hepatic and renal drug clearance than carnivores: analgesic doses (e.g. meloxicam) must be 3-5 times higher than those for dogs.",
          },
          {
            tag: "Patient Parameters",
            title: `Dwarf rabbit · ${weight} kg`,
            desc: "Gastrointestinal stasis for 18 hours: abdominal pain, no fecal output and anorexia. Risk of hypothermia and dehydration of the cecal mass.",
          },
        ],
        step1: {
          title:
            "Evidence Search · Exotic Formularies (BSAVA / Exotic Formulary)",
          badge: "BSAVA Exotics & Formulary",
          desc: "The evidence search selects only guidelines for exotic animals, excluding forbidden antibiotics and extracting the correct doses for motility and analgesia.",
          highlightLabel: "Strictly Forbidden Molecules:",
          highlightVal: "NO Penicillins, NO Macrolides, NO Lincosamides",
          highlightSub: "Lethal risk of Clostridium enterotoxemia",
        },
        step2: {
          title:
            "AI Clinical Engine · Species-Specific Weight-Based Drug Sheet",
          badge: "Species-Specific Microdosing",
          desc: "The AI engine calculates high-dose analgesia for lagomorphs and the combined prokinetic therapy:",
          formula: `Meloxicam: 0.75 mg/kg × ${weight} kg = ${meloxicamDose} mg (${meloxicamMl} ml) | Metoclopramide: 0.5 mg/kg × ${weight} kg = ${metoclopramideDose} mg (${metoclopramideMl} ml)`,
        },
        step3: {
          title: "Gastrointestinal Stasis Risk Stratification",
          badge: "Lagomorph Medical Urgency",
          badgeClass: "badge-warning text-base-content",
          thresholds: [
            {
              label: "< 12 Hours",
              badge: "Mild Stasis",
              text: "Reduced intake and fecal output, treatable on an outpatient basis.",
            },
            {
              label: "12 - 24 Hours",
              badge: "Moderate/Severe Stasis",
              text: "Cecal mass dehydration, intense abdominal pain, hypothermia.",
            },
            {
              label: "> 24 Hours",
              badge: "Torsion / Shock Risk",
              text: "Massive gastric distension, wall rupture or systemic enterotoxemia.",
            },
          ],
          alertBox: {
            title: "Stasis for 18 hours: Aggressive Pain Therapy Mandatory",
            desc: "Without adequate analgesia (Meloxicam), the pain-stasis vicious cycle does not stop.",
          },
        },
        step4: {
          badge: "Rabbit Emergency Therapy Sheet",
          directives: [
            {
              icon: "🚨",
              title: "Alert Status",
              color: "text-warning",
              border: "border-warning/30",
              heading: "Acute Gastrointestinal Stasis (18h)",
              desc: "First rule out mechanical gastric obstruction (palpation/X-ray). Maintain thermal support at 38.5°C.",
            },
            {
              icon: "⚡",
              title: "Analgesia & Prokinetics",
              color: "text-secondary",
              border: "border-secondary/30",
              heading: `Meloxicam (${meloxicamDose} mg) + Metoclopramide (${metoclopramideDose} mg)`,
              desc: `Meloxicam ${meloxicamDose} mg (${meloxicamMl} ml) SC q12-24h. Metoclopramide ${metoclopramideDose} mg (${metoclopramideMl} ml) SC q8h or Cisapride 0.5 mg/kg PO.`,
            },
            {
              icon: "💧",
              title: "Fluid Therapy & Nutrition",
              color: "text-primary",
              border: "border-primary/30",
              heading: "Hydration (90-120 ml/day) & Feeding",
              desc: "Pre-warmed Lactated Ringer's SC/IV (75-100 ml/kg/day). Assisted feeding with emergency herbivore formula (Critical Care).",
            },
          ],
        },
      };
    } else if (key === "vector") {
      const doxyDose = (weight * 10).toFixed(0);
      return {
        key: "vector",
        title:
          "Case 4: Differential Diagnosis of a Complex Clinical Sign (General Visit)",
        problemTitle:
          "1. The Clinical Problem: Shifting Lameness, Lymphadenopathy & Fever (39.8°C)",
        problemTag: "Vector-Borne Infectious Disease Diagnostics",
        chemCards: [
          {
            tag: "Complex Clinical Picture",
            title: "Non-Specific Signs & Ticks",
            desc: "Intermittent shifting lameness, generalized lymphadenopathy and acute fever at 39.8°C in a dog living in the hills with a history of tick removal.",
          },
          {
            tag: "Epidemiological Correlation",
            title: "Vector-Borne Diseases",
            desc: "Ticks (Ixodes ricinus, Rhipicephalus sanguineus) inoculate spirochetes and intracellular bacteria that trigger immune-mediated synovitis and vasculitis.",
          },
          {
            tag: "Patient Parameters",
            title: `German Shepherd, 4 years · ${weight} kg`,
            desc: "High febrile state (39.8°C), alternating bilateral joint tenderness and a state of severe lethargy.",
          },
        ],
        step1: {
          title:
            "Evidence Search · Epidemiological Reports & Vector-Borne Diseases",
          badge: "Vector-Borne Disease Panels",
          desc: "The evidence search analyzes epidemiological databases and CDC/ASPCA literature to cross-reference season, hill area and tick exposure.",
          highlightLabel: "Pathogens Investigated:",
          highlightVal:
            "Borrelia burgdorferi · Anaplasma phagocytophilum · Ehrlichia canis",
          highlightSub:
            "Tick-borne infection panel and immune-mediated polyarthritis",
        },
        step2: {
          title:
            "AI Clinical Engine · Probabilistic Differential Diagnosis Table",
          badge: "Probabilistic Clinical Ranking",
          desc: "The AI engine ranks the diagnostic hypotheses based on epidemiological prevalence and the symptom picture:",
          formula: `1. Borreliosis (Lyme) vs Anaplasmosis (78%) | 2. Immune-mediated polyarthritis (15%) | 3. Ehrlichiosis (7%)`,
        },
        step3: {
          title: "Stratification & Step-by-Step Diagnostic Pathway",
          badge: "Guided Integrated Diagnostics",
          badgeClass: "badge-primary text-white",
          thresholds: [
            {
              label: "Step 1: Serology",
              badge: "SNAP 4Dx Plus",
              text: "Rapid in-clinic whole-blood test (Borrelia, Anaplasma, Ehrlichia, Dirofilaria).",
            },
            {
              label: "Step 2: Synovial",
              badge: "Arthrocentesis",
              text: "Cytological examination of synovial fluid to confirm non-bacterial neutrophilic inflammation.",
            },
            {
              label: "Step 3: Function",
              badge: "Renal Profile",
              text: "Urinary UPC to rule out immune-complex nephropathy (Lyme Nephritis).",
            },
          ],
          alertBox: {
            title: "Primary Diagnosis: Lyme Disease vs Anaplasmosis",
            desc: "Immediate start of first-line empirical therapy while awaiting serological and culture results.",
          },
        },
        step4: {
          badge: "First-Line Therapeutic Protocol",
          directives: [
            {
              icon: "🚨",
              title: "Alert Status",
              color: "text-warning",
              border: "border-warning/30",
              heading: "Vector-Borne Febrile Syndrome / Arthritis",
              desc: "Tick isolation, antiparasitic prophylaxis and immediate 4Dx serological testing.",
            },
            {
              icon: "💊",
              title: "First-Line Therapy",
              color: "text-secondary",
              border: "border-secondary/30",
              heading: `Doxycycline ${doxyDose} mg/day (160 mg q12h)`,
              desc: `Doxycycline at 10 mg/kg/day for ${weight} kg = ${doxyDose} mg/day split into two doses for 28 days.`,
            },
            {
              icon: "⚠️",
              title: "Clinical Warning",
              color: "text-error",
              border: "border-error/30",
              heading: "ALWAYS Give with Food or Water",
              desc: "Strict clinical precaution: doxycycline capsules cause necrotizing esophagitis and stricture if not flushed down with food/water.",
            },
          ],
        },
      };
    } else {
      // Default: Chocolate Case
      const match = (patient?.sintomi || "").match(/(\d+)\s*g/i);
      const grams = match ? parseFloat(match[1]) : 150;
      const concMgG = 16.0;
      const totalLoad = grams * concMgG;
      const dosePerKg = (totalLoad / weight).toFixed(1);
      const apomorphineMg = (weight * 0.035).toFixed(2);
      const apomorphineMl = ((weight * 0.035) / 10).toFixed(3);

      return {
        key: "chocolate",
        title: "Main Case: Dark Bitter Chocolate Poisoning",
        problemTitle: "1. The Chemical Problem: Theobromine Toxicity & Purity",
        problemTag: "Methylxanthine Pharmacokinetics",
        chemCards: [
          {
            tag: "Active Toxic Principle",
            title: "Theobromine (mg/kg)",
            desc: "Purine alkaloid with slow hepatic elimination and extensive enterohepatic recirculation in dogs (half-life ~17.5h). Toxicity strictly depends on the dose per kg.",
          },
          {
            tag: "The Purity Rule",
            title: "Higher Purity = More Toxicity",
            desc: "The higher the percentage of solid cocoa, the higher the theobromine concentration per gram: dark bitter chocolate contains about 16.0 mg/g (4-5x compared to milk chocolate).",
          },
          {
            tag: "Clinical Case Parameters",
            title: `${weight} kg · ${grams}g Dark Bitter Chocolate`,
            desc: `Action window < 2 hours: active decontamination via rapid emesis induction.`,
          },
        ],
        step1: {
          title:
            "Evidence Search · Average Theobromine Concentration Retrieval",
          badge: "Evidence Search",
          desc: "The evidence search queries the official toxicology databases in real time (ASPCA, Merck Vet, BSAVA) and retrieves the average theobromine concentration per gram of dark bitter chocolate.",
          highlightLabel: "Validated Extracted Value:",
          highlightVal: "~16.0 mg theobromine / gram",
          highlightSub: "Dark chocolate 70-85% range: 14-18 mg/g",
        },
        step2: {
          title: "AI Clinical Engine · Deterministic Dose-per-kg Calculation",
          badge: "Reasoning",
          desc: "The AI engine reliably and deterministically calculates the ingested dose per body weight by applying the weight-based clinical formula:",
          formula: `(${grams}g × ${concMgG} mg/g) ÷ ${weight} kg = ${totalLoad} mg ÷ ${weight} kg = ${dosePerKg} mg/kg`,
        },
        step3: {
          title: "Clinical Assessment of Risk Thresholds",
          badge: ">60 mg/kg Threshold Exceeded",
          badgeClass: "badge-error text-white animate-pulse",
          thresholds: [
            {
              label: "20 mg/kg",
              badge: "Gastrointestinal",
              text: "Nausea, vomiting, diarrhea, polydipsia and abdominal distension appear.",
            },
            {
              label: "40 - 50 mg/kg",
              badge: "Cardiotoxic",
              text: "Marked tachycardia, ventricular premature complexes (VPC), sympathetic-driven arrhythmias.",
            },
            {
              label: "> 60 mg/kg",
              badge: "Severe Neurological",
              text: "Diffuse tremors, hyperactivity, tonic-clonic seizures and risk of irreversible collapse.",
            },
          ],
          alertBox: {
            title: `Analysis Result: Critical Threshold Exceeded (+${Math.max(0, Math.round(((dosePerKg - 60) / 60) * 100))}% beyond the seizure level)`,
            desc: `Calculated patient dose: ${dosePerKg} mg/kg. High cardiotoxic and neurological risk.`,
          },
        },
        step4: {
          badge: "Direct Emergency Care",
          directives: [
            {
              icon: "🚨",
              title: "Alert Status",
              color: "text-error",
              border: "border-error/30",
              heading: "High Cardiotoxic & Neurological Risk",
              desc: "Code Red / Critical Priority. High risk of tachyarrhythmias and acute seizures from massive overdose.",
            },
            {
              icon: "⚡",
              title: "Immediate Action",
              color: "text-secondary",
              border: "border-secondary/30",
              heading: `Emesis (< 2h) with Apomorphine (${apomorphineMg} mg / ${apomorphineMl} ml)`,
              desc: `Dose for ${weight} kg: ${apomorphineMg} mg (${apomorphineMl} ml of a 10 mg/ml vial IV or subconjunctival). Emesis in 2-5 min.`,
            },
            {
              icon: "🫀",
              title: "Specialist Monitoring",
              color: "text-primary",
              border: "border-primary/30",
              heading: "Continuous ECG Trace & Fluid Therapy",
              desc: "Continuous surveillance for ventricular arrhythmias, forced fluid therapy for renal clearance and activated charcoal q4-6h.",
            },
          ],
        },
      };
    }
  });

  function getInformationGaps() {
    if (
      artifactsData?.orchestrator &&
      Array.isArray(artifactsData.orchestrator.clinical_gaps) &&
      artifactsData.orchestrator.clinical_gaps.length > 0
    ) {
      return artifactsData.orchestrator.clinical_gaps.map((g, idx) => {
        const sev = (g.severity || "").toLowerCase();
        const isCritical =
          sev.includes("critic") ||
          sev.includes("high");
        return {
          id: idx + 1,
          icon: isCritical ? "🚨" : "⚠️",
          gap: g.title,
          desc: g.description,
          severity: isCritical ? "critical" : "high",
        };
      });
    }

    const key = currentCaseKey;
    if (key === "lily") {
      return [
        {
          id: 1,
          icon: "🌺",
          gap: "Botanical Identification of True Lilies (Lilium vs Hemerocallis)",
          desc: "Differentiation from plants with only mucosal toxicity (e.g. Spathiphyllum) versus true lilies that destroy the renal tubular epithelium.",
          severity: "critical",
        },
        {
          id: 2,
          icon: "⏱️",
          gap: "Continuous Diuresis Window for 48-72h",
          desc: "Forced intravenous diuresis with Lactated Ringer's for 48-72h before irreversible anuria sets in.",
          severity: "critical",
        },
        {
          id: 3,
          icon: "🧪",
          gap: "Early Renal Damage Markers (SDMA/Creatinine)",
          desc: "Baseline determination at T0 before azotemia rises to monitor the progression of tubular necrosis.",
          severity: "high",
        },
      ];
    } else if (key === "amlodipine") {
      return [
        {
          id: 1,
          icon: "💊",
          gap: "Canine Toxic Thresholds & Worst-Case Overdose",
          desc: "The therapeutic dose is 0.1-0.5 mg/kg; above 1.0 mg/kg an uncompensated hypotensive shock develops.",
          severity: "critical",
        },
        {
          id: 2,
          icon: "⏱️",
          gap: "Emesis Window (< 1h) & Extended-Release Drugs",
          desc: "Amlodipine absorption is gradual; immediate emesis with Apomorphine saves the patient from systemic absorption.",
          severity: "critical",
        },
        {
          id: 3,
          icon: "🫀",
          gap: "Calcium-Antagonist Shock Protocol (Calcium Gluconate / ILE)",
          desc: "Avoid fluid boluses that induce pulmonary edema; consider vasopressors, calcium gluconate and lipid emulsion.",
          severity: "high",
        },
      ];
    } else if (key === "rabbit") {
      return [
        {
          id: 1,
          icon: "🦠",
          gap: "Lagomorph Cecal Microbiome & Contraindicated Drugs",
          desc: "Strict exclusion of penicillins, ampicillin, cephalosporins and macrolides to prevent Clostridium enterotoxemia.",
          severity: "critical",
        },
        {
          id: 2,
          icon: "⚖️",
          gap: "Fast Lagomorph Pharmacokinetics & Meloxicam Dosing",
          desc: "Rabbits metabolize NSAIDs much faster than dogs: a dose of 0.5-1.0 mg/kg is needed to settle the paralytic ileus.",
          severity: "critical",
        },
        {
          id: 3,
          icon: "🔄",
          gap: "Gastric & Duodenal Prokinetics (Metoclopramide / Cisapride)",
          desc: "Coordinated stimulation of gastrointestinal motility after analgesia, once mechanical obstruction is ruled out.",
          severity: "high",
        },
      ];
    } else if (key === "vector") {
      return [
        {
          id: 1,
          icon: "🦟",
          gap: "Tick Epidemiological Panel (Borrelia, Anaplasma, Ehrlichia)",
          desc: "Correlation between tick removal in a hill area, intermittent shifting lameness and fever at 39.8°C.",
          severity: "high",
        },
        {
          id: 2,
          icon: "📊",
          gap: "Probabilistic Differential Diagnosis: Borreliosis vs IMPA",
          desc: "Differentiation between direct bacterial infection from spirochetes and secondary immune-mediated polyarthritis.",
          severity: "high",
        },
        {
          id: 3,
          icon: "⚠️",
          gap: "Doxycycline Administration Precautions",
          desc: "Doxycycline 10 mg/kg/day: clinical requirement to administer with food/water to prevent erosive esophagitis.",
          severity: "critical",
        },
      ];
    } else {
      return [
        {
          id: 1,
          icon: "🍫",
          gap: "Average Theobromine Concentration per Gram of Dark Chocolate",
          desc: "Toxicity depends on theobromine (mg/kg). The higher the purity, the higher the concentration: retrieve the value (16 mg/g).",
          severity: "critical",
        },
        {
          id: 2,
          icon: "⚖️",
          gap: "Deterministic Calculation of Ingested Toxic Load over 22 kg",
          desc: "Calculation of the ingested dose per kg and risk stratification against the 20 mg/kg, 40-50 mg/kg and >60 mg/kg thresholds.",
          severity: "critical",
        },
        {
          id: 3,
          icon: "💊",
          gap: "Emesis Protocol with Apomorphine & Enterohepatic Recirculation",
          desc: "Recent ingestion (< 2h): precise Apomorphine calculation in ml for 22 kg and serial activated charcoal every 4-6h.",
          severity: "high",
        },
      ];
    }
  }

  function getGeneratedQueries() {
    if (
      artifactsData?.orchestrator?.function_call?.parameters
    ) {
      const p = artifactsData.orchestrator.function_call.parameters;
      const queries = p.queries || p.target_queries;
      if (Array.isArray(queries) && queries.length > 0) {
        return queries;
      }
    }

    const key = currentCaseKey;
    if (key === "lily") {
      return [
        "site:aspca.org toxic plants feline nephrotoxic flowers Lilium Hemerocallis",
        "site:merckvetmanual.com acute renal failure cat lily intoxication fluid diuresis hours",
        "site:bsava.com cut flower toxicity domestic cat decontamination emesis contraindications",
        "site:ncbi.nlm.nih.gov feline lily toxicity tubular necrosis aggressive fluid therapy",
      ];
    } else if (key === "amlodipine") {
      return [
        "site:aspca.org canine amlodipine toxicity lethal dose calcium channel blocker",
        "site:merckvetmanual.com dog amlodipine overdose hypotension calcium gluconate lipid emulsion",
        "site:bsava.com canine apomorphine decontamination cardiovascular collapse amlodipine",
      ];
    } else if (key === "rabbit") {
      return [
        "site:bsava.com rabbit gastrointestinal stasis meloxicam dosage prokinetics",
        "site:merckvetmanual.com rabbit cecal dysbiosis clostridium enterotoxemia contraindicated antibiotics",
        "site:ncbi.nlm.nih.gov lagomorph meloxicam pharmacokinetics high clearance dosage",
      ];
    } else if (key === "vector") {
      return [
        "site:aspca.org canine vector borne disease shifting lameness lymphadenopathy fever",
        "site:merckvetmanual.com lyme disease borreliosis anaplasmosis dog joint fluid doxycycline",
        "site:bsava.com canine polyarthritis differential diagnosis doxycycline administration food",
      ];
    } else {
      return [
        "site:aspca.org dark bitter chocolate theobromine concentration mg per gram canine toxicity",
        "site:merckvetmanual.com dog chocolate poisoning cardiac arrhythmias threshold mg per kg",
        "site:bsava.com canine apomorphine emesis dosage per kg chocolate intoxication window 2 hours",
        "site:ncbi.nlm.nih.gov canine theobromine pharmacokinetics enterohepatic circulation fluid therapy",
      ];
    }
  }

  let urgencyBadgeClass = $derived.by(() => {
    const p = (patient?.priorita || "").toLowerCase();
    if (p === "critical" || p === "critica") return "badge-error text-white";
    if (p === "urgent" || p === "urgente")
      return "badge-warning text-base-content";
    return "badge-success text-white";
  });

  let stepList = $derived([
    { num: 1, label: t("orchestrator.substep1"), tag: "Retrieval" },
    { num: 2, label: t("orchestrator.substep2"), tag: "Calculation" },
    { num: 3, label: t("orchestrator.substep3"), tag: "Assessment" },
    { num: 4, label: t("orchestrator.substep4"), tag: "Emergency" },
  ]);

  function selectSubStep(s) {
    activeSubStep = s;
  }
</script>

<div
  class="card bg-base-100/90 shadow-2xl border border-base-300 backdrop-blur-md transition-all duration-500 ease-in-out"
  in:fly={{ y: 24, duration: 450, easing: cubicInOut }}
>
  <div class="card-body p-6 lg:p-8 space-y-6">
    <!-- Header Step 2 Component -->
    <ClinicalAssessmentHeader
      {patient}
      priority={currentCasePriority}
      {urgencyBadgeClass}
      hasLiveData={Boolean(artifactsData?.orchestrator)}
      isRunning={isAnalyzing}
      modelUsed={artifactsData?.orchestrator?.model || ""}
    />

    <!-- Live Execution Status Bar Component -->
    <ClinicalAssessmentLiveStatus
      {runStatus}
      {runId}
      {elapsedSeconds}
      {stepNodes}
      {logsText}
      {errorMessage}
      {artifactsData}
      {onOpenDagu}
    />

    <!-- Interactive Clinical Case Selector Component -->
    <OrchestratorCaseSelector
      {clinicalCases}
      {currentCaseKey}
      onSelectCase={selectCasePreset}
    />

    <!-- Chemical & Pathophysiological Problem Breakdown Component -->
    <OrchestratorProblemCard {caseData} />

    <!-- 2. What VetSentinel Does (Coordinated Steps) -->
    <div class="space-y-4 pt-2">
      <div
        class="flex flex-col sm:flex-row sm:items-center justify-between gap-3"
      >
        <div class="flex items-center gap-2">
          <span class="text-2xl">⚡</span>
          <div>
            <h3
              class="text-sm lg:text-base font-black text-base-content font-display uppercase tracking-wide"
            >
              {t("orchestrator.workflowTitle")}
            </h3>
            <p class="text-xs text-base-content/60">
              {t("orchestrator.workflowSubtitle")}
            </p>
          </div>
        </div>

        <!-- View Switcher -->
        <div class="join">
          <button
            type="button"
            class="btn btn-xs join-item font-bold cursor-pointer {activeTab ===
            'pipeline'
              ? 'btn-secondary text-white'
              : 'btn-ghost'}"
            onclick={() => (activeTab = "pipeline")}
          >
            📋 {t("orchestrator.tabWorkflow")}
          </button>
          <button
            type="button"
            class="btn btn-xs join-item font-bold cursor-pointer {activeTab ===
            'gaps'
              ? 'btn-secondary text-white'
              : 'btn-ghost'}"
            onclick={() => (activeTab = "gaps")}
          >
            🔍 {t("orchestrator.tabGaps")} ({getInformationGaps().length})
          </button>
          <button
            type="button"
            class="btn btn-xs join-item font-bold cursor-pointer {activeTab ===
            'queries'
              ? 'btn-secondary text-white'
              : 'btn-ghost'}"
            onclick={() => (activeTab = "queries")}
          >
            🎯 {t("orchestrator.tabSources")} ({getGeneratedQueries().length})
          </button>
        </div>
      </div>

      {#if activeTab === "pipeline"}
        <!-- Sub-step coordinator bar -->
        <div class="flex items-center justify-between gap-2 p-2 rounded-xl bg-base-200/50 border border-base-300 flex-wrap text-xs">
          <div class="flex items-center gap-1.5 flex-wrap">
            <span class="font-bold text-base-content/70 text-[11px] uppercase tracking-wider pl-1 font-label">
              {t("orchestrator.stepNavigator")}
            </span>
            <button
              type="button"
              class="btn btn-xs font-mono font-bold cursor-pointer transition-all duration-200 {activeSubStep === 'all' ? 'btn-neutral text-white shadow-xs' : 'btn-ghost'}"
              onclick={() => selectSubStep('all')}
            >
              {t("orchestrator.allSteps")}
            </button>
            {#each stepList as s}
              <button
                type="button"
                class="btn btn-xs gap-1 font-bold cursor-pointer transition-all duration-200 {activeSubStep === s.num ? 'btn-secondary text-white shadow-xs' : 'btn-ghost'}"
                onclick={() => selectSubStep(s.num)}
              >
                <span class="w-4 h-4 rounded-full bg-base-100/30 flex items-center justify-center font-mono text-[10px]">{s.num}</span>
                <span>{s.label}</span>
              </button>
            {/each}
          </div>

          <div class="text-[11px] font-mono text-base-content/50 pr-1">
            {#if activeSubStep === 'all'}
              <span>{t("orchestrator.flowIndicator")}</span>
            {:else}
              <span>{t("orchestrator.focusStep", { step: activeSubStep })}</span>
            {/if}
          </div>
        </div>

        <!-- The 4 Coordinated Step Components -->
        <div class="space-y-3" in:fade={{ duration: 300, easing: cubicInOut }}>
          <!-- STEP 1: Tavily Retrieval & Evidence Search Component -->
          {#if activeSubStep === "all" || activeSubStep === 1}
            <OrchestratorEvidenceStep
              stepData={caseData?.step1}
              isCurrent={activeSubStep === 1}
              stepNumber={1}
              onSelectStep={selectSubStep}
            />
          {/if}

          <!-- STEP 2: AI Clinical Engine & Dosing Calculation Component -->
          {#if activeSubStep === "all" || activeSubStep === 2}
            <OrchestratorCalculationStep
              stepData={caseData?.step2}
              {patient}
              isCurrent={activeSubStep === 2}
              stepNumber={2}
              onSelectStep={selectSubStep}
            />
          {/if}

          <!-- STEP 3: Risk Threshold Assessment & Alert Component -->
          {#if activeSubStep === "all" || activeSubStep === 3}
            <OrchestratorRiskStep
              stepData={caseData?.step3}
              isCurrent={activeSubStep === 3}
              stepNumber={3}
              onSelectStep={selectSubStep}
            />
          {/if}

          <!-- STEP 4: Emergency Care & Action Directives Component -->
          {#if activeSubStep === "all" || activeSubStep === 4}
            <OrchestratorDirectivesStep
              stepData={caseData?.step4}
              isCurrent={activeSubStep === 4}
              stepNumber={4}
              onSelectStep={selectSubStep}
            />
          {/if}
        </div>
      {:else if activeTab === "gaps"}
        <!-- Information Gaps View (Separate Component) -->
        <OrchestratorGapsTab gaps={getInformationGaps()} />
      {:else if activeTab === "queries"}
        <!-- Targeted Queries View (Separate Component) -->
        <OrchestratorQueriesTab queries={getGeneratedQueries()} />
      {/if}
    </div>

    <!-- Actions Footer -->
    <div
      class="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-base-200"
    >
      <button
        type="button"
        class="btn btn-ghost btn-sm gap-2 text-base-content/70 hover:text-base-content cursor-pointer"
        onclick={onBack}
      >
        <svg
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M10 19l-7-7m0 0l7-7m-7 7h18"
          />
        </svg>
        <span>{t("common.backToTriage")}</span>
      </button>

      <div class="flex items-center gap-3 w-full sm:w-auto">
        {#if onOpenDagu}
          <button
            type="button"
            class="btn btn-warning btn-outline btn-sm gap-1.5 shadow-sm font-bold cursor-pointer hover:scale-105 transition-transform"
            onclick={onOpenDagu}
            title={t("common.rerunAnalysis")}
          >
            <span>🔬</span>
            <span>{t("common.rerunAnalysis")}</span>
          </button>
        {/if}

        <button
          type="button"
          class="btn btn-primary px-8 gap-2 shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 ease-in-out w-full sm:w-auto font-bold cursor-pointer"
          onclick={onNext}
        >
          <span>{t("common.continueToSources")}</span>
          <svg
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M14 5l7 7m0 0l-7 7m7-7H3"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</div>
