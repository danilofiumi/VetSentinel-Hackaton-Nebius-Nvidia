<script>
  import { cubicInOut } from "svelte/easing";
  import { fly } from "svelte/transition";
  import VetTelemetryGrid from "./VetTelemetryGrid.svelte";
  import Image from "./Image.svelte";
  import { t } from "$lib";

  let selectedPillar = $state(0);

  let pillars = $derived([
    {
      number: "01",
      title: t("landing.specialists.p1Title"),
      clinicalRole: t("landing.specialists.p1Role"),
      icon: "⚡",
      badge: t("landing.specialists.p1Badge"),
      badgeColor: "badge-primary",
      description: t("landing.specialists.p1Desc"),
      exampleAction: t("landing.specialists.p1Example"),
    },
    {
      number: "02",
      title: t("landing.specialists.p2Title"),
      clinicalRole: t("landing.specialists.p2Role"),
      icon: "📚",
      badge: t("landing.specialists.p2Badge"),
      badgeColor: "badge-accent",
      description: t("landing.specialists.p2Desc"),
      exampleAction: t("landing.specialists.p2Example"),
    },
    {
      number: "03",
      title: t("landing.specialists.p3Title"),
      clinicalRole: t("landing.specialists.p3Role"),
      icon: "📐",
      badge: t("landing.specialists.p3Badge"),
      badgeColor: "badge-secondary",
      description: t("landing.specialists.p3Desc"),
      exampleAction: t("landing.specialists.p3Example"),
    },
  ]);
</script>

<section
  id="solution"
  class="py-16 sm:py-20 border-b border-base-content/10 relative bg-gradient-to-b from-base-100 via-emerald-500/[0.03] to-base-100 overflow-hidden"
>
  <!-- Authentic Veterinary Telemetry Millimeter Grid -->
  <VetTelemetryGrid opacity={0.4} showEcg={false} showTicks={true} showStamp={true} />
  <!-- Surgical Emerald Ambient Radial Glows -->
  <div
    class="absolute top-1/3 -right-24 w-[650px] h-[650px] bg-[radial-gradient(circle,color-mix(in_srgb,var(--color-primary)_15%,transparent)_0%,transparent_70%)] blur-3xl pointer-events-none -z-10"
    aria-hidden="true"
  ></div>
  <div
    class="absolute -bottom-24 -left-24 w-[550px] h-[550px] bg-[radial-gradient(circle,color-mix(in_srgb,var(--color-accent)_12%,transparent)_0%,transparent_70%)] blur-3xl pointer-events-none -z-10"
    aria-hidden="true"
  ></div>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 space-y-12">
    <!-- Header -->
    <div class="text-center max-w-3xl mx-auto space-y-3">
      <div
        class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-primary/80 border border-primary/40 text-white font-mono text-xs font-bold uppercase tracking-wider"
      >
        <span>🛡️</span>
        <span>{t("landing.specialists.badge")}</span>
      </div>
      <h2
        class="text-3xl sm:text-4xl lg:text-5xl font-black font-display tracking-tight text-base-content"
      >
        {t("landing.specialists.title")}
      </h2>
      <p class="text-sm sm:text-base text-base-content/70 font-sans">
        {t("landing.specialists.subtitle")}
      </p>
    </div>

    <!-- Precision Dosing Equipment Hero Showcase Split with Gradient Shell -->
    <div class="p-[1.5px] rounded-3xl bg-gradient-to-r from-primary/40 via-base-content/10 to-emerald-400/35 shadow-xl">
      <div
        class="card bg-gradient-to-br from-base-100/95 via-base-100/90 to-primary/[0.02] rounded-[calc(1.5rem-1.5px)] overflow-hidden backdrop-blur-xl"
      >
        <div class="grid grid-cols-1 lg:grid-cols-12 items-center">
        <!-- Text Explanation -->
        <div class="lg:col-span-6 p-6 sm:p-8 space-y-5 order-2 lg:order-1">
          <div
            class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent/10 border border-accent/20 text-accent font-mono text-xs font-bold"
          >
            <span>{t("landing.specialists.showcaseBadge")}</span>
          </div>

          <h3
            class="text-2xl sm:text-3xl font-bold font-display text-base-content"
          >
            {t("landing.specialists.showcaseTitle")}
          </h3>

          <p
            class="text-xs sm:text-sm text-base-content/75 font-sans leading-relaxed"
          >
            {t("landing.specialists.showcaseDesc")}
          </p>

          <div class="space-y-2.5 text-xs text-base-content/80 font-sans">
            <div class="flex items-start gap-2.5">
              <span class="text-primary font-bold">✓</span>
              <span
                ><strong>{t("landing.specialists.feat1Title")}</strong> {t("landing.specialists.feat1Desc")}</span
              >
            </div>
            <div class="flex items-start gap-2.5">
              <span class="text-primary font-bold">✓</span>
              <span
                ><strong>{t("landing.specialists.feat2Title")}</strong> {t("landing.specialists.feat2Desc")}</span
              >
            </div>
            <div class="flex items-start gap-2.5">
              <span class="text-primary font-bold">✓</span>
              <span
                ><strong>{t("landing.specialists.feat3Title")}</strong> {t("landing.specialists.feat3Desc")}</span
              >
            </div>
          </div>

          <div class="pt-2">
            <a
              href="/dashboard"
              data-sveltekit-preload-code="eager"
              data-sveltekit-preload-data="tap"
              class="btn btn-primary btn-sm rounded-xl font-bold font-display gap-2 hover:scale-105 active:scale-95 transition-all duration-200 select-none"
            >
              <span>{t("landing.specialists.btnPresets")}</span>
              <span>→</span>
            </a>
          </div>
        </div>

        <!-- Visual: Precision ICU Dosing Equipment -->
        <div
          class="lg:col-span-6 relative aspect-video sm:aspect-[4/3] lg:aspect-auto h-full min-h-[340px] order-1 lg:order-2 bg-slate-950"
        >
          <Image
            src="/images/vector/vet_icu_dosing.jpg"
            alt="Stylized 2D vector illustration of calibrated veterinary IV infusion pump showing precise fluid delivery and toxicology telemetry chart"
            class="w-full h-full object-cover"
          />
          <div
            class="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent pointer-events-none"
          ></div>

          <div class="absolute bottom-4 left-4 right-4 text-white">
            <span
              class="badge badge-accent font-mono text-[10px] font-bold uppercase tracking-wider mb-1"
            >
              {t("landing.specialists.imgBadge")}
            </span>
            <p class="font-display font-bold text-sm sm:text-base">
              {t("landing.specialists.imgTitle")}
            </p>
            <p class="text-[11px] text-white/80 font-mono">
              {t("landing.specialists.imgDesc")}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>

    <!-- 3 Pillars Cards Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      {#each pillars as item, i}
        <div
          class="card bg-gradient-to-b from-base-100 via-base-100/95 to-base-200/40 border border-base-content/10 shadow-md hover:shadow-2xl rounded-3xl p-6 hover:border-primary/50 transition-all duration-500 ease-out hover:-translate-y-1.5 flex flex-col justify-between group"
        >
          <div>
            <div class="flex items-center justify-between">
              <div
                class="w-12 h-12 rounded-2xl bg-base-200 border border-base-300 flex items-center justify-center text-2xl shadow-inner"
              >
                {item.icon}
              </div>
              <span
                class="badge {item.badgeColor} badge-sm font-mono font-bold text-white shadow-xs"
              >
                {item.badge}
              </span>
            </div>

            <div class="mt-4">
              <span
                class="text-[10px] font-mono uppercase tracking-wider text-base-content/50 font-bold"
              >
                {t("landing.specialists.stagePrefix")} #{item.number} · {item.clinicalRole}
              </span>
              <h3
                class="text-lg font-bold font-display text-base-content mt-0.5"
              >
                {item.title}
              </h3>
            </div>

            <p
              class="text-xs text-base-content/75 mt-3 leading-relaxed font-sans"
            >
              {item.description}
            </p>
          </div>

          <div
            class="mt-5 p-3 rounded-2xl bg-base-200/60 border border-base-content/10"
          >
            <p class="text-[11px] font-mono text-base-content/90 leading-snug">
              <span class="text-primary font-bold">{t("landing.specialists.protocolExample")}</span>
              {item.exampleAction}
            </p>
          </div>
        </div>
      {/each}
    </div>
  </div>
</section>
