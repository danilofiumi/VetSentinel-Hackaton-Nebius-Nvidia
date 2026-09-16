<script>
  import { cubicInOut } from "svelte/easing";
  import { fade, fly } from "svelte/transition";
  import { t } from "$lib";

  let { p = {}, patient = {}, isCopilotOpen = false } = $props();

  // Helper to extract concise status and directive text for Emesis
  let emesisStatus = $derived.by(() => {
    const raw = (p?.emesis?.label || "").trim();
    const isNo =
      raw.toUpperCase().startsWith("NO") ||
      raw.toLowerCase().includes("contraindicat") ||
      raw.toLowerCase().includes("cannot vomit") ||
      raw.toLowerCase().includes("never");
    const isYes =
      p?.emesis?.allowed ||
      raw.toUpperCase().startsWith("YES") ||
      raw.toLowerCase().includes("induce") ||
      raw.toLowerCase().includes("indicat");

    return {
      isAllowed: isYes && !isNo,
      statusBadge: isNo
        ? t("protocol.statusContraindicated")
        : isYes
          ? t("protocol.statusIndicated")
          : t("protocol.statusAssess"),
      badgeClass: isNo ? "badge-error text-white" : "badge-success text-white",
      directiveText: raw,
      details:
        p?.emesis?.details ||
        "Emesis assessment per species toxicology protocol.",
    };
  });

  // Helper to extract concise status and directive text for Charcoal
  let charcoalStatus = $derived.by(() => {
    const raw = (p?.charcoal?.label || "").trim();
    const isNo =
      raw.toUpperCase().startsWith("NO") ||
      raw.toLowerCase().includes("contraindicat") ||
      raw.toLowerCase().includes("not indicat") ||
      raw.toLowerCase().includes("ineffective");
    const isYes =
      p?.charcoal?.allowed ||
      raw.toUpperCase().startsWith("YES") ||
      raw.toLowerCase().includes("indicat") ||
      raw.toLowerCase().includes("dose");

    return {
      isAllowed: isYes && !isNo,
      statusBadge: isNo
        ? t("protocol.statusNotIndicated")
        : isYes
          ? t("protocol.statusIndicated")
          : t("protocol.statusEvaluate"),
      badgeClass: isNo
        ? "badge-neutral text-base-content/70"
        : "badge-primary text-primary-content",
      directiveText: raw,
      details:
        p?.charcoal?.details ||
        "Adsorbent slurry administration per toxicology guidelines.",
    };
  });

  // Helper to extract concise status and directive text for Antidote
  let antidoteStatus = $derived.by(() => {
    const raw = (p?.antidote?.label || "").trim();
    const name = (p?.antidote?.name || "").trim();
    const isNo =
      raw.toLowerCase().includes("no specific") ||
      name.toLowerCase().includes("no specific") ||
      name.toLowerCase().includes("none exists");
    const isSpecific =
      p?.antidote?.hasSpecific ||
      (!isNo && (raw.length > 0 || name.length > 0));

    return {
      isSpecific,
      statusBadge: isSpecific
        ? t("protocol.statusSpecificRescue")
        : t("protocol.statusSupportiveCare"),
      badgeClass: isSpecific
        ? "badge-warning text-warning-content"
        : "badge-info text-info-content",
      directiveText: raw,
      targetName: name,
      details:
        p?.antidote?.details ||
        "Hemodynamic protocol and continuous organ-support diuresis.",
    };
  });

  // Helper to split text into plain text chunks and clickable citation reference tokens [1], [2], etc.
  function parseCitations(text = "") {
    if (!text) return [];
    const parts = [];
    const regex = /\[(\d+(?:\s*,\s*\d+)*)\]/g;
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push({ type: "text", value: text.slice(lastIndex, match.index) });
      }
      const rawBracket = match[1];
      const nums = rawBracket
        .split(",")
        .map((n) => n.trim())
        .filter(Boolean);
      for (const num of nums) {
        parts.push({ type: "citation", value: `[${num}]`, num });
      }
      lastIndex = regex.lastIndex;
    }

    if (lastIndex < text.length) {
      parts.push({ type: "text", value: text.slice(lastIndex) });
    }

    return parts;
  }

  function scrollToCitation(num) {
    if (typeof document === "undefined") return;
    const targetEl =
      document.getElementById(`citation-${num}`) ||
      document.getElementById("citation-sources");

    if (targetEl) {
      targetEl.scrollIntoView({ behavior: "smooth", block: "center" });
      targetEl.classList.add(
        "ring-2",
        "ring-primary",
        "ring-offset-2",
        "scale-[1.02]",
        "bg-primary/10",
      );
      setTimeout(() => {
        targetEl.classList.remove(
          "ring-2",
          "ring-primary",
          "ring-offset-2",
          "scale-[1.02]",
          "bg-primary/10",
        );
      }, 2000);
    }
  }
</script>

{#snippet citationText(rawText)}
  {#each parseCitations(rawText) as part}
    {#if part.type === "citation"}
      <button
        type="button"
        class="inline-flex items-center px-1.5 py-0.5 mx-0.5 rounded-md font-mono font-bold text-[10px] text-primary bg-primary/10 hover:bg-primary hover:text-primary-content border border-primary/30 transition-all cursor-pointer hover:scale-105 active:scale-95 align-baseline"
        onclick={() => scrollToCitation(part.num)}
        title={`Jump to Source Citation [${part.num}]`}
      >
        {part.value}
      </button>
    {:else}
      {part.value}
    {/if}
  {/each}
{/snippet}

<div
  class="protocol-deck-container w-full space-y-3.5 {isCopilotOpen ? 'is-copilot-open' : ''}"
  in:fade={{ duration: 350, easing: cubicInOut }}
>
  <!-- Section Header -->
  <div
    class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-1"
  >
    <div class="flex items-center gap-2">
      <span class="text-lg">🚨</span>
      <div>
        <h3
          class="text-xs sm:text-sm font-black uppercase tracking-wider text-base-content font-display flex items-center gap-2 flex-wrap"
        >
          <span>{t("protocol.title")}</span>
        </h3>
        <p class="text-[11px] text-base-content/60 mt-0.5">
          {t("protocol.subtitle", { species: patient.specie || "Patient", weight: patient.peso || "?" })}
        </p>
      </div>
    </div>
  </div>

  <!-- Responsive 3-Card Deck -->
  <div
    class="protocol-cards-grid flex flex-col gap-4 items-stretch transition-all duration-300 ease-in-out {isCopilotOpen
      ? 'force-column'
      : ''}"
  >
    <!-- ══════════════════════════════════════════════════ -->
    <!-- CARD 1: GASTRIC EMESIS INDUCTION                   -->
    <!-- ══════════════════════════════════════════════════ -->
    <div
      class="group flex-1 relative flex flex-col justify-between rounded-2xl border backdrop-blur-md overflow-hidden transition-all duration-300 ease-in-out hover:-translate-y-1 hover:shadow-xl {emesisStatus.isAllowed
        ? 'border-success/40 bg-gradient-to-b from-success/10 via-base-100 to-base-100 shadow-success/10'
        : 'border-error/40 bg-gradient-to-b from-error/10 via-base-100 to-base-100 shadow-error/10'}"
      in:fly={{ y: 12, duration: 300, delay: 50, easing: cubicInOut }}
    >
      <!-- Top glowing accent line -->
      <div
        class="h-1.5 w-full {emesisStatus.isAllowed
          ? 'bg-gradient-to-r from-success via-emerald-400 to-success'
          : 'bg-gradient-to-r from-error via-rose-400 to-error'}"
      ></div>

      <div class="p-4 sm:p-5 space-y-3.5 flex-1 flex flex-col">
        <!-- Card Top Bar: Icon + Step Title + Repositioned Status Badge (No truncation) -->
        <div class="flex items-start gap-3">
          <div
            class="w-10 h-10 rounded-xl flex items-center justify-center text-xl shrink-0 shadow-inner mt-0.5 {emesisStatus.isAllowed
              ? 'bg-success/15 text-success border border-success/30'
              : 'bg-error/15 text-error border border-error/30'}"
          >
            {#if emesisStatus.isAllowed}
              <span>🤮</span>
            {:else}
              <span>⛔</span>
            {/if}
          </div>
          <div class="min-w-0 flex-1">
            <div
              class="text-[10px] font-mono font-bold uppercase tracking-wider text-base-content/60 leading-none mb-1"
            >
              {t("protocol.emesisStep")}
            </div>
            <h4
              class="text-sm sm:text-base font-black text-base-content font-display leading-snug"
            >
              {t("protocol.emesisTitle")}
            </h4>
            <div class="mt-2 flex items-center gap-1.5 flex-wrap">
              <span
                class="badge badge-sm font-mono font-black text-[10px] uppercase shadow-xs {emesisStatus.badgeClass}"
              >
                {#if emesisStatus.isAllowed}✓{:else}✕{/if}
                {emesisStatus.statusBadge}
              </span>
            </div>
          </div>
        </div>

        <!-- Full Clinical Directive Callout Strip -->
        {#if emesisStatus.directiveText}
          <div
            class="rounded-xl p-2.5 border text-xs font-semibold leading-snug transition-colors flex items-start gap-2 shadow-2xs {emesisStatus.isAllowed
              ? 'bg-success/10 border-success/30 text-success-content'
              : 'bg-error/10 border-error/30 text-error-content'}"
          >
            <span class="text-sm shrink-0 mt-0.5">
              {#if emesisStatus.isAllowed}⏱️{:else}⚠️{/if}
            </span>
            <div class="min-w-0 flex-1 break-words">
              <span
                class="text-[10px] font-mono font-bold uppercase opacity-70 block"
                >{t("protocol.indicationDirective")}</span
              >
              <span class="font-bold text-base-content"
                >{emesisStatus.directiveText}</span
              >
            </div>
          </div>
        {/if}

        <!-- Execution Details Block -->
        <div
          class="flex-1 rounded-xl p-3 border bg-base-200/30 border-base-300/80 text-xs leading-relaxed text-base-content/85 flex flex-col justify-start gap-1"
        >
          <span
            class="text-[10px] font-mono font-bold uppercase tracking-wider text-base-content/50"
          >
            {t("protocol.protocolGuidance")}
          </span>
          <p class="leading-relaxed">
            {@render citationText(emesisStatus.details)}
          </p>
        </div>
      </div>

      <!-- Card Bottom Indicator -->
      <div
        class="px-4 py-2 border-t text-[11px] font-mono flex items-center justify-between {emesisStatus.isAllowed
          ? 'border-success/20 bg-success/5 text-success font-bold'
          : 'border-error/20 bg-error/5 text-error font-bold'}"
      >
        <span>{t("protocol.window1to2")}</span>
        <span class="text-[10px]"
          >{emesisStatus.isAllowed
            ? t("protocol.activeDecontamination")
            : t("protocol.protectedAirway")}</span
        >
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════ -->
    <!-- CARD 2: ENTERIC TOXIN ADSORPTION (CHARCOAL)        -->
    <!-- ══════════════════════════════════════════════════ -->
    <div
      class="group relative flex flex-col justify-between rounded-2xl border backdrop-blur-md overflow-hidden transition-all duration-300 ease-in-out hover:-translate-y-1 hover:shadow-xl {charcoalStatus.isAllowed
        ? 'border-primary/40 bg-gradient-to-b from-primary/10 via-base-100 to-base-100 shadow-primary/10'
        : 'border-base-300 bg-gradient-to-b from-base-200/40 via-base-100 to-base-100'}"
      in:fly={{ y: 12, duration: 300, delay: 100, easing: cubicInOut }}
    >
      <!-- Top glowing accent line -->
      <div
        class="h-1.5 w-full {charcoalStatus.isAllowed
          ? 'bg-gradient-to-r from-primary via-cyan-400 to-primary'
          : 'bg-gradient-to-r from-base-300 to-base-300'}"
      ></div>

      <div class="p-4 sm:p-5 space-y-3.5 flex-1 flex flex-col">
        <!-- Card Top Bar: Icon + Step Title + Repositioned Status Badge (No truncation) -->
        <div class="flex items-start gap-3">
          <div
            class="w-10 h-10 rounded-xl flex items-center justify-center text-xl shrink-0 shadow-inner mt-0.5 {charcoalStatus.isAllowed
              ? 'bg-primary/15 text-primary border border-primary/30'
              : 'bg-base-200 text-base-content/60 border border-base-300'}"
          >
            <span>🧪</span>
          </div>
          <div class="min-w-0 flex-1">
            <div
              class="text-[10px] font-mono font-bold uppercase tracking-wider text-base-content/60 leading-none mb-1"
            >
              {t("protocol.charcoalStep")}
            </div>
            <h4
              class="text-sm sm:text-base font-black text-base-content font-display leading-snug"
            >
              {t("protocol.charcoalTitle")}
            </h4>
            <div class="mt-2 flex items-center gap-1.5 flex-wrap">
              <span
                class="badge badge-sm font-mono font-black text-[10px] uppercase shadow-xs {charcoalStatus.badgeClass}"
              >
                {#if charcoalStatus.isAllowed}✓{:else}ℹ{/if}
                {charcoalStatus.statusBadge}
              </span>
            </div>
          </div>
        </div>

        <!-- Full Clinical Directive Callout Strip -->
        {#if charcoalStatus.directiveText}
          <div
            class="rounded-xl p-2.5 border text-xs font-semibold leading-snug transition-colors flex items-start gap-2 shadow-2xs {charcoalStatus.isAllowed
              ? 'bg-primary/10 border-primary/30 text-primary-content'
              : 'bg-base-200/60 border-base-300 text-base-content/80'}"
          >
            <span class="text-sm shrink-0 mt-0.5">
              {#if charcoalStatus.isAllowed}🧫{:else}🚫{/if}
            </span>
            <div class="min-w-0 flex-1 break-words">
              <span
                class="text-[10px] font-mono font-bold uppercase opacity-70 block"
                >{t("protocol.adsorptionDirective")}</span
              >
              <span class="font-bold text-base-content"
                >{charcoalStatus.directiveText}</span
              >
            </div>
          </div>
        {/if}

        <!-- Execution Details Block -->
        <div
          class="flex-1 rounded-xl p-3 border bg-base-200/30 border-base-300/80 text-xs leading-relaxed text-base-content/85 flex flex-col justify-start gap-1"
        >
          <span
            class="text-[10px] font-mono font-bold uppercase tracking-wider text-base-content/50"
          >
            {t("protocol.administrationGuidance")}
          </span>
          <p class="leading-relaxed">
            {@render citationText(charcoalStatus.details)}
          </p>
        </div>
      </div>

      <!-- Card Bottom Indicator -->
      <div
        class="px-4 py-2 border-t text-[11px] font-mono flex items-center justify-between {charcoalStatus.isAllowed
          ? 'border-primary/20 bg-primary/5 text-primary font-bold'
          : 'border-base-200 bg-base-200/30 text-base-content/60'}"
      >
        <span>{t("protocol.standardCharcoal")}</span>
        <span class="text-[10px]"
          >{charcoalStatus.isAllowed
            ? t("protocol.aspirationRiskGuard")
            : t("protocol.standardCare")}</span
        >
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════ -->
    <!-- CARD 3: TARGETED ANTIDOTE & FLUID THERAPY          -->
    <!-- ══════════════════════════════════════════════════ -->
    <div
      class="group relative flex flex-col justify-between rounded-2xl border backdrop-blur-md overflow-hidden transition-all duration-300 ease-in-out hover:-translate-y-1 hover:shadow-xl {antidoteStatus.isSpecific
        ? 'border-warning/40 bg-gradient-to-b from-warning/10 via-base-100 to-base-100 shadow-warning/10'
        : 'border-info/40 bg-gradient-to-b from-info/10 via-base-100 to-base-100 shadow-info/10'}"
      in:fly={{ y: 12, duration: 300, delay: 150, easing: cubicInOut }}
    >
      <!-- Top glowing accent line -->
      <div
        class="h-1.5 w-full {antidoteStatus.isSpecific
          ? 'bg-gradient-to-r from-warning via-amber-400 to-warning'
          : 'bg-gradient-to-r from-info via-sky-400 to-info'}"
      ></div>

      <div class="p-4 sm:p-5 space-y-3.5 flex-1 flex flex-col">
        <!-- Card Top Bar: Icon + Step Title + Repositioned Status Badge (No truncation) -->
        <div class="flex items-start gap-3">
          <div
            class="w-10 h-10 rounded-xl flex items-center justify-center text-xl shrink-0 shadow-inner mt-0.5 {antidoteStatus.isSpecific
              ? 'bg-warning/15 text-warning border border-warning/30'
              : 'bg-info/15 text-info border border-info/30'}"
          >
            <span>💉</span>
          </div>
          <div class="min-w-0 flex-1">
            <div
              class="text-[10px] font-mono font-bold uppercase tracking-wider text-base-content/60 leading-none mb-1"
            >
              {t("protocol.antidoteStep")}
            </div>
            <h4
              class="text-sm sm:text-base font-black text-base-content font-display leading-snug"
            >
              {t("protocol.antidoteTitle")}
            </h4>
            <div class="mt-2 flex items-center gap-1.5 flex-wrap">
              <span
                class="badge badge-sm font-mono font-black text-[10px] uppercase shadow-xs {antidoteStatus.badgeClass}"
              >
                ⚡ {antidoteStatus.statusBadge}
              </span>
            </div>
          </div>
        </div>

        <!-- Dedicated Primary Therapeutic Focus Chip -->
        {#if antidoteStatus.targetName}
          <div
            class="rounded-xl p-2.5 border shadow-2xs flex items-center gap-2.5 {antidoteStatus.isSpecific
              ? 'bg-warning/15 border-warning/35 text-base-content'
              : 'bg-info/15 border-info/35 text-base-content'}"
          >
            <span class="text-base shrink-0">🎯</span>
            <div class="min-w-0 flex-1">
              <span
                class="text-[9px] font-mono font-bold uppercase tracking-wider text-base-content/60 block"
              >
                {t("protocol.primaryTherapeuticFocus")}
              </span>
              <div
                class="text-xs font-black break-words leading-tight font-display {antidoteStatus.isSpecific
                  ? 'text-warning-content'
                  : 'text-info-content'}"
              >
                {antidoteStatus.targetName}
              </div>
            </div>
          </div>
        {/if}

        <!-- Full Clinical Directive Callout Strip -->
        {#if antidoteStatus.directiveText && antidoteStatus.directiveText !== antidoteStatus.targetName}
          <div
            class="rounded-xl p-2.5 border text-xs font-semibold leading-snug transition-colors flex items-start gap-2 shadow-2xs {antidoteStatus.isSpecific
              ? 'bg-warning/10 border-warning/30 text-warning-content'
              : 'bg-info/10 border-info/30 text-info-content'}"
          >
            <span class="text-sm shrink-0 mt-0.5">🧬</span>
            <div class="min-w-0 flex-1 break-words">
              <span
                class="text-[10px] font-mono font-bold uppercase opacity-70 block"
                >{t("protocol.targetDirective")}</span
              >
              <span class="font-bold text-base-content"
                >{antidoteStatus.directiveText}</span
              >
            </div>
          </div>
        {/if}

        <!-- Execution Details Block -->
        <div
          class="flex-1 rounded-xl p-3 border bg-base-200/30 border-base-300/80 text-xs leading-relaxed text-base-content/85 flex flex-col justify-start gap-1"
        >
          <span
            class="text-[10px] font-mono font-bold uppercase tracking-wider text-base-content/50"
          >
            {t("protocol.hemodynamicOrganSupport")}
          </span>
          <p class="leading-relaxed">
            {@render citationText(antidoteStatus.details)}
          </p>
        </div>
      </div>

      <!-- Card Bottom Indicator -->
      <div
        class="px-4 py-2 border-t text-[11px] font-mono flex items-center justify-between {antidoteStatus.isSpecific
          ? 'border-warning/20 bg-warning/5 text-warning font-bold'
          : 'border-info/20 bg-info/5 text-info font-bold'}"
      >
        <span>{t("protocol.hemodynamicStabilization")}</span>
        <span class="text-[10px]">{t("protocol.continuousEcgDiuresis")}</span>
      </div>
    </div>
  </div>
</div>

<style>
  .protocol-deck-container {
    container-type: inline-size;
    container-name: protocolDeck;
  }

  /* Default / Column mode: cards stack vertically with full width when space is constrained or copilot is open */
  .protocol-cards-grid {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
  .protocol-cards-grid > * {
    width: 100%;
  }

  /* When there is enough inline space (>= 900px) AND copilot is NOT open:
     Display as a balanced 3-card horizontal flex row with equal height! */
  @container protocolDeck (min-width: 900px) {
    .protocol-cards-grid:not(.force-column) {
      display: flex;
      flex-direction: row;
      align-items: stretch;
    }
    .protocol-cards-grid:not(.force-column) > * {
      flex: 1 1 0px;
      min-width: 0;
      width: auto;
    }
  }
</style>
