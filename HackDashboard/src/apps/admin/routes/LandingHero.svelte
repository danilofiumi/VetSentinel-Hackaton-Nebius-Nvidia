<script>
  import { cubicInOut } from "svelte/easing";
  import { fly, fade } from "svelte/transition";
  import VetTelemetryGrid from "./VetTelemetryGrid.svelte";
  import Image from "./Image.svelte";
  import { t } from "$lib";

  let { onOpenHotline } = $props();
</script>

<section
  class="relative min-h-[calc(100dvh-4rem)] md:min-h-[calc(100dvh-6.75rem)] flex flex-col justify-center py-4 sm:py-6 lg:py-8 overflow-hidden bg-gradient-to-b from-base-100 via-base-100/90 to-base-100/40 border-b border-base-content/10 z-10"
>
  <!-- Authentic Veterinary Telemetry Millimeter ECG Grid & Waveform -->
  <VetTelemetryGrid opacity={0.6} />

  <!-- Multi-Layered Aurora Mesh Gradients -->
  <div
    class="absolute -top-32 left-0 -translate-x-1/2 w-[1000px] h-[500px] bg-[radial-gradient(ellipse_at_center,color-mix(in_srgb,var(--color-primary)_20%,transparent)_0%,color-mix(in_srgb,var(--color-emerald-400)_10%,transparent)_40%,transparent_70%)] opacity-40 blur-3xl pointer-events-none -z-10"
    aria-hidden="true"
  ></div>
  <div
    class="absolute top-1/4 right-0 opacity-40 w-[450px] h-[450px] bg-[radial-gradient(circle,color-mix(in_srgb,var(--color-accent)_14%,transparent)_0%,transparent_70%)] blur-3xl pointer-events-none -z-10"
    aria-hidden="true"
  ></div>

  <div
    class="max-w-7xl mx-auto px-4 sm:px-6 w-full flex-1 flex flex-col justify-between my-auto"
  >
    <!-- Top Pill with Gradient Glow Border -->
    <div
      class="flex justify-center mb-2 sm:mb-3 lg:mb-3 lg:mt-3 lg:relative lg:top-3"
      in:fly={{ y: -15, duration: 500, easing: cubicInOut }}
    >
      <div
        class="p-[1px] rounded-full bg-gradient-to-r from-primary/50 via-emerald-400/70 to-accent/50 shadow-sm shadow-primary/20"
      >
        <div
          class="inline-flex items-center gap-2 px-3.5 sm:px-4 py-1 sm:py-1.5 rounded-full bg-base-100/95 backdrop-blur-md"
        >
          <span class="relative flex h-2.5 w-2.5">
            <span
              class="animate-ping absolute inline-flex h-full w-full rounded-full bg-error opacity-75"
            ></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-error"
            ></span>
          </span>
          <span
            class="text-[11px] sm:text-xs font-mono font-bold tracking-wide uppercase text-base-content/80"
          >
            {t("landing.hero.pill")}
          </span>
        </div>
      </div>
    </div>

    <!-- Main Hero Split: Story Hook & Hero Image -->
    <div
      class="grid grid-cols-1 lg:grid-cols-12 gap-5 lg:gap-8 xl:gap-10 items-center my-auto"
    >
      <!-- Left Column: Story & Clinician Value -->
      <div
        class="lg:col-span-7 space-y-3 sm:space-y-4 lg:space-y-4.5 text-left"
        in:fly={{ x: -20, duration: 600, easing: cubicInOut }}
      >
        <h1
          class="text-4xl sm:text-5xl md:text-6xl lg:text-[3.25rem] xl:text-[4.1rem] 2xl:text-[4.85rem] font-black font-display tracking-tight text-base-content leading-[1.0]"
        >
          <span class="block">{t("landing.hero.h1Line1")}</span>
          <span class="block text-base-content/90">{t("landing.hero.h1Line2")}</span>
          <span
            class="bg-gradient-to-r from-primary via-emerald-400 to-accent bg-clip-text text-transparent block mt-1"
          >
            {t("landing.hero.h1Line3")}
          </span>
        </h1>

        <p
          class="text-xs sm:text-sm md:text-base text-base-content/80 font-sans max-w-xl leading-relaxed"
        >
          {t("landing.hero.desc")}
        </p>

        <!-- Proof Indicators -->
        <div
          class="flex flex-wrap items-center gap-2 pt-0.5 sm:pt-1 font-mono text-xs"
        >
          <div
            class="flex items-center gap-1.5 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-xl bg-base-100/90 border border-primary/25 shadow-xs text-base-content/90 font-medium"
          >
            <span class="text-primary font-bold">⚡</span>
            <span>{t("landing.hero.proof1")}</span>
          </div>
          <div
            class="flex items-center gap-1.5 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-xl bg-base-100/90 border border-accent/25 shadow-xs text-base-content/90 font-medium"
          >
            <span class="text-accent font-bold">📐</span>
            <span>{t("landing.hero.proof2")}</span>
          </div>
          <div
            class="flex items-center gap-1.5 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-xl bg-base-100/90 border border-base-content/15 shadow-xs text-base-content/90 font-medium"
          >
            <span class="text-emerald-500 font-bold">🛡️</span>
            <span>{t("landing.hero.proof3")}</span>
          </div>
        </div>

        <!-- Action CTAs -->
        <div
          class="pt-1 sm:pt-2 flex flex-col sm:flex-row items-center gap-2.5 sm:gap-3"
        >
          <a
            href="/dashboard"
            data-sveltekit-preload-code="eager"
            data-sveltekit-preload-data="tap"
            class="btn btn-primary btn-md sm:btn-lg rounded-2xl gap-2.5 font-bold font-display shadow-lg shadow-primary/30 hover:scale-105 active:scale-95 transition-all duration-200 ease-in-out cursor-pointer w-full sm:w-auto text-sm sm:text-base select-none"
          >
            <span class="text-xl">⚡</span>
            <span>{t("landing.hero.btnWorkstation")}</span>
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2.5"
                d="M13 7l5 5m0 0l-5 5m5-5H6"
              />
            </svg>
          </a>

          <a
            href="#demo"
            class="btn btn-ghost btn-md sm:btn-lg rounded-2xl gap-2 font-bold font-display border border-base-content/15 hover:bg-base-200/80 transition-all duration-300 ease-in-out cursor-pointer w-full sm:w-auto text-sm sm:text-base"
          >
            <svg
              class="w-5 h-5 opacity-70"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>{t("landing.hero.btnDemo")}</span>
          </a>
        </div>
      </div>

      <!-- Right Column: Visual Narrative Photo Card with Clinical Telemetry -->
      <div
        class="lg:col-span-5 relative"
        in:fly={{ x: 20, duration: 600, easing: cubicInOut }}
      >
        <!-- Outer Glowing Gradient Shell -->
        <div
          class="p-[1.5px] rounded-3xl bg-gradient-to-b from-primary/50 via-emerald-400/20 to-accent/40 shadow-2xl shadow-primary/10 hover:shadow-primary/25 transition-all duration-500 ease-out hover:-translate-y-1"
        >
          <div
            class="card bg-base-100/95 rounded-[calc(1.5rem-1.5px)] overflow-hidden backdrop-blur-xl relative group"
          >
            <!-- Image with Overlay Badge -->
            <div
              class="relative overflow-hidden aspect-[16/10] sm:aspect-[4/3] lg:aspect-[4/3] xl:aspect-[16/11] max-h-[320px] sm:max-h-[380px] lg:max-h-[420px] xl:max-h-[460px] bg-slate-950"
            >
              <Image
                src="/images/vector/hero_cat_lily.jpg"
                alt="Stylized 2D vector illustration of European Shorthair feline patient under ICU telemetry monitors with Easter lily toxicity report"
                class="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-700 ease-out"
              />
              <div
                class="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-slate-950/20 to-transparent pointer-events-none"
              ></div>

              <!-- Top Overlays: Emergency Alert & Countdown Pill -->
              <div
                class="absolute top-3.5 left-3.5 right-3.5 flex items-center justify-between gap-2 pointer-events-none"
              >
                <span
                  class="badge badge-error font-mono font-bold text-[11px] text-white shadow-lg flex items-center gap-1.5 py-2.5 px-3"
                >
                  <span class="w-2 h-2 rounded-full bg-white"></span>
                  <span>{t("landing.hero.acuteBadge")}</span>
                </span>

                <span
                  class="badge bg-black/75 border border-error/40 font-mono font-bold text-[10px] text-error shadow-lg flex items-center gap-1.5 py-2.5 px-2.5 backdrop-blur-md"
                >
                  <span class="animate-pulse">⏱️</span>
                  <span>{t("landing.hero.window")}</span>
                </span>
              </div>

              <!-- Urgent Clinical HUD Overlay (Directly transmits the emergency) -->
              <div
                class="absolute bottom-3.5 left-3.5 right-3.5 text-white space-y-2 pointer-events-none"
              >
                <div class="flex items-center justify-between">
                  <div>
                    <p
                      class="font-display font-bold text-base sm:text-lg drop-shadow-md flex items-center gap-2"
                    >
                      <span>{t("landing.hero.patientInfo")}</span>
                    </p>
                    <p
                      class="text-[11px] font-mono text-error/90 drop-shadow-sm font-semibold flex items-center gap-1"
                    >
                      <span>{t("landing.hero.toxinAlert")}</span>
                    </p>
                  </div>
                  <div class="text-right">
                    <span
                      class="badge badge-warning badge-xs font-mono font-bold uppercase tracking-wider text-black"
                    >
                      {t("landing.hero.highRisk")}
                    </span>
                  </div>
                </div>

                <!-- Mini Protocol Strip: Implies the emergency resolution -->
                <div
                  class="p-2 rounded-xl bg-black/60 backdrop-blur-md border border-white/10 grid grid-cols-2 gap-2 text-[10px] font-mono"
                >
                  <div class="flex items-center gap-1.5 text-emerald-400">
                    <span class="font-bold">✓ {t("landing.hero.diuresis")}</span>
                    <span class="text-white">28.0 ml/hr (48h)</span>
                  </div>
                  <div class="flex items-center gap-1.5 text-amber-300">
                    <span class="font-bold">✕ {t("landing.hero.emesis")}</span>
                    <span class="text-white">{t("landing.hero.contraindicated")}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Bottom Telemetry Stats Bar -->
            <div
              class="p-3 sm:p-3.5 bg-base-200/80 border-t border-base-content/10 grid grid-cols-3 gap-2 text-center font-mono"
            >
              <div>
                <p
                  class="text-[10px] uppercase text-base-content/60 font-semibold"
                >
                  {t("landing.hero.statSpeed")}
                </p>
                <p
                  class="text-sm sm:text-base font-black font-display text-primary"
                >
                  {t("landing.hero.statSpeedVal")}
                </p>
              </div>
              <div class="border-x border-base-content/10">
                <p
                  class="text-[10px] uppercase text-base-content/60 font-semibold"
                >
                  {t("landing.hero.statCalc")}
                </p>
                <p
                  class="text-sm sm:text-base font-black font-display text-accent"
                >
                  {t("landing.hero.statCalcVal")}
                </p>
              </div>
              <div>
                <p
                  class="text-[10px] uppercase text-base-content/60 font-semibold"
                >
                  {t("landing.hero.statEvidence")}
                </p>
                <p
                  class="text-sm sm:text-base font-black font-display text-secondary truncate"
                >
                  {t("landing.hero.statEvidenceVal")}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Telemetry Status / Subtle Scroll Anchor -->
    <div
      class="mt-4 sm:mt-6 pt-3 flex items-center justify-between text-[11px] font-mono text-base-content/50 border-t border-base-content/10"
    >
      <div class="flex items-center gap-2">
        <span class="relative flex h-2 w-2">
          <span
            class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"
          ></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-primary"
          ></span>
        </span>
        <span
          class="hidden sm:inline font-bold uppercase tracking-wider text-base-content/70"
          >{t("landing.hero.monitorTitle")}</span
        >
        <span class="hidden sm:inline text-base-content/30">·</span>
        <span class="text-primary font-semibold">{t("landing.hero.monitorLead")}</span>
      </div>

      <a
        href="#story"
        class="inline-flex items-center gap-1.5 text-base-content/60 hover:text-primary transition-colors cursor-pointer group"
      >
        <span
          class="uppercase tracking-wider font-bold text-[10px] sm:text-[11px]"
          >{t("landing.hero.scrollAnchor")}</span
        >
        <svg
          class="w-3.5 h-3.5 group-hover:translate-y-0.5 transition-transform duration-300"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </a>
    </div>
  </div>
</section>
