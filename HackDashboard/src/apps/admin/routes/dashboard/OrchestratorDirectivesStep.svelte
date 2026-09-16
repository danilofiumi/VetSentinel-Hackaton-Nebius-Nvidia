<script>
  import { cubicInOut } from "svelte/easing";
  import { fly } from "svelte/transition";

  let {
    stepData = {},
    isActive = true,
    isCurrent = false,
    stepNumber = 4,
    onSelectStep = null,
  } = $props();
</script>

<div
  class="p-4 rounded-2xl border-2 transition-all duration-300 ease-in-out shadow-md {isCurrent
    ? 'border-secondary bg-secondary/15 ring-2 ring-secondary/30'
    : 'border-secondary/40 bg-secondary/5 hover:border-secondary/60'}"
  in:fly={{ y: 12, duration: 400, easing: cubicInOut }}
>
  <div class="flex items-start gap-3.5">
    <button
      type="button"
      class="shrink-0 w-8 h-8 rounded-xl bg-secondary text-white flex items-center justify-center font-mono font-black text-sm shadow-sm cursor-pointer hover:scale-110 active:scale-95 transition-transform duration-200"
      onclick={() => onSelectStep && onSelectStep(4)}
      title="Focus Step 4"
    >
      {stepNumber}
    </button>
    <div class="min-w-0 flex-1 space-y-3">
      <div class="flex items-center justify-between gap-2 flex-wrap">
        <div class="flex items-center gap-2">
          <span
            class="text-xs font-black text-base-content font-display uppercase tracking-wide flex items-center gap-2"
          >
            <span>VetSentinel Recommendation · Emergency Actions</span>
            <span
              class="inline-block w-2 h-2 rounded-full bg-secondary animate-ping"
            ></span>
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

      <!-- 3 Action Directives -->
      {#if stepData?.directives && stepData.directives.length > 0}
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          {#each stepData.directives as dir}
            <div
              class="p-3.5 rounded-xl bg-base-100 border {dir.border ||
                'border-base-300'} shadow-xs space-y-1 transition-all duration-300 hover:shadow-md"
            >
              <div
                class="flex items-center gap-2 text-xs font-black {dir.color ||
                  'text-secondary'} font-display uppercase"
              >
                <span>{dir.icon}</span>
                <span>{dir.title}</span>
              </div>
              <div class="text-xs font-bold text-base-content">
                {dir.heading}
              </div>
              <p class="text-[11px] text-base-content/70 leading-relaxed">
                {dir.desc}
              </p>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
</div>
