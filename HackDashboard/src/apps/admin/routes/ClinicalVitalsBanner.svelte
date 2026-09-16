<script>
  import { t } from "$lib";

  let { onOpenEmergency } = $props();

  let activeSpecies = $state("feline"); // 'canine' | 'feline'

  const speciesData = {
    feline: {
      label: "Feline (Felis catus)",
      icon: "🐈",
      hr: "148",
      hrStatus: "Normal Sinus",
      rr: "26",
      spo2: "99%",
      temp: "38.6°C",
      bp: "128/82",
      ward: "ICU Ward",
    },
    canine: {
      label: "Canine (Canis familiaris)",
      icon: "🐕",
      hr: "96",
      hrStatus: "Sinus Arrhythmia (Physiol.)",
      rr: "18",
      spo2: "98%",
      temp: "38.4°C",
      bp: "132/86",
      ward: "Critical Care",
    },
  };

  function toggleSpecies() {
    activeSpecies = activeSpecies === "feline" ? "canine" : "feline";
  }
</script>

<div
  class="w-full bg-base-200/90 border-b border-base-content/10 backdrop-blur-md px-3 sm:px-6 py-2 transition-all duration-300 ease-in-out"
>
  <div
    class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs"
  >
    <!-- Left: Telemetry & ECG Waveform -->
    <div class="flex items-center gap-3 min-w-[240px]">
      <!-- Animated Heartbeat Indicator -->
      <button
        type="button"
        onclick={toggleSpecies}
        class="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-base-100 border border-base-300 hover:border-primary/50 shadow-inner cursor-pointer transition-all duration-300 ease-in-out group"
        title="Toggle telemetry reference species (Canine / Feline)"
      >
        <span
          class="text-sm group-hover:scale-125 transition-transform duration-300 ease-in-out"
        >
          {speciesData[activeSpecies].icon}
        </span>
        <span
          class="font-mono font-bold text-[11px] text-base-content/80 group-hover:text-primary transition-colors"
        >
          {activeSpecies === "feline" ? `${t("triage.species.Cat")} ICU` : `${t("triage.species.Dog")} ICU`}
        </span>
        <span class="text-[9px] badge badge-ghost badge-xs font-mono opacity-70"
          >switch</span
        >
      </button>

      <!-- Dynamic Live ECG SVG Waveform -->
      <!-- <div
        class="flex items-center gap-2 bg-base-100/60 px-2 py-0.5 rounded-lg border border-base-content/5"
      >
        <div class="relative w-28 h-6 overflow-hidden flex items-center">
          <svg
            class="w-full h-full text-primary"
            viewBox="0 0 160 30"
            fill="none"
            preserveAspectRatio="none"
          >
          
            <path
              d="M 0,15 L 160,15"
              stroke="currentColor"
              stroke-opacity="0.15"
              stroke-width="1"
              stroke-dasharray="2,2"
            />
          
            <path
              class="ecg-path"
              d="M 0,15 L 20,15 L 25,14 L 28,16 L 31,15 L 36,15 L 39,18 L 43,2 L 47,24 L 50,15 L 56,15 L 61,12 L 67,15 L 100,15 L 105,14 L 108,16 L 111,15 L 116,15 L 119,18 L 123,2 L 127,24 L 130,15 L 136,15 L 141,12 L 147,15 L 160,15"
              stroke="currentColor"
              stroke-width="1.75"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
          
          <div
            class="absolute inset-y-0 w-8 bg-gradient-to-r from-transparent to-primary/30 pointer-events-none ecg-scanner"
          ></div>
        </div>

        <div class="flex items-center gap-1">
          <span class="relative flex h-2 w-2">
            <span
              class="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"
            ></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-success"
            ></span>
          </span>
          <span
            class="font-mono text-[10px] text-success font-bold tracking-tight"
            >RHYTHM: STABLE</span
          >
        </div>
      </div> -->
    </div>

    <!-- Center: Live Physiological Readout -->
    <div class="hidden md:flex items-center gap-4 font-mono text-[11px]">
      <div class="flex items-center gap-1 text-base-content/80">
        <span class="text-error animate-pulse">💓</span>
        <span class="text-base-content/50">HR:</span>
        <span class="font-bold text-base-content"
          >{speciesData[activeSpecies].hr}</span
        >
        <span class="text-[9px] text-base-content/50">bpm</span>
      </div>

      <span class="text-base-content/20">•</span>

      <div class="flex items-center gap-1 text-base-content/80">
        <span class="text-primary">🫁</span>
        <span class="text-base-content/50">RR:</span>
        <span class="font-bold text-base-content"
          >{speciesData[activeSpecies].rr}</span
        >
        <span class="text-[9px] text-base-content/50">/min</span>
      </div>

      <span class="text-base-content/20">•</span>

      <div class="flex items-center gap-1 text-base-content/80">
        <span class="text-accent">🩸</span>
        <span class="text-base-content/50">SpO₂:</span>
        <span class="font-bold text-accent"
          >{speciesData[activeSpecies].spo2}</span
        >
      </div>

      <span class="text-base-content/20">•</span>

      <div class="flex items-center gap-1 text-base-content/80">
        <span class="text-warning">🌡️</span>
        <span class="text-base-content/50">TEMP:</span>
        <span class="font-bold text-base-content"
          >{speciesData[activeSpecies].temp}</span
        >
      </div>

      <span class="text-base-content/20">•</span>

      <div class="flex items-center gap-1 text-base-content/80">
        <span class="text-base-content/50">BP:</span>
        <span class="font-bold text-base-content"
          >{speciesData[activeSpecies].bp}</span
        >
      </div>
    </div>
  </div>
</div>

<style>
  @keyframes ecg-sweep {
    0% {
      stroke-dashoffset: 320;
    }
    100% {
      stroke-dashoffset: 0;
    }
  }

  @keyframes scan-sweep {
    0% {
      transform: translateX(-100%);
    }
    100% {
      transform: translateX(200%);
    }
  }

  .ecg-path {
    stroke-dasharray: 320;
    animation: ecg-sweep 3s linear infinite;
  }

  .ecg-scanner {
    animation: scan-sweep 3s linear infinite;
  }
</style>
