<script>
  let { priority = $bindable("critical") } = $props();

  const options = [
    {
      id: "critical",
      label: "Red",
      code: "I",
      tooltip: "Code Red · Critical (Immediate life-saving care)",
      activeClass:
        "bg-gradient-to-r from-red-600 via-rose-600 to-red-500 text-white shadow-lg shadow-red-500/30 border-red-400/50 ring-2 ring-red-500/20 scale-[1.03]",
      inactiveClass:
        "text-base-content/70 hover:text-red-500 hover:bg-red-500/10 border-transparent",
      accentBg: "bg-red-500",
      bars: [true, true, true],
    },
    {
      id: "urgent",
      label: "Yellow",
      code: "II",
      tooltip: "Code Yellow · Urgent (Evaluation within 30 min)",
      activeClass:
        "bg-gradient-to-r from-amber-500 via-yellow-500 to-amber-400 text-neutral-950 shadow-lg shadow-amber-500/30 border-amber-300/60 ring-2 ring-amber-400/20 scale-[1.03]",
      inactiveClass:
        "text-base-content/70 hover:text-amber-500 hover:bg-amber-500/10 border-transparent",
      accentBg: "bg-amber-500",
      bars: [true, true, false],
    },
    {
      id: "stable",
      label: "Green",
      code: "III",
      tooltip: "Code Green · Stable (Routine veterinary intake)",
      activeClass:
        "bg-gradient-to-r from-emerald-600 via-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30 border-emerald-400/50 ring-2 ring-emerald-500/20 scale-[1.03]",
      inactiveClass:
        "text-base-content/70 hover:text-emerald-500 hover:bg-emerald-500/10 border-transparent",
      accentBg: "bg-emerald-500",
      bars: [true, false, false],
    },
  ];
</script>

<div
  class="p-1.5 bg-base-200/70 dark:bg-base-300/50 backdrop-blur-md rounded-2xl border border-base-content/10 shadow-inner inline-flex items-center gap-1.5"
  role="radiogroup"
  aria-label="Triage Priority Level"
>
  {#each options as opt}
    <div
      class="tooltip tooltip-bottom before:text-[11px] before:font-medium before:shadow-lg before:z-50"
      data-tip={opt.tooltip}
    >
      <button
        type="button"
        role="radio"
        aria-checked={priority === opt.id}
        class="relative px-3 py-2 rounded-xl text-xs font-bold font-label cursor-pointer flex items-center gap-2 border transition-all duration-300 ease-in-out hover:-translate-y-0.5 active:scale-95 {priority ===
        opt.id
          ? opt.activeClass
          : opt.inactiveClass}"
        onclick={() => (priority = opt.id)}
      >
        <!-- Icon & Pulse Indicator -->
        <span class="relative flex items-center justify-center shrink-0">
          {#if opt.id === "critical"}
            <!-- Emergency Siren Beacon Icon -->
            <svg
              class="w-4 h-4 transition-transform duration-300 ease-in-out {priority ===
              'critical'
                ? 'scale-110'
                : 'opacity-70'}"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M12 2v2" />
              <path d="m4.93 4.93 1.41 1.41" />
              <path d="m19.07 4.93-1.41 1.41" />
              <path d="M12 8a5 5 0 0 0-5 5v5h10v-5a5 5 0 0 0-5-5z" />
              <path d="M5 21h14" />
            </svg>
          {:else if opt.id === "urgent"}
            <!-- Urgent Lightning Zap Icon -->
            <svg
              class="w-4 h-4 transition-transform duration-300 ease-in-out {priority ===
              'urgent'
                ? 'scale-110'
                : 'opacity-70'}"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
          {:else}
            <!-- Stable Medical Shield Check Icon -->
            <svg
              class="w-4 h-4 transition-transform duration-300 ease-in-out {priority ===
              'stable'
                ? 'scale-110'
                : 'opacity-70'}"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              <path d="m9 12 2 2 4-4" />
            </svg>
          {/if}

          <!-- Subtle ping badge on active -->
          {#if priority === opt.id}
            <span
              class="absolute -top-1 -right-1 flex h-2 w-2 items-center justify-center"
            >
              <span
                class="animate-ping absolute inline-flex h-full w-full rounded-full {opt.id ===
                'urgent'
                  ? 'bg-neutral-950 opacity-40'
                  : 'bg-white opacity-75'}"
              ></span>
              <span
                class="relative inline-flex rounded-full h-1.5 w-1.5 {opt.id ===
                'urgent'
                  ? 'bg-neutral-950'
                  : 'bg-white'}"
              ></span>
            </span>
          {/if}
        </span>

        <!-- Visual 3-Stage Urgency Acuity Gauge -->
        <span
          class="flex items-end gap-0.5 h-3.5 px-0.5 shrink-0"
          aria-hidden="true"
        >
          {#each opt.bars as isLit, idx}
            <span
              class="w-1 rounded-full transition-all duration-300 ease-in-out {idx ===
              0
                ? 'h-1.5'
                : idx === 1
                  ? 'h-2.5'
                  : 'h-3.5'} {priority === opt.id
                ? opt.id === 'urgent'
                  ? isLit
                    ? 'bg-neutral-950 font-bold'
                    : 'bg-neutral-950/20'
                  : isLit
                    ? 'bg-white'
                    : 'bg-white/25'
                : isLit
                  ? opt.id === 'critical'
                    ? 'bg-red-500/70'
                    : opt.id === 'urgent'
                      ? 'bg-amber-500/70'
                      : 'bg-emerald-500/70'
                  : 'bg-base-content/15'}"
            ></span>
          {/each}
        </span>

        <!-- Clean Minimal Label (Less Text, High Contrast) -->
        <span class="tracking-tight text-xs">{opt.label}</span>
      </button>
    </div>
  {/each}
</div>
