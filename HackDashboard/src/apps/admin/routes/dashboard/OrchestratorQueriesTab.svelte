<script>
  import { cubicInOut } from "svelte/easing";
  import { fade } from "svelte/transition";

  let { queries = [] } = $props();
</script>

<div class="space-y-2" in:fade={{ duration: 300, easing: cubicInOut }}>
  {#each queries as q, idx}
    <div
      class="flex items-center justify-between p-3.5 rounded-xl border border-primary/20 bg-primary/5 transition-all duration-300 ease-in-out hover:scale-[1.008]"
    >
      <div class="flex items-center gap-3 min-w-0">
        <span class="badge badge-sm badge-primary font-mono font-bold shrink-0">
          #{idx + 1}
        </span>
        <span class="text-xs font-mono font-semibold text-base-content truncate">
          {q}
        </span>
      </div>
      <span
        class="badge badge-xs badge-outline text-primary/80 shrink-0 font-mono"
      >
        Domain Filtered
      </span>
    </div>
  {/each}
</div>
