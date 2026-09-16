<script>
  import { fly, fade } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";
  import ClinicalAssessmentHeader from "./ClinicalAssessmentHeader.svelte";
  import OrchestratorGapsTab from "./OrchestratorGapsTab.svelte";
  import ReasoningFlow from "./ReasoningFlow.svelte";
  import ReasoningLiveMonitor from "./ReasoningLiveMonitor.svelte";
  import { t } from "$lib";

  let {
    patient = {},
    artifactsData = null,
    runStatus = "idle",
    runId = "",
    elapsedSeconds = 0,
    stepNodes = [],
    logsText = "",
    errorMessage = "",
    nextUnlocked = false,
    onNext = null,
    onBack = null,
    onOpenDagu = null,
  } = $props();

  // --- Live orchestrator output (authoritative when a run exists) ---
  let orch = $derived(artifactsData?.orchestrator || null);
  let hasLiveData = $derived(!!orch);
  // Explicit fallback flag emitted by Step 1 when the AI model was unavailable.
  let isFallback = $derived(Boolean(orch?.fallback));
  let fallbackNotice = $derived(
    orch?.fallback_notice || t("assessment.fallbackNotice"),
  );
  // Real patient echoed back by the LLM (falls back to the local intake object)
  let livePatient = $derived(orch?.patient || null);
  let perf = $derived(orch?.performance || null);

  // --- Live pipeline monitoring (Step 2 = nebius_orchestrator node) ---
  let isRunning = $derived(runStatus === "running");
  let nodeById = $derived.by(() => {
    const map = {};
    for (const n of stepNodes || []) map[n.id] = n;
    return map;
  });
  let setupStatus = $derived(nodeById["setup_environment"]?.statusLabel || "");
  let orchStatus = $derived(nodeById["nebius_orchestrator"]?.statusLabel || "");
  // The orchestrator (Step 2) is producing the gap analysis right now
  let reasoningActive = $derived(
    isRunning && !hasLiveData && orchStatus !== "succeeded",
  );
  // Friendly label for whichever node is currently executing
  let activeLabel = $derived.by(() => {
    if (!isRunning) return "";
    if (orchStatus === "running")
      return t("assessment.reasoningToxicology");
    if (setupStatus === "running" || (!setupStatus && !orchStatus))
      return t("assessment.preparingIntake");
    if (orchStatus === "succeeded")
      return t("assessment.reasoningComplete");
    return t("assessment.analyzingAnamnesis");
  });

  // Real information gaps parsed from live orchestrator artifact
  function getInformationGaps() {
    if (
      artifactsData?.orchestrator &&
      Array.isArray(artifactsData.orchestrator.clinical_gaps) &&
      artifactsData.orchestrator.clinical_gaps.length > 0
    ) {
      return artifactsData.orchestrator.clinical_gaps.map((g, idx) => {
        const sev = (g.severity || "").toLowerCase();
        const severity = sev.includes("critic")
          ? "critical"
          : sev.includes("med")
            ? "medium"
            : "high";
        return {
          id: idx + 1,
          icon:
            severity === "critical"
              ? "🚨"
              : severity === "medium"
                ? "ℹ️"
                : "⚠️",
          gap: g.title,
          desc: g.description,
          severity,
        };
      });
    }
    return [];
  }

  function getGeneratedQueries() {
    const p = artifactsData?.orchestrator?.function_call?.parameters;
    const queries = p?.target_queries || p?.queries;
    if (Array.isArray(queries) && queries.length > 0) {
      return queries;
    }
    return [];
  }

  let urgencyBadgeClass = $derived.by(() => {
    const p = (livePatient?.priority || patient?.priorita || "").toLowerCase();
    if (p === "critical" || p === "critica") return "badge-error text-white";
    if (p === "urgent" || p === "urgente")
      return "badge-warning text-base-content";
    if (p === "routine" || p === "stable")
      return "badge-success text-white";
    return "badge-ghost";
  });

  // --- Intake-driven, reasoning-flow + gaps data ---
  // Gaps: real LLM output when available, canned per-case otherwise
  let gapsList = $derived(getInformationGaps());
  let criticalCount = $derived(
    gapsList.filter((g) => g.severity === "critical").length,
  );
  let highCount = $derived(
    gapsList.filter((g) => g.severity === "high").length,
  );
  // Count of prepared source lookups only (the queries themselves are intentionally not shown)
  let queryCount = $derived(getGeneratedQueries().length);
  // While the pipeline runs and no real gaps have arrived yet, show a live skeleton
  let gapsLoading = $derived(isRunning && !hasLiveData);

  // Vertical reasoning flow driven by the actual intake / LLM echo
  let flowSteps = $derived.by(() => {
    const species = livePatient?.species || patient?.specie || "Unknown";
    const breed = livePatient?.breed || patient?.razza || "";
    const weight = livePatient?.weight_kg ?? patient?.peso ?? "?";
    const priority = livePatient?.priority || patient?.priorita || "";
    const triageReasoning = orch?.triage_reasoning || "";
    const anamnesis = livePatient?.symptoms || patient?.sintomi || "";

    return [
      {
        icon: "🐾",
        title: t("assessment.intakeTitle"),
        status: "done",
        desc: anamnesis || t("assessment.noAnamnesis"),
        metrics: [
          { value: breed ? `${species} · ${breed}` : species },
          { value: `${weight} kg` },
        ],
      },
      {
        icon: "🧠",
        title: t("assessment.triageTitle"),
        status: hasLiveData ? "done" : isRunning ? "active" : "pending",
        desc: hasLiveData
          ? (triageReasoning
              ? t("assessment.triageLevel", { priority: String(priority).toUpperCase(), reasoning: triageReasoning })
              : t("assessment.triageClassified", { priority: String(priority).toUpperCase() }))
          : isRunning
            ? (activeLabel || t("assessment.triageEvaluating"))
            : t("assessment.triageRun"),
        metrics: hasLiveData
          ? [
              { label: t("assessment.labelAiTriage"), value: String(priority).toUpperCase() },
              { label: t("assessment.labelModel"), value: orch?.model_used || "GLM-5.3-Flash" },
              { label: "TTFT", value: `${perf?.ttft_ms ?? 0} ms` },
              { value: `${perf?.throughput_tok_sec ?? 132.5} tok/s` },
            ]
          : isRunning
            ? [{ value: t("assessment.classifyingUrgency") }]
            : [{ value: t("assessment.triagePending") }],
      },
      {
        icon: "🔍",
        title: t("assessment.gapsTitle"),
        status: hasLiveData ? "done" : isRunning ? "pending" : "done",
        desc: t("assessment.gapsDesc"),
        metrics: hasLiveData
          ? [
              { value: t("assessment.gapsCount", { count: gapsList.length }) },
              ...(criticalCount
                ? [{ value: t("assessment.criticalCount", { count: criticalCount }) }]
                : []),
              ...(highCount ? [{ value: t("assessment.highCount", { count: highCount }) }] : []),
            ]
          : isRunning
            ? [{ value: t("assessment.awaitingReasoning") }]
            : [{ value: t("assessment.gapsCount", { count: gapsList.length }) }],
      },
      {
        icon: "📚",
        title: t("assessment.handoffTitle"),
        status: hasLiveData ? "next" : isRunning ? "pending" : "next",
        desc: t("assessment.handoffDesc"),
        metrics:
          isRunning && !hasLiveData
            ? []
            : [{ value: t("assessment.lookupsPrepared", { count: queryCount }) }],
      },
    ];
  });
</script>

<div
  class="card bg-base-100/90 shadow-xl border border-base-300 backdrop-blur-md overflow-hidden transition-all duration-300"
  in:fly={{ y: 24, duration: 450, easing: cubicInOut }}
>
  <div class="p-4 sm:p-6 lg:p-8 space-y-6">
    <!-- AI Fallback banner: visible ONLY when step 1 used the deterministic rule-based template -->
    {#if isFallback}
      <div
        class="alert alert-warning shadow-md border border-warning/30 text-xs flex items-start gap-3 rounded-2xl"
        in:fly={{ y: -12, duration: 350, easing: cubicInOut }}
      >
        <span class="text-xl shrink-0">⚠️</span>
        <div>
          <div class="font-black uppercase tracking-wide">
            {t("assessment.fallbackTitle")}
          </div>
          <div class="mt-0.5 opacity-90 leading-relaxed font-mono text-[11px]">
            {fallbackNotice}
          </div>
        </div>
      </div>
    {/if}

    <!-- Header Step 2: Clinical Assessment & Reasoning (Dedicated Component) -->
    <ClinicalAssessmentHeader
      {patient}
      priority={livePatient?.priority || patient?.priorita}
      {urgencyBadgeClass}
      {hasLiveData}
      {isRunning}
      modelUsed={orch?.model_used}
    />

    <!-- SECTION 1: CLINICAL REASONING FLOW (intake ➔ assessment ➔ gaps ➔ handoff) -->
    <div class="space-y-4 pt-1">
      <div class="flex items-center gap-2">
        <span class="text-2xl">🧭</span>
        <div>
          <h3
            class="text-sm lg:text-base font-black text-base-content font-display uppercase tracking-wide"
          >
            {t("assessment.flowReasoningTitle")}
          </h3>
          <p class="text-xs text-base-content/60">
            {t("assessment.flowReasoningDesc")}
          </p>
        </div>
      </div>

      <ReasoningFlow steps={flowSteps} />

      <!-- Live monitoring terminal: direct view of the reasoning as it streams -->
      <!-- {#if isRunning}
        <ReasoningLiveMonitor
          {runStatus}
          {elapsedSeconds}
          {logsText}
          {activeLabel}
          {errorMessage}
        />
      {/if} -->
    </div>

    <!-- SECTION 2: CRITICAL INFORMATION GAPS (the real, intake-driven reasoning output) -->
    <div class="space-y-3 pt-1" in:fade={{ duration: 300, easing: cubicInOut }}>
      <div
        class="flex flex-col sm:flex-row sm:items-center justify-between gap-2"
      >
        <div class="flex items-center gap-2">
          <span class="text-2xl">🔍</span>
          <div>
            <h3
              class="text-sm lg:text-base font-black text-base-content font-display uppercase tracking-wide"
            >
              {t("assessment.gapsSectionTitle")} ({gapsLoading ? "…" : gapsList.length})
            </h3>
            <p class="text-xs text-base-content/60">
              {#if gapsLoading}
                {t("assessment.gapsLoadingDesc")}
              {:else if hasLiveData}
                {t("assessment.gapsLiveDesc")}
              {:else}
                {t("assessment.gapsPreviewDesc")}
              {/if}
            </p>
          </div>
        </div>

        {#if hasLiveData}
          <div class="flex items-center gap-1.5">
            {#if criticalCount}
              <span
                class="badge badge-sm badge-error text-white font-mono font-bold"
              >
                {t("assessment.criticalCount", { count: criticalCount })}
              </span>
            {/if}
            {#if highCount}
              <span class="badge badge-sm badge-warning font-mono font-bold">
                {t("assessment.highCount", { count: highCount })}
              </span>
            {/if}
          </div>
        {:else if gapsLoading}
          <span
            class="badge badge-sm badge-secondary font-mono font-bold gap-1.5 animate-pulse"
          >
            {t("assessment.analyzing")}
          </span>
        {/if}
      </div>

      {#if gapsLoading}
        <!-- Live skeleton placeholders while the gap analysis is being generated -->
        <div class="grid grid-cols-1 gap-2.5">
          {#each [0, 1, 2] as i}
            <div
              class="flex items-start gap-3.5 p-4 rounded-2xl border border-base-300 bg-base-200/30 animate-pulse"
              style="animation-delay: {i * 150}ms"
            >
              <div class="w-10 h-10 rounded-xl bg-base-300/60 shrink-0"></div>
              <div class="flex-1 space-y-2 pt-1">
                <div class="h-3 rounded bg-base-300/60 w-2/3"></div>
                <div class="h-2.5 rounded bg-base-300/40 w-full"></div>
                <div class="h-2.5 rounded bg-base-300/40 w-4/5"></div>
              </div>
            </div>
          {/each}
        </div>
      {:else if gapsList.length > 0}
        <OrchestratorGapsTab gaps={gapsList} />
      {:else}
        <div
          class="p-8 text-center text-base-content/60 rounded-2xl border border-dashed border-base-300 bg-base-200/20"
        >
          <div class="text-3xl mb-2">🩺</div>
          <div class="font-bold text-sm text-base-content/80">
            {t("assessment.noGapsTitle")}
          </div>
          <div class="text-xs text-base-content/50 mt-1">
            {t("assessment.noGapsDesc")}
          </div>
        </div>
      {/if}
    </div>

    <!-- Actions Footer -->
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
        <span>{t("common.backToTriage")}</span>
      </button>

      <div class="flex items-center gap-3 w-full sm:w-auto">
        <button
          type="button"
          class="btn btn-primary px-8 gap-2 shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 ease-in-out w-full sm:w-auto font-bold cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
          onclick={onNext}
          disabled={!nextUnlocked}
          title={!nextUnlocked
            ? t("assessment.nextLockedTooltip")
            : t("common.continueToSources")}
        >
          <span>{t("common.continueToSources")}</span>
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
              d="M14 5l7 7m0 0l-7 7m7-7H3"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</div>
