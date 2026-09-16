<script>
  import { cubicInOut } from "svelte/easing";
  import { fly } from "svelte/transition";

  const pillars = [
    {
      title: "Svelte 5 Runes & Telemetry UI",
      tag: "Reactive Frontend",
      icon: "⚡",
      badge: "Svelte 5 + DaisyUI",
      badgeColor: "badge-primary",
      description:
        "Built with Svelte 5 Runes ($state, $props, $derived) and TailwindCSS. Features hospital-grade telemetry with live Canvas ECG sinus rhythm rendering, 12 clinical ward themes, and smooth cubic easing transitions.",
      metrics: ["Fine-grained reactivity", "12 Hospital Themes", "60 FPS Canvas ECG rhythm", "Zero unnecessary VDOM diffing"]
    },
    {
      title: "Dagu DAG Pipeline Engine",
      tag: "Orchestration & Audit",
      icon: "🔄",
      badge: "Directed Acyclic Graph",
      badgeColor: "badge-accent",
      description:
        "Execution is partitioned into an explicit Directed Acyclic Graph (DAG) rather than an unconstrained single chatbot call. Persists execution artifacts and logs to disk for direct electronic health record (EMR) auditing and medicolegal reproducibility.",
      metrics: ["Medicolegal audit trail", "Auto-saved JSON & MD artifacts", "Isolated step execution", "Error boundary isolation"]
    },
    {
      title: "Nebius AI Token Factory",
      tag: "Ultra-Low Latency Inference",
      icon: "🚀",
      badge: "GLM-5.3-Flash",
      badgeColor: "badge-secondary",
      description:
        "Served via Nebius AI Token Factory utilizing the high-throughput GLM-5.3-Flash model. Delivers sub-300ms time-to-first-token intake hazard categorization so emergency clinicians never wait on slow chat spinners.",
      metrics: ["Sub-300ms time-to-first-token", "Structured JSON extraction", "High concurrency throughput", "Deterministic schema output"]
    },
    {
      title: "Zero-Hallucination Guardrail",
      tag: "Evidence & Math",
      icon: "🛡️",
      badge: "ASPCA · Merck · BSAVA",
      badgeColor: "badge-success",
      description:
        "The LLM is strictly prohibited from guessing drug dosages. Medical protocols are retrieved via Tavily's verified domain whitelist, and weight-based formulas (mg/kg) are evaluated deterministically with mandatory source citations.",
      metrics: ["Strict domain whitelist", "Mathematical weight dosing", "Mandatory clinical citations", "Anti-hallucination boundary"]
    }
  ];
</script>

<div class="space-y-10">
  <div class="text-center max-w-3xl mx-auto space-y-3">
    <div class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary font-mono text-xs font-bold uppercase tracking-wider">
      <span>⚙️ Core Architecture</span>
      <span>·</span>
      <span>Production Stack</span>
    </div>
    <h2 class="text-2xl sm:text-4xl font-black font-display tracking-tight text-base-content">
      Architected for Speed, <span class="text-primary">Reliability & Auditability</span>.
    </h2>
    <p class="text-xs sm:text-sm text-base-content/70 font-sans">
      How VetSentinel combines state-of-the-art AI infrastructure with hospital-grade determinism.
    </p>
  </div>

  <!-- 4 Pillars Grid -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    {#each pillars as p}
      <div
        class="card bg-base-100/90 border border-base-content/15 shadow-md rounded-3xl p-6 sm:p-7 hover:border-primary/50 hover:shadow-xl transition-all duration-300 flex flex-col justify-between"
      >
        <div>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span class="w-12 h-12 rounded-2xl bg-base-200 border border-base-300 flex items-center justify-center text-2xl shadow-inner">
                {p.icon}
              </span>
              <div>
                <span class="text-[10px] font-mono uppercase tracking-widest text-base-content/50 font-bold">
                  {p.tag}
                </span>
                <h3 class="text-lg font-bold font-display text-base-content">
                  {p.title}
                </h3>
              </div>
            </div>
          </div>

          <div class="mt-3">
            <span class="badge {p.badgeColor} badge-sm font-mono font-bold text-white shadow-xs">
              {p.badge}
            </span>
          </div>

          <p class="text-xs sm:text-sm text-base-content/75 mt-3 leading-relaxed font-sans">
            {p.description}
          </p>
        </div>

        <div class="mt-5 pt-4 border-t border-base-content/10">
          <div class="flex flex-wrap items-center gap-1.5">
            {#each p.metrics as m}
              <span class="badge badge-neutral badge-xs font-mono text-[10px] py-2 px-2.5">
                ✓ {m}
              </span>
            {/each}
          </div>
        </div>
      </div>
    {/each}
  </div>
</div>
