<script>
  import { onMount, tick, untrack } from "svelte";
  import { fly, fade, slide, scale } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";
  import SvelteMarkdown from "svelte-markdown";
  import {
    startChatDaguPipeline,
    fetchChatDagRunStatus,
    fetchChatReplyArtifact,
  } from "./daguService.js";
  import { t, i18nState } from "$lib";

  let {
    patient = {},
    artifactsData = null,
    currentSection = "triage",
    runStatus = "idle",
    isOpen = $bindable(false),
    resetTrigger = 0,
  } = $props();

  let userInput = $state("");
  let isLoading = $state(false);
  let copiedIndex = $state(null);
  let chatScrollContainer = $state(null);
  let textareaEl = $state(null);
  let showContextDetails = $state(false);
  let chatElapsed = $state(0);
  let expandedEvidenceIndices = $state(new Set());

  function toggleEvidence(idx) {
    const next = new Set(expandedEvidenceIndices);
    if (next.has(idx)) {
      next.delete(idx);
    } else {
      next.add(idx);
    }
    expandedEvidenceIndices = next;
  }

  let messages = $state([
    {
      role: "assistant",
      content: buildGreeting(patient),
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
      model: "Nemotron-3 550B",
      isGreeting: true,
    },
  ]);

  // Species emoji helper
  function getSpeciesIcon(specie) {
    if (!specie) return "🩺";
    const s = specie.toLowerCase();
    if (s.includes("cat") || s.includes("gatto") || s.includes("feline"))
      return "🐱";
    if (s.includes("dog") || s.includes("cane") || s.includes("canine"))
      return "🐶";
    if (s.includes("rabbit") || s.includes("coniglio")) return "🐰";
    if (s.includes("ferret") || s.includes("furetto")) return "🦡";
    if (s.includes("horse") || s.includes("cavallo")) return "🐴";
    return "🐾";
  }

  // Initial welcome message reflecting active case
  function buildGreeting(p = patient) {
    return (
      `${t("copilot.greetIntro")}\n\n` +
      `${t("copilot.greetTracking")}\n` +
      `- **${t("copilot.greetPatientLabel")}:** ${p?.specie || "Unknown species"} (${p?.razza || "Mixed"}), **${p?.peso || "—"} kg**\n` +
      `- **${t("copilot.greetTriageLabel")}:** ${p?.priorita ? p.priorita.toUpperCase() : t("copilot.greetEvaluating")}\n` +
      `- **${t("copilot.greetPresentationLabel")}:** ${p?.sintomi ? p.sintomi.substring(0, 180) + (p.sintomi.length > 180 ? "..." : "") : t("copilot.greetAwaiting")}\n\n` +
      `${t("copilot.greetAsk")}`
    );
  }

  let initialGreeting = $derived(buildGreeting(patient));

  // Dynamically update the greeting message in the chat feed whenever intake selections change
  $effect(() => {
    const freshGreeting = buildGreeting(patient);
    if (
      messages.length > 0 &&
      messages[0].role === "assistant" &&
      (messages.length === 1 || messages[0].isGreeting)
    ) {
      messages[0].content = freshGreeting;
    }
  });

  // Full reset method for fresh case intake or manual history clear
  export function resetChat() {
    userInput = "";
    isLoading = false;
    copiedIndex = null;
    showContextDetails = false;
    chatElapsed = 0;
    messages = [
      {
        role: "assistant",
        content: buildGreeting(patient),
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        model: "Nemotron-3 550B",
        isGreeting: true,
      },
    ];
  }

  let lastResetTrigger = $state(0);

  $effect(() => {
    const trigger = resetTrigger;
    if (trigger > 0 && trigger !== lastResetTrigger) {
      lastResetTrigger = trigger;
      untrack(() => {
        resetChat();
      });
    }
  });

  onMount(() => {
    if (!messages.length) {
      resetChat();
    }

    // Triggerable by pressing Tab keystroke
    function handleGlobalKeydown(e) {
      if (e.key === "Tab" && !e.altKey && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        toggleOpen();
      }
    }

    window.addEventListener("keydown", handleGlobalKeydown);
    return () => {
      window.removeEventListener("keydown", handleGlobalKeydown);
    };
  });

  // Dynamic quick suggestion prompts based on species and clinical presentation
  let suggestedPrompts = $derived.by(() => {
    const s = (patient?.specie || "").toLowerCase();
    const symptoms = (patient?.sintomi || "").toLowerCase();
    const ivPrompt = "Which IV access should I use?";

    let specificPrompts = [];
    if (
      symptoms.includes("amlodip") ||
      symptoms.includes("calcium channel") ||
      symptoms.includes("hypotension")
    ) {
      specificPrompts = [
        "Amlodipine toxicity & calcium gluconate protocol",
        "Refractory hypotension in canine CCB overdose",
        "Intravenous lipid emulsion (ILE) indication",
        "Target IV fluid rates & inotropes",
      ];
    } else if (
      symptoms.includes("tick") ||
      symptoms.includes("lameness") ||
      symptoms.includes("lyme")
    ) {
      specificPrompts = [
        "Doxycycline dosage & vector-borne protocol",
        "Differential for migratory polyarthritis",
        "Joint fluid cytology & serology timeline",
        "NSAID safety & monitoring guidelines",
      ];
    } else if (
      s.includes("rabbit") ||
      symptoms.includes("stasis") ||
      symptoms.includes("lagomorph")
    ) {
      specificPrompts = [
        "GI stasis prokinetics & analgesia protocol",
        "Species contraindication: do NOT induce emesis",
        "Fluid therapy & critical care syringe feeding",
        "Cecal dysbiosis & safe antimicrobial choices",
      ];
    } else if (
      symptoms.includes("chocolate") ||
      symptoms.includes("theobromine") ||
      symptoms.includes("cioccolato")
    ) {
      specificPrompts = [
        "Theobromine mg/kg toxicity threshold",
        "Apomorphine emesis dosage & protocol",
        "Arrhythmia & cardiovascular risks",
        "IV fluid therapy rates",
      ];
    } else if (
      s.includes("cat") ||
      symptoms.includes("lily") ||
      symptoms.includes("lilium")
    ) {
      specificPrompts = [
        "Aggressive fluid diuresis for feline lily toxicosis",
        "Can we induce emesis in this cat?",
        "Renal biomarker monitoring timeline",
        "Calculate Activated Charcoal dose",
      ];
    } else if (symptoms.includes("xylitol")) {
      specificPrompts = [
        "Dextrose CRI protocol for xylitol hypoglycemia",
        "Hepatic necrosis monitoring timeline",
        "Baseline liver values & N-acetylcysteine",
        "IV fluid therapy rates",
      ];
    } else {
      specificPrompts = [
        "Calculate Activated Charcoal & fluid rates",
        "Check species contraindications for emesis",
        "What are the lethal limits & toxicity thresholds?",
        "Summarize immediate stabilization protocol",
      ];
    }

    return [ivPrompt, ...specificPrompts];
  });

  async function scrollToBottom() {
    await tick();
    if (chatScrollContainer) {
      chatScrollContainer.scrollTo({
        top: chatScrollContainer.scrollHeight,
        behavior: "smooth",
      });
    }
  }

  async function scrollToReplyTop(targetIdx) {
    await tick();
    if (!chatScrollContainer) return;

    const idx = targetIdx !== undefined ? targetIdx : messages.length - 1;
    requestAnimationFrame(() => {
      const targetEl = document.getElementById(`chat-msg-${idx}`);
      if (!targetEl || !chatScrollContainer) return;

      let targetTop = 0;
      if (targetEl.offsetParent === chatScrollContainer) {
        targetTop = targetEl.offsetTop - 12;
      } else {
        const containerRect = chatScrollContainer.getBoundingClientRect();
        const targetRect = targetEl.getBoundingClientRect();
        targetTop =
          chatScrollContainer.scrollTop +
          (targetRect.top - containerRect.top) -
          12;
      }

      chatScrollContainer.scrollTo({
        top: Math.max(0, targetTop),
        behavior: "smooth",
      });
    });
  }

  function toggleOpen() {
    isOpen = !isOpen;
    if (isOpen) {
      scrollToBottom();
      setTimeout(() => {
        if (textareaEl) textareaEl.focus();
      }, 250);
    }
  }

  function clearHistory() {
    resetChat();
  }

  async function sendMessage(textToSend) {
    const text = (textToSend || userInput || "").trim();
    if (!text || isLoading) return;

    const userMsg = {
      role: "user",
      content: text,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    messages = [...messages, userMsg];
    userInput = "";
    isLoading = true;
    chatElapsed = 0;
    scrollToBottom();

    const timer = setInterval(() => {
      chatElapsed++;
    }, 1000);

    try {
      // 1. Build conversation history from prior messages
      const historyPayload = messages.slice(0, -1).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      // 2. Trigger the Dagu workflow (vetsentinel-chat-flow)
      const dagRunId = await startChatDaguPipeline({
        patient,
        query: text,
        history: historyPayload,
        language: i18nState.locale,
      });

      // 3. Poll Dagu run status until completed
      let finished = false;
      let attempts = 0;
      const maxAttempts = 120; // 120s timeout

      while (!finished && attempts < maxAttempts) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
        attempts++;

        try {
          const dagRun = await fetchChatDagRunStatus(dagRunId);
          if (dagRun) {
            if (dagRun.status === 4 || dagRun.statusLabel === "succeeded") {
              finished = true;
              break;
            }
            if (dagRun.status === 5 || dagRun.statusLabel === "failed") {
              throw new Error(
                `Dagu reasoning flow failed with status: ${dagRun.statusLabel || "failed"}`,
              );
            }
          }
        } catch (pollErr) {
          if (pollErr.message && pollErr.message.includes("failed")) {
            throw pollErr;
          }
        }
      }

      if (!finished) {
        throw new Error("Dagu copilot reasoning timed out.");
      }

      // 4. Fetch the generated chat response artifact
      let replyArtifact = await fetchChatReplyArtifact(dagRunId);
      if (!replyArtifact || !replyArtifact.reply) {
        await new Promise((resolve) => setTimeout(resolve, 600));
        replyArtifact = await fetchChatReplyArtifact(dagRunId);
      }

      const fullReply =
        replyArtifact?.reply ||
        "No structured clinical reply returned by copilot.";
      const rawModel =
        replyArtifact?.model || "nvidia/Nemotron-3-Ultra-550b-a55b";
      const modelName = rawModel.includes("Nemotron")
        ? "Nemotron-3 550B"
        : rawModel.includes("GLM")
          ? "z-ai GLM-5.3"
          : rawModel;

      const assistantMsg = {
        role: "assistant",
        content: fullReply,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        model: modelName,
      };
      messages = [...messages, assistantMsg];
      scrollToReplyTop(messages.length - 1);
    } catch (err) {
      console.error("Clinical chat error:", err);
      clearInterval(timer);
      isLoading = false;

      const errorMsg = {
        role: "assistant",
        content:
          `⚠️ **Clinical Copilot Notice:** Unable to reach reasoning engine (${err.message}).\n\n` +
          `**Local Case Insight for ${patient.specie || "Patient"} (${patient.peso || "4.0"} kg):**\n` +
          `- Ensure baseline venous blood gas, renal and hepatic profiles are drawn.\n` +
          `- Balanced crystalloid rate recommendation: **${((Number(patient.peso) || 4) * 3).toFixed(1)}–${((Number(patient.peso) || 4) * 4).toFixed(1)} mL/h**.\n` +
          `- Review Step 4 Protocol & Dosages for synthesized verified recommendations.`,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        model: "Local Fallback",
      };
      messages = [...messages, errorMsg];
      scrollToReplyTop(messages.length - 1);
    } finally {
      clearInterval(timer);
      isLoading = false;
    }
  }

  function handleKeydown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  function copyMessage(index, content) {
    if (!content) return;
    navigator.clipboard.writeText(content);
    copiedIndex = index;
    setTimeout(() => {
      if (copiedIndex === index) copiedIndex = null;
    }, 2000);
  }
</script>

<!-- FIXED RIGHT-TOP DOCKED COPILOT DRAWER (FULL DASHBOARD HEIGHT) -->
<aside
  class="fixed top-16 right-0 z-40 h-[calc(100dvh-4rem)] w-[370px] sm:w-[395px] xl:w-[440px] bg-base-100/95 backdrop-blur-xl border-l border-primary/25 shadow-2xl flex flex-col transition-transform duration-300 ease-in-out select-text {isOpen
    ? 'translate-x-0'
    : 'translate-x-full'}"
  aria-label="VetSentinel AI Clinical Copilot"
>
  <!-- HORIZONTAL WAVY SIDE TAB (POPPY MEDICAL CYAN-BLUE VET PALETTE, WIDE BASE, SHORTER PROJECTION + TAB TRIGGER)
       Permanently lives on the left edge of this drawer.
       Shaped like an organic wavy side tab: wide 148px flared base along the edge, and shorter compact center projection (68px).
       Styled in poppy clinical cyan-blue medical tone (#0ea5e9 -> #2563eb) that pops out cleanly while matching clinical scrub/vet aesthetics.
  -->
  <button
    type="button"
    class="bell-tab-btn absolute -top-3 -left-[68px] w-[68px] h-[148px] flex items-center justify-between text-white transition-all duration-300 ease-in-out hover:-left-[70px] active:scale-95 cursor-pointer select-none group focus:outline-none"
    onclick={toggleOpen}
    title={isOpen
      ? "Collapse AI Copilot (Tab)"
      : "Open Clinical AI Copilot (Press Tab)"}
  >
    <!-- Vector Wavy Bell Tab Silhouette with Poppy Medical Cyan-Blue Gradient -->
    <svg
      class="absolute inset-0 w-full h-full pointer-events-none filter drop-shadow-md"
      viewBox="0 0 68 148"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      preserveAspectRatio="none"
    >
      <defs>
        <!-- Poppy Clinical Veterinary Cyan-to-Cobalt Blue Gradient -->
        <linearGradient
          id="poppyMedBlueGrad"
          x1="100%"
          y1="0%"
          x2="0%"
          y2="100%"
        >
          <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.08" />
          <stop offset="45%" stop-color="#0ea5e9" stop-opacity="0.85" />
          <stop offset="100%" stop-color="#2563eb" stop-opacity="0.0" />
        </linearGradient>
      </defs>

      <!-- Wavy bell body: wide 148px base at drawer edge, short 68px center tip -->
      <path
        d="M 68,0 
           C 68,34 54,50 36,54 
           C 22,57 9,56 4,62 
           C 0.8,66 0,69.5 0,74 
           C 0,78.5 0.8,82 4,86 
           C 9,92 22,91 36,94 
           C 54,98 68,114 68,148 Z"
        fill="url(#poppyMedBlueGrad)"
        stroke="#38bdf8"
        stroke-width="1.25"
      />
    </svg>

    <!-- Tab Contents (Compact layout fitting the shorter 68px center) -->
    <div
      class="relative z-10 flex items-center justify-between w-full pl-2 pr-1.5 text-white"
    >
      <!-- Left: Species Avatar with live pulse indicator -->
      <div class="flex items-center gap-1 min-w-0">
        <div class="relative flex items-center justify-center shrink-0">
          <div
            class="w-5 h-5 rounded-md bg-white/20 text-white border border-white/35 flex items-center justify-center text-[11px] font-bold shadow-xs backdrop-blur-xs transition-transform group-hover:scale-105"
          >
            {getSpeciesIcon(patient.specie)}
          </div>
          {#if !isOpen}
            <span class="absolute -top-1 -right-1 flex h-2 w-2">
              <span
                class="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-200 opacity-75"
              ></span>
              <span
                class="relative inline-flex rounded-full h-2 w-2 bg-cyan-300"
              ></span>
            </span>
          {/if}
        </div>

        <!-- Center: Copilot text & hotkey badge -->
        <div class="flex flex-col text-left min-w-0">
          <div class="flex items-center gap-0.5 leading-tight">
            <span
              class="text-[9px] font-black tracking-tight font-display text-white drop-shadow-xs"
            >
              AI
            </span>
          </div>
          <kbd
            class="kbd kbd-xs bg-black/25 text-white/90 border border-white/25 text-[6.5px] font-mono px-0.5 py-0 leading-none w-fit mt-0.5"
            title="Press Tab to toggle"
          >
            Tab
          </kbd>
        </div>
      </div>

      <!-- Right: Compact Directional Arrow -->
      <div
        class="w-3.5 h-3.5 rounded-sm bg-white/20 text-white border border-white/30 flex items-center justify-center text-[8px] font-bold transition-all duration-300 group-hover:bg-white group-hover:text-sky-600 shadow-xs shrink-0"
      >
        <span>{isOpen ? "›" : "‹"}</span>
      </div>
    </div>
  </button>

  <!-- DRAWER HEADER -->
  <div
    class="px-4 py-3 bg-gradient-to-r from-base-200/90 via-base-100/90 to-base-200/90 border-b border-base-300/80 flex items-center justify-between gap-2 shrink-0"
  >
    <div class="flex items-center gap-2.5 min-w-0">
      <div class="relative">
        <div
          class="w-8 h-8 rounded-xl bg-gradient-to-tr from-primary to-secondary text-primary-content flex items-center justify-center font-bold text-base shadow-sm shadow-primary/20"
        >
          {getSpeciesIcon(patient.specie)}
        </div>
        <span
          class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-success border-2 border-base-100"
          title="Nebius Online"
        ></span>
      </div>

      <div class="min-w-0">
        <div class="flex items-center gap-1.5">
          <span
            class="font-extrabold text-xs sm:text-sm text-base-content font-display truncate"
          >
            {t("copilot.drawerTitle")}
          </span>
          <span
            class="badge badge-xs font-mono text-[9px] bg-primary/10 text-primary border border-primary/25 font-bold"
          >
            Nemotron-3 550B
          </span>
        </div>
        <div
          class="flex items-center gap-1.5 text-[10px] sm:text-[11px] text-base-content/65 font-medium truncate"
        >
          <span>{patient.specie || "Patient"}</span>
          <span>•</span>
          <span class="font-mono">{patient.peso || "—"} kg</span>
          {#if patient.priorita}
            <span>•</span>
            <span
              class="font-bold uppercase text-[9px] {patient.priorita ===
              'critical'
                ? 'text-error'
                : patient.priorita === 'urgent'
                  ? 'text-warning'
                  : 'text-success'}"
            >
              {patient.priorita}
            </span>
          {/if}
        </div>
      </div>
    </div>

    <!-- HEADER ACTION CONTROLS -->
    <div class="flex items-center gap-1">
      <!-- Toggle Context Inspector -->
      <button
        type="button"
        class="btn btn-ghost btn-xs btn-square text-base-content/70 hover:text-primary cursor-pointer transition-all"
        onclick={() => (showContextDetails = !showContextDetails)}
        title="Toggle Context Grounding"
      >
        <span class="text-xs">ℹ️</span>
      </button>

      <!-- Clear Chat History -->
      <button
        type="button"
        class="btn btn-ghost btn-xs btn-square text-base-content/70 hover:text-error cursor-pointer transition-all"
        onclick={clearHistory}
        title="Reset Chat History"
      >
        <span class="text-xs">🗑️</span>
      </button>

      <!-- Close Drawer -->
      <button
        type="button"
        class="btn btn-ghost btn-xs btn-square text-base-content/70 hover:text-base-content hover:bg-base-300/80 cursor-pointer transition-all ml-0.5"
        onclick={toggleOpen}
        title="Collapse Copilot"
      >
        <span class="text-sm font-bold">✕</span>
      </button>
    </div>
  </div>

  <!-- COLLAPSIBLE ACTIVE CASE CONTEXT INSPECTOR -->
  {#if showContextDetails}
    <div
      class="px-4 py-2.5 bg-primary/5 border-b border-primary/15 text-[11px] space-y-1.5"
      transition:slide={{ duration: 200, easing: cubicInOut }}
    >
      <div
        class="flex items-center justify-between text-primary font-bold text-[10px]"
      >
        <span class="flex items-center gap-1.5">
          <span>🩺</span>
          <span>Active Case Context Grounding</span>
        </span>
        <span class="badge badge-xs badge-primary font-mono text-[9px]"
          >Live Synced</span
        >
      </div>
      <div
        class="grid grid-cols-2 gap-1.5 text-base-content/75 font-mono text-[10px]"
      >
        <div>
          Patient: <span class="font-bold text-base-content"
            >{patient.specie || "Unknown"}</span
          >
          ({patient.peso || "—"} kg)
        </div>
        <div>
          Triage: <span class="font-bold uppercase text-base-content"
            >{patient.priorita || "Pending"}</span
          >
        </div>
        <div>
          Section: <span class="font-bold text-base-content capitalize"
            >{currentSection}</span
          >
        </div>
        <div>
          Artifacts:
          <span class="font-bold text-base-content">
            {artifactsData?.synthesis
              ? "Protocol Synced"
              : artifactsData?.orchestrator
                ? "Triage Synced"
                : "Intake Synced"}
          </span>
        </div>
      </div>
      {#if patient.sintomi}
        <div
          class="text-[10px] text-base-content/65 truncate border-t border-primary/10 pt-1"
        >
          <span class="font-bold">Anamnesis:</span>
          {patient.sintomi}
        </div>
      {/if}
    </div>
  {/if}

  <!-- MESSAGES FEED -->
  <div
    bind:this={chatScrollContainer}
    class="relative flex-1 min-h-0 overflow-y-auto p-4 space-y-3.5 text-sm"
  >
    {#each messages as msg, idx}
      {#if msg.role === "user"}
        <!-- USER MESSAGE BUBBLE -->
        <div
          id="chat-msg-{idx}"
          class="flex flex-col items-end gap-1 ml-5 scroll-mt-3"
          in:fly={{ y: 10, duration: 200, easing: cubicInOut }}
        >
          <div
            class="px-3.5 py-2 rounded-2xl rounded-tr-xs bg-primary text-primary-content shadow-xs text-[12px] leading-relaxed max-w-[88%] break-words font-medium"
          >
            {msg.content}
          </div>
          <span class="text-[9px] text-base-content/40 font-mono px-1">
            {msg.timestamp}
          </span>
        </div>
      {:else}
        <!-- ASSISTANT MESSAGE BUBBLE -->
        <div
          id="chat-msg-{idx}"
          class="flex items-start gap-2 mr-1 scroll-mt-3"
          in:fly={{ y: 10, duration: 220, easing: cubicInOut }}
        >
          <div
            class="w-6 h-6 rounded-lg bg-primary/10 border border-primary/20 text-primary flex items-center justify-center shrink-0 mt-0.5 font-bold text-xs"
          >
            {getSpeciesIcon(patient.specie)}
          </div>

          <div class="flex-1 min-w-0 flex flex-col gap-1">
            <div
              class="p-3.5 overflow-scroll rounded-2xl rounded-tl-xs bg-base-200/70 border border-base-300/80 shadow-xs text-base-content/90 text-[12.5px] leading-relaxed copilot-markdown break-words"
            >
              <SvelteMarkdown source={msg.content} />
            </div>

            {#if msg.executionLog}
              <div class="mt-0.5">
                <button
                  type="button"
                  class="btn btn-ghost btn-xs text-[9.5px] h-6 min-h-0 px-2 font-mono gap-1 text-base-content/60 hover:text-primary rounded-lg border border-base-300 hover:border-primary/40 transition-all cursor-pointer"
                  onclick={() => toggleEvidence(idx)}
                  title={t("copilot.toggleTraceTitle")}
                >
                  <span>{expandedEvidenceIndices.has(idx) ? "▾" : "▸"}</span>
                  <span
                    >{expandedEvidenceIndices.has(idx) ? t("copilot.hideTrace") : t("copilot.showTrace")}</span
                  >
                  {#if msg.latencyMs}
                    <span
                      class="badge badge-ghost badge-xs text-[9px] font-mono opacity-80"
                    >
                      {msg.latencyMs}ms
                    </span>
                  {/if}
                  {#if msg.dagRunId}
                    <span
                      class="badge badge-warning/20 text-warning border-warning/30 badge-xs text-[8.5px] font-mono"
                    >
                      DAG
                    </span>
                  {/if}
                </button>

                {#if expandedEvidenceIndices.has(idx)}
                  <div
                    class="mt-1.5 bg-neutral text-neutral-content p-3 rounded-xl font-mono text-[10px] leading-relaxed max-h-56 overflow-y-auto border border-neutral-content/10 shadow-inner select-text"
                    in:slide={{ duration: 200, easing: cubicInOut }}
                  >
                    <div
                      class="flex items-center justify-between text-[9px] text-neutral-content/50 border-b border-white/10 pb-1 mb-1.5 font-mono"
                    >
                      <span>Workflow: vetsentinel-chat-flow</span>
                      <span>Run ID: {msg.dagRunId || "local"}</span>
                    </div>
                    <pre
                      class="whitespace-pre-wrap font-mono text-[9.5px] text-emerald-400/90">{msg.executionLog}</pre>
                  </div>
                {/if}
              </div>
            {/if}

            <div
              class="flex items-center justify-between px-1 text-[9px] text-base-content/45 font-mono"
            >
              <div class="flex items-center gap-1.5">
                <span>{msg.timestamp}</span>
                <span>•</span>
                <span class="text-primary/70">{msg.model}</span>
                {#if msg.dagRunId}
                  <span
                    class="badge badge-outline badge-xs font-mono text-[8px] opacity-70"
                  >
                    dagu:{msg.dagRunId.slice(0, 8)}
                  </span>
                {/if}
              </div>

              <button
                type="button"
                class="btn btn-ghost btn-xs text-[9px] font-mono px-1.5 h-4 min-h-0 text-base-content/50 hover:text-primary cursor-pointer transition-all gap-1"
                onclick={() => copyMessage(idx, msg.content)}
                title="Copy response"
              >
                <span>{copiedIndex === idx ? "✓ Copied" : "📋 Copy"}</span>
              </button>
            </div>
          </div>
        </div>
      {/if}
    {/each}

    <!-- COMPACT LEAN CLINICAL COPILOT LOADER -->
    {#if isLoading}
      <div
        class="flex items-start gap-2 mr-1"
        in:fly={{ y: 8, duration: 220, easing: cubicInOut }}
        out:fade={{ duration: 150, easing: cubicInOut }}
      >
        <div
          class="w-6 h-6 rounded-lg bg-primary/15 border border-primary/30 text-primary flex items-center justify-center shrink-0 mt-0.5 text-xs font-bold shadow-xs animate-pulse"
        >
          <span>🩺</span>
        </div>

        <div class="flex-1 min-w-0 flex flex-col gap-1">
          <div
            class="px-3.5 py-3 rounded-2xl rounded-tl-xs bg-base-200/90 border border-primary/20 shadow-xs flex flex-col gap-1.5 backdrop-blur-sm"
          >
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-2">
                <span class="loading loading-dots loading-xs text-primary"
                ></span>
                <span
                  class="font-bold text-xs text-base-content/90 font-display"
                >
                  Evaluating clinical case...
                </span>
              </div>
              <span
                class="badge badge-primary/10 text-primary border-primary/20 badge-xs font-mono text-[9px]"
              >
                {chatElapsed}s
              </span>
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>

  <!-- QUICK SUGGESTION CHIPS -->
  <div class="px-3 py-2 border-t border-base-300/60 bg-base-200/30 shrink-0">
    <div
      class="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none text-xs"
    >
      <span
        class="text-[9px] font-bold uppercase font-mono text-base-content/40 shrink-0 pl-0.5"
      >
        Prompts:
      </span>
      {#each suggestedPrompts as prompt}
        <button
          type="button"
          class="btn btn-xs rounded-xl bg-base-100 hover:bg-primary/10 hover:border-primary/40 border border-base-300/80 text-base-content/75 text-[10px] font-normal shrink-0 shadow-2xs transition-all cursor-pointer"
          onclick={() => sendMessage(prompt)}
          disabled={isLoading}
        >
          {prompt}
        </button>
      {/each}
    </div>
  </div>

  <!-- INPUT COMPOSER -->
  <div class="p-3 bg-base-200/80 border-t border-base-300 shrink-0">
    <form
      onsubmit={(e) => {
        e.preventDefault();
        sendMessage();
      }}
      class="flex items-end gap-2"
    >
      <div class="relative flex-1">
        <textarea
          bind:this={textareaEl}
          bind:value={userInput}
          onkeydown={handleKeydown}
          placeholder={t("copilot.placeholder")}
          rows="1"
          class="textarea textarea-bordered w-full text-xs min-h-[40px] max-h-24 resize-none leading-normal py-2 px-3 rounded-xl bg-base-100/90 focus:outline-primary placeholder:text-base-content/40 placeholder:text-nowrap"
          disabled={isLoading}
        ></textarea>
      </div>

      <button
        type="submit"
        class="btn btn-primary btn-sm h-[40px] px-3 rounded-xl shadow-sm cursor-pointer transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
        disabled={!userInput.trim() || isLoading}
        title="Send inquiry (Enter)"
      >
        {#if isLoading}
          <span class="loading loading-spinner loading-xs"></span>
        {:else}
          <span class="font-bold text-sm">➤</span>
        {/if}
      </button>
    </form>
    <div
      class="flex items-center justify-between mt-2 px-1 text-[9px] text-base-content/40 font-mono"
    >
      <span>Enter to send, Shift+Enter for new line</span>
      <span>Patient: {patient.peso || "—"} kg</span>
    </div>
  </div>
</aside>

<style>
  /* Punchy Gaussian Bell Wave Tab Styling & Glow */
  .bell-tab-btn {
    filter: drop-shadow(0 6px 18px rgba(79, 70, 229, 0.4))
      drop-shadow(0 2px 8px rgba(6, 182, 212, 0.35));
  }
  .bell-tab-btn:hover {
    filter: drop-shadow(0 8px 25px rgba(79, 70, 229, 0.65))
      drop-shadow(0 4px 12px rgba(6, 182, 212, 0.6));
  }

  /* Markdown Styling for Copilot responses inside chat bubbles */
  .copilot-markdown :global(p) {
    margin-bottom: 0.45rem;
  }
  .copilot-markdown :global(p:last-child) {
    margin-bottom: 0;
  }
  .copilot-markdown :global(h1),
  .copilot-markdown :global(h2),
  .copilot-markdown :global(h3),
  .copilot-markdown :global(h4) {
    font-weight: 800;
    margin-top: 0.65rem;
    margin-bottom: 0.3rem;
    color: var(--color-base-content, #ffffff);
  }
  .copilot-markdown :global(h1) {
    font-size: 1rem;
  }
  .copilot-markdown :global(h2) {
    font-size: 0.94rem;
  }
  .copilot-markdown :global(h3) {
    font-size: 0.88rem;
  }
  .copilot-markdown :global(ul),
  .copilot-markdown :global(ol) {
    margin: 0.35rem 0 0.45rem 1.15rem;
    padding: 0;
    list-style-type: disc;
  }
  .copilot-markdown :global(li) {
    margin-bottom: 0.2rem;
  }
  .copilot-markdown :global(code) {
    font-family: ui-monospace, "Cascadia Code", Menlo, monospace;
    font-size: 0.85em;
    background: color-mix(in srgb, currentColor 12%, transparent);
    padding: 0.12em 0.3em;
    border-radius: 0.3em;
    font-weight: 600;
  }
  .copilot-markdown :global(blockquote) {
    border-left: 3px solid var(--color-primary, #6c8ef5);
    margin: 0.45rem 0;
    padding: 0.3rem 0.65rem;
    background: color-mix(
      in srgb,
      var(--color-primary, #6c8ef5) 8%,
      transparent
    );
    border-radius: 0 0.4rem 0.4rem 0;
    font-size: 0.9em;
  }
  .copilot-markdown :global(strong) {
    font-weight: 700;
  }
  .copilot-markdown :global(table) {
    width: 100%;
    margin: 0.45rem 0;
    font-size: 0.82em;
    border-collapse: collapse;
  }
  .copilot-markdown :global(th),
  .copilot-markdown :global(td) {
    padding: 0.3rem 0.45rem;
    border: 1px solid color-mix(in srgb, currentColor 12%, transparent);
  }
  .copilot-markdown :global(th) {
    background: color-mix(in srgb, currentColor 8%, transparent);
    font-weight: 700;
  }
</style>
