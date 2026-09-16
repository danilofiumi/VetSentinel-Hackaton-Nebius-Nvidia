<script>
  import { onMount, onDestroy } from "svelte";
  import { fly, fade, slide } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";
  // Eagerly loaded — needed on first paint
  import DashboardTopStepper from "./DashboardTopStepper.svelte";
  import DaguRunLoader from "./DaguRunLoader.svelte";
  import TriageInputStep from "./TriageInputStep.svelte";
  import {
    fetchAllArtifacts,
    fetchArtifactByName,
    fetchLatestDagRun,
    startDaguPipeline,
    stopDaguPipeline,
    fetchDagRunStatus,
    fetchNodeLog,
  } from "./daguService.js";
  import { i18nState, t } from "$lib";

  // Lazy-loaded — not visible on initial render, loaded on demand
  let ClinicalAssessmentStep = $state(null);
  let WebSearchStep = $state(null);
  let ClinicalSynthesisStep = $state(null);
  let EmergencySheetViewer = $state(null);
  let ClinicalChatWidget = $state(null);
  let SectionPullSwipeTransitionv2 = $state(null);

  // Patient Intake State
  let patient = $state({
    specie: "Cat",
    razza: "European Shorthair",
    peso: 4.0,
    priorita: "",
    sintomi: "",
  });

  let orchestratorState = $state({
    model: "zai-org/GLM-5.3-Flash",
  });

  // Navigation State: 'triage' | 'orchestrator' | 'sources' | 'synthesis' | 'sheet'
  let currentSection = $state("triage");

  // Pipeline & Artifacts State (Starts Fresh: NO previous analysis active on fresh open!)
  let artifactsData = $state(null);
  let latestDagRun = $state(null);
  let runStatus = $state("idle"); // 'idle' | 'running' | 'succeeded' | 'failed'
  let runId = $state("");
  let stepNodes = $state([]);
  let errorMessage = $state("");
  let logsText = $state("");
  let elapsedSeconds = $state(0);
  let pollTimer = null;
  let elapsedTimer = null;

  // Real-Time Right-Margin Copilot Drawer State
  let isCopilotOpen = $state(false);
  let chatResetTrigger = $state(0);
  let chatWidgetRef = $state(null);

  // Mobile DAG Run Loader Drawer State
  let isMobileRunDrawerOpen = $state(false);

  let isAnalysisComplete = $derived(
    runStatus === "succeeded" && artifactsData !== null,
  );

  const defaultStepDefs = [
    {
      id: "setup_environment",
      name: "1. Intake Preparation",
      icon: "⚙️",
    },
    {
      id: "nebius_orchestrator",
      name: "2. Case Triage & Search Planning",
      icon: "🩺",
    },
    {
      id: "tavily_web_search",
      name: "3. Scientific Sources",
      icon: "📚",
    },
    {
      id: "clinical_synthesis",
      name: "4. Protocol & Dosages",
      icon: "🧬",
    },
    {
      id: "export_summary",
      name: "5. Emergency Sheet",
      icon: "📋",
    },
  ];

  // Load remaining step components on demand when their section becomes active
  $effect(() => {
    if (currentSection === "sources" && !WebSearchStep) {
      import("./WebSearchStep.svelte").then((m) => (WebSearchStep = m.default));
    }
    if (currentSection === "synthesis" && !ClinicalSynthesisStep) {
      import("./ClinicalSynthesisStep.svelte").then((m) => (ClinicalSynthesisStep = m.default));
    }
    if (currentSection === "sheet" && !EmergencySheetViewer) {
      import("./EmergencySheetViewer.svelte").then((m) => (EmergencySheetViewer = m.default));
    }
  });

  // Preload next-needed components + init DAG ping on mount
  onMount(async () => {
    // Start loading the copilot widget + step 2 immediately in the background (idle time)
    import("./ClinicalChatWidget.svelte").then((m) => (ClinicalChatWidget = m.default));
    import("./ClinicalAssessmentStep.svelte").then((m) => (ClinicalAssessmentStep = m.default));

    // Background DAG server connectivity check — fire-and-forget, never blocks rendering
    fetchLatestDagRun()
      .then((run) => {
        if (run) latestDagRun = run;
      })
      .catch((e) => console.warn("DAG status ping failed:", e));

    if (typeof window !== "undefined") {
      const sp = new URLSearchParams(window.location.search);
      const sec = sp.get("section");
      if (
        sec &&
        ["triage", "orchestrator", "sources", "synthesis", "sheet"].includes(
          sec,
        )
      ) {
        // Set section immediately for instant visual feedback
        currentSection = sec;
        try {
          const artifacts = await fetchAllArtifacts();
          if (artifacts) {
            artifactsData = artifacts;
            runStatus = "succeeded";
          }
        } catch (e) {
          console.warn("Artifacts load failed:", e);
        }
      }
    }
  });

  onDestroy(() => {
    if (pollTimer) clearInterval(pollTimer);
    if (elapsedTimer) clearInterval(elapsedTimer);
  });

  // Map each wizard section to its DAG node
  const sectionDag = {
    triage: "setup_environment",
    orchestrator: "nebius_orchestrator",
    sources: "tavily_web_search",
    synthesis: "clinical_synthesis",
    sheet: "export_summary",
  };

  function nodeStatusOf(dagId) {
    const n = (stepNodes || []).find((x) => x.id === dagId || x.name === dagId);
    return n && n.statusLabel ? n.statusLabel : "not_started";
  }

  // A step unlocks only once its own process has started (running/succeeded).
  // This keeps every step after the LLM triage locked until the LLM finishes.
  function isSectionUnlocked(sectionId) {
    if (sectionId === "triage") return true;
    if (runStatus === "succeeded" && artifactsData) return true;
    // The LLM-triage step is unlocked for the whole duration of the run
    if (sectionId === "orchestrator" && runStatus === "running") return true;
    const st = nodeStatusOf(sectionDag[sectionId]);
    if (st === "running" || st === "succeeded") return true;
    // Data already present (e.g. early load or deep-link)
    if (sectionId === "orchestrator" && artifactsData?.orchestrator)
      return true;
    if (sectionId === "sources" && artifactsData?.tavily) return true;
    if (sectionId === "synthesis" && artifactsData?.synthesis) return true;
    if (sectionId === "sheet" && artifactsData?.sheetMd) return true;
    return false;
  }

  // Section sequence in dashboard
  const sectionSequence = [
    "triage",
    "orchestrator",
    "sources",
    "synthesis",
    "sheet",
  ];

  function getNextSection(sectionKey) {
    const idx = sectionSequence.indexOf(sectionKey);
    if (idx !== -1 && idx < sectionSequence.length - 1) {
      return sectionSequence[idx + 1];
    }
    return null;
  }

  function getPreviousSection(sectionKey) {
    const idx = sectionSequence.indexOf(sectionKey);
    if (idx > 0) {
      return sectionSequence[idx - 1];
    }
    return null;
  }

  function goToSection(sectionKey) {
    if (!isSectionUnlocked(sectionKey)) return; // locked until its process starts
    currentSection = sectionKey;
    if (typeof window !== "undefined") {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }

  function scrollToIntake() {
    currentSection = "triage";
    if (typeof window !== "undefined") {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }

  async function triggerAnalysis(force = false) {
    if (runStatus === "running" && !force) return;

    if (runStatus === "running") {
      // Gracefully stop active prior run first before restarting
      if (pollTimer) clearInterval(pollTimer);
      if (elapsedTimer) clearInterval(elapsedTimer);
      try {
        await stopDaguPipeline(runId);
      } catch (e) {}
    }

    runStatus = "running";
    errorMessage = "";
    elapsedSeconds = 0;
    // Clear any previous run so Step 2 shows THIS analysis live, never stale gaps
    artifactsData = null;
    logsText = `[${new Date().toLocaleTimeString()}] Initiating VetSentinel Dagu Emergency Pipeline...\n`;

    // Initialize step nodes with waiting states
    stepNodes = defaultStepDefs.map((def) => ({
      id: def.id,
      name: def.name,
      icon: def.icon,
      statusLabel: def.id === "setup_environment" ? "running" : "not_started",
      stdout: "",
    }));

    // Immediately advance to Step 2: Clinical Assessment screen while pipeline runs
    goToSection("orchestrator");

    if (elapsedTimer) clearInterval(elapsedTimer);
    elapsedTimer = setInterval(() => {
      elapsedSeconds += 5;
    }, 5000);

    try {
      runId = await startDaguPipeline(patient, i18nState.locale);
      logsText += `[${new Date().toLocaleTimeString()}] DAG Run initiated with ID: ${runId}\n`;
      logsText += `[Patient Vitals] Species: ${patient.specie} | Breed: ${patient.razza} | Weight: ${patient.peso} kg | Priority: AI Evaluated on Run\n\n`;
      startPolling(runId);
    } catch (err) {
      runStatus = "failed";
      errorMessage = err.message || "Unable to start the clinical analysis.";
      logsText += `[ERROR] ${errorMessage}\n`;
      if (elapsedTimer) clearInterval(elapsedTimer);
    }
  }

  async function stopAnalysis() {
    if (pollTimer) clearInterval(pollTimer);
    if (elapsedTimer) clearInterval(elapsedTimer);
    runStatus = "idle";
    logsText += `\n[${new Date().toLocaleTimeString()}] ⏹ Clinical analysis stopped by user.\n`;
    try {
      await stopDaguPipeline(runId);
    } catch (err) {
      console.error("Failed to stop analysis:", err);
    }
  }

  async function stopAndRetrigger() {
    await triggerAnalysis(true);
  }

  function startPolling(id) {
    if (pollTimer) clearInterval(pollTimer);

    const earlyLoaded = {};
    // Each pipeline node's artifact is mirrored to the central folder the moment
    // that node finishes, so we can load it live without waiting for the whole run.
    const earlyArtifacts = [
      {
        dagId: "nebius_orchestrator",
        file: "01_orchestrator_result.json",
        key: "orchestrator",
        valid: (d) => d && Array.isArray(d.clinical_gaps),
      },
      {
        dagId: "tavily_web_search",
        file: "02_tavily_search_result.json",
        key: "tavily",
        valid: (d) => d && Array.isArray(d.documents),
      },
      {
        dagId: "clinical_synthesis",
        file: "03_clinical_synthesis.json",
        key: "synthesis",
        valid: (d) => d && typeof d === "object" && !d.error,
      },
    ];
    pollTimer = setInterval(async () => {
      try {
        const dagRun = await fetchDagRunStatus(id);
        if (!dagRun) return;

        // Update step nodes
        if (dagRun.nodes && dagRun.nodes.length > 0) {
          stepNodes = dagRun.nodes.map((n, idx) => {
            const stepKey = n.step.id || n.step.name || "";
            const def = defaultStepDefs.find(
              (d) => d.id === stepKey || d.name === stepKey,
            ) || {
              name: n.step.name || `Step ${idx + 1}`,
              icon: "📌",
            };
            return {
              id: stepKey,
              name: def.name || n.step.name,
              icon: def.icon,
              statusLabel: n.statusLabel || "not_started",
              stdout: n.stdout || "",
              startedAt: n.startedAt,
              finishedAt: n.finishedAt,
            };
          });

          // Fetch active node logs for real-time streaming
          const activeOrRecentNode =
            dagRun.nodes.find((n) => n.statusLabel === "running") ||
            dagRun.nodes
              .slice()
              .reverse()
              .find((n) => n.statusLabel === "succeeded" && n.stdout);

          if (activeOrRecentNode && activeOrRecentNode.stdout) {
            const nodeLog = await fetchNodeLog(activeOrRecentNode.stdout);
            if (nodeLog && nodeLog.trim()) {
              logsText = nodeLog;
            }
          }

          // As each node finishes, load its artifact so that step's data appears live —
          // without waiting for the rest of the pipeline to complete.
          for (const art of earlyArtifacts) {
            if (earlyLoaded[art.key]) continue;
            const node = dagRun.nodes.find(
              (n) =>
                (n.step.id || n.step.name) === art.dagId &&
                n.statusLabel === "succeeded",
            );
            if (!node) continue;
            try {
              const data = await fetchArtifactByName(art.file);
              if (art.valid(data)) {
                earlyLoaded[art.key] = true;
                const patch = { [art.key]: data };
                // The emergency sheet is produced by the synthesis step too
                if (art.key === "synthesis") {
                  try {
                    const md = await fetchArtifactByName(
                      "final_clinical_emergency_sheet.md",
                    );
                    if (md) patch.sheetMd = md;
                  } catch (e) {
                    console.warn("Early sheet load failed:", e);
                  }
                }
                // Only update if a new key was actually added (avoids unnecessary reactive cascades)
                const prev = artifactsData || {};
                const hasNew = Object.keys(patch).some((k) => !prev[k]);
                if (hasNew) {
                  artifactsData = { ...prev, ...patch };
                }
              }
            } catch (e) {
              console.warn(`Early load failed for ${art.key}:`, e);
            }
          }
        }

        // Check if finished
        if (dagRun.status === 4 || dagRun.statusLabel === "succeeded") {
          clearInterval(pollTimer);
          if (elapsedTimer) clearInterval(elapsedTimer);
          runStatus = "succeeded";

          logsText += `\n[${new Date().toLocaleTimeString()}] ✓ Pipeline completed successfully in ${elapsedSeconds}s!\nLoading verified clinical artifacts...\n`;

          // Fetch real artifacts
          try {
            const artifacts = await fetchAllArtifacts();
            artifactsData = artifacts;

            // Sync patient if present in normalized artifact
            if (artifacts.orchestrator && artifacts.orchestrator.patient) {
              const p = artifacts.orchestrator.patient;
              patient.specie = p.species || patient.specie;
              patient.razza = p.breed || patient.razza;
              patient.peso = Number(p.weight_kg) || patient.peso;
              patient.priorita = p.priority || patient.priorita;
            }

            // NOTE: intentionally NO navigation here — the user stays on whatever
            // step they are viewing when the pipeline completes.
          } catch (e) {
            console.error("Failed to load artifacts:", e);
          }
        } else if (dagRun.status === 5 || dagRun.statusLabel === "failed") {
          clearInterval(pollTimer);
          if (elapsedTimer) clearInterval(elapsedTimer);
          runStatus = "failed";
          errorMessage =
            "The clinical analysis did not complete successfully. Please review logs.";
          logsText += `\n[${new Date().toLocaleTimeString()}] ✕ Pipeline failed. See engine logs for details.\n`;
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 2000);
  }

  function handleReset() {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
    if (elapsedTimer) {
      clearInterval(elapsedTimer);
      elapsedTimer = null;
    }
    elapsedSeconds = 0;

    patient = {
      specie: "Cat",
      razza: "European Shorthair",
      peso: 4.0,
      priorita: "",
      sintomi: "",
    };
    runStatus = "idle";
    artifactsData = null;
    latestDagRun = null;
    runId = "";
    stepNodes = [];
    logsText = "";
    errorMessage = "";

    isCopilotOpen = false;
    chatResetTrigger++;
    if (chatWidgetRef && typeof chatWidgetRef.resetChat === "function") {
      chatWidgetRef.resetChat();
    }

    goToSection("triage");

    if (typeof window !== "undefined" && window.location.search) {
      window.history.replaceState({}, "", window.location.pathname);
    }
  }

  async function loadSpecificDagRun(targetRunId) {
    if (!targetRunId || !targetRunId.trim()) return;
    const cleanId = targetRunId.trim();

    if (pollTimer) clearInterval(pollTimer);
    if (elapsedTimer) clearInterval(elapsedTimer);

    // 1. Fetch DAG Run metadata & status from Dagu
    let dagRun = null;
    try {
      dagRun = await fetchDagRunStatus(cleanId);
      if (dagRun) {
        runId = cleanId;
        latestDagRun = dagRun;
        runStatus =
          dagRun.statusLabel === "succeeded" || dagRun.status === 4
            ? "succeeded"
            : dagRun.statusLabel === "failed" || dagRun.status === 5
              ? "failed"
              : "running";

        // Update step nodes for sidebar stepper
        if (dagRun.nodes && dagRun.nodes.length > 0) {
          stepNodes = dagRun.nodes.map((n, idx) => {
            const stepKey = n.step.id || n.step.name || "";
            const def = defaultStepDefs.find(
              (d) => d.id === stepKey || d.name === stepKey,
            ) || {
              name: n.step.name || `Step ${idx + 1}`,
              icon: "📌",
            };
            return {
              id: stepKey,
              name: def.name || n.step.name,
              icon: def.icon,
              statusLabel: n.statusLabel || "not_started",
              stdout: n.stdout || "",
              startedAt: n.startedAt,
              finishedAt: n.finishedAt,
            };
          });

          // Fetch active or last stdout log
          const lastLogNode =
            dagRun.nodes.find((n) => n.statusLabel === "running") ||
            dagRun.nodes
              .slice()
              .reverse()
              .find((n) => n.stdout);
          if (lastLogNode && lastLogNode.stdout) {
            try {
              const nodeLog = await fetchNodeLog(lastLogNode.stdout);
              if (nodeLog && nodeLog.trim()) logsText = nodeLog;
            } catch (e) {}
          }
        }

        // Parse patient from DAG params if present
        if (dagRun.params) {
          const mSpecies = dagRun.params.match(/SPECIES="([^"]+)"/i);
          const mBreed = dagRun.params.match(/BREED="([^"]+)"/i);
          const mWeight = dagRun.params.match(/WEIGHT="([^"]+)"/i);
          const mPriority = dagRun.params.match(/PRIORITY="([^"]+)"/i);
          const mSymptoms = dagRun.params.match(/SYMPTOMS="([^"]+)"/i);
          if (mSpecies) patient.specie = mSpecies[1];
          if (mBreed) patient.razza = mBreed[1];
          if (mWeight) patient.peso = Number(mWeight[1]) || patient.peso;
          if (mPriority) patient.priorita = mPriority[1];
          if (mSymptoms) patient.sintomi = mSymptoms[1];
        }
      }
    } catch (e) {
      console.warn(
        "Could not fetch DAG run status from Dagu, falling back to artifacts:",
        e,
      );
    }

    // 2. Fetch all artifacts for this specific run ID from /api/artifacts?run_id=...
    try {
      const artifacts = await fetchAllArtifacts(cleanId);
      if (artifacts) {
        artifactsData = artifacts;
        runId = cleanId;
        if (runStatus === "idle") {
          runStatus = "succeeded";
        }

        // Sync patient if present in orchestrator artifact
        if (artifacts.orchestrator && artifacts.orchestrator.patient) {
          const p = artifacts.orchestrator.patient;
          patient.specie = p.species || patient.specie;
          patient.razza = p.breed || patient.razza;
          patient.peso = Number(p.weight_kg) || patient.peso;
          patient.priorita = p.priority || patient.priorita;
        }

        // Take the user to Step 2 (orchestrator) so the loaded run data is immediately viewed
        if (currentSection === "triage") {
          goToSection("orchestrator");
        }
      }
    } catch (e) {
      console.error("Failed to load artifacts for run ID:", e);
      throw e;
    }

    // 3. If the run is still active in Dagu, resume polling
    if (runStatus === "running") {
      startPolling(cleanId);
    }
  }

  const nextSectionMeta = $derived.by(() => {
    const next = getNextSection(currentSection);
    if (!next) return null;
    const isUnlocked = isSectionUnlocked(next);
    const names = {
      orchestrator: {
        name: "Case Triage & Search Planning",
        icon: "🩺",
        step: "Step 2",
      },
      sources: { name: "Scientific Sources", icon: "📚", step: "Step 3" },
      synthesis: { name: "Protocol & Dosages", icon: "🧬", step: "Step 4" },
      sheet: { name: "Emergency Sheet", icon: "📋", step: "Step 5" },
    };
    return {
      id: next,
      isUnlocked,
      ...(names[next] || { name: next, icon: "➡️", step: "" }),
    };
  });

  const prevSectionMeta = $derived.by(() => {
    const prev = getPreviousSection(currentSection);
    if (!prev) return null;
    const isUnlocked = isSectionUnlocked(prev);
    const names = {
      triage: { name: t("stepper.intake"), icon: "📋", step: "Step 1" },
      orchestrator: {
        name: t("stepper.orchestrator"),
        icon: "🩺",
        step: "Step 2",
      },
      sources: { name: t("stepper.sources"), icon: "📚", step: "Step 3" },
      synthesis: { name: t("stepper.synthesis"), icon: "🧬", step: "Step 4" },
      sheet: { name: t("stepper.sheet"), icon: "📋", step: "Step 5" },
    };
    return {
      id: prev,
      isUnlocked,
      ...(names[prev] || { name: prev, icon: "⬅️", step: "" }),
    };
  });
</script>

<div
  class="container mx-auto pr-3 pl-2 sm:pr-4 py-6 !max-w-full transition-all duration-300 ease-in-out {isCopilotOpen
    ? 'lg:pr-[395px] xl:pr-[445px]'
    : 'lg:pr-8'}"
>
  <div class="flex flex-col lg:flex-row items-start gap-2">
    <!-- LEFT SIDEBAR: Always visible on desktop with sticky positioning -->
    <aside
      class="w-full lg:w-72 xl:w-80 shrink-0 sticky top-20 z-30 max-h-[calc(100vh-6rem)] overflow-y-auto space-y-3"
    >
      <DashboardTopStepper
        {currentSection}
        {isAnalysisComplete}
        isAnalysisRunning={runStatus === "running"}
        {runStatus}
        {runId}
        {elapsedSeconds}
        {stepNodes}
        {artifactsData}
        {logsText}
        {errorMessage}
        onNavigate={goToSection}
        onPromptTrigger={scrollToIntake}
        onRerun={triggerAnalysis}
        onOpenRunLoader={() => (isMobileRunDrawerOpen = true)}
      />

      <!-- Desktop Sidebar Run Loader: Visible on desktop (lg+) -->
      <div class="hidden lg:block">
        <DaguRunLoader
          currentRunId={runId}
          onLoadRun={loadSpecificDagRun}
          onReset={handleReset}
        />
      </div>

      <!-- Mobile Run Manager Trigger: Compact pill to save space on mobile (< lg) -->
      <div class="lg:hidden">
        <button
          type="button"
          class="w-full flex items-center justify-between p-2 rounded-xl bg-base-100/90 border border-base-300 shadow-xs hover:border-primary/40 hover:bg-base-200/50 transition-all duration-200 ease-in-out cursor-pointer text-left"
          onclick={() => (isMobileRunDrawerOpen = true)}
        >
          <div class="flex items-center gap-2 min-w-0">
            <div
              class="w-6 h-6 rounded-lg bg-primary/10 text-primary flex items-center justify-center text-xs shrink-0 border border-primary/20"
            >
              🔎
            </div>
            <div class="min-w-0">
              <div
                class="text-[11px] font-black text-base-content font-display tracking-tight truncate flex items-center gap-1.5"
              >
                <span>{t("daguLoader.managerTitle")}</span>
                {#if runId}
                  <span
                    class="badge badge-xs font-mono badge-ghost text-[9px] truncate max-w-[90px]"
                  >
                    {runId.slice(0, 8)}…
                  </span>
                {/if}
              </div>
              <p class="text-[9px] text-base-content/50 font-mono truncate">
                {t("daguLoader.managerSubtitle")}
              </p>
            </div>
          </div>
          <span
            class="badge badge-xs badge-primary/15 text-primary font-mono text-[9px] font-bold shrink-0 ml-1"
          >
            {t("daguLoader.openBtn")}
          </span>
        </button>
      </div>
    </aside>

    <!-- MAIN CLINICAL CONTENT AREA -->
    <div class="flex-1 min-w-0 w-full space-y-2">
      <!-- Patient Vitals Sticky Quick Bar (Shown on Steps 2 to 5 for constant clinical context) -->
      {#if currentSection !== "triage"}
        <div
          class="flex flex-wrap items-center justify-between gap-3 p-3 rounded-2xl bg-base-100/95 border border-primary/20 backdrop-blur-md shadow-sm transition-all duration-300"
          in:fly={{ y: -8, duration: 150, easing: cubicInOut }}
        >
          <div class="flex items-center gap-3">
            <div
              class="w-8 h-8 rounded-xl bg-primary/10 text-primary flex items-center justify-center font-bold text-base"
            >
              {#if patient.specie === "Cat"}
                🐱
              {:else if patient.specie === "Dog"}
                🐶
              {:else if patient.specie === "Rabbit"}
                🐰
              {:else if patient.specie === "Ferret"}
                🦡
              {:else if patient.specie === "Horse"}
                🐴
              {:else}
                🦎
              {/if}
            </div>

            <div class="text-xs">
              <div class="flex items-center gap-2">
                <span class="font-black text-base-content font-display">
                  {patient.specie} ({patient.razza || "Mixed"})
                </span>
                <span class="badge badge-xs font-mono font-bold badge-outline">
                  {patient.peso} kg
                </span>
                {#if patient.priorita}
                  <span
                    class="badge badge-xs font-mono font-bold uppercase {patient.priorita ===
                    'critical'
                      ? 'badge-error text-white'
                      : patient.priorita === 'urgent'
                        ? 'badge-warning'
                        : 'badge-success text-white'}"
                  >
                    {t("common.aiTriagePrefix")} {patient.priorita}
                  </span>
                {:else}
                  <span
                    class="badge badge-xs font-mono font-bold text-[9px] badge-outline text-primary border-primary/40 gap-1"
                  >
                    <span
                      class="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"
                    ></span>
                    {t("common.triagePending")}
                  </span>
                {/if}
              </div>
              <p
                class="text-[11px] text-base-content/60 text-wrap max-w-xl truncate mt-0.5"
              >
                {patient.sintomi}
              </p>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button
              type="button"
              class="btn btn-ghost btn-xs gap-1 font-mono text-[11px] cursor-pointer"
              onclick={() => goToSection("triage")}
              title="Return to Step 1 to edit patient intake"
            >
              <span>✏️</span>
              <span>{t("common.editIntake")}</span>
            </button>

            <button
              type="button"
              class="btn btn-primary btn-xs gap-1 font-bold shadow-xs cursor-pointer hover:scale-105 transition-all"
              onclick={triggerAnalysis}
              disabled={runStatus === "running"}
              title="Re-run pipeline with current inputs"
            >
              <span>🔄</span>
              <span>{t("common.rerunAnalysis")}</span>
            </button>
          </div>
        </div>
      {/if}

      <!-- SEQUENTIAL SECTION CONTAINER WITH EASING TRANSITIONS -->
      <div class="relative">
        {#if currentSection === "triage"}
          <!-- STEP 1: PATIENT TRIAGE (Main Intake Cockpit) -->
          <div in:fly={{ y: 15, duration: 200, easing: cubicInOut }}>
            <TriageInputStep
              bind:patient
              {artifactsData}
              {runStatus}
              {elapsedSeconds}
              isResultsAvailable={isAnalysisComplete}
              onTriggerAnalysis={triggerAnalysis}
              onStopAnalysis={stopAnalysis}
              onStopAndRetrigger={stopAndRetrigger}
              onNext={() => goToSection("orchestrator")}
            />
          </div>
        {:else if currentSection === "orchestrator"}
          <!-- STEP 2: CLINICAL ASSESSMENT (Standalone Dedicated Component) -->
          <div in:fly={{ y: 15, duration: 200, easing: cubicInOut }}>
            {#if ClinicalAssessmentStep}
              <svelte:component this={ClinicalAssessmentStep}
                {patient}
                {artifactsData}
                {runStatus}
                {runId}
                {elapsedSeconds}
                {stepNodes}
                {logsText}
                {errorMessage}
                nextUnlocked={isSectionUnlocked("sources")}
                onNext={() => goToSection("sources")}
                onBack={() => goToSection("triage")}
                onOpenDagu={triggerAnalysis}
              />
            {:else}
              <div class="flex items-center justify-center py-24"><span class="loading loading-spinner loading-lg text-primary"></span></div>
            {/if}
          </div>
        {:else if currentSection === "sources"}
          <!-- STEP 3: SCIENTIFIC SOURCES (Tavily Literature) -->
          <div in:fly={{ y: 15, duration: 200, easing: cubicInOut }}>
            {#if WebSearchStep}
              <svelte:component this={WebSearchStep}
                {patient}
                {artifactsData}
                {runStatus}
                nodeStatus={nodeStatusOf("tavily_web_search")}
                nextUnlocked={isSectionUnlocked("synthesis")}
                onNext={() => goToSection("synthesis")}
                onBack={() => goToSection("orchestrator")}
                onOpenDagu={triggerAnalysis}
              />
            {:else}
              <div class="flex items-center justify-center py-24"><span class="loading loading-spinner loading-lg text-primary"></span></div>
            {/if}
          </div>
        {:else if currentSection === "synthesis"}
          <!-- STEP 4: PROTOCOL & DOSAGES (Synthesis) -->
          <div in:fly={{ y: 15, duration: 200, easing: cubicInOut }}>
            {#if ClinicalSynthesisStep}
              <svelte:component this={ClinicalSynthesisStep}
                {patient}
                {artifactsData}
                {runStatus}
                nodeStatus={nodeStatusOf("clinical_synthesis")}
                nextUnlocked={isSectionUnlocked("sheet")}
                onNext={() => goToSection("sheet")}
                onBack={() => goToSection("sources")}
                onReset={handleReset}
                onOpenDagu={triggerAnalysis}
                {isCopilotOpen}
              />
            {:else}
              <div class="flex items-center justify-center py-24"><span class="loading loading-spinner loading-lg text-primary"></span></div>
            {/if}
          </div>
        {:else if currentSection === "sheet"}
          <!-- STEP 5: EMERGENCY SHEET (Official Final Sheet) -->
          <div in:fly={{ y: 15, duration: 200, easing: cubicInOut }}>
            {#if EmergencySheetViewer}
              <svelte:component this={EmergencySheetViewer}
                sheetMd={artifactsData ? artifactsData.sheetMd : ""}
                {patient}
                {artifactsData}
                {runStatus}
                nodeStatus={nodeStatusOf("export_summary")}
                onBack={() => goToSection("synthesis")}
                onReset={handleReset}
                onEditIntake={() => goToSection("triage")}
                onRerun={triggerAnalysis}
              />
            {:else}
              <div class="flex items-center justify-center py-24"><span class="loading loading-spinner loading-lg text-primary"></span></div>
            {/if}
          </div>
        {/if}
      </div>

      <!-- SECTION PULL-DOWN / PULL-TOP SWIPE TRANSITION COMPONENT (V2) -->
      <!-- <SectionPullSwipeTransitionv2
        {nextSectionMeta}
        {prevSectionMeta}
        onAdvance={(id) => goToSection(id)}
        onPrevious={(id) => goToSection(id)}
      /> -->
    </div>
  </div>
</div>

<!-- FIXED RIGHT-MARGIN CLINICAL AI COPILOT (BELL BOOKMARK DRAWER) -->
{#if ClinicalChatWidget}
  <svelte:component this={ClinicalChatWidget}
    bind:this={chatWidgetRef}
    {patient}
    {artifactsData}
    {currentSection}
    {runStatus}
    resetTrigger={chatResetTrigger}
    bind:isOpen={isCopilotOpen}
  />
{/if}

<!-- MOBILE RUN MANAGER MODAL / DRAWER (< lg) -->
{#if isMobileRunDrawerOpen}
  <div
    class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/60 backdrop-blur-xs"
    transition:fade={{ duration: 250, easing: cubicInOut }}
    onclick={(e) => {
      if (e.target === e.currentTarget) isMobileRunDrawerOpen = false;
    }}
    role="dialog"
    aria-modal="true"
    tabindex="-1"
  >
    <div
      class="bg-base-100 border border-base-300 w-full sm:max-w-md rounded-t-3xl sm:rounded-2xl p-4 shadow-2xl space-y-3 max-h-[85vh] overflow-y-auto"
      transition:fly={{ y: 100, duration: 300, easing: cubicInOut }}
    >
      <!-- Mobile Drawer Drag Handle -->
      <div class="flex flex-col items-center gap-1.5 pb-1 sm:hidden">
        <div class="w-12 h-1 rounded-full bg-base-300"></div>
      </div>

      <!-- Drawer Header -->
      <div
        class="flex items-center justify-between border-b border-base-200 pb-2"
      >
        <div class="flex items-center gap-2 min-w-0">
          <div
            class="w-7 h-7 rounded-lg bg-primary/10 text-primary flex items-center justify-center font-bold text-sm shrink-0 border border-primary/20"
          >
            🔎
          </div>
          <div class="min-w-0">
            <h3
              class="text-xs font-black font-display tracking-wide uppercase text-base-content truncate"
            >
              {t("daguLoader.title")}
            </h3>
            <p class="text-[10px] text-base-content/50 font-mono truncate">
              {t("daguLoader.subtitle")}
            </p>
          </div>
        </div>
        <button
          type="button"
          class="btn btn-ghost btn-xs btn-circle text-base-content/60 hover:text-base-content cursor-pointer"
          onclick={() => (isMobileRunDrawerOpen = false)}
          aria-label="Close run manager"
        >
          ✕
        </button>
      </div>

      <!-- Loader Component inside modal -->
      <DaguRunLoader
        currentRunId={runId}
        onLoadRun={async (id) => {
          await loadSpecificDagRun(id);
          setTimeout(() => {
            isMobileRunDrawerOpen = false;
          }, 600);
        }}
        onReset={() => {
          handleReset();
          isMobileRunDrawerOpen = false;
        }}
      />
    </div>
  </div>
{/if}
