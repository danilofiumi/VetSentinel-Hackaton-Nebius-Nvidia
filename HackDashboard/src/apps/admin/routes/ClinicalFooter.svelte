<script>
  import Links from "$lib/components/Links.svelte";
  import { cubicInOut } from "svelte/easing";
  import { fly, fade } from "svelte/transition";
  import VetSentinelLogo from "./VetSentinelLogo.svelte";
  import AuthCredits from "$lib/components/AuthCredits.svelte";
  import { t } from "$lib";

  let { onOpenEmergency } = $props();

  let activeLegalModal = $state(null); // 'privacy' | 'terms' | null

  function openLegal(type) {
    activeLegalModal = type;
  }

  function closeLegal() {
    activeLegalModal = null;
  }
</script>

<footer
  class="border-t border-base-content/10 bg-base-100/85 backdrop-blur-xl text-base-content/75 transition-colors duration-300 relative z-10"
>
  <!-- Main Multi-Column Links Section -->
  <div class="max-w-7xl relative mx-auto px-4 sm:px-6 py-12">
    <div
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-8 lg:gap-10"
    >
      <!-- Column 1: Brand & Veterinary Mission (4 cols) -->
      <div class="lg:col-span-4 space-y-4 text-left">
        <div class="flex items-center gap-3">
          <VetSentinelLogo size="md" withPulse={false} />
          <div>
            <span
              class="text-lg font-black tracking-tight font-display text-base-content"
            >
              VetSentinel
            </span>
            <span
              class="badge badge-xs badge-primary font-mono font-bold ml-1.5 uppercase"
            >
              ER Copilot
            </span>
          </div>
        </div>

        <p class="text-xs text-base-content/70 font-sans leading-relaxed">
          Veterinary Emergency & Toxicology Clinical Decision Support System.
          Engineered to turn acute poisoning panic into verified,
          milligram-precise protocols in under 10 seconds.
        </p>

        <!-- Clinical Decision Support Notice -->
        <div
          class="p-3 rounded-2xl bg-base-200/60 border border-base-content/10 space-y-1 text-[11px] text-base-content/70"
        >
          <div
            class="flex items-center gap-1.5 font-bold text-base-content/90 font-mono uppercase tracking-wider text-[10px]"
          >
            <span>⚖️</span>
            <span>{t("footer.disclaimerTitle")}</span>
          </div>
          <p class="leading-snug">
            {t("footer.disclaimer")}
          </p>
        </div>
      </div>

      <!-- Column 2: Clinical Workflows (2 cols) -->
      <div class="lg:col-span-2 space-y-3">
        <p
          class="text-xs font-bold font-mono uppercase tracking-wider text-base-content"
        >
          {t("footer.toolsTitle")}
        </p>
        <ul class="space-y-2 text-xs text-base-content/70">
          <li>
            <a
              href="/dashboard"
              class="hover:text-primary transition-colors flex items-center gap-1.5"
            >
              <span>›</span> {t("footer.liveWorkstation")}
            </a>
          </li>
          <li>
            <a
              href="/dashboard"
              class="hover:text-primary transition-colors flex items-center gap-1.5"
            >
              <span>›</span> {t("footer.triageIntake")}
            </a>
          </li>
          <li>
            <a
              href="/dashboard"
              class="hover:text-primary transition-colors flex items-center gap-1.5"
            >
              <span>›</span> {t("footer.massDosing")}
            </a>
          </li>
          <li>
            <button
              type="button"
              onclick={onOpenEmergency}
              class="hover:text-primary transition-colors flex items-center gap-1.5 cursor-pointer text-left"
            >
              <span>›</span> {t("footer.poisonDirectory")}
            </button>
          </li>
          <li>
            <a
              href="/dashboard"
              class="hover:text-primary transition-colors flex items-center gap-1.5"
            >
              <span>›</span> {t("footer.emrTransfer")}
            </a>
          </li>
        </ul>
      </div>

      <!-- Column 3: Platform & Hackathon (3 cols) -->
      <div class="lg:col-span-3 space-y-3">
        <p
          class="text-xs font-bold font-mono uppercase tracking-wider text-base-content"
        >
          {t("footer.techTitle")}
        </p>
        <ul class="space-y-2 text-xs text-base-content/70">
          <li>
            <a
              href="/hackathon"
              class="hover:text-primary transition-colors flex items-center gap-1.5 font-bold text-primary"
            >
              <span>★</span> Hackathon Tech Specs
            </a>
          </li>
          <li>
            <a
              href="/hackathon"
              class="hover:text-primary transition-colors flex items-center gap-1.5"
            >
              <span>›</span> Dagu DAG Pipeline Engine
            </a>
          </li>
          <li>
            <a
              href="/hackathon"
              class="hover:text-primary transition-colors flex items-center gap-1.5"
            >
              <span>›</span> Nebius AI (GLM-5.3-Flash)
            </a>
          </li>
          <li>
            <a
              href="/hackathon"
              class="hover:text-primary transition-colors flex items-center gap-1.5"
            >
              <span>›</span> Tavily Whitelisted Search
            </a>
          </li>
          <li>
            <a
              href="/hackathon"
              class="hover:text-primary transition-colors flex items-center gap-1.5"
            >
              <span>›</span> Svelte 5 Runes Telemetry
            </a>
          </li>
          <li>
            <a
              href="/hackathon"
              class="hover:text-primary transition-colors flex items-center gap-1.5"
            >
              <span>›</span> Expanded 8-Question Q&A
            </a>
          </li>
        </ul>
      </div>

      <!-- Column 4: Evidence & Legal (3 cols) -->
      <div class="lg:col-span-3 space-y-3">
        <p
          class="text-xs font-bold font-mono uppercase tracking-wider text-base-content"
        >
          {t("footer.complianceTitle")}
        </p>
        <ul class="space-y-2 text-xs text-base-content/70">
          <li class="flex items-center gap-1.5">
            <span class="text-success">✓</span> ASPCA APCC Formularies
          </li>
          <li class="flex items-center gap-1.5">
            <span class="text-success">✓</span> Merck Veterinary Manual 11th Ed
          </li>
          <li class="flex items-center gap-1.5">
            <span class="text-success">✓</span> BSAVA Small Animal Formulary
          </li>
          <li class="pt-2">
            <button
              type="button"
              onclick={() => openLegal("privacy")}
              class="text-xs font-bold hover:text-primary transition-colors underline cursor-pointer text-left"
            >
              {t("footer.privacyPolicy")}
            </button>
          </li>
          <li>
            <button
              type="button"
              onclick={() => openLegal("terms")}
              class="text-xs font-bold hover:text-primary transition-colors underline cursor-pointer text-left"
            >
              {t("footer.termsOfUse")}
            </button>
          </li>
        </ul>
      </div>
    </div>

    <!-- Creator Credit & Community Bar -->
    <div
      class="mt-10 pt-8 border-t border-base-content/10 flex flex-col sm:flex-row items-center justify-between gap-4"
    >
      <AuthCredits />
      <Links />
    </div>
  </div>

  <!-- Bottom Legal & Copyright Bar -->
  <div
    class="border-t border-base-content/10 bg-base-200/50 py-4 px-4 sm:px-6 text-xs text-base-content/60"
  >
    <div
      class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 font-sans"
    >
      <p class="text-[11px]">
        © 2026 {t("footer.copyright")}. All rights reserved.
      </p>

      <div class="flex flex-wrap items-center gap-4 text-[11px] font-mono">
        <button
          type="button"
          onclick={() => openLegal("privacy")}
          class="hover:text-base-content hover:underline cursor-pointer"
        >
          {t("footer.privacyPolicy")}
        </button>
        <span>·</span>
        <button
          type="button"
          onclick={() => openLegal("terms")}
          class="hover:text-base-content hover:underline cursor-pointer"
        >
          {t("footer.termsOfUse")}
        </button>
      </div>
    </div>
  </div>
</footer>

<!-- Interactive Legal Modal (Privacy Policy & Terms) -->
{#if activeLegalModal}
  <div
    class="modal modal-open z-50 backdrop-blur-md"
    transition:fade={{ duration: 200 }}
  >
    <div
      class="modal-box max-w-3xl bg-base-100/95 border border-base-content/20 shadow-2xl rounded-3xl p-6 sm:p-8 space-y-5"
      in:fly={{ y: 20, duration: 300, easing: cubicInOut }}
    >
      <div
        class="flex items-center justify-between border-b border-base-content/10 pb-4"
      >
        <div class="flex items-center gap-2.5">
          <span class="text-2xl">⚖️</span>
          <div>
            <h3
              class="font-bold font-display text-lg sm:text-xl text-base-content"
            >
              {activeLegalModal === "privacy"
                ? "Privacy Policy & Zero-PII Guarantee"
                : "Terms of Clinical Use & Medical Disclaimer"}
            </h3>
            <p class="text-xs text-base-content/60 font-mono">
              VetSentinel Veterinary Clinical Compliance · Revision 2026.09
            </p>
          </div>
        </div>

        <button
          type="button"
          class="btn btn-sm btn-circle btn-ghost"
          onclick={closeLegal}
        >
          ✕
        </button>
      </div>

      <div
        class="max-h-96 overflow-y-auto space-y-4 text-xs sm:text-sm text-base-content/80 font-sans leading-relaxed pr-2"
      >
        {#if activeLegalModal === "privacy"}
          <div>
            <h4 class="font-bold text-base-content text-sm mb-1">
              1. Zero-PII (Personally Identifiable Information) Architecture
            </h4>
            <p>
              VetSentinel does not collect, transmit, or store personal
              information regarding pet owners, client billing information, or
              veterinary personnel. When entering clinical cases into the intake
              system, only species, estimated mass (kg), time since ingestion,
              and clinical symptoms are processed.
            </p>
          </div>

          <div>
            <h4 class="font-bold text-base-content text-sm mb-1">
              2. Localized Artifact Persistence
            </h4>
            <p>
              All Dagu pipeline outputs (JSON reports and Markdown emergency
              sheets) are stored locally on the clinic's local workstation
              filesystem. No case data is monetized, sold, or shared with
              third-party advertisers.
            </p>
          </div>

          <div>
            <h4 class="font-bold text-base-content text-sm mb-1">
              3. External Query Sanitization
            </h4>
            <p>
              Inquiries dispatched to search services (Tavily) are strictly
              sanitized into generic veterinary pharmacological terms (e.g. <em
                >"feline lilium nephrotoxicosis fluid rate"</em
              >). No identifiers link searches back to specific patients or
              clinical practices.
            </p>
          </div>
        {:else}
          <div>
            <h4 class="font-bold text-base-content text-sm mb-1">
              1. Clinical Decision-Support Scope
            </h4>
            <p>
              VetSentinel is provided exclusively as an emergency clinical
              decision-support co-pilot for licensed veterinarians, veterinary
              technicians, and trained animal care practitioners. It is not an
              automated medical dispensing device and does not form a
              veterinarian-client-patient relationship (VCPR).
            </p>
          </div>

          <div>
            <h4 class="font-bold text-base-content text-sm mb-1">
              2. Veterinary Practitioner Responsibility
            </h4>
            <p>
              All calculated fluid rates, drug concentrations, and emesis
              recommendations must be reviewed, verified, and approved by the
              attending licensed veterinarian before patient administration.
              Clinicians must independently confirm compatibility with
              underlying conditions (cardiac, renal, or hepatic impairment).
            </p>
          </div>

          <div>
            <h4 class="font-bold text-base-content text-sm mb-1">
              3. Limitation of Liability
            </h4>
            <p>
              While VetSentinel synthesizes guidelines strictly from certified
              reference authorities (ASPCA APCC, Merck Veterinary Manual,
              BSAVA), the software authors and contributors disclaim liability
              for adverse reactions, patient idiosyncrasies, or clinical
              outcomes resulting from emergency interventions.
            </p>
          </div>
        {/if}
      </div>

      <div class="border-t border-base-content/10 pt-4 flex justify-end">
        <button
          type="button"
          class="btn btn-primary btn-sm rounded-xl font-bold font-display"
          onclick={closeLegal}
        >
          Understood & Close
        </button>
      </div>
    </div>
  </div>
{/if}
