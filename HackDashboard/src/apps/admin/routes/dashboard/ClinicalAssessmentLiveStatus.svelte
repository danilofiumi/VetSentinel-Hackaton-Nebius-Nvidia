<script>
  import { cubicInOut } from "svelte/easing";
  import { fade, slide } from "svelte/transition";
  import PipelineProgressTracker from "./PipelineProgressTracker.svelte";
  import { t } from "$lib";

  let {
    runStatus = "idle",
    runId = "",
    elapsedSeconds = 0,
    stepNodes = [],
    logsText = "",
    errorMessage = "",
    artifactsData = null,
    onOpenDagu = null,
  } = $props();

  let showPipelineSteps = $state(false);
</script>

{#if runStatus === "running"}
  <div class="space-y-4" in:slide={{ duration: 400, easing: cubicInOut }}>
    <div
      class="p-4 rounded-2xl bg-secondary/10 border border-secondary/30 flex flex-wrap items-center justify-between gap-3 shadow-sm"
    >
      <div class="flex items-center gap-3">
        <span class="loading loading-spinner text-secondary loading-md"></span>
        <div>
          <div class="flex items-center gap-2">
            <span class="text-sm font-black font-display text-base-content">
              {t("orchestrator.realtimeExecution")}
            </span>
            <span
              class="badge badge-secondary badge-xs font-mono font-bold uppercase animate-pulse"
            >
              {t("stepper.active")}
            </span>
          </div>
          <p class="text-xs text-base-content/75 mt-0.5">
            {t("orchestrator.realtimeDesc")}
          </p>
        </div>
      </div>
      <div class="font-mono text-xs font-bold text-secondary">
        ⏱️ {t("orchestrator.elapsed", { seconds: elapsedSeconds })}
      </div>
    </div>

    <!-- Live Step Progress Tracker directly on Clinical Assessment screen -->
    <PipelineProgressTracker
      {runStatus}
      {runId}
      {elapsedSeconds}
      {stepNodes}
      {logsText}
      {errorMessage}
      activeExplorerTab="orchestrator"
      onSelectStep={null}
      onRerun={onOpenDagu}
    />
  </div>
{:else if runStatus === "succeeded" || artifactsData?.orchestrator}
  <div
    class="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-2xl bg-success/10 border border-success/30 text-xs shadow-xs"
    in:fade={{ duration: 300, easing: cubicInOut }}
  >
    <div class="flex items-center gap-2.5">
      <span class="w-2.5 h-2.5 rounded-full bg-success"></span>
      <span
        class="font-black text-success uppercase tracking-wider font-mono"
      >
        {t("orchestrator.liveAnalysisResult")}
      </span>
      <span class="text-base-content font-bold font-mono">
        {t("orchestrator.readyForReview")}
      </span>
      {#if elapsedSeconds > 0}
        <span
          class="badge badge-success badge-xs font-mono font-bold text-success-content"
        >
          {elapsedSeconds}s
        </span>
      {/if}
    </div>

    <div class="flex items-center gap-2">
      <button
        type="button"
        class="btn btn-xs btn-ghost border border-success/30 hover:bg-success/15 gap-1 font-mono text-[11px] cursor-pointer"
        onclick={() => (showPipelineSteps = !showPipelineSteps)}
      >
        <span>{showPipelineSteps ? "▲ " + t("orchestrator.hideSteps") : "▼ " + t("orchestrator.viewSteps")} ({stepNodes?.length || 5})</span>
      </button>

      {#if onOpenDagu}
        <button
          type="button"
          class="btn btn-xs btn-outline btn-success gap-1 font-bold cursor-pointer hover:scale-105 transition-transform"
          onclick={onOpenDagu}
          title={t("common.rerunAnalysis")}
        >
          <span>🔄 {t("common.rerunAnalysis")}</span>
        </button>
      {/if}
    </div>
  </div>

  {#if showPipelineSteps}
    <div in:slide={{ duration: 350, easing: cubicInOut }}>
      <PipelineProgressTracker
        {runStatus}
        {runId}
        {elapsedSeconds}
        {stepNodes}
        {logsText}
        {errorMessage}
        activeExplorerTab="orchestrator"
        onSelectStep={null}
        onRerun={onOpenDagu}
      />
    </div>
  {/if}
{/if}
