<script>
  import { t } from "$lib";

  let {
    patient = {},
    priority = "",
    urgencyBadgeClass = "badge-success text-white",
    hasLiveData = false,
    isRunning = false,
    modelUsed = "",
  } = $props();
</script>

<div
  class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-base-200 pb-5"
>
  <div>
    <div class="flex items-center gap-2 flex-wrap">
      <div
        class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-secondary font-label"
      >
        <span class="inline-block w-2.5 h-2.5 rounded-full bg-secondary"></span>
        {t("stepper.step2Label")}
      </div>
      {#if hasLiveData}
        <span
          class="badge badge-xs badge-success text-white font-mono font-bold gap-1"
        >
          <span
            class="inline-block w-1.5 h-1.5 rounded-full bg-white animate-pulse"
          ></span>
          {t("orchestrator.liveInference")}{modelUsed ? " · " + modelUsed : ""}
        </span>
        {#if priority}
          <span
            class="badge badge-xs font-mono font-bold uppercase gap-1 {urgencyBadgeClass}"
          >
            {t("orchestrator.aiTriage")}
            {priority}
          </span>
        {/if}
      {:else if isRunning}
        <span
          class="badge relative -top-1 badge-xs badge-secondary text-white font-mono font-bold gap-1.5 animate-pulse"
        >
          {t("orchestrator.reasoningLive")}
        </span>
      {:else}
        <span class="badge badge-xs badge-ghost font-mono font-bold">
          {t("orchestrator.previewNotice")}
        </span>
      {/if}
    </div>
    <h2
      class="text-2xl lg:text-3xl font-black tracking-tight text-base-content font-display mt-1"
    >
      {t("orchestrator.headerTitle")}
    </h2>
    <p class="text-sm text-base-content/70 mt-0.5">
      {t("orchestrator.headerDesc")}
    </p>
  </div>
</div>
