<script>
  import { fly, fade } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";
  import {
    startDaguPipeline,
    fetchDagRunStatus,
    fetchNodeLog,
    fetchAllArtifacts,
  } from "./daguService.js";

  let { patient, isOpen = $bindable(false), onWorkflowComplete } = $props();

  let runStatus = $state("idle"); // 'idle' | 'running' | 'succeeded' | 'failed'
  let runId = $state("");
  let stepNodes = $state([]);
  let activeTab = $state("steps"); // 'steps' | 'artifacts' | 'logs'
  let errorMessage = $state("");
  let logsText = $state("");
  let pollTimer = null;
  let elapsedSeconds = $state(0);
  let elapsedTimer = null;
  let loadedArtifacts = $state(null);

  const defaultStepDefs = [
    {
      id: "setup_environment",
      name: "Preparing the clinical case",
      icon: "⚙️",
    },
    {
      id: "nebius_orchestrator",
      name: "Case triage & search planning",
      icon: "🩺",
    },
    {
      id: "tavily_web_search",
      name: "Searching validated scientific sources",
      icon: "📚",
    },
    {
      id: "clinical_synthesis",
      name: "Protocol synthesis & dosage calculation",
      icon: "🧬",
    },
    {
      id: "export_summary",
      name: "Preparing the sheet for review",
      icon: "📋",
    },
  ];

  // Generated clinical documents shown to the vet for review.
  const artifactDefinitions = [
    {
      name: "final_clinical_emergency_sheet.md",
      title: "Clinical Emergency Sheet",
      icon: "🚨",
    },
    {
      name: "02_web_search_report.md",
      title: "Scientific Sources Consulted",
      icon: "📚",
    },
    {
      name: "01_orchestrator_report.md",
      title: "Case Triage & Search Planning Summary",
      icon: "🩺",
    },
  ];

  async function triggerDaguRun() {
    if (runStatus === "running") return;

    runStatus = "running";
    errorMessage = "";
    elapsedSeconds = 0;
    logsText = `[${new Date().toLocaleTimeString()}] Starting request to the Dagu Workflow Engine...\n`;

    // Initialize step nodes UI with waiting states
    stepNodes = defaultStepDefs.map((def) => ({
      id: def.id,
      name: def.name,
      icon: def.icon,
      statusLabel: def.id === "setup_environment" ? "running" : "not_started",
      stdout: "",
    }));

    if (elapsedTimer) clearInterval(elapsedTimer);
    elapsedTimer = setInterval(() => {
      elapsedSeconds++;
    }, 1000);

    try {
      runId = await startDaguPipeline(patient);
      logsText += `[${new Date().toLocaleTimeString()}] DAG Run avviato con ID: ${runId}\n`;
      logsText += `[Dagu Engine] Specie: ${patient.specie} | Peso: ${patient.peso} kg | Priorità: ${patient.priorita}\n\n`;
      startPolling(runId);
    } catch (err) {
      runStatus = "failed";
      errorMessage = err.message || "Unable to start the clinical analysis.";
      logsText += `[ERRORE] ${errorMessage}\n`;
      if (elapsedTimer) clearInterval(elapsedTimer);
    }
  }

  function startPolling(id) {
    if (pollTimer) clearInterval(pollTimer);

    pollTimer = setInterval(async () => {
      try {
        const dagRun = await fetchDagRunStatus(id);
        if (!dagRun) return;

        // Update step nodes
        if (dagRun.nodes && dagRun.nodes.length > 0) {
          stepNodes = dagRun.nodes.map((n, idx) => {
            const stepKey = n.step.id || n.step.name || "";
            const def = defaultStepDefs.find(
              (d) => d.id === stepKey || d.name === stepKey
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
        }

        // Check if finished
        if (dagRun.status === 4 || dagRun.statusLabel === "succeeded") {
          clearInterval(pollTimer);
          if (elapsedTimer) clearInterval(elapsedTimer);
          runStatus = "succeeded";

          logsText += `\n[${new Date().toLocaleTimeString()}] ✓ Pipeline completata con successo in ${elapsedSeconds}s!\nCaricamento artefatti clinici generati...\n`;

          // Fetch real artifacts
          try {
            const artifacts = await fetchAllArtifacts();
            loadedArtifacts = artifacts;
            if (onWorkflowComplete) {
              onWorkflowComplete(artifacts);
            }
          } catch (e) {
            console.error("Failed to load artifacts:", e);
          }
        } else if (dagRun.status === 5 || dagRun.statusLabel === "failed") {
          clearInterval(pollTimer);
          if (elapsedTimer) clearInterval(elapsedTimer);
          runStatus = "failed";
          errorMessage = "The clinical analysis did not complete successfully. Please try again.";
          logsText += `\n[${new Date().toLocaleTimeString()}] ✕ Pipeline failed. Check the logs for details.\n`;
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 800);
  }

  $effect(() => {
    if (isOpen && runStatus === "idle") {
      triggerDaguRun();
    }
  });

  function close() {
    if (pollTimer) clearInterval(pollTimer);
    if (elapsedTimer) clearInterval(elapsedTimer);
    isOpen = false;
  }
</script>

{#if isOpen}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/60 backdrop-blur-sm"
    in:fade={{ duration: 200 }}
  >
    <div
      class="card w-full max-w-2xl bg-base-100 shadow-2xl border border-base-300 overflow-hidden"
      in:fly={{ y: 20, duration: 300, easing: cubicInOut }}
    >
      <!-- Header -->
      <div
        class="p-4 sm:p-5 bg-base-200/80 border-b border-base-300 flex items-center justify-between"
      >
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center text-xl shadow-inner"
          >
            🔬
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span
                class="text-xs font-bold uppercase tracking-wider text-primary font-label"
              >
                Assistente Clinico AI
              </span>
            </div>
            <h3 class="text-base font-black text-base-content font-display">
              Patient Clinical Analysis
            </h3>
          </div>
        </div>

        <div class="flex items-center gap-2">
          {#if runStatus === "running"}
            <span
              class="badge badge-warning gap-1.5 font-bold font-mono text-xs shadow-xs"
            >
              <span class="w-2 h-2 rounded-full bg-warning animate-ping"></span>
              Running ({elapsedSeconds}s)
            </span>
          {:else if runStatus === "succeeded"}
            <span
              class="badge badge-success gap-1 font-bold font-mono text-xs shadow-xs"
            >
              ✓ Completed ({elapsedSeconds}s)
            </span>
          {:else if runStatus === "failed"}
            <span
              class="badge badge-error gap-1 font-bold font-mono text-xs shadow-xs text-white"
            >
              ✕ Error
            </span>
          {/if}

          <button
            type="button"
            class="btn btn-ghost btn-sm btn-circle"
            onclick={close}
            aria-label="Close"
          >
            ✕
          </button>
        </div>
      </div>

      <!-- Body -->
      <div class="p-4 sm:p-6 space-y-4">
        <!-- Patient Summary Bar -->
        <div
          class="flex flex-wrap items-center justify-between p-3 rounded-xl bg-base-200/60 border border-base-300 text-xs gap-2"
        >
          <div class="flex items-center gap-2">
            <span class="text-base-content/60">Patient:</span>
            <span class="font-bold text-base-content"
              >{patient.specie} ({patient.peso} kg)</span
            >
            <span class="badge badge-xs badge-outline uppercase font-mono"
              >{patient.priorita}</span
            >
          </div>
          {#if runStatus === "running"}
            <div class="flex items-center gap-2 text-base-content/60">
              <span class="w-2 h-2 rounded-full bg-primary animate-ping"></span>
              <span>Analysis in progress…</span>
            </div>
          {/if}
        </div>

        {#if errorMessage}
          <div class="alert alert-error text-xs text-white font-medium p-3">
            <span>⚠️ {errorMessage}</span>
          </div>
        {/if}

        <!-- Review indication once the analysis is ready -->
        {#if runStatus === "succeeded"}
          <div
            class="flex items-start gap-3 p-3.5 rounded-xl bg-success/10 border border-success/30 text-xs"
            in:fade
          >
            <span class="text-lg leading-none">📝</span>
            <div>
              <div class="font-bold text-success">
                Analysis complete — ready for your review
              </div>
              <p class="text-base-content/70 mt-0.5">
                Open the documents below and review the suggested protocol and
                dosages before applying them to the patient.
              </p>
            </div>
          </div>
        {/if}

        <!-- Navigation Tabs -->
        <div class="tabs tabs-box bg-base-200/70 p-1 rounded-xl">
          <button
            type="button"
            class="tab text-xs font-bold transition-all duration-200 {activeTab ===
            'steps'
              ? 'tab-active shadow-xs'
              : ''}"
            onclick={() => (activeTab = "steps")}
          >
            <span>Progress ({stepNodes.length})</span>
          </button>
          <button
            type="button"
            class="tab text-xs font-bold transition-all duration-200 {activeTab ===
            'artifacts'
              ? 'tab-active shadow-xs'
              : ''}"
            onclick={() => (activeTab = "artifacts")}
          >
            <span>Documents to Review ({artifactDefinitions.length})</span>
          </button>
        </div>

        <!-- Tab 1: Step Nodes List -->
        {#if activeTab === "steps"}
          <div class="space-y-2">
            {#each stepNodes as step, i}
              <div
                class="flex items-center justify-between p-3 rounded-xl border transition-all duration-300 ease-in-out {step.statusLabel ===
                'running'
                  ? 'border-primary/40 bg-primary/5 shadow-sm'
                  : step.statusLabel === 'succeeded'
                    ? 'border-success/30 bg-success/5'
                    : 'border-base-300 bg-base-100'}"
              >
                <div class="flex items-center gap-3">
                  <div
                    class="w-7 h-7 rounded-xl flex items-center justify-center font-mono font-bold text-xs {step.statusLabel ===
                    'succeeded'
                      ? 'bg-success/20 text-success'
                      : step.statusLabel === 'running'
                        ? 'bg-primary/20 text-primary'
                        : 'bg-base-200 text-base-content/50'}"
                  >
                    {#if step.statusLabel === "succeeded"}
                      ✓
                    {:else if step.statusLabel === "running"}
                      <span
                        class="w-2 h-2 rounded-full bg-primary animate-ping"
                      ></span>
                    {:else}
                      {i + 1}
                    {/if}
                  </div>
                  <div>
                    <div
                      class="text-xs font-bold text-base-content flex items-center gap-1.5"
                    >
                      <span>{step.icon || "⚡"}</span>
                      <span>{step.name}</span>
                    </div>
                  </div>
                </div>

                <div>
                  {#if step.statusLabel === "succeeded"}
                    <span
                      class="badge badge-success badge-sm font-bold gap-1 font-mono"
                    >
                      ✓ Done
                    </span>
                  {:else if step.statusLabel === "running"}
                    <span
                      class="badge badge-warning badge-sm font-bold gap-1 font-mono"
                    >
                      <span
                        class="w-1.5 h-1.5 rounded-full bg-warning animate-ping"
                      ></span>
                      In progress...
                    </span>
                  {:else if step.statusLabel === "failed"}
                    <span
                      class="badge badge-error badge-sm font-bold font-mono text-white"
                    >
                      ✕ Failed
                    </span>
                  {:else}
                    <span
                      class="badge badge-ghost badge-sm text-base-content/50 font-mono"
                    >
                      Queued
                    </span>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        {:else if activeTab === "artifacts"}
          <!-- Tab 2: Artifacts List -->
          <div class="space-y-2 max-h-72 overflow-y-auto pr-1">
            {#each artifactDefinitions as art}
              {@const isReady =
                loadedArtifacts &&
                loadedArtifacts.availableFiles &&
                loadedArtifacts.availableFiles.includes(art.name)}
              <div
                class="flex items-center justify-between p-3 rounded-xl border border-base-300 bg-base-100 transition-all duration-200 hover:bg-base-200/40"
              >
                <div class="flex items-center gap-3">
                  <span class="text-xl">{art.icon}</span>
                  <div>
                    <div class="text-xs font-bold text-base-content">
                      {art.title}
                    </div>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  {#if isReady || runStatus === "succeeded"}
                    <a
                      href={`/api/artifacts?name=${art.name}`}
                      target="_blank"
                      rel="noreferrer"
                      class="badge badge-sm badge-success font-bold hover:scale-105 transition-transform cursor-pointer"
                    >
                      Review ↗
                    </a>
                  {:else}
                    <span
                      class="badge badge-sm badge-ghost text-base-content/40"
                    >
                      Waiting
                    </span>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <!-- Footer -->
      <div
        class="p-4 bg-base-200/60 border-t border-base-300 flex flex-wrap items-center justify-end gap-2"
      >
        <div class="flex items-center gap-2">
          {#if runStatus !== "running"}
            <button
              type="button"
              class="btn btn-outline btn-sm gap-1 cursor-pointer"
              onclick={triggerDaguRun}
            >
              <span>🔄 Run Again</span>
            </button>
          {/if}

          <button
            type="button"
            class="btn btn-ghost btn-sm cursor-pointer"
            onclick={close}
          >
            Close
          </button>

          {#if runStatus === "succeeded"}
            <button
              type="button"
              class="btn btn-primary btn-sm gap-1.5 shadow-md shadow-primary/20 cursor-pointer font-bold"
              onclick={close}
            >
              <span>Review Results</span>
              <span>→</span>
            </button>
          {/if}
        </div>
      </div>
    </div>
  </div>
{/if}
