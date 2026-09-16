<script>
  import { cubicInOut } from "svelte/easing";
  import { fly, fade } from "svelte/transition";

  let {
    stepData = {},
    isActive = true,
    isCurrent = false,
    stepNumber = 1,
    onSelectStep = null,
  } = $props();
</script>

<div
  class="p-4 rounded-2xl border transition-all duration-300 ease-in-out shadow-xs {isCurrent
    ? 'border-secondary bg-secondary/10 shadow-md ring-2 ring-secondary/20'
    : 'border-base-300 bg-base-200/40 hover:bg-base-200/70 hover:border-secondary/40'}"
  in:fly={{ y: 12, duration: 400, easing: cubicInOut }}
>
  <div class="flex items-start gap-3.5">
    <button
      type="button"
      class="shrink-0 w-8 h-8 rounded-xl bg-secondary/15 text-secondary flex items-center justify-center font-mono font-black text-sm border border-secondary/20 cursor-pointer hover:scale-110 active:scale-95 transition-transform duration-200"
      onclick={() => onSelectStep && onSelectStep(1)}
      title="Focus Step 1"
    >
      {stepNumber}
    </button>
    <div class="min-w-0 flex-1 space-y-1.5">
      <div class="flex items-center justify-between gap-2 flex-wrap">
        <div class="flex items-center gap-2">
          <span
            class="text-xs font-black text-base-content font-display uppercase tracking-wide"
          >
            {stepData?.title || "Evidence Search · Botanical & Toxicological Retrieval"}
          </span>
          {#if isCurrent}
            <span class="badge badge-xs badge-secondary font-mono font-bold animate-pulse">
              Active Focus
            </span>
          {/if}
        </div>
        {#if stepData?.badge}
          <span class="badge badge-xs badge-secondary font-mono font-bold">
            {stepData.badge}
          </span>
        {/if}
      </div>
      <p class="text-xs text-base-content/80 leading-relaxed">
        {stepData?.desc || ""}
      </p>

      {#if stepData?.highlightLabel}
        <div
          class="inline-flex items-center gap-2 p-2 rounded-lg bg-base-100 border border-base-300 text-xs font-mono flex-wrap shadow-2xs"
        >
          <span class="text-base-content/60 font-semibold">{stepData.highlightLabel}</span>
          <span class="badge badge-sm badge-secondary font-bold font-mono">
            {stepData.highlightVal}
          </span>
          {#if stepData.highlightSub}
            <span class="text-[11px] text-base-content/50">({stepData.highlightSub})</span>
          {/if}
        </div>
      {/if}
    </div>
  </div>
</div>
