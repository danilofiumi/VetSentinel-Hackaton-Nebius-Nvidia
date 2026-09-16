<script>
  import { cubicInOut } from "svelte/easing";
  import { fly } from "svelte/transition";

  let { steps = [] } = $props();

  function statusStyle(status) {
    if (status === "done")
      return {
        dot: "bg-success text-white",
        card: "border-success/40 bg-success/5",
        badge: "badge-success text-white",
        label: "Done",
      };
    if (status === "active")
      return {
        dot: "bg-warning text-white",
        card: "border-warning/50 bg-warning/10 ring-2 ring-warning/25 shadow-md",
        badge: "badge-warning text-base-content",
        label: "Running",
      };
    if (status === "next")
      return {
        dot: "bg-primary text-white animate-pulse",
        card: "border-primary/40 bg-primary/10 ring-2 ring-primary/15",
        badge: "badge-primary text-white",
        label: "Next",
      };
    return {
      dot: "bg-base-300 text-base-content/60",
      card: "border-base-300 bg-base-200/40",
      badge: "badge-ghost",
      label: "Pending",
    };
  }
</script>

<div class="relative">
  {#each steps as step, idx}
    {@const s = statusStyle(step.status)}
    <div
      class="relative flex gap-4 pb-4 last:pb-0"
      in:fly={{ y: 12, duration: 350, delay: idx * 70, easing: cubicInOut }}
    >
      <!-- Left rail: numbered node + connecting spine -->
      <div class="flex flex-col items-center shrink-0">
        <div
          class="w-9 h-9 rounded-xl flex items-center justify-center font-mono font-black text-sm shadow-sm transition-all duration-300 {s.dot}"
        >
          {#if step.status === "active"}
            <span class="loading loading-spinner loading-xs"></span>
          {:else if step.status === "done"}
            ✓
          {:else}
            {idx + 1}
          {/if}
        </div>
        {#if idx < steps.length - 1}
          <div
            class="w-0.5 flex-1 mt-1 rounded-full bg-gradient-to-b from-base-300 to-base-300/20"
          ></div>
        {/if}
      </div>

      <!-- Right: content card -->
      <div
        class="flex-1 rounded-2xl border p-4 shadow-xs transition-all duration-300 ease-in-out hover:shadow-md {s.card}"
      >
        <div class="flex items-center justify-between gap-2 flex-wrap">
          <div class="flex items-center gap-2">
            <span class="text-xl">{step.icon}</span>
            <h4
              class="text-sm font-black text-base-content font-display uppercase tracking-wide"
            >
              {step.title}
            </h4>
          </div>
          <span class="badge badge-xs font-mono font-bold uppercase {s.badge}">
            {s.label}
          </span>
        </div>

        {#if step.desc}
          <p class="text-xs text-base-content/70 mt-1.5 leading-relaxed">
            {step.desc}
          </p>
        {/if}

        {#if step.metrics && step.metrics.length > 0}
          <div class="flex flex-wrap items-center gap-1.5 mt-2.5">
            {#each step.metrics as m}
              <span
                class="badge badge-sm badge-outline font-mono font-bold text-[11px]"
              >
                {#if m.label}<span class="text-base-content/50 mr-1"
                    >{m.label}</span
                  >{/if}{m.value}
              </span>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  {/each}
</div>
