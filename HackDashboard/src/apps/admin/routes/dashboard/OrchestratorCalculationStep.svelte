<script>
  import { cubicInOut } from "svelte/easing";
  import { fly } from "svelte/transition";

  let {
    stepData = {},
    patient = {},
    isActive = true,
    isCurrent = false,
    stepNumber = 2,
    onSelectStep = null,
  } = $props();
</script>

<div
  class="p-4 rounded-2xl border transition-all duration-300 ease-in-out shadow-xs {isCurrent
    ? 'border-primary bg-primary/10 shadow-md ring-2 ring-primary/20'
    : 'border-base-300 bg-base-200/40 hover:bg-base-200/70 hover:border-primary/40'}"
  in:fly={{ y: 12, duration: 400, easing: cubicInOut }}
>
  <div class="flex items-start gap-3.5">
    <button
      type="button"
      class="shrink-0 w-8 h-8 rounded-xl bg-primary/15 text-primary flex items-center justify-center font-mono font-black text-sm border border-primary/20 cursor-pointer hover:scale-110 active:scale-95 transition-transform duration-200"
      onclick={() => onSelectStep && onSelectStep(2)}
      title="Focus Step 2"
    >
      {stepNumber}
    </button>
    <div class="min-w-0 flex-1 space-y-2">
      <div class="flex items-center justify-between gap-2 flex-wrap">
        <div class="flex items-center gap-2">
          <span
            class="text-xs font-black text-base-content font-display uppercase tracking-wide"
          >
            {stepData?.title || "AI Clinical Engine · Weight-Based Dosage Calculation"}
          </span>
          {#if isCurrent}
            <span class="badge badge-xs badge-primary font-mono font-bold animate-pulse">
              Active Focus
            </span>
          {/if}
        </div>
        {#if stepData?.badge}
          <span class="badge badge-xs badge-primary font-mono font-bold">
            {stepData.badge}
          </span>
        {/if}
      </div>
      <p class="text-xs text-base-content/80 leading-relaxed">
        {stepData?.desc || ""}
      </p>

      <!-- Formula / Calculation Card -->
      {#if stepData?.formula}
        <div
          class="p-3 rounded-xl bg-base-100 border border-primary/20 shadow-inner flex flex-col md:flex-row items-center justify-between gap-3"
        >
          <div class="flex items-center gap-2 font-mono text-xs flex-wrap">
            <span class="text-base-content/60 font-semibold">Calculation:</span>
            <span class="px-2.5 py-1 rounded-lg bg-primary/10 text-primary font-bold break-all">
              {stepData.formula}
            </span>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            {#if patient?.peso}
              <span class="badge badge-xs badge-neutral font-mono">
                {patient.peso} kg
              </span>
            {/if}
            <span
              class="badge badge-sm badge-outline font-mono text-primary font-bold"
            >
              Deterministic Calculation
            </span>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>
