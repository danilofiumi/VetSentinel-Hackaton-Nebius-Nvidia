<script>
  import { cubicInOut } from "svelte/easing";
  import { fly } from "svelte/transition";

  let { caseData = {} } = $props();
</script>

<div
  class="rounded-2xl border border-primary/25 bg-primary/5 p-5 shadow-sm space-y-3 transition-all duration-300 ease-in-out hover:border-primary/40"
  in:fly={{ y: 12, duration: 400, easing: cubicInOut }}
>
  <div class="flex items-center justify-between flex-wrap gap-2">
    <div class="flex items-center gap-2">
      <span class="text-2xl">🧪</span>
      <h3
        class="text-sm lg:text-base font-black text-base-content font-display uppercase tracking-wide"
      >
        {caseData?.problemTitle || "1. Chemical & Pathophysiological Problem"}
      </h3>
    </div>
    {#if caseData?.problemTag}
      <span class="badge badge-sm badge-primary font-mono font-bold">
        {caseData.problemTag}
      </span>
    {/if}
  </div>

  {#if caseData?.chemCards && caseData.chemCards.length > 0}
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1 text-xs">
      {#each caseData.chemCards as card, idx}
        <div
          class="bg-base-100/90 p-3.5 rounded-xl border border-base-200 shadow-xs transition-all duration-300 hover:shadow-md hover:border-primary/30"
        >
          <div
            class="{idx === 0
              ? 'text-primary'
              : idx === 1
                ? 'text-secondary'
                : 'text-accent'} font-bold uppercase tracking-wider text-[11px] font-label"
          >
            {card.tag}
          </div>
          <div class="font-bold text-base-content text-sm mt-0.5 font-display">
            {card.title}
          </div>
          <p class="text-base-content/70 mt-1 leading-relaxed">
            {card.desc}
          </p>
        </div>
      {/each}
    </div>
  {/if}
</div>
