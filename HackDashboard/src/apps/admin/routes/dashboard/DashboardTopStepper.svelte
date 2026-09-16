<script>
  import { cubicInOut } from "svelte/easing";
  import { fly, fade, slide } from "svelte/transition";
  import { t } from "$lib";

  let {
    currentSection = "triage", // 'triage' | 'orchestrator' | 'sources' | 'synthesis' | 'sheet'
    isAnalysisComplete = false,
    isAnalysisRunning = false,
    runStatus = "idle", // 'idle' | 'running' | 'succeeded' | 'failed'
    runId = "",
    elapsedSeconds = 0,
    stepNodes = [],
    artifactsData = null,
    logsText = "",
    errorMessage = "",
    onNavigate = null,
    onPromptTrigger = null,
    onRerun = null,
    onOpenRunLoader = null,
  } = $props();

  let showLogs = $state(false);
  let lockedTooltipSection = $state(null);
  let tooltipTimer = null;

  let isRunning = $derived(isAnalysisRunning || runStatus === "running");
  let isComplete = $derived(isAnalysisComplete || runStatus === "succeeded");
  let isFailed = $derived(runStatus === "failed");

  let sections = $derived([
    {
      id: "triage",
      dagId: "setup_environment",
      num: 1,
      nameKey: "stepper.intake",
      name: t("stepper.intake"),
      shortName: t("stepper.shortIntake"),
      icon: "⚙️",
      desc: t("stepper.intakeDesc"),
    },
    {
      id: "orchestrator",
      dagId: "nebius_orchestrator",
      num: 2,
      nameKey: "stepper.orchestrator",
      name: t("stepper.orchestrator"),
      shortName: t("stepper.shortOrchestrator"),
      icon: `🩺`,
      desc: t("stepper.orchestratorDesc"),
    },
    {
      id: "sources",
      dagId: "tavily_web_search",
      num: 3,
      nameKey: "stepper.sources",
      name: t("stepper.sources"),
      shortName: t("stepper.shortSources"),
      icon: "📚",
      desc: t("stepper.sourcesDesc"),
    },
    {
      id: "synthesis",
      dagId: "clinical_synthesis",
      num: 4,
      nameKey: "stepper.synthesis",
      name: t("stepper.synthesis"),
      shortName: t("stepper.shortSynthesis"),
      icon: "🧬",
      desc: t("stepper.synthesisDesc"),
    },
    {
      id: "sheet",
      dagId: "export_summary",
      num: 5,
      nameKey: "stepper.sheet",
      name: t("stepper.sheet"),
      shortName: t("stepper.shortSheet"),
      icon: "📋",
      desc: t("stepper.sheetDesc"),
    },
  ]);

  function getNodeStatus(sec) {
    const node = stepNodes.find(
      (n) => n.id === sec.dagId || n.name === sec.dagId,
    );
    if (node && node.statusLabel) {
      return node.statusLabel; // 'running' | 'succeeded' | 'failed' | 'not_started'
    }
    if (isComplete) return "succeeded";
    if (isRunning && sec.id === "triage") return "succeeded";
    return "not_started";
  }

  // A step unlocks only once its own DAG node has started (running/succeeded).
  // Everything after the LLM triage therefore stays locked until the LLM finishes.
  function isSectionUnlocked(sec) {
    if (sec.id === "triage") return true;
    if (isComplete) return true;
    if (sec.id === "orchestrator" && (isRunning || artifactsData?.orchestrator))
      return true;
    if (sec.id === "sources" && artifactsData?.tavily) return true;
    if (sec.id === "synthesis" && artifactsData?.synthesis) return true;
    if (sec.id === "sheet" && artifactsData?.sheetMd) return true;
    const st = getNodeStatus(sec);
    return st === "running" || st === "succeeded";
  }

  let currentStepIndex = $derived(
    sections.findIndex((s) => s.id === currentSection),
  );

  let completedNodesCount = $derived(
    sections.filter((s) => getNodeStatus(s) === "succeeded").length,
  );

  let progressPercent = $derived(
    isComplete
      ? 100
      : isRunning
        ? Math.max(
            15,
            Math.round((completedNodesCount / sections.length) * 100),
          )
        : Math.round(
            ((Math.max(0, currentStepIndex) + 1) / sections.length) * 100,
          ),
  );

  function handleSectionClick(sec) {
    const isLocked = !isSectionUnlocked(sec);

    if (isLocked) {
      lockedTooltipSection = sec.id;
      if (tooltipTimer) clearTimeout(tooltipTimer);
      tooltipTimer = setTimeout(() => {
        lockedTooltipSection = null;
      }, 2500);
      // NOTE: Never redirect to another section when clicking a locked step.
      return;
    }

    if (onNavigate) {
      onNavigate(sec.id);
    }
  }
</script>

<!-- Left Sidebar Navigation Component with Integrated Progress Tracker -->
<nav
  aria-label="Clinical workflow sections and pipeline telemetry"
  class="card bg-base-100/90 shadow-lg border border-base-300 overflow-hidden backdrop-blur-md p-3 sm:p-4 transition-all duration-300 ease-in-out rounded-2xl flex flex-col gap-3"
  in:fly={{ x: -20, duration: 400, easing: cubicInOut }}
>
  <!-- Error Alert if any -->
  {#if errorMessage}
    <div
      class="p-2.5 rounded-xl bg-error/15 border border-error/30 text-error text-[11px] font-semibold flex items-center gap-2"
      in:slide={{ duration: 250, easing: cubicInOut }}
    >
      <span class="text-sm">⚠️</span>
      <span class="leading-tight truncate">{errorMessage}</span>
    </div>
  {/if}

  <!-- DESKTOP VERTICAL SIDEBAR LAYOUT (lg+) -->
  <div class="hidden lg:flex flex-col gap-3.5">
    <!-- Header: Telemetry & Brand -->
    <div
      class="flex items-center justify-between gap-2 pb-2.5 border-b border-base-200"
    >
      <div class="flex items-center gap-2">
        <span class="relative flex h-2.5 w-2.5">
          {#if isRunning}
            <span
              class="animate-ping absolute inline-flex h-full w-full rounded-full bg-warning opacity-75"
            ></span>
            <span
              class="relative inline-flex rounded-full h-2.5 w-2.5 bg-warning"
            ></span>
          {:else if isComplete}
            <span
              class="relative inline-flex rounded-full h-2.5 w-2.5 bg-success"
            ></span>
          {:else if isFailed}
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-error"
            ></span>
          {:else}
            <span
              class="relative inline-flex rounded-full h-2.5 w-2.5 bg-primary"
            ></span>
          {/if}
        </span>
        <span
          class="text-xs font-black font-display tracking-wider uppercase text-base-content/80"
        >
          {t("stepper.workflowTag")}
        </span>
      </div>

      <div class="shrink-0">
        {#if isRunning}
          <span
            class="badge whitespace-nowrap badge-warning badge-xs font-mono font-bold text-[10px] gap-1 shadow-xs"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-warning animate-ping"
            ></span>
            {t("stepper.runStatus.running")} ({elapsedSeconds}s)
          </span>
        {:else if isComplete}
          <span
            class="badge badge-success badge-xs font-mono font-bold text-white text-[10px] shadow-xs"
          >
            ✓ {t("stepper.runStatus.succeeded")} ({elapsedSeconds}s)
          </span>
        {:else if isFailed}
          <span
            class="badge badge-error text-nowrap badge-xs font-mono font-bold text-white text-[10px]"
          >
            ✕ {t("stepper.runStatus.failed")}
          </span>
        {:else}
          <span class="badge badge-ghost badge-xs font-mono text-[10px]">
            {t("stepper.stepCounter", {
              current: currentStepIndex + 1,
              total: 5,
            })}
          </span>
        {/if}
      </div>
    </div>

    <!-- DAG Run ID if available -->
    {#if runId}
      <div
        class="flex items-center justify-between text-[10px] font-mono text-base-content/60 px-0.5"
      >
        <span>{t("stepper.runIdLabel")}</span>
        <span
          class="font-bold text-base-content truncate max-w-[170px]"
          title={runId}
        >
          {runId}
        </span>
      </div>
    {/if}

    <!-- Progress Bar Indicator -->
    <div class="space-y-1.5">
      <div
        class="flex items-center justify-between text-[11px] font-mono text-base-content/60"
      >
        <span>{t("stepper.pipelineProgress")}</span>
        <span class="font-bold text-base-content/90">{progressPercent}%</span>
      </div>
      <div class="w-full bg-base-200/90 rounded-full h-1.5 overflow-hidden">
        <div
          class="h-full bg-primary rounded-full transition-all duration-500 ease-in-out"
          style="width: {progressPercent}%"
        ></div>
      </div>
    </div>

    <!-- Vertical Step Items with Timeline Line -->
    <div class="relative flex flex-col gap-2 py-0.5">
      <!-- Background Connecting Timeline Bar -->
      <div
        class="absolute left-[1.4rem] top-4 bottom-4 w-0.5 bg-base-200/80 pointer-events-none"
      ></div>

      {#each sections as sec}
        {@const nodeStatus = getNodeStatus(sec)}
        {@const isActive = currentSection === sec.id}
        {@const isLocked = !isSectionUnlocked(sec)}
        {@const isTooltipActive = lockedTooltipSection === sec.id}

        <button
          type="button"
          class="relative flex items-center justify-between w-full p-2.5 rounded-xl transition-all duration-300 ease-in-out cursor-pointer group text-left {isActive
            ? 'bg-primary text-primary-content shadow-md shadow-primary/25 ring-2 ring-primary/40 translate-x-1'
            : nodeStatus === 'running'
              ? 'border-warning/60 bg-warning/15 ring-2 ring-warning/30 text-base-content animate-pulse'
              : nodeStatus === 'failed'
                ? 'border-error/40 bg-error/10 text-error'
                : isLocked
                  ? 'bg-base-200/30 text-base-content/40 hover:bg-base-200/60'
                  : 'bg-base-200/60 text-base-content/80 hover:bg-base-200 hover:text-primary hover:translate-x-0.5'}"
          onclick={() => handleSectionClick(sec)}
          title={isLocked
            ? `Locked: Run clinical analysis to unlock ${sec.name}`
            : `Navigate to ${sec.name}`}
        >
          <div class="flex items-center gap-2.5 min-w-0">
            <!-- Step icon badge -->
            <div
              class="relative z-10 w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 transition-transform duration-300 ease-in-out group-hover:scale-110 {isActive
                ? 'bg-white/20 text-white shadow-inner'
                : nodeStatus === 'succeeded'
                  ? 'bg-success/20 text-success'
                  : nodeStatus === 'running'
                    ? 'bg-warning/20 text-warning animate-pulse'
                    : nodeStatus === 'failed'
                      ? 'bg-error/20 text-error'
                      : isLocked
                        ? 'bg-base-300 text-base-content/40'
                        : 'bg-base-300/80 text-base-content/70'}"
            >
              {#if nodeStatus === "succeeded" && !isActive}
                <span class="text-success font-black text-xs">✓</span>
              {:else if nodeStatus === "running"}
                <span class="w-2 h-2 rounded-full bg-warning animate-ping"
                ></span>
              {:else if nodeStatus === "failed"}
                <span class="text-error font-black text-xs">✕</span>
              {:else if isLocked}
                <span class="text-[10px]">🔒</span>
              {:else}
                <span>{sec.icon}</span>
              {/if}
            </div>

            <!-- Step Text Labels -->
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-1.5">
                <span class="text-[10px] font-mono font-bold opacity-60"
                  >#{sec.num}</span
                >
                <span
                  class="text-xs font-bold truncate leading-tight {isActive
                    ? 'text-primary-content'
                    : 'group-hover:text-primary'}"
                >
                  {sec.name}
                </span>
              </div>
              <div
                class="text-[10px] truncate mt-0.5 {isActive
                  ? 'text-primary-content/80'
                  : 'text-base-content/50'}"
              >
                {sec.desc}
              </div>
            </div>
          </div>

          <!-- Step Status Badge & Active Arrow -->
          <div class="shrink-0 flex items-center gap-1.5 pl-1">
            {#if nodeStatus === "succeeded"}
              <span
                class="badge badge-success badge-xs font-mono font-bold text-[9px] gap-0.5 {isActive
                  ? 'bg-white text-success border-none'
                  : ''}"
              >
                ✓ {t("stepper.done")}
              </span>
            {:else if nodeStatus === "running"}
              <span
                class="badge badge-warning badge-xs font-mono font-bold text-[9px] gap-1"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-warning animate-ping"
                ></span>
                {t("stepper.active")}
              </span>
            {:else if nodeStatus === "failed"}
              <span
                class="badge badge-error badge-xs font-mono font-bold text-[9px] text-white"
              >
                ✕ {t("stepper.error")}
              </span>
            {:else if isLocked}
              <span
                class="badge badge-ghost badge-xs font-mono text-[9px] opacity-60"
              >
                🔒
              </span>
            {:else}
              <span
                class="badge badge-ghost badge-xs font-mono text-[9px] opacity-60"
              >
                {t("stepper.queued")}
              </span>
            {/if}

            {#if isActive}
              <span class="text-xs font-black animate-pulse">→</span>
            {/if}
          </div>

          <!-- Locked Tooltip Popup -->
          {#if isTooltipActive}
            <div
              class="absolute left-full ml-2 top-1/2 -translate-y-1/2 z-40 bg-neutral text-neutral-content text-[11px] font-mono py-1.5 px-2.5 rounded-lg shadow-xl whitespace-nowrap"
              in:fade={{ duration: 150 }}
            >
              🔒 {t("stepper.lockedTooltip")}
            </div>
          {/if}
        </button>
      {/each}
    </div>

    <!-- Live Engine Logs Drawer -->
    <div class="pt-1.5 border-t border-base-200 flex flex-col gap-2">
      <button
        type="button"
        class="btn btn-ghost btn-xs gap-1 font-mono text-[10px] border border-base-300 hover:border-base-content/30 cursor-pointer w-full justify-between"
        onclick={() => (showLogs = !showLogs)}
        title="Toggle Real-time Dagu Pipeline Engine Logs"
      >
        <div class="flex items-center gap-1.5">
          <span>💻</span>
          <span>{showLogs ? t("stepper.hideLogs") : t("stepper.viewLogs")}</span
          >
        </div>
        <span class="badge badge-xs badge-ghost font-mono text-[9px]">
          {showLogs ? "▲ " + t("stepper.hide") : "▼ " + t("stepper.logs")}
        </span>
      </button>

      {#if showLogs}
        <div
          class="rounded-xl bg-neutral text-neutral-content p-3 font-mono text-[10px] overflow-hidden border border-base-content/10 shadow-inner"
          transition:slide={{ duration: 300, easing: cubicInOut }}
        >
          <div
            class="flex items-center justify-between pb-1.5 border-b border-white/10 mb-1.5"
          >
            <div class="flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-error inline-block"></span>
              <span class="w-2 h-2 rounded-full bg-warning inline-block"></span>
              <span class="w-2 h-2 rounded-full bg-success inline-block"></span>
              <span class="text-[10px] font-bold text-white/70 ml-1">
                {t("stepper.daguEngineLogs")}
              </span>
            </div>
            <span class="text-[9px] text-white/40"
              >{t("stepper.autoStreaming")}</span
            >
          </div>

          <pre
            class="whitespace-pre-wrap font-mono text-[10px] leading-relaxed max-h-48 overflow-y-auto pr-1 text-emerald-400/90">{logsText ||
              t("stepper.waitingLogs")}</pre>
        </div>
      {/if}
    </div>

    <!-- Quick Action / Guidance Box -->
    {#if onRerun && !isRunning && isComplete}
      <button
        type="button"
        class="btn btn-primary btn-xs w-full gap-1.5 font-bold shadow-xs cursor-pointer hover:scale-[1.02] active:scale-[0.98] transition-all"
        onclick={onRerun}
        title="Re-run pipeline with current patient inputs"
      >
        <span>🔄</span>
        <span>{t("common.rerunAnalysis")}</span>
      </button>
    {/if}
  </div>

  <!-- MOBILE COMPACT HORIZONTAL STEPPER (< lg) -->
  <div class="lg:hidden flex flex-col gap-2">
    <div
      class="flex items-center justify-between text-xs pb-1.5 border-b border-base-200"
    >
      <div class="flex items-center gap-2">
        <span
          class="w-2 h-2 rounded-full {isRunning
            ? 'bg-warning animate-ping'
            : isComplete
              ? 'bg-success'
              : 'bg-primary'}"
        ></span>
        <span
          class="text-xs font-black font-display tracking-wide uppercase text-base-content/80"
        >
          {t("stepper.workflow")}
        </span>
      </div>
      <div class="flex items-center gap-1.5">
        <span
          class="badge badge-xs {isComplete
            ? 'badge-success text-white'
            : isRunning
              ? 'badge-warning font-bold'
              : 'badge-ghost'} font-mono"
        >
          {isRunning
            ? `${t("stepper.running")} (${elapsedSeconds}s)`
            : isComplete
              ? t("stepper.done")
              : t("stepper.stepCounter", {
                  current: currentStepIndex + 1,
                  total: 5,
                })}
        </span>
        <button
          type="button"
          class="btn btn-ghost btn-xs text-[10px] font-mono px-1 h-5 min-h-0"
          onclick={() => (showLogs = !showLogs)}
        >
          💻 {showLogs ? t("stepper.hide") : t("stepper.logs")}
        </button>
        {#if onOpenRunLoader}
          <button
            type="button"
            class="btn btn-ghost btn-xs text-[10px] font-mono px-1.5 h-5 min-h-0 text-primary hover:bg-primary/10 cursor-pointer"
            onclick={onOpenRunLoader}
            title="Open DAG Run Loader / History"
          >
            🔎 {t("stepper.runs")}
          </button>
        {/if}
      </div>
    </div>

    <div class="grid grid-cols-5 gap-1.5">
      {#each sections as sec}
        {@const nodeStatus = getNodeStatus(sec)}
        {@const isActive = currentSection === sec.id}
        {@const isLocked = !isSectionUnlocked(sec)}
        {@const isTooltipActive = lockedTooltipSection === sec.id}

        <button
          type="button"
          class="relative flex flex-col items-center text-center p-1.5 rounded-lg transition-all duration-300 ease-in-out cursor-pointer {isActive
            ? 'bg-primary text-primary-content shadow-sm ring-1 ring-primary/40 font-bold'
            : nodeStatus === 'running'
              ? 'bg-warning/20 text-warning font-bold'
              : isLocked
                ? 'bg-base-200/40 text-base-content/40'
                : 'bg-base-200/70 text-base-content/80'}"
          onclick={() => handleSectionClick(sec)}
          title={isLocked ? `Locked: Run analysis first` : sec.name}
        >
          <div class="flex items-center gap-0.5 mb-0.5">
            <span class="text-xs">{sec.icon}</span>
            {#if nodeStatus === "succeeded"}
              <span class="text-[9px] text-success font-black">✓</span>
            {:else if nodeStatus === "running"}
              <span class="w-1.5 h-1.5 rounded-full bg-warning animate-ping"
              ></span>
            {:else if isLocked}
              <span class="text-[9px]">🔒</span>
            {/if}
          </div>
          <span class="text-[10px] truncate w-full font-mono"
            >{sec.shortName}</span
          >

          {#if isTooltipActive}
            <div
              class="absolute -bottom-8 left-1/2 -translate-x-1/2 z-30 bg-neutral text-neutral-content text-[10px] font-mono py-1 px-2 rounded shadow-xl whitespace-nowrap"
              in:fade={{ duration: 150 }}
            >
              🔒 {t("stepper.lockedTooltip")}
            </div>
          {/if}
        </button>
      {/each}
    </div>

    {#if showLogs}
      <div
        class="rounded-xl bg-neutral text-neutral-content p-2.5 font-mono text-[10px] overflow-hidden border border-base-content/10 mt-1"
        transition:slide={{ duration: 250, easing: cubicInOut }}
      >
        <pre
          class="whitespace-pre-wrap font-mono text-[9px] leading-relaxed max-h-36 overflow-y-auto pr-1 text-emerald-400/90">{logsText ||
            t("stepper.waitingLogs")}</pre>
      </div>
    {/if}
  </div>
</nav>
