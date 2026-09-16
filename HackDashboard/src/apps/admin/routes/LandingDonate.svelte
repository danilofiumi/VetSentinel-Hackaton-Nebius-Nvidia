<script>
  import { t } from "$lib";
</script>

<section
  id="donate"
  class="scroll-mt-20 py-16 sm:py-24 border-b border-base-content/10 relative bg-gradient-to-b from-base-200/90 via-base-100 to-base-200/90 overflow-hidden"
>
  <!-- Ambient Radiant Support Glow -->
  <div
    class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[550px] bg-[radial-gradient(ellipse_at_center,color-mix(in_srgb,var(--color-primary)_12%,transparent)_0%,color-mix(in_srgb,#ec4899_10%,transparent)_35%,color-mix(in_srgb,#f59e0b_8%,transparent)_60%,transparent_75%)] blur-3xl pointer-events-none -z-10"
    aria-hidden="true"
  ></div>

  <!-- Micro Grid Pattern -->
  <div
    class="absolute inset-0 bg-[radial-gradient(circle_at_1px_1px,currentColor_1px,transparent_0)] [background-size:24px_24px] opacity-[0.025] pointer-events-none -z-10"
    aria-hidden="true"
  ></div>

  <div class="max-w-5xl mx-auto px-4 sm:px-6 space-y-10">
    <!-- Header Section -->
    <div class="text-center max-w-2xl mx-auto space-y-3">
      <div
        class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-rose-500/10 border border-rose-500/25 text-rose-500 font-mono text-xs font-bold uppercase tracking-wider"
      >
        <span
          class="inline-block transition-transform duration-300 ease-in-out hover:scale-125"
          >💖</span
        >
        <span>{t("landing.donate.badge")}</span>
      </div>

      <h2
        class="text-3xl sm:text-4xl lg:text-5xl font-black font-display tracking-tight text-base-content"
      >
        {t("landing.donate.title")}
      </h2>

      <p
        class="text-sm sm:text-base text-base-content/75 leading-relaxed font-sans max-w-xl mx-auto"
      >
        {t("landing.donate.subtitle")}
      </p>
    </div>

    <!-- Dual Donation Cards Grid -->
    <div
      class="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8 max-w-4xl mx-auto"
    >
      <!-- Method 1: Ko-fi -->
      <div
        class="group relative rounded-3xl p-[1.5px] bg-gradient-to-b from-rose-500/40 via-rose-500/15 to-base-content/10 hover:from-rose-500/70 hover:to-rose-500/40 transition-all duration-300 ease-in-out shadow-xl hover:shadow-2xl hover:shadow-rose-500/15 hover:-translate-y-1.5"
      >
        <div
          class="bg-base-100/95 rounded-[calc(1.5rem-1.5px)] p-6 sm:p-8 flex flex-col justify-between h-full backdrop-blur-2xl relative overflow-hidden"
        >
          <!-- Subtle corner flare -->
          <div
            class="absolute -right-10 -bottom-10 w-44 h-44 bg-rose-500/10 rounded-full blur-2xl pointer-events-none group-hover:bg-rose-500/20 transition-all duration-500 ease-in-out"
          ></div>

          <div class="space-y-5 relative z-10">
            <!-- Card Top Header -->
            <div class="flex items-center justify-between gap-4">
              <div
                class="w-16 h-16 rounded-2xl bg-[#FF5E5B]/10 border border-[#FF5E5B]/25 flex items-center justify-center shadow-inner transition-transform duration-300 ease-in-out group-hover:scale-110 overflow-hidden"
              >
                <!-- Ko-fi Rainbow Animated GIF -->
                <img
                  src="/branding/Ko-fi_RAINBOW.gif"
                  alt="Ko-fi Rainbow"
                  class="w-full h-full object-contain select-none pointer-events-none"
                  loading="lazy"
                />
              </div>

              <span
                class="badge badge-sm font-mono text-[11px] font-bold bg-rose-500/15 text-rose-600 dark:text-rose-400 border border-rose-500/30"
              >
                {t("landing.donate.kofiBadge")}
              </span>
            </div>

            <!-- Card Body -->
            <div class="space-y-2">
              <h3
                class="text-xl sm:text-2xl font-black font-display text-base-content flex items-center gap-2"
              >
                <span>{t("landing.donate.kofiTitle")}</span>
              </h3>
              <div
                class="inline-block font-mono text-xs text-rose-500/90 font-medium"
              >
                https://ko-fi.com/danilofiumi
              </div>
              <p
                class="text-xs sm:text-sm text-base-content/70 leading-relaxed font-sans pt-1"
              >
                {t("landing.donate.kofiDesc")}
              </p>
            </div>
          </div>

          <!-- Card Footer Action -->
          <div class="pt-6 relative z-10">
            <a
              href="https://ko-fi.com/danilofiumi"
              target="_blank"
              rel="noopener noreferrer"
              class="btn w-full bg-[#FF5E5B] hover:bg-[#f04b48] text-white border-0 rounded-2xl font-bold font-display shadow-lg shadow-[#FF5E5B]/25 flex items-center justify-center gap-2 transition-all duration-300 ease-in-out hover:scale-[1.02] active:scale-[0.98] select-none"
            >
              <span>{t("landing.donate.kofiAction")}</span>
              <svg
                class="w-4 h-4 transition-transform duration-300 ease-in-out group-hover:translate-x-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2.5"
                  d="M14 5l7 7m0 0l-7 7m7-7H3"
                />
              </svg>
            </a>
          </div>
        </div>
      </div>

      <!-- Method 2: Buy Me a Coffee -->
      <div
        class="group relative rounded-3xl p-[1.5px] bg-gradient-to-b from-amber-400/40 via-amber-400/15 to-base-content/10 hover:from-amber-400/70 hover:to-amber-400/40 transition-all duration-300 ease-in-out shadow-xl hover:shadow-2xl hover:shadow-amber-400/15 hover:-translate-y-1.5"
      >
        <div
          class="bg-base-100/95 rounded-[calc(1.5rem-1.5px)] p-6 sm:p-8 flex flex-col justify-between h-full backdrop-blur-2xl relative overflow-hidden"
        >
          <!-- Subtle corner flare -->
          <div
            class="absolute -right-10 -bottom-10 w-44 h-44 bg-amber-400/10 rounded-full blur-2xl pointer-events-none group-hover:bg-amber-400/20 transition-all duration-500 ease-in-out"
          ></div>

          <div class="space-y-5 relative z-10">
            <!-- Card Top Header -->
            <div class="flex items-center justify-between gap-4">
              <div
                class="w-16 h-16 rounded-2xl bg-[#FFDD00]/15 border border-[#FFDD00]/30 flex items-center justify-center p-1 shadow-inner transition-transform duration-300 ease-in-out group-hover:scale-110 overflow-hidden"
              >
                <!-- Buy Me A Coffee Animated Sticker GIF -->
                <img
                  src="/branding/Support Me Sticker by Buy Me a Coffee - Find & Share on GIPHY.gif"
                  alt="Buy Me a Coffee Sticker"
                  class="w-full mix-blend-darken h-full object-contain select-none pointer-events-none"
                  loading="lazy"
                />
              </div>

              <span
                class="badge badge-sm font-mono text-[11px] font-bold bg-amber-400/15 text-amber-600 dark:text-amber-400 border border-amber-400/30"
              >
                {t("landing.donate.bmacBadge")}
              </span>
            </div>

            <!-- Card Body -->
            <div class="space-y-2">
              <h3
                class="text-xl sm:text-2xl font-black font-display text-base-content flex items-center gap-2"
              >
                <span>{t("landing.donate.bmacTitle")}</span>
              </h3>
              <div
                class="inline-block font-mono text-xs text-amber-500/90 font-medium"
              >
                https://buymeacoffee.com/danilofiumi
              </div>
              <p
                class="text-xs sm:text-sm text-base-content/70 leading-relaxed font-sans pt-1"
              >
                {t("landing.donate.bmacDesc")}
              </p>
            </div>
          </div>

          <!-- Card Footer Action -->
          <div class="pt-6 relative z-10">
            <a
              href="https://buymeacoffee.com/danilofiumi"
              target="_blank"
              rel="noopener noreferrer"
              class="btn w-full bg-[#FFDD00] hover:bg-[#f5d300] text-slate-900 border-0 rounded-2xl font-bold font-display shadow-lg shadow-amber-400/25 flex items-center justify-center gap-2 transition-all duration-300 ease-in-out hover:scale-[1.02] active:scale-[0.98] select-none"
            >
              <span>{t("landing.donate.bmacAction")}</span>
              <svg
                class="w-4 h-4 transition-transform duration-300 ease-in-out group-hover:translate-x-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2.5"
                  d="M14 5l7 7m0 0l-7 7m7-7H3"
                />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Open Source Code on GitHub Badge -->
    <div
      class="flex flex-col sm:flex-row items-center justify-center gap-3 pt-4"
    >
      <a
        href="https://github.com/danilofiumi/Hackaton_VetSentinel"
        target="_blank"
        rel="noopener noreferrer"
        class="group inline-flex items-center gap-3 px-5 py-3 rounded-2xl bg-base-100/90 hover:bg-base-100 border border-base-content/15 hover:border-primary/50 shadow-md hover:shadow-xl hover:shadow-primary/10 transition-all duration-300 ease-in-out hover:-translate-y-1 active:scale-95 text-base-content backdrop-blur-md select-none"
      >
        <div
          class="w-8 h-8 rounded-xl bg-base-content/5 group-hover:bg-primary/10 border border-base-content/10 group-hover:border-primary/30 flex items-center justify-center text-base-content group-hover:text-primary transition-all duration-300 ease-in-out"
        >
          <!-- GitHub SVG Icon -->
          <svg
            class="w-4 h-4 fill-current transition-transform duration-300 ease-in-out group-hover:scale-110"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
            />
          </svg>
        </div>

        <div class="flex items-center gap-2 font-mono text-xs">
          <span
            class="font-bold hidden sm:block text-base-content/90 group-hover:text-primary transition-colors"
          >
            {t("landing.donate.githubBadge")}
          </span>
          <span class="text-base-content/30 font-normal">|</span>
          <span
            class="text-base-content/60 font-medium group-hover:text-base-content/80 transition-colors"
          >
            danilofiumi/Hackaton_VetSentinel
          </span>
        </div>

        <span
          class="badge badge-xs sm:badge-sm font-mono text-[10px] bg-primary/10 text-primary border border-primary/25 ml-1 transition-transform duration-300 ease-in-out group-hover:translate-x-0.5"
        >
          ★ Open Source
        </span>

        <svg
          class="w-4 h-4 text-base-content/40 group-hover:text-primary transition-all duration-300 ease-in-out group-hover:translate-x-0.5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
          />
        </svg>
      </a>
    </div>
  </div>
</section>
