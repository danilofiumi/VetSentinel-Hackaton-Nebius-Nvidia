<script>
  import { cubicInOut } from "svelte/easing";
  import { fly } from "svelte/transition";
  import HackathonArchitecture from "./HackathonArchitecture.svelte";
  import HackathonPipeline from "./HackathonPipeline.svelte";
  import HackathonMetaphors from "./HackathonMetaphors.svelte";
  import HackathonFaq from "./HackathonFaq.svelte";
</script>

<div class="min-h-screen py-8 px-4 sm:px-6 max-w-7xl mx-auto space-y-12">
  <!-- Top Navigation & Breadcrumbs -->
  <div class="flex items-center justify-between text-xs text-base-content/70">
    <a
      href="/"
      class="inline-flex items-center gap-1.5 font-bold hover:text-primary transition-colors cursor-pointer"
    >
      <span>←</span>
      <span>Back to Veterinary Story & Overview</span>
    </a>

    <div class="flex items-center gap-3">
      <a
        href="/dashboard"
        data-sveltekit-preload-code="eager"
        data-sveltekit-preload-data="tap"
        class="btn btn-primary btn-xs sm:btn-sm rounded-xl font-bold font-display shadow-xs gap-1.5 hover:scale-105 active:scale-95 transition-all duration-200"
      >
        <span>⚡ Open Live ER Copilot</span>
        <span>→</span>
      </a>
    </div>
  </div>

  <!-- Hero Header for Hackathon Judges -->
  <div
    class="p-6 sm:p-10 rounded-3xl bg-base-100/90 border border-primary/30 shadow-2xl backdrop-blur-xl relative overflow-hidden"
    in:fly={{ y: 20, duration: 500, easing: cubicInOut }}
  >
    <div class="flex flex-col md:flex-row items-center justify-between gap-6">
      <div class="space-y-3 text-center md:text-left">
        <div class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary font-mono text-xs font-bold uppercase tracking-wider">
          <span>🏆 Hackathon Technical Showcase</span>
          <span>·</span>
          <span>Engineering Architecture</span>
        </div>
        <h1 class="text-3xl sm:text-5xl font-black font-display text-base-content leading-tight">
          Under The Hood: <span class="text-primary">VetSentinel</span>
        </h1>
        <p class="text-xs sm:text-sm text-base-content/75 font-sans max-w-2xl leading-relaxed">
          Comprehensive technical defense, enterprise-grade DAG pipeline architecture, low-latency LLM inference, and zero-hallucination deterministic medical boundaries.
        </p>
      </div>

      <div class="flex flex-wrap items-center justify-center gap-2 font-mono text-xs">
        <span class="badge badge-primary font-bold py-2.5 px-3 shadow-xs">Svelte 5 Runes</span>
        <span class="badge badge-accent font-bold py-2.5 px-3 shadow-xs">Dagu DAG Engine</span>
        <span class="badge badge-secondary font-bold py-2.5 px-3 shadow-xs">Nebius AI</span>
        <span class="badge badge-neutral font-bold py-2.5 px-3">Tavily Whitelist</span>
      </div>
    </div>
  </div>

  <!-- 4 Architectural Pillars -->
  <HackathonArchitecture />

  <!-- Dagu Pipeline & Medicolegal Artifacts Visualizer -->
  <HackathonPipeline />

  <!-- 3 Winning ELI5 Metaphors -->
  <HackathonMetaphors />

  <!-- Expanded 8-Question Judge Q&A -->
  <HackathonFaq />

  <!-- Bottom CTA -->
  <div class="p-8 rounded-3xl bg-base-100/80 border border-base-content/15 text-center space-y-4">
    <h3 class="text-xl sm:text-2xl font-bold font-display text-base-content">
      Ready to test the live workstation?
    </h3>
    <p class="text-xs sm:text-sm text-base-content/70 max-w-xl mx-auto">
      Experience the real-time Dagu execution graph, inspect the live node streaming logs, and verify the weight-based dosing formulas.
    </p>
    <div class="pt-2">
      <a
        href="/dashboard"
        data-sveltekit-preload-code="eager"
        data-sveltekit-preload-data="tap"
        class="btn btn-primary btn-md rounded-2xl gap-2 font-bold font-display shadow-lg shadow-primary/25 hover:scale-105 active:scale-95 transition-all duration-200 select-none"
      >
        <span>⚡ Launch ER Copilot Workstation</span>
        <span>→</span>
      </a>
    </div>
  </div>
</div>
