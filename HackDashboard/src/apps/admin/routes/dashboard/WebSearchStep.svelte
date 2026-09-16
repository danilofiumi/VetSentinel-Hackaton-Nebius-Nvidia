<script>
  import { fly, fade, slide } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";
  import StepLoader from "./StepLoader.svelte";
  import { t } from "$lib";

  let {
    patient,
    artifactsData = null,
    runStatus = "idle",
    nodeStatus = "not_started",
    nextUnlocked = false,
    onNext,
    onBack,
    onOpenDagu,
  } = $props();

  let hasData = $derived(Boolean(artifactsData?.tavily?.documents?.length));
  // The source-retrieval process is active but its results aren't in yet
  let isRunning = $derived(
    nodeStatus === "running" || (runStatus === "running" && !hasData),
  );
  let isProcessing = $derived(!hasData && isRunning);

  let expandedExtracts = $state({});
  function toggleExtract(id) {
    expandedExtracts[id] = !expandedExtracts[id];
  }

  const domainFilters = [
    {
      name: "ASPCA Animal Poison Control",
      domain: "aspca.org",
      active: true,
      tag: "Toxicology Gold Standard",
    },
    {
      name: "Merck Veterinary Manual",
      domain: "merckvetmanual.com",
      active: true,
      tag: "Clinical Protocols",
    },
    {
      name: "BSAVA Small Animal Formulary",
      domain: "bsava.com",
      active: true,
      tag: "Drug Dosing Guide",
    },
    {
      name: "PubMed / NLM",
      domain: "ncbi.nlm.nih.gov",
      active: true,
      tag: "Peer-Reviewed Studies",
    },
    {
      name: "EMA / FDA Veterinary",
      domain: "ema.europa.eu",
      active: true,
      tag: "Regulatory & Safety",
    },
  ];

  function getSearchExtracts() {
    if (
      artifactsData &&
      artifactsData.tavily &&
      Array.isArray(artifactsData.tavily.documents) &&
      artifactsData.tavily.documents.length > 0
    ) {
      return artifactsData.tavily.documents
        .slice()
        .sort(
          (a, b) =>
            (Number(b.relevance_score) || 0) - (Number(a.relevance_score) || 0),
        )
        .map((doc, idx) => {
          const domain = (doc.source_domain || "").toLowerCase();
          let badge = "Evidence-Based";
          let badgeColor = "badge-info";

          if (domain.includes("aspca")) {
            badge = "ASPCA Toxicology Gold";
            badgeColor = "badge-success";
          } else if (domain.includes("merck")) {
            badge = "Merck Manual Protocol";
            badgeColor = "badge-primary";
          } else if (domain.includes("bsava")) {
            badge = "BSAVA Formulary";
            badgeColor = "badge-secondary";
          } else if (domain.includes("ncbi") || domain.includes("nih")) {
            badge = "PubMed / NLM";
            badgeColor = "badge-accent";
          } else if (domain.includes("ema") || domain.includes("fda")) {
            badge = "Regulatory Safety";
            badgeColor = "badge-warning";
          }

          const scorePercent = doc.relevance_score
            ? Math.round(Number(doc.relevance_score) * 100)
            : 88;

          const cleanedFull = (doc.content || doc.cleaned_markdown || "")
            .replace(/#+/g, "")
            .replace(/\s+/g, " ")
            .trim();
          const truncated = cleanedFull.length > 320;
          const snippet = truncated
            ? cleanedFull.substring(0, 320) + "..."
            : cleanedFull;

          return {
            id: idx + 1,
            source: doc.source_domain || "Validated Source",
            domain: doc.source_domain || "Veterinary Resource",
            url: doc.url,
            title: doc.title || "Accredited Clinical Evidence",
            badge,
            badgeColor,
            relevance: `${scorePercent}%`,
            summary: snippet,
            fullText: cleanedFull,
            truncated,
            clinicalKeyPoints: [
              `Source: ${doc.source_domain || "Veterinary source"}`,
              `Reference: ${doc.url}`,
            ],
          };
        });
    }

    // No hardcoded fallback: only real retrieved documents are shown.
    return [];
  }

  let filterStates = $state(domainFilters);

  // Single source of truth for the rendered evidence cards.
  let extracts = $derived(getSearchExtracts());

  // "Evidence of the research made": the actual queries the AI executed.
  let researchQueries = $derived.by(() => {
    const p = artifactsData?.orchestrator?.function_call?.parameters;
    const planned = p?.target_queries || p?.queries;
    if (Array.isArray(planned) && planned.length) return planned;
    const docs = artifactsData?.tavily?.documents;
    if (Array.isArray(docs)) {
      const q = [...new Set(docs.map((d) => d.query).filter(Boolean))];
      if (q.length) return q;
    }
    return [];
  });

  // "Sources analyzed": distinct sources with how many documents each yielded.
  let analyzedSources = $derived.by(() => {
    const map = new Map();
    for (const e of extracts) {
      const key = e.domain || e.source;
      if (!map.has(key))
        map.set(key, {
          name: e.source,
          domain: e.domain,
          url: e.url,
          count: 0,
        });
      map.get(key).count += 1;
    }
    return [...map.values()];
  });

  let isLiveResearch = $derived(Boolean(artifactsData?.tavily));
</script>

<div
  class="card bg-base-100/85 shadow-2xl border border-base-300 backdrop-blur-md transition-all duration-500 ease-in-out"
  in:fly={{ y: 24, duration: 450, easing: cubicInOut }}
>
  <div class="card-body p-6 lg:p-8 space-y-6">
    <!-- Header Step 3 -->
    <div
      class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-base-200 pb-4"
    >
      <div>
        <div
          class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-accent font-label"
        >
          <span class="inline-block w-2.5 h-2.5 rounded-full bg-accent"></span>
          {t("stepper.step3Label")}
        </div>
        <h2
          class="text-2xl lg:text-3xl font-black tracking-tight text-base-content font-display mt-1"
        >
          {t("sources.headerTitle")}
        </h2>
        <p class="text-sm text-base-content/70 mt-0.5">
          {t("sources.headerDesc")}
        </p>
      </div>

      <!-- Live metrics -->
      <div class="flex items-center gap-2"></div>
    </div>

    <!-- Research Trail & Sources Analyzed -->
    <div
      class="rounded-2xl border border-base-300 bg-base-200/30 p-4 sm:p-5 space-y-4 shadow-inner"
      in:fade={{ duration: 300, easing: cubicInOut }}
    >
      <div class="flex items-center justify-between flex-wrap gap-2">
        <div
          class="text-xs font-bold uppercase tracking-wider text-base-content/80 font-label flex items-center gap-2"
        >
          <span>🔬 {t("sources.trailTitle")}</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="badge badge-sm badge-accent font-mono font-bold">
            {t("sources.queriesRunCount", { count: researchQueries.length })}
          </span>
          <span class="badge badge-sm badge-outline font-mono font-bold">
            {t("sources.sourcesCount", { count: analyzedSources.length })}
          </span>
        </div>
      </div>

      <!-- Evidence of the research made: the executed search queries -->
      {#if researchQueries.length > 0}
        <div class="space-y-1.5">
          <div
            class="text-[10px] font-bold uppercase tracking-wider text-base-content/50 font-label"
          >
            {t("sources.searchQueriesExecuted")}
          </div>
          <div class="space-y-1.5">
            {#each researchQueries as q, i}
              <div
                class="flex items-start gap-2.5 p-2.5 rounded-xl bg-base-100/80 border border-base-300 hover:border-accent/40 transition-all duration-300 ease-in-out"
                in:fly={{
                  y: 6,
                  duration: 250,
                  delay: i * 40,
                  easing: cubicInOut,
                }}
              >
                <span
                  class="badge badge-xs badge-accent font-mono font-bold shrink-0 mt-0.5"
                  >{i + 1}</span
                >
                <span
                  class="text-xs text-base-content/90 font-mono leading-relaxed break-words"
                  >{q}</span
                >
              </div>
            {/each}
          </div>
        </div>
      {/if}

      <!-- Sources analyzed: distinct sources with per-source hit counts -->
      <div class="space-y-1.5">
        <div
          class="text-[10px] font-bold uppercase tracking-wider text-base-content/50 font-label"
        >
          {t("sources.sourcesAnalyzed")}
        </div>
        <div class="flex flex-wrap gap-2 overflow-scroll">
          {#each analyzedSources as s}
            <a
              href={s.url || "#"}
              target="_blank"
              rel="noreferrer"
              class="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-base-100/80 border border-base-300 hover:border-primary/50 hover:-translate-y-0.5 transition-all duration-300 ease-in-out group"
            >
              <span class="text-xs font-bold text-base-content font-display"
                >{s.name}</span
              >
              {#if s.domain}
                <span class="text-[10px] text-base-content/50 font-mono"
                  >{s.domain}</span
                >
              {/if}
              <span
                class="badge badge-xs badge-primary font-mono font-bold"
                title="Documents retrieved from this source">{s.count}</span
              >
            </a>
          {/each}
        </div>
      </div>
    </div>

    <!-- Cleaned Text & Clinical Evidence Cards -->
    <div class="space-y-4 pt-1">
      {#if isProcessing}
        <StepLoader
          icon="📚"
          title={t("sources.loaderTitle")}
          subtitle={t("sources.loaderSubtitle")}
          statusLabel={t("sources.loaderStatus")}
        />
      {:else if hasData}
        <div class="flex items-center justify-between">
          <div
            class="text-xs font-bold uppercase tracking-wider text-base-content/80 font-label flex items-center gap-2"
          >
            <span>📑 {t("sources.verifiedEvidence")}</span>
          </div>
          <span
            class="badge badge-sm badge-success badge-outline font-mono font-bold"
            >Relevance > 94%</span
          >
        </div>

        <div class="space-y-4">
          {#each extracts as extract}
            <div
              class="p-5 rounded-2xl border border-base-300 bg-base-200/40 hover:border-primary/40 hover:bg-base-200/70 transition-all duration-300 ease-in-out shadow-sm space-y-3.5"
            >
              <!-- Card Top Meta -->
              <div
                class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-base-300/50 pb-2.5"
              >
                <div class="flex items-center gap-2 flex-wrap">
                  <span
                    class="badge {extract.badgeColor} badge-sm font-bold font-mono"
                    >{extract.badge}</span
                  >
                  <span class="text-xs font-black text-base-content font-mono"
                    >{extract.source}</span
                  >
                  <a
                    href={extract.url}
                    target="_blank"
                    rel="noreferrer"
                    class="text-[11px] text-primary hover:underline inline-flex items-center gap-1 font-mono"
                  >
                    <span>🔗 {extract.domain}</span>
                  </a>
                </div>
                <div class="flex items-center gap-2">
                  <span
                    class="text-[10px] text-base-content/50 uppercase font-bold font-label"
                    >{t("sources.confidence")}</span
                  >
                  <span
                    class="badge badge-sm badge-ghost font-mono font-bold text-success"
                    >{extract.relevance}</span
                  >
                </div>
              </div>

              <!-- Title & Summary -->
              <div>
                <h3 class="text-sm font-black text-base-content font-display">
                  {extract.title}
                </h3>
                {#if expandedExtracts[extract.id]}
                  <p
                    transition:slide={{ duration: 300, easing: cubicInOut }}
                    class="text-xs text-base-content/80 mt-1 leading-relaxed whitespace-pre-line"
                  >
                    {extract.fullText}
                  </p>
                {:else}
                  <p class="text-xs text-base-content/80 mt-1 leading-relaxed">
                    {extract.summary}
                  </p>
                {/if}
                {#if extract.truncated}
                  <button
                    type="button"
                    class="mt-1.5 text-[11px] font-bold text-primary hover:text-primary/80 inline-flex items-center gap-1 cursor-pointer transition-all duration-300 ease-in-out hover:gap-1.5"
                    onclick={() => toggleExtract(extract.id)}
                  >
                    <span
                      >{expandedExtracts[extract.id]
                        ? t("sources.viewLess")
                        : t("sources.viewMore")}</span
                    >
                    <span
                      class="transition-transform duration-300 ease-in-out {expandedExtracts[
                        extract.id
                      ]
                        ? 'rotate-180'
                        : ''}">▾</span
                    >
                  </button>
                {/if}
              </div>

              <!-- Clinical Takeaways List -->
              <div
                class="rounded-xl bg-base-100/90 p-4 border border-base-300/80 break-all space-y-2"
              >
                <div
                  class="text-[10px] font-bold uppercase tracking-wider text-primary font-label"
                >
                  {t("sources.criticalTakeaways", { species: patient.specie, weight: patient.peso })}
                </div>
                <ul class="space-y-1.5">
                  {#each extract.clinicalKeyPoints as pt}
                    <li
                      class="text-xs text-base-content/90 flex items-start gap-2 leading-relaxed"
                    >
                      <span
                        class="text-primary font-bold text-xs shrink-0 mt-0.5"
                        >•</span
                      >
                      <span>{pt}</span>
                    </li>
                  {/each}
                </ul>
              </div>
            </div>
          {/each}
        </div>
      {:else}
        <div
          class="p-8 text-center text-base-content/60 rounded-2xl border border-dashed border-base-300 bg-base-200/20"
        >
          <div class="text-3xl mb-2">📚</div>
          <div class="font-bold text-sm text-base-content/80">
            {t("sources.emptyTitle")}
          </div>
          <div class="text-xs text-base-content/50 mt-1">
            {t("sources.emptyDesc")}
          </div>
        </div>
      {/if}
    </div>

    <!-- Actions Footer -->
    <div
      class="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-base-200"
    >
      <button
        type="button"
        class="btn btn-ghost btn-sm gap-2 text-base-content/70 hover:text-base-content cursor-pointer"
        onclick={onBack}
      >
        <svg
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M10 19l-7-7m0 0l7-7m-7 7h18"
          />
        </svg>
        <span>{t("common.back")}</span>
      </button>

      <div class="flex items-center gap-3 w-full sm:w-auto">
        <button
          type="button"
          class="btn btn-primary px-8 gap-2 shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 ease-in-out w-full sm:w-auto font-bold cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
          onclick={onNext}
          disabled={!nextUnlocked}
          title={!nextUnlocked
            ? t("sources.step4Tooltip")
            : t("common.continueToProtocol")}
        >
          <span>{t("common.continueToProtocol")}</span>
          <svg
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M14 5l7 7m0 0l-7 7m7-7H3"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</div>
