<script>
  let activeArtifact = $state("json");

  const sampleJsonArtifact = `{
  "patient": {
    "species": "Feline",
    "breed": "Domestic Shorthair",
    "weight_kg": 4.0,
    "priority": "Class 1: Resuscitation",
    "intake_toxin": "Lilium longiflorum (Easter Lily)"
  },
  "triage_assessment": {
    "active_toxin_risk": "Acute Nephrotoxicity",
    "window_hours": 18,
    "emesis_indicated": false,
    "emesis_contraindication": "Lethargy and impending neurological depression"
  },
  "calculated_dosing": {
    "crystalloid_diuresis_rate_ml_hr": 28.0,
    "diuresis_duration_hours": 48,
    "activated_charcoal_g": 6.0
  },
  "sources_cited": [
    "ASPCA APCC Lily Ingestion Guidelines (2024)",
    "Merck Veterinary Manual 11th Ed - Feline Toxicosis"
  ]
}`;

  const sampleMdArtifact = `# VETSENTINEL EMERGENCY TOXICOLOGY REPORT
**Ward:** Veterinary ICU | **Timestamp:** 2026-09-11T09:40:15Z
**Patient:** Milo (Cat, 4.0 kg, DSH) | **Triage Class:** Resuscitation

## 1. Acute Hazard Profile
- **Suspected Agent:** Lilium spp. (True Lily)
- **Toxicity Mechanism:** Feline-specific renal tubular necrosis
- **Time Window:** 18-36 hours to irreversible anuric failure

## 2. Emergency Interventions
- **IV Fluid Perfusion:** Balanced Electrolytes @ 28.0 ml/hr (7 ml/kg/hr) for 48h
- **GI Decontamination:** Activated Charcoal 6.0 g PO with sorbitol
- **Anti-Emetic:** Maropitant 4.0 mg SC q24h

## 3. Mandatory Safety Contraindications
- [CRITICAL] DO NOT induce emesis: Patient exhibiting lethargy.
- [CRITICAL] AVOID all NSAIDs (Meloxicam) due to acute renal perfusion compromise.`;
</script>

<div class="card bg-base-100/90 border border-base-content/15 shadow-xl rounded-3xl p-6 sm:p-8 backdrop-blur-xl space-y-6">
  <div class="flex flex-col md:flex-row items-center justify-between gap-4">
    <div>
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent/10 border border-accent/20 text-accent font-mono text-xs font-bold uppercase tracking-wider">
        <span>🔄 Dagu Orchestrator Telemetry</span>
      </div>
      <h3 class="text-xl sm:text-2xl font-bold font-display text-base-content mt-1">
        Direct Acyclic Graph (DAG) & Medicolegal Artifacts
      </h3>
      <p class="text-xs text-base-content/70 font-sans mt-0.5">
        How every execution persists deterministic, audit-ready files to disk.
      </p>
    </div>

    <!-- Switch Artifact View -->
    <div class="join border border-base-300">
      <button
        type="button"
        class="btn btn-xs join-item font-mono {activeArtifact === 'json' ? 'btn-primary font-bold' : 'btn-ghost'}"
        onclick={() => activeArtifact = 'json'}
      >
        03_synthesis.json
      </button>
      <button
        type="button"
        class="btn btn-xs join-item font-mono {activeArtifact === 'md' ? 'btn-primary font-bold' : 'btn-ghost'}"
        onclick={() => activeArtifact = 'md'}
      >
        final_sheet.md
      </button>
    </div>
  </div>

  <!-- Interactive DAG Execution Visualizer -->
  <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
    <div class="p-4 rounded-2xl bg-base-200/80 border border-primary/30 relative">
      <div class="flex items-center justify-between mb-2">
        <span class="badge badge-primary badge-xs font-bold">NODE 01</span>
        <span class="text-[10px] text-success font-bold">~180ms</span>
      </div>
      <p class="font-bold text-base-content font-sans">01_orchestrator_extraction</p>
      <p class="text-[11px] text-base-content/60 mt-1">Nebius AI (GLM-5.3-Flash) schema extraction.</p>
    </div>

    <div class="p-4 rounded-2xl bg-base-200/80 border border-accent/30 relative">
      <div class="flex items-center justify-between mb-2">
        <span class="badge badge-accent badge-xs font-bold">NODE 02</span>
        <span class="text-[10px] text-success font-bold">~610ms</span>
      </div>
      <p class="font-bold text-base-content font-sans">02_tavily_search_whitelist</p>
      <p class="text-[11px] text-base-content/60 mt-1">ASPCA, Merck, BSAVA verified domain search.</p>
    </div>

    <div class="p-4 rounded-2xl bg-base-200/80 border border-secondary/30 relative">
      <div class="flex items-center justify-between mb-2">
        <span class="badge badge-secondary badge-xs font-bold">NODE 03</span>
        <span class="text-[10px] text-success font-bold">~40ms</span>
      </div>
      <p class="font-bold text-base-content font-sans">03_clinical_synthesis</p>
      <p class="text-[11px] text-base-content/60 mt-1">Deterministic math engine (kg × mg/kg formula).</p>
    </div>
  </div>

  <!-- Artifact Content Viewer -->
  <div class="rounded-2xl bg-base-300/80 border border-base-content/10 p-4 font-mono text-xs overflow-x-auto max-h-72">
    {#if activeArtifact === 'json'}
      <pre class="text-primary font-mono">{sampleJsonArtifact}</pre>
    {:else}
      <pre class="text-base-content/90 font-mono whitespace-pre-wrap">{sampleMdArtifact}</pre>
    {/if}
  </div>
</div>
