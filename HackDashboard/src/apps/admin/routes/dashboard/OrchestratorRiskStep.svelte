<script>
  import { cubicInOut } from "svelte/easing";
  import { fly } from "svelte/transition";

  let {
    stepData = {},
    isActive = true,
    isCurrent = false,
    stepNumber = 3,
    onSelectStep = null,
  } = $props();
</script>

<div
  class="p-4 rounded-2xl border transition-all duration-300 ease-in-out shadow-xs {isCurrent
    ? 'border-warning bg-warning/10 shadow-md ring-2 ring-warning/20'
    : 'border-base-300 bg-base-200/40 hover:bg-base-200/70 hover:border-warning/40'}"
  in:fly={{ y: 12, duration: 400, easing: cubicInOut }}
>
  <div class="flex items-start gap-3.5">
    <button
      type="button"
      class="shrink-0 w-8 h-8 rounded-xl bg-warning/15 text-warning flex items-center justify-center font-mono font-black text-sm border border-warning/20 cursor-pointer hover:scale-110 active:scale-95 transition-transform duration-200"
      onclick={() => onSelectStep && onSelectStep(3)}
      title="Focus Step 3"
    >
      {stepNumber}
    </button>
    <div class="min-w-0 flex-1 space-y-2.5">
      <div class="flex items-center justify-between gap-2 flex-wrap">
        <div class="flex items-center gap-2">
          <span
            class="text-xs font-black text-base-content font-display uppercase tracking-wide"
          >
            {stepData?.title || "Clinical Assessment of Risk Thresholds"}
          </span>
          {#if isCurrent}
            <span class="badge badge-xs badge-warning font-mono font-bold animate-pulse">
              Active Focus
            </span>
          {/if}
        </div>
        {#if stepData?.badge}
          <span
            class="badge badge-xs {stepData.badgeClass || 'badge-warning'} font-mono font-bold"
          >
            {stepData.badge}
          </span>
        {/if}
      </div>

      <!-- Risk Threshold Meter -->
      {#if stepData?.thresholds && stepData.thresholds.length > 0}
        <div class="grid grid-cols-1 md:grid-cols-3 gap-2.5 pt-1 text-xs">
          {#each stepData.thresholds as thr}
            <div class="p-3 rounded-xl bg-base-100 border border-base-200 shadow-xs transition-all duration-300 hover:border-warning/40">
              <div class="flex items-center justify-between">
                <span class="font-bold text-base-content font-mono">{thr.label}</span>
                <span class="badge badge-xs badge-neutral font-mono">{thr.badge}</span>
              </div>
              <p class="text-[11px] text-base-content/70 mt-1 leading-relaxed">
                {thr.text}
              </p>
            </div>
          {/each}
        </div>
      {/if}

      <!-- Alert Box -->
      {#if stepData?.alertBox}
        <div
          class="p-3 rounded-xl bg-base-100 border border-warning/40 shadow-xs flex items-center justify-between gap-3"
        >
          <div class="flex items-center gap-2.5">
            <span class="text-xl">⚠️</span>
            <div>
              <div class="text-xs font-black text-base-content">
                {stepData.alertBox.title}
              </div>
              <div class="text-[11px] text-base-content/60 font-mono mt-0.5">
                {stepData.alertBox.desc}
              </div>
            </div>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>
