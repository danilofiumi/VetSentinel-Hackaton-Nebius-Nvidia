<script>
  import VetTelemetryGrid from "./VetTelemetryGrid.svelte";
  import { t } from "$lib";
</script>

<section
  id="demo"
  class="scroll-mt-20 py-16 sm:py-20 border-b border-base-content/10 relative bg-gradient-to-b from-base-300 via-base-300/80 to-base-200/90 overflow-hidden"
>
  <!-- Authentic Veterinary Telemetry Millimeter Grid & Waveform -->
  <VetTelemetryGrid opacity={0.5} showEcg={true} showTicks={true} showStamp={true} />

  <!-- Ambient High-Tech Workstation Radial Glows -->
  <div
    class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[550px] bg-[radial-gradient(ellipse_at_center,color-mix(in_srgb,var(--color-primary)_18%,transparent)_0%,color-mix(in_srgb,var(--color-accent)_12%,transparent)_45%,transparent_70%)] blur-3xl pointer-events-none -z-10"
    aria-hidden="true"
  ></div>

  <div class="max-w-6xl mx-auto px-4 sm:px-6 space-y-8">
    <!-- Header -->
    <div class="text-center max-w-3xl mx-auto space-y-3">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent/10 border border-accent/20 text-accent font-mono text-xs font-bold uppercase tracking-wider">
        <span>⏱️</span>
        <span>{t("landing.demo.badge")}</span>
      </div>
      <h2 class="text-2xl sm:text-4xl font-black font-display tracking-tight text-base-content">
        {t("landing.demo.title")}
      </h2>
      <p class="text-sm sm:text-base text-base-content/70">
        {t("landing.demo.subtitle")}
      </p>
    </div>

    <!-- Interactive Workspace Preview Card with Gradient Frame -->
    <div class="p-[1.5px] rounded-3xl bg-gradient-to-r from-accent/40 via-primary/30 to-emerald-400/40 shadow-2xl shadow-primary/10">
      <div class="card bg-base-100/95 rounded-[calc(1.5rem-1.5px)] backdrop-blur-2xl overflow-hidden">
        <!-- Mac Window Top Bar -->
        <div class="bg-base-200/90 px-4 py-3 border-b border-base-content/10 flex flex-wrap items-center justify-between gap-3">
          <div class="flex items-center gap-2">
            <div class="flex items-center gap-1.5">
              <span class="w-3 h-3 rounded-full bg-error/80 inline-block transition-transform duration-300 ease-in-out hover:scale-125"></span>
              <span class="w-3 h-3 rounded-full bg-warning/80 inline-block transition-transform duration-300 ease-in-out hover:scale-125"></span>
              <span class="w-3 h-3 rounded-full bg-success/80 inline-block transition-transform duration-300 ease-in-out hover:scale-125"></span>
            </div>
            <span class="text-xs font-mono font-bold text-base-content/80 ml-2">
              vetsentinel-emergency-pipeline-demo
            </span>
          </div>

          <div class="flex items-center gap-2.5">
            <span class="badge badge-xs sm:badge-sm font-mono text-[10px] bg-base-300/80 border border-base-content/10 text-base-content/70">
              1080p HD
            </span>
            <span class="badge badge-xs sm:badge-sm font-mono text-[10px] badge-primary/20 text-primary border border-primary/30">
              YouTube Demo
            </span>
            <a
              href="/dashboard"
              data-sveltekit-preload-code="eager"
              data-sveltekit-preload-data="tap"
              class="btn btn-xs btn-primary font-mono font-bold rounded-lg gap-1 shadow-sm hover:scale-105 active:scale-95 transition-all duration-200 ease-in-out select-none"
            >
              <span>{t("landing.demo.btnCopilot")}</span>
              <span>→</span>
            </a>
          </div>
        </div>

        <!-- YouTube Video Player Section -->
        <div class="relative w-full aspect-video bg-black overflow-hidden">
          <iframe
            class="w-full h-full border-0"
            src="https://www.youtube-nocookie.com/embed/zL8pyruFO58?rel=0"
            title="VetSentinel Emergency Pipeline Demo"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            referrerpolicy="strict-origin-when-cross-origin"
            allowfullscreen
          ></iframe>
        </div>

        <!-- Sleek Bottom Information Bar inside Mac Window -->
        <div class="p-4 sm:p-5 bg-base-200/60 border-t border-base-content/10 flex flex-wrap items-center justify-between gap-4">
          <div class="flex flex-wrap items-center gap-2">
            <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-base-100 border border-base-300 text-xs font-mono">
              <span class="text-primary font-bold">01</span>
              <span class="text-base-content/80 font-medium">{t("landing.demo.step1")}</span>
            </div>
            <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-base-100 border border-base-300 text-xs font-mono">
              <span class="text-accent font-bold">02</span>
              <span class="text-base-content/80 font-medium">{t("landing.demo.step2")}</span>
            </div>
            <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-base-100 border border-base-300 text-xs font-mono">
              <span class="text-success font-bold">03</span>
              <span class="text-base-content/80 font-medium">{t("landing.demo.step3")}</span>
            </div>
            <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-base-100 border border-base-300 text-xs font-mono">
              <span class="text-info font-bold">04</span>
              <span class="text-base-content/80 font-medium">{t("landing.demo.step4")}</span>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <a
              href="/dashboard"
              data-sveltekit-preload-code="eager"
              data-sveltekit-preload-data="tap"
              class="btn btn-primary btn-sm rounded-xl font-display font-bold gap-2 shadow-md hover:scale-105 active:scale-95 transition-all duration-200 ease-in-out select-none"
            >
              <span>{t("landing.demo.btnLaunch")}</span>
              <span>🚀</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
