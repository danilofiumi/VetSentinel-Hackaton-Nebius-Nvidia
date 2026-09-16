<script>
  import { slide, fade, fly } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";
  import { t } from "$lib";

  let {
    runStatus = "idle", // 'idle' | 'running' | 'succeeded' | 'failed'
    runId = "",
    elapsedSeconds = 0,
    stepNodes = [],
    logsText = "",
    errorMessage = "",
    activeExplorerTab = "synthesis",
    onSelectStep = null,
    onRerun = null,
  } = $props();

  let showLogs = $state(false);

  let defaultStepDefs = $derived([
    {
      id: "setup_environment",
      tabKey: "triage",
      name: t("stepper.step1"),
      desc: t("stepper.step1Desc"),
      icon: "⚙️",
    },
    {
      id: "nebius_orchestrator",
      tabKey: "orchestrator",
      name: t("stepper.step2"),
      desc: t("stepper.step2Desc"),
      icon: "🩺",
    },
    {
      id: "tavily_web_search",
      tabKey: "sources",
      name: t("stepper.step3"),
      desc: t("stepper.step3Desc"),
      icon: "📚",
    },
    {
      id: "clinical_synthesis",
      tabKey: "synthesis",
      name: t("stepper.step4"),
      desc: t("stepper.step4Desc"),
      icon: "🧬",
    },
    {
      id: "export_summary",
      tabKey: "sheet",
      name: t("stepper.step5"),
      desc: t("stepper.step5Desc"),
      icon: "📋",
    },
  ]);

  function handleStepClick(def) {
    if (onSelectStep && def.tabKey) {
      onSelectStep(def.tabKey);
    }
  }
</script>

<div
  class="card bg-base-100/90 shadow-xl border border-base-300 backdrop-blur-md overflow-hidden transition-all duration-300"
  in:fly={{ y: 20, duration: 400, easing: cubicInOut }}
>
  <!-- Pipeline Header Bar -->

  <!-- Error Alert if any -->
  {#if errorMessage}
    <div
      class="p-3 bg-error/15 border-b border-error/30 text-error text-xs font-semibold flex items-center gap-2"
    >
      <span>⚠️</span>
      <span>{errorMessage}</span>
    </div>
  {/if}

  <!-- 5-Step Process Visualizer Cards -->
  <div class="p-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5">
    {#each defaultStepDefs as def, index}
      {@const node = stepNodes.find(
        (n) => n.id === def.id || n.name === def.id,
      )}
      {@const status = node
        ? node.statusLabel
        : runStatus === "succeeded"
          ? "succeeded"
          : "not_started"}
      {@const isCurrentActiveTab = activeExplorerTab === def.tabKey}

      <button
        type="button"
        class="flex flex-col text-left p-3 rounded-xl border transition-all duration-300 ease-in-out cursor-pointer group hover:scale-[1.02] active:scale-[0.98] {status ===
        'running'
          ? 'border-warning/60 bg-warning/10 shadow-md shadow-warning/10 ring-2 ring-warning/30'
          : status === 'succeeded'
            ? isCurrentActiveTab
              ? 'border-primary bg-primary/10 shadow-md shadow-primary/15 ring-2 ring-primary/40'
              : 'border-success/30 bg-success/5 hover:border-success/60'
            : status === 'failed'
              ? 'border-error/40 bg-error/10'
              : 'border-base-300 bg-base-200/40 opacity-70 hover:opacity-100'}"
        onclick={() => handleStepClick(def)}
        title="Click to explore {def.name}"
      >
        <div class="flex items-center justify-between gap-1 mb-1.5">
          <span class="text-base">{def.icon}</span>
          <div>
            {#if status === "succeeded"}
              <span
                class="badge badge-success badge-xs font-mono font-bold text-[9px] gap-0.5"
              >
                ✓ {t("stepper.done")}
              </span>
            {:else if status === "running"}
              <span
                class="badge badge-warning badge-xs font-mono font-bold text-[9px] gap-1"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-warning animate-ping"
                ></span>
                {t("stepper.active")}
              </span>
            {:else if status === "failed"}
              <span
                class="badge badge-error badge-xs font-mono font-bold text-[9px] text-white"
              >
                ✕ {t("stepper.error")}
              </span>
            {:else}
              <span
                class="badge badge-ghost badge-xs font-mono text-[9px] text-base-content/40"
              >
                {t("stepper.queued")}
              </span>
            {/if}
          </div>
        </div>

        <div
          class="text-xs font-bold text-base-content leading-tight group-hover:text-primary transition-colors"
        >
          {def.name}
        </div>
        <p class="text-[10px] text-base-content/60 leading-tight mt-1 truncate">
          {def.desc}
        </p>

        {#if isCurrentActiveTab}
          <div class="mt-2 w-full h-0.5 bg-primary rounded-full"></div>
        {/if}
      </button>
    {/each}
  </div>

  <!-- Expandable Live Logs Terminal Drawer -->
  {#if showLogs}
    <div
      class="border-t border-base-300 bg-neutral text-neutral-content p-4 font-mono text-xs overflow-hidden"
      transition:slide={{ duration: 300, easing: cubicInOut }}
    >
      <div
        class="flex items-center justify-between pb-2 border-b border-white/10 mb-2"
      >
        <div class="flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-error inline-block"></span>
          <span class="w-2.5 h-2.5 rounded-full bg-warning inline-block"></span>
          <span class="w-2.5 h-2.5 rounded-full bg-success inline-block"></span>
          <span class="text-[11px] font-bold text-white/70 ml-1">
            {t("stepper.daguLogsTitle")}
          </span>
        </div>
        <span class="text-[10px] text-white/40">{t("stepper.autoStreaming")}</span>
      </div>

      <pre
        class="whitespace-pre-wrap font-mono text-[11px] leading-relaxed max-h-64 overflow-y-auto pr-2 text-emerald-400/90">{logsText ||
          t("stepper.waitingLogs")}</pre>
    </div>
  {/if}
</div>
