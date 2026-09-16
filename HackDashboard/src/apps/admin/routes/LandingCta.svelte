<script>
  import Image from "./Image.svelte";
  import { t } from "$lib";
  let { onOpenHotline } = $props();
</script>

<section
  class="py-24 relative overflow-hidden bg-gradient-to-b from-base-100 via-primary/[0.08] to-base-200/95 border-t border-base-content/10"
>
  <!-- Radiant Multi-Stop Healing ICU Aura -->
  <div
    class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[550px] bg-[radial-gradient(ellipse_at_center,color-mix(in_srgb,var(--color-primary)_24%,transparent)_0%,color-mix(in_srgb,var(--color-emerald-400)_15%,transparent)_40%,transparent_70%)] blur-3xl pointer-events-none -z-10"
    aria-hidden="true"
  ></div>
  <div
    class="absolute inset-0 bg-[radial-gradient(circle_at_1px_1px,currentColor_1px,transparent_0)] [background-size:24px_24px] opacity-[0.025] pointer-events-none -z-10"
    aria-hidden="true"
  ></div>

  <div class="max-w-7xl mx-auto px-4 sm:px-6">
    <!-- Recovery Story Card with Glowing Gradient Shell -->
    <div
      class="p-[1.5px] rounded-3xl bg-base-100 shadow-2xl shadow-primary/15 mb-12"
    >
      <div
        class="card bg-gradient-to-br from-base-100/95 via-base-100/90 to-primary/[0.03] rounded-[calc(1.5rem-1.5px)] overflow-hidden backdrop-blur-xl"
      >
        <div class="grid grid-cols-1 lg:grid-cols-12 items-center">
          <!-- Visual: Recovered Patient -->
          <div
            class="lg:col-span-6 relative aspect-video sm:aspect-[4/3] lg:aspect-auto h-full min-h-[360px] bg-slate-950"
          >
            <Image
              src="/images/vet_recovery_dog.jpg"
              alt="Stylized 2D vector illustration of healthy golden retriever resting peacefully in veterinary recovery ward with telemetry vitals"
              class="w-full h-full object-cover"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent pointer-events-none"
            ></div>

            <div class="absolute bottom-4 left-4 right-4 text-white">
              <span
                class="badge badge-success font-mono text-[10px] font-bold uppercase tracking-wider mb-1 text-black"
              >
                {t("landing.cta.dischargedBadge")}
              </span>
              <p class="font-display font-bold text-base sm:text-lg">
                {t("landing.cta.patientTitle")}
              </p>
              <p class="text-xs text-white/85 font-sans">
                {t("landing.cta.patientSubtitle")}
              </p>
            </div>
          </div>

          <!-- Copy: Clinical Impact & Mission -->
          <div class="lg:col-span-6 p-6 sm:p-10 space-y-6">
            <div
              class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary font-mono text-xs font-bold uppercase tracking-wider"
            >
              <span>🐾</span>
              <span>{t("landing.cta.badge")}</span>
            </div>

            <h2
              class="text-2xl sm:text-3xl lg:text-4xl font-black font-display tracking-tight text-base-content leading-tight"
            >
              {t("landing.cta.title")}
            </h2>

            <p
              class="text-xs sm:text-sm text-base-content/80 leading-relaxed font-sans"
            >
              {t("landing.cta.subtitle")}
            </p>

            <div class="pt-2 flex flex-col sm:flex-row items-center gap-3">
              <a
                href="/dashboard"
                data-sveltekit-preload-code="eager"
                data-sveltekit-preload-data="tap"
                class="btn btn-primary btn-md rounded-2xl gap-2 font-bold font-display shadow-lg shadow-primary/25 hover:scale-105 active:scale-95 transition-all duration-200 ease-in-out cursor-pointer w-full sm:w-auto select-none"
              >
                <span class="text-lg">🚀</span>
                <span>{t("landing.cta.btnLaunch")}</span>
                <svg
                  class="w-4 h-4"
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
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
