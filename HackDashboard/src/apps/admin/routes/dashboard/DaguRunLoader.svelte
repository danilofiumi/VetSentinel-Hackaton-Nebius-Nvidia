<script>
  import { onMount } from "svelte";
  import { fade, slide } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";
  import { fetchRecentDagRuns } from "./daguService.js";
  import { t } from "$lib";

  let { currentRunId = "", onLoadRun, onReset = null } = $props();

  let inputRunId = $state("");
  let isSubmitting = $state(false);
  let errorMsg = $state("");
  let successMsg = $state("");
  let recentRuns = $state([]);
  let showRecent = $state(false);

  // Sync with currentRunId if available or reset when empty
  $effect(() => {
    if (currentRunId) {
      inputRunId = currentRunId;
    } else {
      inputRunId = "";
      errorMsg = "";
      successMsg = "";
      isSubmitting = false;
    }
  });

  onMount(async () => {
    try {
      const runs = await fetchRecentDagRuns();
      if (Array.isArray(runs)) {
        recentRuns = runs.slice(0, 10);
      }
    } catch (e) {
      console.warn("Could not load recent DAG runs:", e);
    }
  });

  function parseRunSummary(run) {
    if (!run) return "";
    const params = run.params || "";
    const mSpecies = params.match(/SPECIES="([^"]+)"/i);
    const mWeight = params.match(/WEIGHT="([^"]+)"/i);
    const mPriority = params.match(/PRIORITY="([^"]+)"/i);
    const species = mSpecies ? mSpecies[1] : "";
    const weight = mWeight ? `${mWeight[1]}kg` : "";
    const priority = mPriority ? mPriority[1] : "";
    const parts = [species, weight, priority].filter(Boolean);
    return parts.join(" · ");
  }

  async function handleSubmit(e) {
    if (e) e.preventDefault();
    const id = (inputRunId || "").trim();
    if (!id) {
      errorMsg = "Please enter a valid DAG Run ID.";
      return;
    }

    isSubmitting = true;
    errorMsg = "";
    successMsg = "";

    try {
      await onLoadRun(id);
      successMsg = `✓ Run ${id.slice(0, 8)}… loaded!`;
      setTimeout(() => {
        successMsg = "";
      }, 4000);
    } catch (err) {
      errorMsg = err.message || "Failed to load data for this DAG run.";
    } finally {
      isSubmitting = false;
    }
  }

  function handleSelectRun(run) {
    if (!run || !run.dagRunId) return;
    inputRunId = run.dagRunId;
    showRecent = false;
    handleSubmit();
  }

  async function handlePaste() {
    try {
      const text = await navigator.clipboard.readText();
      if (text && text.trim()) {
        inputRunId = text.trim();
      }
    } catch (e) {
      console.warn("Clipboard paste failed:", e);
    }
  }
</script>

<div
  class="card bg-base-100/90 border border-base-300 shadow-sm backdrop-blur-md rounded-2xl p-3 sm:p-3.5 space-y-2.5 transition-all duration-300"
  in:fade={{ duration: 300, easing: cubicInOut }}
>
  <!-- Card Header -->
  <div
    class="flex items-center justify-between gap-2 border-b border-base-200/80 pb-2"
  >
    <div class="flex items-center gap-2 min-w-0">
      <div
        class="w-7 h-7 rounded-lg bg-primary/10 text-primary flex items-center justify-center font-bold text-sm shrink-0 border border-primary/20"
      >
        🔎
      </div>
      <div class="min-w-0">
        <h4
          class="text-xs font-black text-base-content font-display tracking-wide truncate"
        >
          {t("daguLoader.title")}
        </h4>
        <p class="text-[10px] text-base-content/50 truncate font-mono">
          {t("daguLoader.subtitle")}
        </p>
      </div>
    </div>

    {#if recentRuns.length > 0}
      <button
        type="button"
        class="btn btn-ghost btn-xs text-[10px] font-mono gap-1 px-1.5 cursor-pointer hover:bg-base-200 text-base-content/70"
        onclick={() => (showRecent = !showRecent)}
        title="Toggle recent runs list"
      >
        <span>⏱️ {t("daguLoader.recentBtn")}</span>
        <span class="text-[8px]">{showRecent ? "▲" : "▼"}</span>
      </button>
    {/if}
  </div>

  <!-- Recent Runs Quick Picker Dropdown -->
  {#if showRecent && recentRuns.length > 0}
    <div
      class="p-2 rounded-xl bg-base-200/60 border border-base-300 space-y-1 max-h-48 overflow-y-auto"
      transition:slide={{ duration: 200, easing: cubicInOut }}
    >
      <div
        class="text-[10px] font-bold uppercase tracking-wider text-base-content/50 px-1 font-label"
      >
        {t("daguLoader.selectRecentTitle")}
      </div>
      {#each recentRuns as r}
        {@const summary = parseRunSummary(r)}
        <button
          type="button"
          class="w-full text-left p-1.5 rounded-lg text-xs font-mono transition-colors hover:bg-primary/10 hover:text-primary flex items-center justify-between gap-1.5 cursor-pointer border border-transparent hover:border-primary/20 {r.dagRunId ===
          inputRunId
            ? 'bg-primary/15 text-primary font-bold border-primary/30'
            : 'text-base-content/80'}"
          onclick={() => handleSelectRun(r)}
        >
          <div class="min-w-0 truncate">
            <span class="font-bold">{r.dagRunId.slice(0, 10)}…</span>
            {#if summary}
              <span class="text-[10px] text-base-content/60 ml-1"
                >({summary})</span
              >
            {/if}
          </div>
          <span
            class="badge badge-xs font-mono text-[9px] shrink-0 uppercase {r.statusLabel ===
            'succeeded'
              ? 'badge-success text-white'
              : r.statusLabel === 'failed'
                ? 'badge-error text-white'
                : 'badge-warning'}"
          >
            {r.statusLabel || "done"}
          </span>
        </button>
      {/each}
    </div>
  {/if}

  <!-- Form Input & Submit -->
  <form onsubmit={handleSubmit} class="space-y-2">
    <div class="relative flex items-center">
      <input
        type="text"
        placeholder={t("daguLoader.placeholder")}
        bind:value={inputRunId}
        disabled={isSubmitting}
        class="input input-xs sm:input-sm input-bordered rounded-xl w-full font-mono text-xs pr-14 pl-2.5 focus:border-primary"
      />
      <div class="absolute right-1 flex items-center gap-0.5">
        {#if !inputRunId}
          <button
            type="button"
            class="btn btn-ghost btn-xs text-[10px] px-1.5 h-6 min-h-0 text-base-content/50 hover:text-base-content"
            onclick={handlePaste}
            title="Paste from clipboard"
          >
            {t("daguLoader.pasteBtn")}
          </button>
        {:else}
          <button
            type="button"
            class="btn btn-ghost btn-xs text-[10px] px-1.5 h-6 min-h-0 text-base-content/40 hover:text-base-content"
            onclick={() => (inputRunId = "")}
            title="Clear input"
          >
            ✕
          </button>
        {/if}
      </div>
    </div>

    <!-- Feedback messages -->
    {#if errorMsg}
      <div
        class="p-2 rounded-xl bg-error/10 border border-error/30 text-error text-[11px] leading-tight flex items-start gap-1.5"
        transition:slide={{ duration: 150, easing: cubicInOut }}
      >
        <span class="shrink-0">⚠️</span>
        <span class="break-words">{errorMsg}</span>
      </div>
    {/if}

    {#if successMsg}
      <div
        class="p-2 rounded-xl bg-success/10 border border-success/30 text-success text-[11px] leading-tight flex items-center gap-1.5 font-mono"
        transition:slide={{ duration: 150, easing: cubicInOut }}
      >
        <span>{successMsg}</span>
      </div>
    {/if}

    <!-- Action Buttons -->
    <div class="flex items-center gap-1.5 pt-0.5">
      <button
        type="submit"
        disabled={isSubmitting || !inputRunId.trim()}
        class="btn btn-xs sm:btn-sm btn-primary flex-1 font-bold gap-1.5 shadow-xs cursor-pointer disabled:opacity-50"
      >
        {#if isSubmitting}
          <span class="loading loading-spinner loading-xs"></span>
          <span>{t("daguLoader.loadingBtn")}</span>
        {:else}
          <span>📥</span>
          <span>{t("daguLoader.submitBtn")}</span>
        {/if}
      </button>

      {#if onReset}
        <button
          type="button"
          class="btn btn-xs sm:btn-sm btn-ghost text-base-content/60 hover:text-base-content px-2 cursor-pointer"
          onclick={onReset}
          title={t("daguLoader.resetTooltip")}
        >
          🔄
        </button>
      {/if}
    </div>
  </form>

  <!-- Currently Active Run Indicator -->
  {#if currentRunId}
    <div
      class="pt-1 border-t border-base-200/80 flex items-center justify-between text-[10px] font-mono text-base-content/60"
    >
      <span class="flex items-center gap-1 truncate">
        <span class="text-success">●</span>
        <span>{t("daguLoader.activeRun")}</span>
        <strong class="text-base-content truncate"
          >{currentRunId.slice(0, 12)}…</strong
        >
      </span>
      <button
        type="button"
        class="text-primary hover:underline cursor-pointer ml-1 shrink-0"
        onclick={() => {
          navigator.clipboard.writeText(currentRunId);
        }}
        title="Copy full Run ID"
      >
        {t("daguLoader.copyBtn")}
      </button>
    </div>
  {/if}
</div>
