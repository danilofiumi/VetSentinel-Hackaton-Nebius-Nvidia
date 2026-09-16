<script>
  import { cubicInOut } from "svelte/easing";
  import { slide } from "svelte/transition";
  import { t } from "$lib";

  let openIndex = $state(0);

  let vetFaqs = $derived([
    {
      q: t("landing.faq.item1.q"),
      badge: t("landing.faq.item1.badge"),
      badgeColor: "badge-error",
      answer: t("landing.faq.item1.a"),
    },
    {
      q: t("landing.faq.item2.q"),
      badge: t("landing.faq.item2.badge"),
      badgeColor: "badge-success",
      answer: t("landing.faq.item2.a"),
    },
    {
      q: t("landing.faq.item3.q"),
      badge: t("landing.faq.item3.badge"),
      badgeColor: "badge-primary",
      answer: t("landing.faq.item3.a"),
    },
    {
      q: t("landing.faq.item4.q"),
      badge: t("landing.faq.item4.badge"),
      badgeColor: "badge-warning",
      answer: t("landing.faq.item4.a"),
    },
    {
      q: t("landing.faq.item5.q"),
      badge: t("landing.faq.item5.badge"),
      badgeColor: "badge-accent",
      answer: t("landing.faq.item5.a"),
    },
    {
      q: t("landing.faq.item6.q"),
      badge: t("landing.faq.item6.badge"),
      badgeColor: "badge-secondary",
      answer: t("landing.faq.item6.a"),
    },
    {
      q: t("landing.faq.item7.q"),
      badge: t("landing.faq.item7.badge"),
      badgeColor: "badge-neutral",
      answer: t("landing.faq.item7.a"),
    },
  ]);

  function toggle(idx) {
    openIndex = openIndex === idx ? -1 : idx;
  }
</script>

<section
  id="vet-faq"
  class="py-16 sm:py-20 border-b border-base-content/10 relative bg-gradient-to-b from-base-200/90 via-base-100/70 to-base-200/90 overflow-hidden"
>
  <!-- Centered Ambient Radial Pulse Glow -->
  <div
    class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[850px] h-[450px] bg-[radial-gradient(ellipse_at_center,color-mix(in_srgb,var(--color-primary)_14%,transparent)_0%,transparent_70%)] blur-3xl pointer-events-none -z-10"
    aria-hidden="true"
  ></div>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 space-y-8">
    <!-- Header -->
    <div class="text-center space-y-3">
      <div
        class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary font-mono text-xs font-bold uppercase tracking-wider"
      >
        <span>🩺</span>
        <span>{t("landing.faq.badge")}</span>
      </div>
      <h2
        class="text-3xl sm:text-4xl font-black font-display tracking-tight text-base-content"
      >
        {t("landing.faq.title")}
      </h2>
      <p class="text-sm sm:text-base text-base-content/70 font-sans">
        {t("landing.faq.subtitle")}
      </p>
    </div>

    <!-- Accordion List -->
    <div class="space-y-3">
      {#each vetFaqs as item, i}
        <div
          class="card border rounded-3xl overflow-hidden transition-all duration-500 ease-out {openIndex ===
          i
            ? 'bg-gradient-to-r from-primary/[0.01] via-base-100 to-base-100/95 border-primary/50 shadow-lg -translate-y-0.5'
            : 'bg-base-100/90 border-base-content/12 hover:border-primary/40 shadow-xs'}"
        >
          <button
            type="button"
            class="w-full p-5 sm:p-6 text-left flex items-center justify-between gap-4 cursor-pointer"
            onclick={() => toggle(i)}
          >
            <div class="flex items-center gap-3">
              <span
                class="w-8 h-8 rounded-xl bg-base-200 border border-base-300 flex items-center justify-center font-mono font-bold text-xs text-primary shadow-xs shrink-0"
              >
                Q{i + 1}
              </span>
              <div>
                <span
                  class="badge badge-ghost badge-xs font-mono font-bold text-[9px] mb-1 text-black shadow-xs"
                >
                  {item.badge}
                </span>
                <h3
                  class="text-sm sm:text-base font-bold font-display text-black"
                >
                  {item.q}
                </h3>
              </div>
            </div>

            <div
              class="w-8 h-8 rounded-full bg-base-200 flex items-center justify-center text-xs transition-transform duration-300 shrink-0 {openIndex ===
              i
                ? 'rotate-180 text-primary'
                : 'text-base-content/50'}"
            >
              ▼
            </div>
          </button>

          {#if openIndex === i}
            <div
              transition:slide={{ duration: 300, easing: cubicInOut }}
              class="px-5 pb-6 pt-1 sm:px-6 sm:pb-7 text-xs sm:text-sm text-base-content/85 leading-relaxed font-sans border-t border-base-content/10 bg-base-200/30"
            >
              <div
                class="p-4 rounded-2xl bg-base-100/95 border border-base-content/10 text-base-content/90 shadow-inner leading-relaxed"
              >
                {item.answer}
              </div>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  </div>
</section>
