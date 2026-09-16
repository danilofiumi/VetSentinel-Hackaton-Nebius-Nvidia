<script>
  import { fly, slide, scale } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";
  import Image from "./Image.svelte";
  import { t } from "$lib";

  let {
    patient = $bindable(),
    artifactsData = null,
    runStatus = "idle",
    elapsedSeconds = 0,
    onTriggerAnalysis = null,
    onStopAnalysis = null,
    onStopAndRetrigger = null,
    onScrollToResults = null,
    onNext = null,
    isResultsAvailable = false,
  } = $props();

  const speciesList = [
    {
      id: "Cat",
      label: "Cat",
      sub: "Feline",
      image: "/images/triage/cat.png",
      icon: "🐱",
      defaultBreeds: [
        "European Shorthair",
        "Maine Coon",
        "Persian",
        "British Shorthair",
        "Siamese",
        "Ragdoll",
        "Domestic Shorthair",
      ],
      defaultWeight: 4.0,
    },
    {
      id: "Dog",
      label: "Dog",
      sub: "Canine",
      image: "/images/triage/dog.png",
      icon: "🐶",
      defaultBreeds: [
        "Labrador Retriever",
        "German Shepherd",
        "Golden Retriever",
        "French Bulldog",
        "Border Collie",
        "Beagle",
        "Mixed Breed",
      ],
      defaultWeight: 22.0,
    },
    {
      id: "Ferret",
      label: "Ferret",
      sub: "Mustelid",
      image: "/images/triage/ferret.png",
      icon: "🦡",
      defaultBreeds: [
        "Standard Domestic",
        "Black Sable",
        "Albino",
        "Cinnamon",
        "Angora",
      ],
      defaultWeight: 1.2,
    },
    {
      id: "Rabbit",
      label: "Rabbit",
      sub: "Lagomorph",
      image: "/images/triage/rabbit.png",
      icon: "🐰",
      defaultBreeds: [
        "Holland Lop",
        "Netherland Dwarf",
        "Flemish Giant",
        "Lionhead",
        "Rex",
      ],
      defaultWeight: 2.5,
    },
    {
      id: "Horse",
      label: "Horse",
      sub: "Equine",
      image: "/images/triage/horse.png",
      icon: "🐴",
      defaultBreeds: [
        "Quarter Horse",
        "Thoroughbred",
        "Arabian",
        "Warmblood",
        "Pony",
      ],
      defaultWeight: 480.0,
    },
    {
      id: "Exotic",
      label: "Exotic",
      sub: "Reptile / Other",
      image: "/images/triage/exotic.png",
      icon: "🦎",
      defaultBreeds: [
        "Bearded Dragon",
        "Leopard Gecko",
        "Ball Python",
        "Red-Eared Slider",
        "Green Iguana",
      ],
      defaultWeight: 0.6,
    },
  ];

  const presets = [
    {
      title: "Dog · Dark Bitter Chocolate Ingestion (22.0 kg)",
      shortTitle: "Dog · Dark Chocolate",
      subtitle: "Theobromine Neuro & Cardiotoxicity",
      badge: "Critical",
      badgeColor: "badge-error",
      specie: "Dog",
      razza: "Labrador Retriever",
      peso: 22.0,
      image: "/images/triage/dog.png",
      sintomi:
        "22.0 kg Labrador Retriever, Dark Chocolate / Theobromine ingestion (150g dark chocolate ~1h ago). Patient is tachycardic with Tremors & Seizures and Tachycardia (>160 bpm).",
    },
    {
      title: "Cat · Unknown Lily Houseplant (3.5 kg)",
      shortTitle: "Cat · Lily Leaves",
      subtitle: "Feline Acute Tubular Necrosis Risk",
      badge: "Critical",
      badgeColor: "badge-error",
      specie: "Cat",
      razza: "European Shorthair",
      peso: 3.5,
      image: "/images/triage/cat.png",
      sintomi:
        "3.5 kg European Shorthair, Lilium / Cut Flower Ingestion (Easter Lily leaves). Excessive Hypersalivation, Acute Vomiting (x3+), and Severe Lethargy & Stupor.",
    },
    {
      title: "Dog · Human Amlodipine 10mg Overdose (28.0 kg)",
      shortTitle: "Dog · Amlodipine Overdose",
      subtitle: "Calcium Channel Blocker Severe Hypotension",
      badge: "Critical",
      badgeColor: "badge-error",
      specie: "Dog",
      razza: "Golden Retriever",
      peso: 28.0,
      image: "/images/triage/dog.png",
      sintomi:
        "28.0 kg Golden Retriever, Human NSAID / Ibuprofen Ingestion (Amlodipine 10mg blister pack ~45m ago). High risk of refractory hypotension, Severe Lethargy & Stupor, and acute shock.",
    },
    {
      title: "Rabbit · GI Stasis in Orphan Species (1.2 kg)",
      shortTitle: "Rabbit · GI Stasis",
      subtitle: "Cecal Dysbiosis Prevention & Prokinetics",
      badge: "Urgent",
      badgeColor: "badge-warning",
      specie: "Rabbit",
      razza: "Holland Lop",
      peso: 1.2,
      image: "/images/triage/rabbit.png",
      sintomi:
        "1.2 kg Holland Lop dwarf rabbit with Acute GI Stasis & Anorexia: no fecal pellet production for 18 hours and Severe Lethargy & Stupor.",
    },
    {
      title: "Dog · Tick-Borne Migrating Lameness (32.0 kg)",
      shortTitle: "Dog · Tick Lameness",
      subtitle: "Vector-Borne Differential & Doxycycline",
      badge: "Urgent",
      badgeColor: "badge-warning",
      specie: "Dog",
      razza: "German Shepherd",
      peso: 32.0,
      image: "/images/triage/dog.png",
      sintomi:
        "32.0 kg German Shepherd (4yo), intermittent migrating lameness and fever at 39.8°C. Severe Lethargy & Stupor with history of frequent tick bites.",
    },
  ];

  // Chips grouped by clinical category for easy navigation.
  // Toxin chips can carry `related` refinement chips that only appear
  // once the parent chip is selected (e.g. chocolate → cocoa purity).
  const chipCategories = [
    {
      id: "toxins",
      title: "Toxin / Ingestion Source",
      icon: "☠️",
      chips: [
        {
          id: "chocolate",
          label: "Dark Chocolate / Theobromine",
          icon: "🍫",
          keywords: ["chocolate", "theobromine", "cioccolato", "cocoa"],
          related: [
            {
              id: "choc-milk",
              label: "Milk Chocolate (~10% cocoa)",
              icon: "🥛",
            },
            {
              id: "choc-dark",
              label: "Dark Chocolate (~50% cocoa)",
              icon: "🍫",
            },
            {
              id: "choc-extra",
              label: "Extra-Dark (~70–85% cocoa)",
              icon: "🌑",
            },
            {
              id: "choc-baking",
              label: "Baking Chocolate / Cocoa Powder (~100%)",
              icon: "⚫",
            },
            {
              id: "choc-amount",
              label: "Large volume ingested (>100 g)",
              icon: "⚖️",
            },
          ],
        },
        {
          id: "grapes",
          label: "Grapes / Raisins (Nephrotoxic)",
          icon: "🍇",
          keywords: ["grape", "raisin", "uva", "sultana"],
          related: [
            {
              id: "grape-few",
              label: "A few grapes / small amount",
              icon: "🔹",
            },
            { id: "grape-handful", label: "Handful (~10–20)", icon: "✋" },
            { id: "grape-large", label: "Large quantity ingested", icon: "🪣" },
          ],
        },
        {
          id: "xylitol",
          label: "Xylitol / Sweetener (Hypoglycemia)",
          icon: "🍬",
          keywords: ["xylitol", "sweetener", "birch sugar"],
          related: [
            { id: "xyl-gum", label: "Source: sugar-free gum", icon: "🫧" },
            { id: "xyl-pb", label: "Source: peanut butter", icon: "🥜" },
            {
              id: "xyl-baked",
              label: "Source: baked goods / candy",
              icon: "🧁",
            },
          ],
        },
        {
          id: "lilium",
          label: "Lilium / Cut Flower Ingestion",
          icon: "🌺",
          keywords: ["lilium", "lily", "cut flower", "bouquet"],
          related: [
            { id: "lily-leaves", label: "Part: leaves / petals", icon: "🌿" },
            {
              id: "lily-pollen",
              label: "Part: pollen (groomed from fur)",
              icon: "🌼",
            },
            { id: "lily-water", label: "Part: vase / pot water", icon: "🏺" },
          ],
        },
        {
          id: "allium",
          label: "Onion / Garlic (Allium)",
          icon: "🧅",
          keywords: ["onion", "garlic", "allium", "chive", "leek"],
        },
        {
          id: "nsaid",
          label: "Human NSAID / Analgesic",
          icon: "💊",
          keywords: ["nsaid", "analgesic", "ibuprofen", "naproxen", "aspirin"],
          related: [
            { id: "nsaid-ibu", label: "Drug: Ibuprofen", icon: "💊" },
            { id: "nsaid-nap", label: "Drug: Naproxen", icon: "💊" },
            {
              id: "nsaid-asa",
              label: "Drug: Aspirin / Salicylate",
              icon: "💊",
            },
            {
              id: "nsaid-amlo",
              label: "Drug: Amlodipine (Ca-channel blocker)",
              icon: "🫀",
            },
          ],
        },
        {
          id: "paracetamol",
          label: "Paracetamol / Acetaminophen",
          icon: "🩹",
          keywords: ["paracetamol", "acetaminophen", "tylenol"],
        },
        {
          id: "antifreeze",
          label: "Ethylene Glycol / Antifreeze",
          icon: "🧊",
          keywords: ["ethylene glycol", "antifreeze", "coolant"],
        },
        {
          id: "rodenticide",
          label: "Rodenticide / Rat Poison",
          icon: "🧪",
          keywords: ["rodenticide", "rat poison", "topicide"],
          related: [
            {
              id: "rod-antico",
              label: "Type: Anticoagulant (warfarin-like)",
              icon: "🩸",
            },
            {
              id: "rod-brome",
              label: "Type: Bromethalin (neurotoxic)",
              icon: "🧠",
            },
            {
              id: "rod-chole",
              label: "Type: Cholecalciferol (Vit D3)",
              icon: "🦴",
            },
          ],
        },
        {
          id: "cannabis",
          label: "Cannabis / THC Toxicosis",
          icon: "🌿",
          keywords: ["cannabis", "thc", "marijuana", "weed", "edible"],
        },
        {
          id: "metaldehyde",
          label: "Snail Bait / Metaldehyde",
          icon: "🐌",
          keywords: ["metaldehyde", "snail bait", "slug bait", "molluscicide"],
        },
        {
          id: "permethrin",
          label: "Permethrin / Pyrethroid (Feline)",
          icon: "🐛",
          keywords: ["permethrin", "pyrethroid", "pyrethrin", "spot-on"],
        },
      ],
    },
    {
      id: "neuro",
      title: "Neurological Signs",
      icon: "🧠",
      chips: [
        {
          id: "tremors",
          label: "Tremors & Seizures",
          icon: "⚡",
          keywords: [
            "tremor",
            "tremors",
            "seizure",
            "seizures",
            "convuls",
            "twitch",
          ],
        },
        {
          id: "ataxia",
          label: "Ataxia / Incoordination",
          icon: "🌀",
          keywords: ["ataxia", "incoordination", "wobbly", "disoriented"],
        },
        {
          id: "lethargy",
          label: "Severe Lethargy & Stupor",
          icon: "💤",
          keywords: ["lethargy", "lethargic", "stupor", "depress", "weakness"],
        },
        {
          id: "blindness",
          label: "Acute Blindness / Mydriasis",
          icon: "👁️",
          keywords: ["blindness", "blind", "mydriasis", "dilated pupil"],
        },
      ],
    },
    {
      id: "gi",
      title: "Gastrointestinal Signs",
      icon: "🍽️",
      chips: [
        {
          id: "vomiting",
          label: "Acute Vomiting (x3+)",
          icon: "🤮",
          keywords: ["vomit", "vomiting", "emesis"],
        },
        {
          id: "diarrhea",
          label: "Diarrhea / Hematochezia",
          icon: "💩",
          keywords: ["diarrhea", "diarrhoea", "hematochezia", "bloody stool"],
        },
        {
          id: "hypersalivation",
          label: "Excessive Hypersalivation",
          icon: "💧",
          keywords: [
            "hypersalivation",
            "salivation",
            "drool",
            "drooling",
            "ptyalism",
          ],
        },
        {
          id: "stasis",
          label: "Acute GI Stasis & Anorexia",
          icon: "🌾",
          keywords: [
            "stasis",
            "anorexia",
            "anorexic",
            "fecal",
            "gastrointestinal",
          ],
        },
        {
          id: "colic",
          label: "Equine Colic & Abdominal Pain",
          icon: "🐴",
          keywords: ["colic", "abdominal pain", "pawing", "sweating"],
        },
      ],
    },
    {
      id: "cardioresp",
      title: "Cardiovascular / Respiratory",
      icon: "🫀",
      chips: [
        {
          id: "tachycardia",
          label: "Tachycardia (>160 bpm)",
          icon: "🫀",
          keywords: ["tachycardia", "tachycardic", "heart rate", "bpm"],
        },
        {
          id: "bradycardia",
          label: "Bradycardia / Weak Pulse",
          icon: "💗",
          keywords: ["bradycardia", "bradycardic", "weak pulse", "slow heart"],
        },
        {
          id: "dyspnea",
          label: "Dyspnea / Labored Breathing",
          icon: "🫁",
          keywords: ["dyspnea", "breathing", "respiratory", "tachypnea"],
        },
        {
          id: "mucous",
          label: "Pale / Cyanotic Mucous Membranes",
          icon: "🩸",
          keywords: [
            "pale",
            "cyanotic",
            "cyanosis",
            "mucous membrane",
            "gum color",
          ],
        },
      ],
    },
    {
      id: "systemic",
      title: "Systemic & Other Signs",
      icon: "🌡️",
      chips: [
        {
          id: "hyperthermia",
          label: "Hyperthermia / Fever (>39.5°C)",
          icon: "🔥",
          keywords: ["hyperthermia", "fever", "pyrexia", "hot"],
        },
        {
          id: "hypothermia",
          label: "Hypothermia / Cold Temp",
          icon: "❄️",
          keywords: [
            "hypothermia",
            "cold temp",
            "hypotherm",
            "low temperature",
          ],
        },
        {
          id: "collapse",
          label: "Collapse / Hypovolemic Shock",
          icon: "🥴",
          keywords: [
            "collapse",
            "shock",
            "hypovolemic",
            "syncope",
            "unresponsive",
          ],
        },
        {
          id: "metabolic",
          label: "Metabolic Bone Disease",
          icon: "🦎",
          keywords: ["metabolic", "calcium deficiency", "mbd", "bone disease"],
        },
        {
          id: "hematuria",
          label: "Hematuria / Pigmenturia",
          icon: "🚽",
          keywords: [
            "hematuria",
            "pigmenturia",
            "blood in urine",
            "dark urine",
          ],
        },
      ],
    },
    {
      id: "timeline",
      title: "Ingestion Timeline",
      icon: "⏱️",
      chips: [
        {
          id: "t-recent",
          label: "Ingestion <30 min ago",
          icon: "⏱️",
          keywords: ["<30 min", "just ingested", "minutes ago"],
        },
        {
          id: "t-1h",
          label: "Ingestion ~1h ago",
          icon: "🕐",
          keywords: ["1h ago", "1 hour ago", "an hour ago"],
        },
        {
          id: "t-hours",
          label: "Ingestion 2–6h ago",
          icon: "🕓",
          keywords: ["2-6h", "hours ago", "several hours"],
        },
        {
          id: "t-unknown",
          label: "Unknown ingestion time",
          icon: "❓",
          keywords: ["unknown time", "unknown ingestion", "time unknown"],
        },
      ],
    },
  ];

  let currentSpecies = $derived(
    speciesList.find((s) => s.id === patient.specie) || speciesList[0],
  );

  let weightLbs = $derived((patient.peso * 2.20462).toFixed(1));

  let sizeCategory = $derived.by(() => {
    const w = patient.peso;
    if (w < 1.0) return { label: "Micro / Pocket Pet", color: "badge-accent" };
    if (w <= 5.0)
      return { label: "Small / Feline Size", color: "badge-primary" };
    if (w <= 15.0) return { label: "Medium Small", color: "badge-secondary" };
    if (w <= 35.0) return { label: "Large Canine", color: "badge-info" };
    return { label: "Giant / Large Animal", color: "badge-warning" };
  });

  let activePresetTitle = $state(null);
  let previousBreed = $state(patient?.razza || "European Shorthair");
  let previousWeight = $state(patient?.peso || 4.0);

  // Centralized demographics & prompt synchronization to guarantee maximum sync between UI selections and textarea
  function syncDemographicsToPrompt(newWeight, newBreed, newSpecies) {
    const cleanBreed = (newBreed || "").trim();
    const cleanSpecies = (newSpecies || "").trim();
    const cleanWeight =
      typeof newWeight === "number" ? newWeight : parseFloat(newWeight);

    if (isNaN(cleanWeight) || cleanWeight <= 0) return;

    const oldBreed = previousBreed;
    previousBreed = cleanBreed || cleanSpecies;
    previousWeight = cleanWeight;

    if (!patient.sintomi || !patient.sintomi.trim()) {
      patient.sintomi = `${cleanWeight} kg ${cleanBreed || cleanSpecies}, `;
      return;
    }

    let text = patient.sintomi;

    // 1. Sync weight: replace the first occurrence of weight
    const weightRegex = /\b\d+(?:\.\d+)?\s*kg\b/i;
    if (weightRegex.test(text)) {
      text = text.replace(weightRegex, `${cleanWeight} kg`);
    } else {
      text = `${cleanWeight} kg ${cleanBreed || cleanSpecies}, ` + text;
    }

    // 2. Sync breed / species without leaving residual tokens
    let replaced = false;

    if (oldBreed && oldBreed.trim() && text.includes(oldBreed.trim())) {
      text = text.replace(oldBreed.trim(), cleanBreed || cleanSpecies);
      replaced = true;
    }

    if (!replaced) {
      for (const sp of speciesList) {
        for (const b of sp.defaultBreeds) {
          if (text.includes(b)) {
            text = text.replace(b, cleanBreed || cleanSpecies);
            replaced = true;
            break;
          }
        }
        if (replaced) break;
      }
    }

    if (!replaced) {
      for (const sp of speciesList) {
        const spRegex = new RegExp(`\\b${sp.id}\\b`, "i");
        if (spRegex.test(text)) {
          text = text.replace(spRegex, cleanBreed || cleanSpecies);
          replaced = true;
          break;
        }
      }
    }

    patient.sintomi = text;
  }

  function syncWeightToTextarea(newWeight) {
    const val =
      typeof newWeight === "number" ? newWeight : parseFloat(newWeight);
    if (isNaN(val) || val <= 0) return;
    patient.peso = val;
    syncDemographicsToPrompt(val, patient.razza, patient.specie);
  }

  function syncBreedToTextarea(newBreed) {
    if (!newBreed || !newBreed.trim()) return;
    patient.razza = newBreed.trim();
    syncDemographicsToPrompt(patient.peso, newBreed.trim(), patient.specie);
  }

  function selectBreed(breed) {
    patient.razza = breed;
    syncDemographicsToPrompt(patient.peso, breed, patient.specie);
  }

  function selectSpecies(sp) {
    patient.specie = sp.id;
    patient.peso = sp.defaultWeight;
    patient.razza = sp.defaultBreeds[0];

    // If switching species while a preset of a different species was loaded, clear active preset
    if (activePresetTitle) {
      const matchPreset = presets.find(
        (p) => (p.shortTitle || p.title) === activePresetTitle,
      );
      if (matchPreset && matchPreset.specie !== sp.id) {
        activePresetTitle = null;
      }
    }

    syncDemographicsToPrompt(sp.defaultWeight, sp.defaultBreeds[0], sp.id);
  }

  function applyPreset(p) {
    activePresetTitle = p.shortTitle || p.title;
    patient.specie = p.specie;
    patient.razza = p.razza;
    patient.peso = p.peso;
    patient.priorita = ""; // Determined dynamically by AI during diagnosis phase
    patient.sintomi = p.sintomi;
    previousBreed = p.razza;
    previousWeight = p.peso;
  }

  function resetPresetToManual() {
    activePresetTitle = null;
    patient.peso = currentSpecies.defaultWeight;
    patient.razza = currentSpecies.defaultBreeds[0];
    patient.priorita = "";
    previousBreed = currentSpecies.defaultBreeds[0];
    previousWeight = currentSpecies.defaultWeight;
    patient.sintomi = `${patient.peso} kg ${patient.razza}, `;
  }

  function clearIntakeValues() {
    activePresetTitle = null;
    patient.priorita = "";
    patient.sintomi = `${patient.peso} kg ${patient.razza}, `;
  }

  function handleTextareaInput(e) {
    const text = e.currentTarget.value;
    patient.sintomi = text;

    // Modifying the textarea breaks out of strict preset mode into manual editing
    if (activePresetTitle) {
      const matchPreset = presets.find(
        (p) => (p.shortTitle || p.title) === activePresetTitle,
      );
      if (!matchPreset || matchPreset.sintomi !== text) {
        activePresetTitle = null;
      }
    }

    // Bidirectional sync: parse weight from textarea
    const weightMatch = text.match(/\b(\d+(?:\.\d+)?)\s*kg\b/i);
    if (weightMatch) {
      const parsed = parseFloat(weightMatch[1]);
      if (
        !isNaN(parsed) &&
        parsed > 0 &&
        parsed <= 1000 &&
        parsed !== patient.peso
      ) {
        patient.peso = parsed;
        previousWeight = parsed;
      }
    }

    // Bidirectional sync: detect breed if typed
    for (const sp of speciesList) {
      for (const b of sp.defaultBreeds) {
        if (text.includes(b) && patient.razza !== b) {
          patient.razza = b;
          patient.specie = sp.id;
          previousBreed = b;
          break;
        }
      }
    }
  }

  function adjustWeight(delta) {
    const val = parseFloat((patient.peso + delta).toFixed(1));
    if (val >= 0.1) {
      syncWeightToTextarea(val);
    }
  }

  function isSymptomUsed(chip) {
    if (!patient.sintomi) return false;
    const text = patient.sintomi.toLowerCase();
    if (text.includes(chip.label.toLowerCase())) return true;
    if (
      chip.keywords &&
      chip.keywords.some((kw) => text.includes(kw.toLowerCase()))
    ) {
      return true;
    }
    return false;
  }

  function toggleSymptom(chip) {
    if (activePresetTitle) {
      activePresetTitle = null;
    }
    if (!patient.sintomi) {
      patient.sintomi = `${patient.peso} kg ${patient.razza || patient.specie}, ${chip.label}`;
      return;
    }
    if (isSymptomUsed(chip)) {
      const escaped = chip.label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      const pattern = new RegExp(`(,?\\s*${escaped}|${escaped}\\s*,?)`, "i");
      let updated = patient.sintomi.replace(pattern, "").trim();

      // If exact label wasn't directly found, remove matching keywords
      if (updated === patient.sintomi && chip.keywords) {
        for (const kw of chip.keywords) {
          const kwEscaped = kw.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
          const kwPattern = new RegExp(
            `(,\\s*\\b${kwEscaped}\\b[^,.]*|\\b${kwEscaped}\\b[^,.]*\\s*,?)`,
            "i",
          );
          updated = updated.replace(kwPattern, "").trim();
        }
      }

      if (updated.startsWith(",")) updated = updated.slice(1).trim();
      if (updated.endsWith(",")) updated = updated.slice(0, -1).trim();
      patient.sintomi = updated;
    } else {
      patient.sintomi = patient.sintomi.trim()
        ? `${patient.sintomi.trim()}, ${chip.label}`
        : `${patient.peso} kg ${patient.razza || patient.specie}, ${chip.label}`;
    }
  }

  function appendSymptom(chip) {
    toggleSymptom(chip);
  }
</script>

<div
  class="card bg-base-100/85 shadow-2xl border border-base-300 backdrop-blur-md transition-all duration-500 ease-in-out"
  in:fly={{ y: 24, duration: 450, easing: cubicInOut }}
>
  <div class="card-body p-6 lg:p-8 space-y-7">
    <!-- Header Step 1 -->
    <div
      class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-base-200 pb-5"
    >
      <div>
        <div
          class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-primary font-label"
        >
          <span class="inline-block w-2.5 h-2.5 rounded-full bg-primary"></span>
          {t("triage.stepBadge")}
        </div>
        <h2
          class="text-2xl lg:text-3xl font-black tracking-tight text-base-content font-display mt-1"
        >
          {t("triage.title")}
        </h2>
        <p class="text-sm text-base-content/70 mt-0.5">
          {t("triage.subtitle")}
        </p>
      </div>

      <!-- Automated AI Triage Assessment Indicator -->
      <div class="flex flex-col sm:items-end gap-1.5">
        <div
          class="flex items-center justify-between sm:justify-end gap-2 w-full"
        >
          <span
            class="text-[11px] font-bold uppercase tracking-wider text-base-content/60 font-label flex items-center gap-1.5"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"
            ></span>
            {t("triage.priorityAssessment")}
          </span>
          {#if patient.priorita}
            <span
              class="text-[10px] font-mono font-bold uppercase px-2.5 py-0.5 rounded-full border transition-all duration-300 ease-in-out {patient.priorita ===
              'critical'
                ? 'bg-error/15 text-error border-error/30'
                : patient.priorita === 'urgent'
                  ? 'bg-warning/15 text-warning border-warning/30'
                  : 'bg-success/15 text-success border-success/30'}"
            >
              {t("triage.aiAssigned", { priority: patient.priorita })}
            </span>
          {/if}
        </div>

        <div
          class="px-3.5 py-2 rounded-2xl bg-base-200/60 border border-base-content/10 backdrop-blur-sm flex items-center gap-2.5 shadow-inner transition-all duration-300 ease-in-out hover:border-primary/30"
        >
          <div
            class="w-7 h-7 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-xs shrink-0 shadow-xs"
          >
            🤖
          </div>
          <div class="flex flex-col">
            <span
              class="text-xs font-bold text-base-content flex items-center gap-1.5"
            >
              <span>{t("triage.determinedByAi")}</span>
              <span
                class="badge badge-primary badge-xs font-mono font-bold text-[9px] uppercase"
              >
                {t("triage.autoBadge")}
              </span>
            </span>
            <span class="text-[10px] text-base-content/60 font-mono">
              {t("triage.classifiedFrom")}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Clinical Presets (Compact Single-Line Bar) -->
    <div
      class="flex shadow-inner bg-base-200/50 border border-base-content/5 py-1.5 px-3 rounded-2xl items-center gap-2 w-full overflow-x-auto"
    >
      <span
        class="text-[11px] font-bold uppercase tracking-wider text-base-content/60 font-label shrink-0 flex items-center gap-1.5 mr-0.5"
      >
        <span>⚡ {t("triage.quickCases")}</span>
      </span>
      {#each presets as p}
        {@const isActive = activePresetTitle === (p.shortTitle || p.title)}
        <button
          type="button"
          class="cursor-pointer shrink-0 inline-flex items-center gap-2 px-2.5 py-1.5 rounded-xl border transition-all duration-300 ease-in-out hover:-translate-y-0.5 hover:shadow-md active:scale-95 group text-left {isActive
            ? 'border-primary bg-primary/20 text-primary ring-2 ring-primary/40 shadow-sm font-bold scale-[1.02]'
            : 'border-base-300 bg-base-200/50 hover:bg-primary/10 hover:border-primary/50'}"
          onclick={() => applyPreset(p)}
          title="{p.title} - {p.sintomi}"
        >
          <Image
            src={p.image}
            alt={p.specie}
            class="w-5 h-5 rounded-md object-cover border border-base-content/10 shadow-xs shrink-0 group-hover:scale-110 transition-transform duration-300 ease-in-out"
          />
          <span
            class="text-xs font-bold {isActive
              ? 'text-primary'
              : 'text-base-content'} group-hover:text-primary transition-colors font-display whitespace-nowrap"
          >
            {p.shortTitle || p.title}
          </span>
          {#if isActive}
            <span
              class="badge badge-primary badge-xs font-bold font-mono text-[9px] shadow-xs"
              in:scale={{ duration: 200, easing: cubicInOut }}
            >
              {t("triage.activeBadge")}
            </span>
          {:else}
            <span
              class="badge badge-outline badge-xs {p.badgeColor} font-bold font-mono text-[9px]"
            >
              {p.badge}
            </span>
          {/if}
          <span class="text-[10px] text-base-content/60 font-mono font-bold">
            {p.peso} kg
          </span>
        </button>
      {/each}

      <!-- Reset / Clear Intake Button -->
      {#if activePresetTitle}
        <button
          type="button"
          class="cursor-pointer shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-warning/50 bg-warning/15 hover:bg-warning/25 text-warning font-bold text-xs transition-all duration-300 ease-in-out hover:scale-105 active:scale-95 shadow-xs ml-auto"
          onclick={resetPresetToManual}
          title="Reset preset values and switch to manual intake"
          in:scale={{ duration: 200, easing: cubicInOut }}
        >
          <span>✕</span>
          <span>{t("triage.resetPreset")}</span>
        </button>
      {:else}
        <button
          type="button"
          class="cursor-pointer shrink-0 inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl border border-base-300 hover:border-base-content/30 bg-base-100 hover:bg-base-200 text-base-content/60 hover:text-base-content text-xs font-medium transition-all duration-300 ease-in-out ml-auto"
          onclick={clearIntakeValues}
          title="Reset symptoms and start clean manual intake"
        >
          <span>↺</span>
          <span>{t("triage.clearIntake")}</span>
        </button>
      {/if}
    </div>

    <!-- 1. VISUAL SPECIES SELECTOR (PHOTO BADGE CARDS) -->
    <div class="space-y-3">
      <div class="flex justify-between items-center">
        <label
          for="species-selection"
          class="block text-xs font-bold uppercase tracking-wider text-base-content/80 font-label"
        >
          {t("triage.speciesTitle")} <span class="text-error">*</span>
        </label>
        <span
          class="text-xs font-bold text-primary font-mono flex items-center gap-1"
        >
          {t(`triage.species.${currentSpecies.id}`) || currentSpecies.label} ({t(`triage.species.${currentSpecies.id}Sub`) || currentSpecies.sub})
        </span>
      </div>

      <div
        id="species-selection"
        class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3"
      >
        {#each speciesList as sp}
          {@const isSelected = patient.specie === sp.id}
          <button
            type="button"
            class="relative flex flex-col items-center text-center p-3 rounded-2xl border-2 transition-all duration-300 ease-in-out cursor-pointer group {isSelected
              ? 'border-primary bg-primary/10 shadow-lg shadow-primary/15 scale-[1.03]'
              : 'border-base-300 bg-base-200/30 hover:border-base-content/30 hover:bg-base-200/60'}"
            onclick={() => selectSpecies(sp)}
          >
            {#if isSelected}
              <div
                class="absolute -top-2 -right-2 w-6 h-6 bg-primary text-primary-content rounded-full flex items-center justify-center text-xs font-black shadow-md border-2 border-base-100 z-10"
                in:scale={{ duration: 250 }}
              >
                ✓
              </div>
            {/if}

            <div
              class="relative w-16 h-16 sm:w-20 sm:h-20 mb-2 rounded-2xl overflow-hidden border border-base-content/15 shadow-inner"
            >
              <Image
                src={sp.image}
                alt={sp.label}
                class="w-full p-1 h-full object-cover group-hover:scale-110 transition-transform duration-500"
              />
              <span
                class="absolute bottom-1 right-1 text-sm bg-base-100/80 rounded-full px-1 shadow-sm backdrop-blur-xs"
              >
                {sp.icon}
              </span>
            </div>

            <div
              class="font-black text-xs text-base-content group-hover:text-primary transition-colors font-display"
            >
              {t(`triage.species.${sp.id}`) || sp.label}
            </div>
            <div
              class="text-[10px] text-base-content/60 font-semibold tracking-tight uppercase font-label"
            >
              {t(`triage.species.${sp.id}Sub`) || sp.sub}
            </div>
          </button>
        {/each}
      </div>
    </div>

    <!-- 2. VISUAL WEIGHT & DIGITAL SCALE SECTION + BREED -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 pt-1">
      <!-- Digital Veterinary Scale Card (Left / 7 cols) -->
      <div
        class="lg:col-span-7 rounded-2xl border border-base-300 bg-base-200/30 p-5 space-y-4 shadow-sm"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <Image
              src="/images/triage/scale.png"
              alt="Veterinary Scale"
              class="w-12 p-2 h-12 rounded-xl object-cover border border-base-content/10 shadow-sm"
            />
            <div>
              <div
                class="text-xs font-bold uppercase tracking-wider text-base-content/80 font-label flex items-center gap-1.5"
              >
                <span>{t("triage.scaleTitle")}</span>
                <span class="text-error">*</span>
              </div>
              <div class="text-[11px] text-base-content/60">
                {t("triage.scaleDesc")}
              </div>
            </div>
          </div>
          <span
            class="badge badge-sm text-nowrap {sizeCategory.color} font-bold font-mono"
          >
            {sizeCategory.label}
          </span>
        </div>

        <!-- Digital Readout Display -->
        <div
          class="p-4 rounded-xl bg-base-300/80 border border-base-content/10 flex items-center justify-between shadow-inner"
        >
          <div>
            <div
              class="text-[10px] text-base-content/50 uppercase font-mono font-bold tracking-wider"
            >
              {t("triage.digitalReadout")}
            </div>
            <div
              class="text-3xl sm:text-4xl font-black font-mono tracking-tight text-primary flex items-baseline gap-1"
            >
              {patient.peso}
              <span class="text-lg font-bold text-base-content/70">kg</span>
            </div>
          </div>
          <div class="text-right">
            <div
              class="text-[10px] text-base-content/50 uppercase font-mono font-bold tracking-wider"
            >
              {t("triage.imperialEquivalent")}
            </div>
            <div
              class="text-xl sm:text-2xl font-bold font-mono text-base-content/80"
            >
              {weightLbs}
              <span class="text-xs font-semibold text-base-content/50">lbs</span
              >
            </div>
          </div>
        </div>

        <!-- Slider & Quick Adjust Controls -->
        <div class="space-y-3">
          <div class="flex items-center gap-3">
            <span class="text-[11px] font-mono font-bold text-base-content/50"
              >0.1 kg</span
            >
            <input
              type="range"
              min="0.1"
              max={patient.specie === "Horse" ? "800" : "80"}
              step="0.1"
              bind:value={patient.peso}
              oninput={(e) =>
                syncWeightToTextarea(parseFloat(e.currentTarget.value))}
              class="range range-primary range-sm flex-1 cursor-pointer"
            />
            <span class="text-[11px] font-mono font-bold text-base-content/50">
              {patient.specie === "Horse" ? "800 kg" : "80 kg"}
            </span>
          </div>

          <!-- Quick Steppers -->
          <div class="flex items-center justify-between flex-wrap gap-1.5">
            <div class="flex items-center gap-1">
              <button
                type="button"
                class="btn btn-xs btn-outline border-base-300 hover:btn-primary"
                onclick={() => adjustWeight(-5.0)}
                title="Subtract 5.0 kg"
              >
                -5 kg
              </button>
              <button
                type="button"
                class="btn btn-xs btn-outline border-base-300 hover:btn-primary"
                onclick={() => adjustWeight(-1.0)}
                title="Subtract 1.0 kg"
              >
                -1 kg
              </button>
              <button
                type="button"
                class="btn btn-xs btn-outline border-base-300 hover:btn-primary"
                onclick={() => adjustWeight(-0.1)}
                title="Subtract 0.1 kg"
              >
                -0.1 kg
              </button>
            </div>

            <!-- Precision Direct Input -->
            <div class="flex items-center gap-1.5">
              <span class="text-[11px] font-semibold text-base-content/60"
                >{t("triage.manualLabel")}</span
              >
              <input
                type="number"
                step="0.1"
                min="0.1"
                max="1000"
                bind:value={patient.peso}
                oninput={(e) =>
                  syncWeightToTextarea(parseFloat(e.currentTarget.value))}
                class="input input-xs input-bordered w-20 text-center font-mono font-bold focus:input-primary"
              />
            </div>

            <div class="flex items-center gap-1">
              <button
                type="button"
                class="btn btn-xs btn-outline border-base-300 hover:btn-primary"
                onclick={() => adjustWeight(0.1)}
                title="Add 0.1 kg"
              >
                +0.1 kg
              </button>
              <button
                type="button"
                class="btn btn-xs btn-outline border-base-300 hover:btn-primary"
                onclick={() => adjustWeight(1.0)}
                title="Add 1.0 kg"
              >
                +1 kg
              </button>
              <button
                type="button"
                class="btn btn-xs btn-outline border-base-300 hover:btn-primary"
                onclick={() => adjustWeight(5.0)}
                title="Add 5.0 kg"
              >
                +5 kg
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Breed Selection & Suggestions (Right / 5 cols) -->
      <div
        class="lg:col-span-5 rounded-2xl border border-base-300 bg-base-200/30 p-5 space-y-3.5 flex flex-col justify-between shadow-sm"
      >
        <div class="space-y-2">
          <label
            for="patient-breed"
            class="block text-xs font-bold uppercase tracking-wider text-base-content/80 font-label"
          >
            {t("triage.breedLabel")}
          </label>
          <input
            id="patient-breed"
            type="text"
            bind:value={patient.razza}
            oninput={(e) => syncBreedToTextarea(e.currentTarget.value)}
            placeholder={t("triage.breedPlaceholder")}
            class="input input-bordered w-full font-medium focus:input-primary transition-all duration-300 ease-in-out"
          />
        </div>

        <!-- Quick Breed Suggestions Chips -->
        <div class="space-y-1.5">
          <div
            class="text-[10px] font-bold uppercase tracking-wider text-base-content/50 font-label"
          >
            {t("triage.suggestedBreeds", { species: currentSpecies.label })}
          </div>
          <div class="flex flex-wrap gap-1.5">
            {#each currentSpecies.defaultBreeds as breed}
              <button
                type="button"
                class="badge badge-sm cursor-pointer transition-all duration-200 {patient.razza ===
                breed
                  ? 'badge-primary font-bold shadow-xs'
                  : 'badge-outline border-base-300 hover:badge-primary'}"
                onclick={() => selectBreed(breed)}
              >
                {breed}
              </button>
            {/each}
          </div>
        </div>

        <div
          class="p-3 rounded-xl bg-base-300/50 border border-base-content/5 text-xs text-base-content/70 flex items-center gap-2"
        >
          <span class="text-base">ℹ️</span>
          <span>{t("triage.breedPharmacogenomics")}</span>
        </div>
      </div>
    </div>

    <!-- 3. SYMPTOMS, ANAMNESIS & QUICK TOXICITY CHIPS -->
    <div class="space-y-3 pt-1">
      <div
        class="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5"
      >
        <div class="flex items-center gap-2 flex-wrap">
          <label
            for="patient-symptoms"
            class="block text-xs font-bold uppercase tracking-wider text-base-content/80 font-label"
          >
            {t("triage.symptomsTitle")} <span
              class="text-error">*</span
            >
          </label>
          <span
            class="badge badge-xs bg-success/15 border border-success/30 text-success text-[10px] font-mono font-bold flex items-center gap-1"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-success animate-pulse"
            ></span>
            {t("triage.autoSyncedBadge")}
          </span>
        </div>

        <div class="flex items-center gap-2">
          {#if activePresetTitle}
            <span
              class="badge badge-xs badge-warning/20 border border-warning/40 text-warning text-[10px] font-mono font-bold flex items-center gap-1"
              in:scale={{ duration: 180, easing: cubicInOut }}
            >
              <span>{t("triage.presetBadge", { title: activePresetTitle })}</span>
            </span>
            <button
              type="button"
              class="btn btn-ghost btn-xs text-warning hover:bg-warning/15 text-[10px] h-5 min-h-0 px-2 py-0 font-bold cursor-pointer rounded-lg border border-warning/30 transition-all duration-200"
              onclick={resetPresetToManual}
              title={t("triage.resetPreset")}
            >
              ✕ {t("triage.resetPreset")}
            </button>
          {:else}
            <span
              class="badge badge-xs badge-primary/15 border border-primary/30 text-primary text-[10px] font-mono font-bold"
            >
              {t("triage.manualModeBadge")}
            </span>
          {/if}
          <span class="text-[11px] text-base-content/50 font-mono">
            {patient.sintomi ? patient.sintomi.length : 0} chars
          </span>
        </div>
      </div>

      <!-- Reusable chip button (used for both category chips and refinements) -->
      {#snippet chipButton(chip, accent)}
        {@const isUsed = isSymptomUsed(chip)}
        <button
          type="button"
          class="badge badge-sm cursor-pointer transition-all duration-300 ease-in-out gap-1.5 py-2.5 px-2.5 group hover:-translate-y-0.5 active:scale-95 {isUsed
            ? accent
              ? 'badge-accent text-accent-content shadow-md shadow-accent/25 ring-2 ring-accent/40 font-bold'
              : 'badge-primary text-primary-content shadow-md shadow-primary/25 ring-2 ring-primary/40 font-bold'
            : accent
              ? 'badge-outline border-accent/40 text-accent/90 hover:border-accent hover:bg-accent/10 font-medium'
              : 'badge-outline border-base-300 text-base-content/75 hover:border-primary/60 hover:text-primary hover:bg-base-200/50 font-medium'}"
          onclick={() => toggleSymptom(chip)}
          title={isUsed ? "Click to remove" : "Click to add"}
        >
          <span
            class="transition-transform duration-300 ease-in-out group-hover:scale-110"
            >{chip.icon}</span
          >
          <span>{chip.label}</span>
          {#if isUsed}
            <span
              class="flex items-center justify-center w-3.5 h-3.5 rounded-full bg-white/25 text-[10px] font-black leading-none"
            >
              ✓
            </span>
          {:else}
            <span
              class="text-[10px] text-base-content/40 font-bold transition-colors duration-200"
            >
              +
            </span>
          {/if}
        </button>
      {/snippet}

      <!-- Quick Symptom / Toxin Chips — grouped by clinical category -->
      <div
        class="space-y-3 rounded-2xl border border-base-300 bg-base-200/30 p-3.5 shadow-inner"
      >
        <div
          class="text-[10px] font-bold uppercase tracking-wider text-base-content/60 font-label flex items-center gap-1.5"
        >
          <span>{t("triage.quickAddLabel")}</span>
        </div>

        {#each chipCategories as cat (cat.id)}
          <div class="space-y-1.5">
            <div
              class="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-base-content/50 font-label"
            >
              <span class="text-sm">{cat.icon}</span>
              <span>{cat.title}</span>
              <span class="flex-1 h-px bg-base-content/10"></span>
            </div>

            <div class="flex flex-wrap gap-1.5">
              {#each cat.chips as chip (chip.id)}
                {@render chipButton(chip, false)}
              {/each}
            </div>

            <!-- Conditional refinement chips: only shown when the parent is selected -->
            {#each cat.chips.filter((c) => c.related && isSymptomUsed(c)) as parent (parent.id)}
              <div
                transition:slide|local={{ duration: 300, easing: cubicInOut }}
                class="ml-1 mt-1 pl-3 border-l-2 border-accent/40 space-y-1.5"
              >
                <div
                  class="text-[10px] font-semibold text-accent/80 flex items-center gap-1"
                >
                  <span>{parent.icon}</span>
                  <span>{t("triage.refineLabel", { parent: parent.label })}</span>
                </div>
                <div class="flex flex-wrap gap-1.5">
                  {#each parent.related as sub (sub.id)}
                    {@render chipButton(sub, true)}
                  {/each}
                </div>
              </div>
            {/each}
          </div>
        {/each}
      </div>

      <textarea
        id="patient-symptoms"
        rows="4"
        bind:value={patient.sintomi}
        oninput={handleTextareaInput}
        placeholder={t("triage.symptomsPlaceholder")}
        class="textarea textarea-bordered w-full text-sm leading-relaxed focus:textarea-primary transition-all duration-300 ease-in-out font-sans"
      ></textarea>
    </div>

    <!-- Actions Footer: Direct Intake Trigger -->
    <div
      class="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-base-200"
    >
      <div class="flex items-center gap-2 text-xs text-base-content/70">
        {#if runStatus === "running"}
          <span
            class="badge badge-warning badge-sm font-bold gap-1.5 font-mono shadow-xs"
          >
            <span class="w-2 h-2 rounded-full bg-warning animate-ping"></span>
            {t("triage.analysisInProgress", { elapsed: elapsedSeconds })}
          </span>
          <span class="text-xs text-base-content/60 hidden sm:inline">
            {t("triage.updateAbovePrompt")}
          </span>
        {:else if isResultsAvailable || (artifactsData && artifactsData.availableFiles && artifactsData.availableFiles.length > 0)}
          <span
            class="badge text-nowrap badge-success badge-sm font-bold gap-1 shadow-xs"
          >
            {t("triage.protocolAvailable")}
          </span>
        {:else}
          <span class="flex items-center gap-1.5 text-base-content/60">
            <span>ℹ️</span>
            <span>{t("triage.intakeReady")}</span>
          </span>
        {/if}
      </div>

      <div
        class="flex flex-wrap items-center gap-3 w-full sm:w-auto justify-end"
      >
        {#if isResultsAvailable || runStatus === "succeeded"}
          {#if onNext}
            <button
              type="button"
              class="btn btn-outline btn-primary btn-md gap-1.5 font-bold cursor-pointer hover:scale-105 transition-all duration-300 ease-in-out"
              onclick={onNext}
              title="Continue to Step 2: Case Triage & Search Planning"
            >
              <span>{t("triage.btnContinueAssessment")}</span>
              <span>→</span>
            </button>
          {/if}
        {/if}

        {#if runStatus === "running"}
          {#if onStopAnalysis}
            <button
              type="button"
              class="btn btn-outline btn-error btn-md px-4 gap-1.5 font-bold hover:scale-[1.03] active:scale-[0.97] transition-all duration-300 ease-in-out cursor-pointer shadow-xs"
              onclick={onStopAnalysis}
              title="Stop the current running analysis"
            >
              <span>⏹</span>
              <span>{t("triage.btnStopRun")}</span>
            </button>
          {/if}

          <button
            type="button"
            class="btn btn-warning btn-md px-6 gap-2 shadow-xl shadow-warning/25 font-display font-black hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 ease-in-out cursor-pointer"
            onclick={async () => {
              if (onStopAndRetrigger) {
                await onStopAndRetrigger();
              } else {
                if (onStopAnalysis) await onStopAnalysis();
                if (onTriggerAnalysis) await onTriggerAnalysis();
              }
            }}
            disabled={!patient.sintomi || patient.peso <= 0}
            title="Stop current execution and re-trigger immediately with the updated intake data"
          >
            <span>🔄</span>
            <span>{t("triage.btnStopAndRerun")}</span>
          </button>
        {:else if onTriggerAnalysis}
          <button
            type="button"
            class="btn btn-primary btn-md px-6 gap-2 shadow-xl shadow-primary/25 font-display font-black hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 ease-in-out cursor-pointer"
            onclick={onTriggerAnalysis}
            disabled={!patient.sintomi || patient.peso <= 0}
            title="Trigger real-time veterinary clinical analysis pipeline"
          >
            {#if runStatus === "succeeded"}
              <span>⚡</span>
              <span>{t("triage.btnRunAnalysis")}</span>
            {:else}
              <span>⚡</span>
              <span>{t("triage.btnRunAnalysis")}</span>
            {/if}
          </button>
        {/if}
      </div>
    </div>
  </div>
</div>
