<script>
  let { size = "md", withText = false, withPulse = true, class: className = "" } = $props();

  const sizeClasses = {
    sm: "w-8 h-8",
    md: "w-10 h-10",
    lg: "w-12 h-12",
    xl: "w-16 h-16",
  };

  const iconSizes = {
    sm: "w-5 h-5",
    md: "w-6 h-6",
    lg: "w-7 h-7",
    xl: "w-10 h-10",
  };
</script>

<div class="inline-flex items-center gap-3 select-none {className}">
  <!-- Logo Icon Container -->
  <div
    class="relative {sizeClasses[size] || sizeClasses.md} rounded-2xl bg-gradient-to-br from-primary/25 via-primary/10 to-base-200 border border-primary/40 flex items-center justify-center text-primary shadow-inner shadow-primary/10 transition-transform duration-300 hover:scale-105 group"
  >
    <!-- Medical Shield + Veterinary Cross + Vital Lifeline SVG -->
    <svg
      class="{iconSizes[size] || iconSizes.md} fill-none stroke-current"
      viewBox="0 0 32 32"
      xmlns="http://www.w3.org/2000/svg"
    >
      <!-- Subtle Medical Cross Background Glow -->
      <path
        d="M13 5h6v7h7v6h-7v9h-6v-9H6v-6h7V5z"
        class="fill-primary/15 stroke-primary/30"
        stroke-width="1.5"
        stroke-linejoin="round"
      />

      <!-- Stylized Central Heartbeat / Lifeline Trace -->
      <path
        d="M5 16h6l2.5-5 3.5 10 2.5-6 1.5 2 6-1"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="drop-shadow-[0_0_6px_rgba(16,185,129,0.7)]"
      />

      <!-- Stylized Protective Veterinary Paw Elements -->
      <circle cx="16" cy="19.5" r="2.2" class="fill-primary stroke-none" />
      <circle cx="12.5" cy="16.5" r="1.2" class="fill-primary stroke-none" />
      <circle cx="19.5" cy="16.5" r="1.2" class="fill-primary stroke-none" />
      <circle cx="10.5" cy="19" r="1" class="fill-primary/80 stroke-none" />
      <circle cx="21.5" cy="19" r="1" class="fill-primary/80 stroke-none" />
    </svg>

    <!-- Active Telemetry Pulse Ring -->
    {#if withPulse}
      <span
        class="absolute -bottom-0.5 -right-0.5 flex h-3 w-3"
        title="Clinical Telemetry Active"
      >
        <span
          class="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"
        ></span>
        <span
          class="relative inline-flex rounded-full h-3 w-3 bg-success border-2 border-base-100"
        ></span>
      </span>
    {/if}
  </div>

  <!-- Optional Logo Wordmark -->
  {#if withText}
    <div class="flex flex-col text-left">
      <div class="flex items-center gap-2">
        <span class="text-base sm:text-lg font-black tracking-tight font-display text-base-content leading-none">
          VetSentinel
        </span>
        <span class="badge badge-sm badge-primary font-bold font-mono text-[9px] tracking-wider uppercase py-0.5 shadow-xs">
          ER
        </span>
      </div>
      <span class="text-[9px] font-mono tracking-widest uppercase text-base-content/50 font-bold mt-0.5">
        Clinical Toxicology Copilot
      </span>
    </div>
  {/if}
</div>
