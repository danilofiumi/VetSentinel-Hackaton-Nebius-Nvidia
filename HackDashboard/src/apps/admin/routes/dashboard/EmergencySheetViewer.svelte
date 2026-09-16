<script>
  import { fly, fade } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";
  import SvelteMarkdown from "svelte-markdown";
  import StepLoader from "./StepLoader.svelte";
  import { t } from "$lib";

  let {
    sheetMd = "",
    patient = {},
    artifactsData = null,
    runStatus = "idle",
    nodeStatus = "not_started",
    onEditIntake = null,
    onRerun = null,
    onBack = null,
    onReset = null,
  } = $props();

  let hasData = $derived(Boolean(sheetMd && sheetMd.trim()));
  let isRunning = $derived(
    nodeStatus === "running" || (runStatus === "running" && !hasData),
  );
  let isProcessing = $derived(!hasData && isRunning);

  let copied = $state(false);

  function copyMarkdown() {
    if (!hasData) return;
    navigator.clipboard.writeText(sheetMd);
    copied = true;
    setTimeout(() => {
      copied = false;
    }, 2500);
  }

  function printSheet() {
    if (!hasData) return;
    window.print();
  }
</script>

<div
  class="card bg-base-100/90 shadow-xl border border-base-300 backdrop-blur-md overflow-hidden transition-all duration-300"
  in:fly={{ y: 20, duration: 400, easing: cubicInOut }}
>
  <!-- Header Bar -->
  <div
    class="p-4 sm:p-5 bg-base-200/80 border-b border-base-300 flex flex-wrap items-center justify-between gap-3"
  >
    <div class="flex items-center gap-3">
      <div
        class="w-10 h-10 rounded-2xl bg-error/10 border border-error/20 flex items-center justify-center text-xl shadow-inner text-error"
      >
        🚨
      </div>
      <div>
        <div class="flex items-center gap-2">
          <span
            class="badge badge-error badge-xs font-mono font-bold text-[10px] text-white"
          >
            {t("sheet.officialProtocol")}
          </span>
          <span class="text-xs text-base-content/60 font-mono">
            final_clinical_emergency_sheet.md
          </span>
        </div>
        <h3 class="text-base font-black text-base-content font-display">
          {t("sheet.title")}
        </h3>
      </div>
    </div>

    <!-- Quick Action Buttons -->
    <div class="flex items-center gap-2">
      <button
        type="button"
        class="btn btn-outline btn-sm gap-1.5 cursor-pointer font-bold hover:scale-105 transition-transform disabled:opacity-40 disabled:cursor-not-allowed"
        onclick={printSheet}
        disabled={!hasData}
        title="Print Clinical Sheet for Patient Chart"
      >
        <span>🖨️</span>
        <span class="hidden sm:inline">{t("sheet.printBtn")}</span>
      </button>

      <button
        type="button"
        class="btn btn-secondary btn-sm gap-1.5 cursor-pointer font-bold shadow-xs hover:scale-105 transition-transform disabled:opacity-40 disabled:cursor-not-allowed"
        onclick={copyMarkdown}
        disabled={!hasData}
        title="Copy Markdown to Clipboard"
      >
        <span>{copied ? "✓" : "📋"}</span>
        <span>{copied ? t("sheet.copied") : t("sheet.copyBtn")}</span>
      </button>

      {#if onEditIntake}
        <button
          type="button"
          class="btn btn-ghost btn-sm gap-1 cursor-pointer text-xs"
          onclick={onEditIntake}
        >
          <span>✏️</span>
          <span>{t("common.editIntake")}</span>
        </button>
      {/if}
    </div>
  </div>

  <!-- Sheet Body Container -->
  <div class="p-5 sm:p-7 space-y-6">
    <!-- Clinician Validation Banner -->
    <div
      class="p-4 rounded-2xl bg-primary/5 border border-primary/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
    >
      <div class="flex items-start gap-3">
        <span class="text-2xl">📋</span>
        <div>
          <div class="font-bold text-base-content">
            {t("sheet.validationTitle")}
          </div>
          <p class="text-base-content/70 mt-0.5">
            {t("sheet.validationDesc")}
          </p>
        </div>
      </div>
    </div>

    <!-- Document Content Preview -->
    {#if isProcessing}
      <StepLoader
        icon="📋"
        title={t("sheet.finalizingTitle")}
        subtitle={t("sheet.finalizingDesc")}
        statusLabel={t("sheet.finalizingStatus")}
      />
    {:else if hasData}
      <div class="sheet-body">
        <SvelteMarkdown source={sheetMd} />
      </div>
    {:else}
      <div
        class="p-8 text-center text-base-content/60 rounded-2xl border border-dashed border-base-300 bg-base-200/20"
      >
        <div class="text-3xl mb-2">📋</div>
        <div class="font-bold text-sm text-base-content/80">
          {t("sheet.emptyTitle")}
        </div>
        <div class="text-xs text-base-content/50 mt-1">
          {t("sheet.emptyDesc")}
        </div>
      </div>
    {/if}

    <!-- Actions Footer for Sequential Navigation -->
    <div
      class="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-base-200"
    >
      {#if onBack}
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
      {:else}
        <div></div>
      {/if}

      <div class="flex flex-wrap items-center gap-2">
        {#if onReset}
          <button
            type="button"
            class="btn btn-primary btn-sm gap-1.5 shadow-md shadow-primary/20 hover:scale-105 transition-all duration-300 font-bold cursor-pointer"
            onclick={onReset}
          >
            <span>🔄 {t("sheet.newPatientBtn")}</span>
          </button>
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  /* ── Scoped to .sheet-body only — no effect on the rest of the page ── */
  .sheet-body {
    background: color-mix(
      in srgb,
      var(--color-base-200, #1e2430) 40%,
      transparent
    );
    border: 1px solid
      color-mix(in srgb, var(--color-base-300, #2a3040) 80%, transparent);
    border-radius: 1rem;
    padding: 2rem 2.25rem;
    overflow-x: auto;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 0.9375rem;
    line-height: 1.8;
    color: var(--color-base-content, #d4d8e2);
    letter-spacing: 0.01em;
  }

  /* Headings */
  .sheet-body :global(h1),
  .sheet-body :global(h2),
  .sheet-body :global(h3),
  .sheet-body :global(h4) {
    font-family: Georgia, "Times New Roman", serif;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: var(--color-base-content, #e2e6f0);
    margin-top: 1.6em;
    margin-bottom: 0.4em;
  }
  .sheet-body :global(h1) {
    font-size: 1.5rem;
    border-bottom: 2px solid color-mix(in srgb, currentColor 15%, transparent);
    padding-bottom: 0.35em;
  }
  .sheet-body :global(h2) {
    font-size: 1.2rem;
    border-bottom: 1px solid color-mix(in srgb, currentColor 12%, transparent);
    padding-bottom: 0.25em;
  }
  .sheet-body :global(h3) {
    font-size: 1.05rem;
  }
  .sheet-body :global(h4) {
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    opacity: 0.65;
  }

  /* Paragraphs */
  .sheet-body :global(p) {
    margin: 0.65em 0;
  }

  /* Emphasis */
  .sheet-body :global(strong) {
    font-weight: 700;
    color: var(--color-base-content, #e8ecf4);
  }
  .sheet-body :global(em) {
    font-style: italic;
    opacity: 0.85;
  }

  /* Horizontal rule */
  .sheet-body :global(hr) {
    border: none;
    border-top: 1px solid color-mix(in srgb, currentColor 18%, transparent);
    margin: 1.6em 0;
  }

  /* Lists */
  .sheet-body :global(ul),
  .sheet-body :global(ol) {
    padding-left: 1.4em;
    margin: 0.6em 0;
  }
  .sheet-body :global(li) {
    margin: 0.3em 0;
  }
  .sheet-body :global(li::marker) {
    color: var(--color-primary, #6c8ef5);
  }

  /* Inline code */
  .sheet-body :global(code) {
    font-family: ui-monospace, "Cascadia Code", Menlo, monospace;
    font-size: 0.82em;
    background: color-mix(
      in srgb,
      var(--color-base-300, #2a3040) 60%,
      transparent
    );
    border: 1px solid color-mix(in srgb, currentColor 12%, transparent);
    border-radius: 0.3em;
    padding: 0.1em 0.4em;
  }

  /* Code blocks */
  .sheet-body :global(pre) {
    font-family: ui-monospace, "Cascadia Code", Menlo, monospace;
    font-size: 0.8em;
    background: color-mix(
      in srgb,
      var(--color-base-300, #1a1f2e) 80%,
      transparent
    );
    border: 1px solid color-mix(in srgb, currentColor 10%, transparent);
    border-radius: 0.75em;
    padding: 1em 1.25em;
    overflow-x: auto;
    line-height: 1.6;
  }
  .sheet-body :global(pre code) {
    background: none;
    border: none;
    padding: 0;
    font-size: 1em;
  }

  /* Blockquote */
  .sheet-body :global(blockquote) {
    border-left: 3px solid var(--color-primary, #6c8ef5);
    margin: 1em 0;
    padding: 0.5em 1em;
    opacity: 0.85;
    font-style: italic;
  }

  /* Tables */
  .sheet-body :global(table) {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88em;
    margin: 1em 0;
  }
  .sheet-body :global(th) {
    font-family: ui-monospace, "Cascadia Code", Menlo, monospace;
    font-size: 0.78em;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
    border-bottom: 2px solid color-mix(in srgb, currentColor 20%, transparent);
    padding: 0.5em 0.75em;
    text-align: left;
    opacity: 0.7;
  }
  .sheet-body :global(td) {
    padding: 0.45em 0.75em;
    border-bottom: 1px solid color-mix(in srgb, currentColor 8%, transparent);
    vertical-align: top;
  }
  .sheet-body :global(tr:last-child td) {
    border-bottom: none;
  }
</style>
