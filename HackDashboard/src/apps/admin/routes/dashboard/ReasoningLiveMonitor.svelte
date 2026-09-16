<script>
  import { cubicInOut } from "svelte/easing";
  import { slide } from "svelte/transition";

  let {
    runStatus = "running",
    elapsedSeconds = 0,
    logsText = "",
    activeLabel = "",
    errorMessage = "",
  } = $props();

  let termEl = $state(null);

  // Keep the terminal pinned to the newest line as logs stream in
  $effect(() => {
    // touch logsText so the effect re-runs on every new chunk
    logsText;
    if (termEl) {
      termEl.scrollTop = termEl.scrollHeight;
    }
  });
</script>

<div
  class="rounded-2xl border border-secondary/30 bg-base-100/90 shadow-md overflow-hidden"
  in:slide={{ duration: 400, easing: cubicInOut }}
>
  <!-- Status bar -->
  <div
    class="flex flex-wrap items-center justify-between gap-3 p-3.5 bg-secondary/10 border-b border-secondary/20"
  >
    <div class="flex items-center gap-3 min-w-0">
      <span class="loading loading-spinner text-secondary loading-sm"></span>
      <div class="min-w-0">
        <div class="flex items-center gap-2 flex-wrap">
          <span class="text-sm font-black font-display text-base-content">
            AI Reasoning · Live
          </span>
          <span
            class="badge badge-secondary badge-xs font-mono font-bold uppercase animate-pulse"
          >
            Streaming
          </span>
        </div>
        <p class="text-[11px] text-base-content/70 mt-0.5 truncate">
          {activeLabel || "Nebius LLM is analyzing the anamnesis in real time…"}
        </p>
      </div>
    </div>
    <div
      class="font-mono text-xs font-bold text-secondary flex items-center gap-1.5 shrink-0"
    >
      <span>⏱️</span>
      <span>{elapsedSeconds}s</span>
    </div>
  </div>

  {#if errorMessage}
    <div
      class="p-2.5 bg-error/15 border-b border-error/30 text-error text-xs font-semibold flex items-center gap-2"
    >
      <span>⚠️</span>
      <span>{errorMessage}</span>
    </div>
  {/if}

  <!-- Live terminal -->
  <div class="bg-neutral text-neutral-content p-3.5 font-mono text-xs">
    <div
      class="flex items-center justify-between pb-2 border-b border-white/10 mb-2"
    >
      <div class="flex items-center gap-2">
        <span class="w-2.5 h-2.5 rounded-full bg-error inline-block"></span>
        <span class="w-2.5 h-2.5 rounded-full bg-warning inline-block"></span>
        <span class="w-2.5 h-2.5 rounded-full bg-success inline-block"></span>
        <span class="text-[11px] font-bold text-white/70 ml-1">
          Dagu · Nebius reasoning stream
        </span>
      </div>
      <span class="text-[10px] text-white/40">Auto-streaming</span>
    </div>

    <pre
      bind:this={termEl}
      class="whitespace-pre-wrap font-mono text-[11px] leading-relaxed max-h-64 overflow-y-auto pr-2 text-emerald-400/90">{logsText ||
        "Waiting for the reasoning engine to emit its first tokens…"}{#if runStatus === "running"}<span
          class="inline-block w-2 h-3.5 bg-emerald-400/90 ml-0.5 animate-pulse align-middle"
        ></span>{/if}</pre>
  </div>
</div>
