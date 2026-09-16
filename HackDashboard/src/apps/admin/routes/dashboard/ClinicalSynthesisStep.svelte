<script>
  import { fly, fade } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";
  import StepLoader from "./StepLoader.svelte";
  import ImmediateInterventionProtocol from "./ImmediateInterventionProtocol.svelte";
  import DosageCalculationDeck from "./DosageCalculationDeck.svelte";
  import { t } from "$lib";

  let {
    patient,
    artifactsData = null,
    runStatus = "idle",
    nodeStatus = "not_started",
    nextUnlocked = false,
    onBack,
    onNext = null,
    onReset,
    onOpenDagu,
    isCopilotOpen = false,
  } = $props();

  let hasData = $derived(Boolean(artifactsData?.synthesis));
  let isRunning = $derived(
    nodeStatus === "running" || (runStatus === "running" && !hasData),
  );
  let isProcessing = $derived(!hasData && isRunning);

  let copied = $state(false);

  function getProtocol() {
    if (artifactsData && artifactsData.synthesis) {
      const syn = artifactsData.synthesis;
      const proto = syn.immediate_intervention_protocol || {};
      const emesisInfo = proto.emesis_induction || {};
      const charcoalInfo = proto.activated_charcoal || {};
      const antidoteInfo = proto.specific_antidote || {};

      const isEmesisYes = (emesisInfo.indication || "")
        .toUpperCase()
        .includes("YES");
      const isCharcoalYes = (charcoalInfo.indication || "")
        .toUpperCase()
        .includes("YES");

      const drugsList = Array.isArray(syn.dosage_calculation_table)
        ? syn.dosage_calculation_table.map((d) => ({
            name: d.drug,
            standardDose: d.standard_dosage,
            calculatedDose: d.patient_dose,
            route: d.route,
            concentration: d.formulation,
            notes: d.monitoring,
          }))
        : [];

      const citationsList = Array.isArray(syn.mandatory_sources)
        ? syn.mandatory_sources.map((f, i) => ({
            ref: f.id || `[${i + 1}]`,
            source: f.source || "Official Source",
            title: f.title || "Toxicology Guidelines",
            url: f.url || "https://www.aspca.org",
          }))
        : [];

      return {
        tipo:
          syn.presumptive_diagnosis ||
          "Emergency Clinical Synthesis & Dosage Calculation",
        emesis: {
          allowed: isEmesisYes,
          label: emesisInfo.indication || (isEmesisYes ? "YES" : "NO"),
          badgeColor: isEmesisYes ? "badge-success" : "badge-error",
          details:
            emesisInfo.details || "Emesis assessment per clinical protocol.",
        },
        charcoal: {
          allowed: isCharcoalYes,
          label: charcoalInfo.indication || (isCharcoalYes ? "YES" : "NO"),
          badgeColor: isCharcoalYes ? "badge-success" : "badge-neutral",
          details:
            charcoalInfo.details ||
            "Adsorbent assessment per clinical protocol.",
        },
        antidote: {
          hasSpecific: Boolean(antidoteInfo.indication),
          label: antidoteInfo.indication || "Intensive Support",
          badgeColor: "badge-warning",
          name: antidoteInfo.indication || "Supportive Therapy",
          details:
            antidoteInfo.details ||
            "Hemodynamic protocol and continuous hydration.",
        },
        drugs: drugsList,
        citations: citationsList,
      };
    }

    return null;
  }

  let p = $derived(getProtocol());

  function copyClinicalReport() {
    if (artifactsData && artifactsData.sheetMd) {
      navigator.clipboard.writeText(artifactsData.sheetMd);
      copied = true;
      setTimeout(() => (copied = false), 3000);
      return;
    }
    if (!p) return;

    let report = `=== VETSENTINEL · EMERGENCY CLINICAL PROTOCOL ===\n`;
    report += `Patient: ${patient.specie} (${patient.razza || "Unspecified"}), Weight: ${patient.peso} kg\n`;
    report += `Priority: ${patient.priorita.toUpperCase()} | Presumptive Diagnosis: ${p.tipo}\n`;
    report += `Anamnesis: ${patient.sintomi}\n\n`;
    report += `--- IMMEDIATE INTERVENTION PROTOCOL ---\n`;
    report += `1. Emesis Induction: ${p.emesis.label} - ${p.emesis.details}\n`;
    report += `2. Activated Charcoal: ${p.charcoal.label} - ${p.charcoal.details}\n`;
    report += `3. Antidote/Supportive Care: ${p.antidote.name} - ${p.antidote.details}\n\n`;
    report += `--- DOSAGE CALCULATIONS FOR ${patient.peso} KG ---\n`;
    p.drugs.forEach((d) => {
      report += `• ${d.name}: DOSE ${d.calculatedDose} (${d.route}) [Rate: ${d.standardDose}, Conc: ${d.concentration}] - Notes: ${d.notes}\n`;
    });
    report += `\n--- MANDATORY EVIDENCE CITATIONS ---\n`;
    p.citations.forEach((c) => {
      report += `${c.ref} ${c.source}: "${c.title}" (${c.url})\n`;
    });

    navigator.clipboard.writeText(report);
    copied = true;
    setTimeout(() => (copied = false), 3000);
  }

  function printClinicalSheet() {
    window.print();
  }

  let urgencyBadgeClass = $derived.by(() => {
    const pr = (patient.priorita || "").toLowerCase();
    if (pr === "critical" || pr === "critica") return "badge-error text-white";
    if (pr === "urgent" || pr === "urgente")
      return "badge-warning text-base-content";
    return "badge-success text-white";
  });

  // Explicit fallback flag emitted by Step 3 when the AI model was unavailable.
  let isFallback = $derived(Boolean(artifactsData?.synthesis?.fallback));
  let fallbackNotice = $derived(
    artifactsData?.synthesis?.fallback_notice ||
      "AI model unavailable — this protocol was generated by the deterministic rule-based formula, NOT by evidence-grounded AI synthesis. A clinician must manually verify every dose before use.",
  );

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

  // Smart breakdown of presumptive diagnosis into primary condition and structured clinical rationale
  let diagnosisSections = $derived.by(() => {
    const raw = (p?.tipo || "").trim();
    if (!raw) return { title: "", details: [] };

    // If already split by line breaks or bullet points
    if (raw.includes("\n")) {
      const lines = raw
        .split("\n")
        .map((l) => l.replace(/^[-•*]\s*/, "").trim())
        .filter(Boolean);
      return {
        title: lines[0] || raw,
        details: lines.slice(1),
      };
    }

    // Protect decimals (e.g. 32.0kg, 28.1 mg/kg, 0.5ml, .5mg) so periods are never treated as sentence breaks
    const safeText = raw.replace(
      /(?<=\d)\.(?=\d)|(?<=\s|^)\.(?=\d)/g,
      "\u2024",
    );

    // Protect common abbreviations (e.g. approx., vs., etc.)
    const abbrProtected = safeText.replace(
      /\b(spp|sp|vs|eg|ie|dr|mr|ms|approx|min|sec|no|fig|ref|tab|dept)\./gi,
      "$1\u2027",
    );

    // Split on sentence boundaries: punctuation [.!?] optionally followed by citations/brackets/quotes, followed by whitespace
    const rawParts = abbrProtected.split(
      /(?<=[.!?](?:[\]\)\"']|\s*\[\d+(?:\s*,\s*\d+)*\])*)\s+(?=[A-Z0-9\[\(\"'\-])/g,
    );

    // Restore protected decimal dots and abbreviation periods
    const segments = rawParts
      .map((p) =>
        p
          .replace(/\u2024/g, ".")
          .replace(/\u2027/g, ".")
          .trim(),
      )
      .filter(Boolean);

    // Merge back any dangling punctuation, continuation units, or orphaned citations
    const merged = [];
    for (const s of segments) {
      if (!s) continue;
      if (merged.length > 0) {
        const prev = merged[merged.length - 1];
        const prevLastWord = (prev.split(/\s+/).pop() || "").toLowerCase();
        const isAbbr =
          /^(spp|sp|vs|eg|ie|dr|mr|ms|approx|min|sec|no|fig|ref|tab|dept)\.?$/i.test(
            prevLastWord,
          );
        const isDanglingPunct = /^[\)\]\}\:;,]/.test(s);
        const isCitationOnly =
          /^\[\d+(?:\s*,\s*\d+)*\]/.test(s) && !/[.!?]$/.test(prev);
        const isLowerStart = /^[a-z]/.test(s);
        const isDecimalUnitContinuation =
          /^(kg|g|mg|mcg|ml|l|%|cm|mm|oz|lb|hours?|hrs?|mins?|days?)/i.test(s);

        if (
          isAbbr ||
          isDanglingPunct ||
          isCitationOnly ||
          isLowerStart ||
          isDecimalUnitContinuation
        ) {
          merged[merged.length - 1] = prev + " " + s;
          continue;
        }
      }
      merged.push(s);
    }

    if (merged.length > 1) {
      return {
        title: merged[0],
        details: merged.slice(1),
      };
    }

    return {
      title: raw,
      details: [],
    };
  });

  $effect(function log() {
    console.log(diagnosisSections.details);
  });
</script>

{#snippet citationText(rawText)}
  {#each parseCitations(rawText) as part}
    {#if part.type === "citation"}
      <button
        type="button"
        class="inline-flex items-center px-1.5 py-0.5 mx-0.5 rounded-md font-mono font-bold text-[10px] text-primary bg-primary/15 hover:bg-primary hover:text-primary-content border border-primary/30 transition-all cursor-pointer hover:scale-105 active:scale-95 align-baseline shadow-2xs"
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
  class="card bg-base-100/85 shadow-2xl border border-base-300 backdrop-blur-md transition-all duration-500 ease-in-out"
  in:fly={{ y: 24, duration: 450, easing: cubicInOut }}
>
  <div class="card-body p-6 lg:p-8 space-y-6">
    {#if isFallback}
      <!-- Loud fallback alert: the AI model was unavailable, rule-based formula used -->
      <div
        class="alert bg-error/15 border-2 border-error/50 text-base-content rounded-2xl shadow-lg"
        in:fly={{ y: -12, duration: 350, easing: cubicInOut }}
      >
        <span class="text-2xl shrink-0 animate-pulse">🚨</span>
        <div>
          <div
            class="font-black text-error uppercase tracking-wide font-display text-sm"
          >
            {t("protocol.fallbackTitle")}
          </div>
          <p class="text-xs text-base-content/80 mt-0.5 leading-relaxed">
            {fallbackNotice}
          </p>
        </div>
        <span
          class="badge badge-error text-white font-mono font-bold shrink-0 self-start"
          >{t("protocol.notAiVerified")}</span
        >
      </div>
    {/if}

    <!-- Header Step 4 -->
    <div
      class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-base-200 pb-4"
    >
      <div>
        <div
          class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-success font-label"
        >
          <span class="inline-block w-2.5 h-2.5 rounded-full bg-success"></span>
          {t("stepper.step4Label")}
        </div>
        <h2
          class="text-2xl lg:text-3xl font-black tracking-tight text-base-content font-display mt-1"
        >
          {t("protocol.mainTitle")}
        </h2>
        <p class="text-sm text-base-content/70 mt-0.5">
          {t("protocol.mainDesc")}
        </p>
      </div>
    </div>

    {#if isProcessing}
      <StepLoader
        icon="🧬"
        title={t("protocol.loaderTitle")}
        subtitle={t("protocol.loaderSubtitle")}
        statusLabel={t("protocol.loaderStatus")}
      />
    {:else if hasData && p}
      {#if artifactsData && artifactsData.synthesis}
        <div
          class="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-2xl bg-success/10 border border-success/30 text-xs shadow-xs"
          in:fade
        >
          <div class="flex items-center gap-2.5">
            <span
              class="font-black text-success uppercase tracking-wider font-mono"
              >{t("protocol.liveProtocol")}</span
            >
            <span class="text-base-content font-bold font-mono">
              {artifactsData.synthesis.timestamp || "Latest run"}
            </span>
            <span
              class="badge badge-sm badge-outline badge-success font-bold font-mono"
            >
              {t("protocol.dosagesCalculatedCount", { count: p.drugs.length })}
            </span>
          </div>

          <div class="flex items-center gap-2">
            {#if artifactsData.sheetMd}
              <a
                href="/api/artifacts?name=final_clinical_emergency_sheet.md"
                target="_blank"
                rel="noreferrer"
                class="btn btn-xs btn-outline btn-success gap-1 font-bold cursor-pointer"
              >
                <span>📄 {t("sheet.fullSheet")}</span>
                <span>↗</span>
              </a>
            {/if}
          </div>
        </div>
      {/if}

      <!-- Clinical Condition Diagnosis Banner -->
      <div
        class="rounded-2xl border border-info/30 bg-info/10 text-info-content p-4 sm:p-5 shadow-sm space-y-3.5 transition-all duration-300 ease-in-out"
      >
        <div class="flex items-start gap-3">
          <div
            class="p-2 rounded-xl bg-info/20 text-info shrink-0 mt-0.5 shadow-2xs"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>

          <div class="flex-1 min-w-0 space-y-1">
            <div class="flex flex-wrap items-center gap-2">
              <span
                class="font-bold text-[11px] uppercase tracking-wider text-info font-label"
              >
                {t("protocol.presumptiveDiagnosis")}
              </span>
              {#if diagnosisSections.details.length > 0}
                <span
                  class="badge badge-xs badge-info badge-outline font-mono font-bold"
                >
                  {t("protocol.clinicalInsightsCount", { count: diagnosisSections.details.length + 1 })}
                </span>
              {/if}
            </div>

            <!-- Primary Diagnosis Headline -->
            <div
              class="text-base sm:text-lg font-black text-base-content font-display tracking-tight leading-snug"
            >
              {@render citationText(diagnosisSections.title)}
            </div>
          </div>
        </div>

        <!-- Clinical Assessment & Pathophysiological Findings -->
        {#if diagnosisSections.details.length > 0}
          <div class="pt-2.5 border-t border-info/20 space-y-2">
            <div
              class="text-[11px] font-bold uppercase tracking-wider text-info/90 font-label flex items-center gap-1.5"
            >
              <span class="inline-block w-1.5 h-1.5 rounded-full bg-info"
              ></span>
              {t("protocol.clinicalAssessmentEvidence")}
            </div>

            <div class="grid grid-cols-1 gap-2">
              {#each diagnosisSections.details as detail, idx}
                <div
                  class="flex items-start gap-2.5 text-xs sm:text-sm text-base-content/85 leading-relaxed bg-base-100/70 dark:bg-base-200/50 rounded-xl p-3 border border-info/15 shadow-2xs hover:border-info/30 transition-all duration-200"
                >
                  <span
                    class="badge badge-xs badge-info font-mono font-bold shrink-0 mt-0.5"
                  >
                    {idx + 1}
                  </span>
                  <div class="flex-1 min-w-0 font-medium">
                    {@render citationText(detail)}
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </div>

      <!-- Immediate Intervention Protocol (Golden Hour Checklist Component) -->
      <ImmediateInterventionProtocol {p} {patient} {isCopilotOpen} />

      <!-- Weight-Based Dosage Calculation (Deck & Structured Table) -->
      <DosageCalculationDeck drugs={p.drugs} {patient} />

      <!-- Mandatory Source Citations (ASPCA, Merck, BSAVA, PubMed) -->
      <div id="citation-sources" class="space-y-2 pt-1 scroll-mt-20">
        <div class="flex items-center justify-between">
          <div
            class="text-xs font-bold uppercase tracking-wider text-base-content/80 font-label flex items-center gap-2"
          >
            <span>{t("protocol.mandatoryCitations")}</span>
          </div>
          <span class="badge badge-sm badge-outline font-mono font-bold"
            >{t("protocol.evidenceBased")}</span
          >
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5">
          {#each p.citations as cit}
            <a
              id={`citation-${(cit.ref || "").replace(/[^0-9]/g, "")}`}
              href={cit.url}
              target="_blank"
              rel="noreferrer"
              class="flex items-start gap-3 p-3.5 rounded-xl border border-base-300 bg-base-200/30 hover:bg-base-200/80 hover:border-primary/40 transition-all duration-300 ease-in-out group scroll-mt-24"
            >
              <span class="badge badge-sm badge-neutral font-mono font-bold"
                >{cit.ref}</span
              >
              <div class="min-w-0 flex-1">
                <div
                  class="text-[11px] font-bold text-primary font-mono group-hover:underline"
                >
                  {cit.source}
                </div>
                <div
                  class="text-xs text-base-content font-medium mt-0.5 font-display break-words"
                >
                  {cit.title}
                </div>
              </div>
              <span
                class="text-xs text-base-content/40 group-hover:text-primary transition-colors"
                >↗</span
              >
            </a>
          {/each}
        </div>
      </div>
    {:else}
      <div
        class="p-8 text-center text-base-content/60 rounded-2xl border border-dashed border-base-300 bg-base-200/20"
      >
        <div class="text-3xl mb-2">🧬</div>
        <div class="font-bold text-sm text-base-content/80">
          {t("protocol.emptyTitle")}
        </div>
        <div class="text-xs text-base-content/50 mt-1">
          {t("protocol.emptyDesc")}
        </div>
      </div>
    {/if}

    <!-- Actions Footer Toolbar -->
    <div
      class="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-base-200"
    >
      <button
        type="button"
        class="btn btn-ghost btn-sm gap-2 text-base-content/70 hover:text-base-content cursor-pointer"
        onclick={onBack}
      >
        <svg
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M10 19l-7-7m0 0l7-7m-7 7h18"
          />
        </svg>
        <span>{t("common.back")}</span>
      </button>

      <div class="flex flex-wrap items-center gap-2 w-full sm:w-auto">
        <button
          type="button"
          class="btn btn-outline btn-sm gap-1.5 hover:scale-105 transition-all duration-300 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
          onclick={printClinicalSheet}
          disabled={!p && !artifactsData?.sheetMd}
          title={t("sheet.printBtn")}
        >
          <span>🖨️ {t("sheet.printBtn")}</span>
        </button>

        <button
          type="button"
          class="btn btn-secondary btn-sm gap-1.5 hover:scale-105 transition-all duration-300 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
          onclick={copyClinicalReport}
          disabled={!p && !artifactsData?.sheetMd}
        >
          {#if copied}
            <span>✓ {t("sheet.copied")}</span>
          {:else}
            <span>📋 {t("sheet.copyBtn")}</span>
          {/if}
        </button>

        {#if onNext}
          <button
            type="button"
            class="btn btn-primary btn-sm gap-1.5 shadow-md shadow-primary/20 hover:scale-105 transition-all duration-300 font-bold cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
            onclick={onNext}
            disabled={!nextUnlocked}
            title={!nextUnlocked
              ? t("protocol.step5Tooltip")
              : t("common.continueToSheet")}
          >
            <span>{t("common.continueToSheet")}</span>
            <span>→</span>
          </button>
        {/if}

        <button
          type="button"
          class="btn btn-ghost btn-sm gap-1.5 hover:scale-105 transition-all duration-300 font-bold cursor-pointer"
          onclick={onReset}
        >
          <span>🔄 {t("common.newIntake")}</span>
        </button>
      </div>
    </div>
  </div>
</div>
