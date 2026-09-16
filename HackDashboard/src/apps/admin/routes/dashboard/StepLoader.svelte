<script>
  import { cubicInOut } from "svelte/easing";
  import { fade } from "svelte/transition";

  let {
    icon = "⏳",
    title = "Processing…",
    subtitle = "This step is running. Results will appear here as soon as it finishes.",
    statusLabel = "",
  } = $props();
</script>

<div
  class="flex flex-col items-center justify-center text-center gap-4 py-16 px-6"
  in:fade={{ duration: 300, easing: cubicInOut }}
>
  <div class="relative flex items-center justify-center">
    <span
      class="loading loading-spinner loading-lg text-secondary"
    ></span>
    <span class="absolute text-2xl">{icon}</span>
  </div>

  <div class="space-y-1.5 max-w-md">
    <h3
      class="text-base lg:text-lg font-black text-base-content font-display flex items-center justify-center gap-2"
    >
      {title}
      <span
        class="badge badge-secondary badge-xs font-mono font-bold uppercase animate-pulse"
      >
        Live
      </span>
    </h3>
    <p class="text-sm text-base-content/70 leading-relaxed">
      {subtitle}
    </p>
    {#if statusLabel}
      <p class="text-xs font-mono text-secondary/80 pt-1">{statusLabel}</p>
    {/if}
  </div>

  <!-- Indeterminate progress shimmer -->
  <div class="w-full max-w-xs h-1.5 rounded-full bg-base-200 overflow-hidden">
    <div
      class="h-full w-1/3 rounded-full bg-secondary animate-[loaderSlide_1.4s_ease-in-out_infinite]"
    ></div>
  </div>
</div>

<style>
  @keyframes loaderSlide {
    0% {
      transform: translateX(-120%);
    }
    50% {
      transform: translateX(120%);
    }
    100% {
      transform: translateX(320%);
    }
  }
</style>
