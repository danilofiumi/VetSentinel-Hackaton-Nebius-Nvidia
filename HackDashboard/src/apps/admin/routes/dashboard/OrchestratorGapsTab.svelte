<script>
  import { cubicInOut } from "svelte/easing";
  import { fade } from "svelte/transition";

  let { gaps = [] } = $props();
</script>

<div class="grid grid-cols-1 gap-2.5" in:fade={{ duration: 300, easing: cubicInOut }}>
  {#each gaps as gap}
    <div
      class="flex items-start gap-3.5 p-4 rounded-2xl border border-base-300 bg-base-200/30 transition-all duration-300 ease-in-out hover:bg-base-200/70"
    >
      <span
        class="text-2xl shrink-0 p-2 bg-base-100 rounded-xl shadow-xs border border-base-content/5"
      >
        {gap.icon}
      </span>
      <div class="min-w-0 flex-1">
        <div class="flex items-center justify-between gap-2">
          <span class="text-xs font-bold text-base-content font-display">
            {gap.gap}
          </span>
          <span
            class="badge badge-xs {gap.severity === 'critical'
              ? 'badge-error text-white'
              : gap.severity === 'high'
                ? 'badge-warning text-base-content'
                : 'badge-info text-white'} font-bold uppercase font-mono"
          >
            {gap.severity} impact
          </span>
        </div>
        <p class="text-xs text-base-content/70 mt-1.5 leading-relaxed">
          {gap.desc}
        </p>
      </div>
    </div>
  {/each}
</div>
