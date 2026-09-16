<script>
  const metaphors = [
    {
      concept: "Dagu Workflow Engine",
      metaphor: "The Emergency Assembly Line",
      icon: "🏭",
      quote:
        "It works like an emergency assembly line: if doctor one doesn’t finish the diagnosis, doctor two won’t run searches, and doctor three won’t prepare the medication. No compounding errors.",
      badge: "Orchestration",
      color: "border-primary/40 bg-primary/5 text-primary"
    },
    {
      concept: "Tavily Whitelist Search",
      metaphor: "The AI with Focused Glasses",
      icon: "👓",
      quote:
        "We gave the AI a pair of focused glasses: it can only read peer-reviewed veterinary manuals (ASPCA, Merck, BSAVA), completely ignoring internet forums, ad blogs, and random opinions.",
      badge: "Evidence Guardrail",
      color: "border-accent/40 bg-accent/5 text-accent"
    },
    {
      concept: "Deterministic Dosing Engine",
      metaphor: "Never Let a Chatbot Do Drug Math",
      icon: "🧮",
      quote:
        "We never let a probabilistic chatbot guess milligrams: we compute exact volumes by multiplying verified formulas with weight, because drug dosing in a 1 kg or 4 kg patient cannot rely on guesswork.",
      badge: "Zero Guesswork",
      color: "border-secondary/40 bg-secondary/5 text-secondary"
    },
  ];
</script>

<div class="space-y-8">
  <div class="text-center max-w-2xl mx-auto space-y-2">
    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-warning/10 border border-warning/20 text-warning font-mono text-xs font-bold uppercase tracking-wider">
      <span>💡 Conceptual Clarity</span>
      <span>·</span>
      <span>ELI5 Metaphors</span>
    </div>
    <h3 class="text-2xl sm:text-3xl font-black font-display text-base-content">
      3 Winning Metaphors for the Hackathon Pitch
    </h3>
    <p class="text-xs sm:text-sm text-base-content/70 font-sans">
      How we communicate complex systems architecture to non-technical stakeholders and judges.
    </p>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    {#each metaphors as m}
      <div
        class="card bg-base-100/90 border border-base-content/15 shadow-md rounded-3xl p-6 hover:border-primary/50 hover:shadow-xl transition-all duration-300 flex flex-col justify-between"
      >
        <div>
          <div class="flex items-center justify-between">
            <span class="text-3xl p-2.5 rounded-2xl bg-base-200 border border-base-300 shadow-inner">
              {m.icon}
            </span>
            <span class="badge badge-sm font-mono font-bold {m.color}">
              {m.badge}
            </span>
          </div>

          <div class="mt-4">
            <p class="text-[10px] font-mono uppercase text-base-content/50 font-bold tracking-wider">
              Concept: {m.concept}
            </p>
            <h4 class="text-base font-bold font-display text-base-content mt-0.5">
              "{m.metaphor}"
            </h4>
          </div>

          <p class="text-xs text-base-content/80 mt-3 font-sans italic leading-relaxed">
            "{m.quote}"
          </p>
        </div>
      </div>
    {/each}
  </div>
</div>
