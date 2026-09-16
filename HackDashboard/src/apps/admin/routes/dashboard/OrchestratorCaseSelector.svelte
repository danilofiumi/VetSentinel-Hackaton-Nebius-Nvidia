<script>
  import { t } from "$lib";

  let {
    clinicalCases = [],
    currentCaseKey = "chocolate",
    onSelectCase,
  } = $props();
</script>

<div class="space-y-2 p-3.5 rounded-2xl bg-base-200/50 border border-base-300">
  <div class="flex items-center justify-between">
    <span
      class="text-[11px] font-bold uppercase tracking-wider text-base-content/70 font-label flex items-center gap-1.5"
    >
      <span>🩺 {t("orchestrator.selectCase")}</span>
    </span>
    <span class="badge badge-xs badge-outline font-mono">{t("orchestrator.quickCaseBadge")}</span>
  </div>
  <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
    {#each clinicalCases as c}
      <button
        type="button"
        class="btn btn-sm text-xs font-bold justify-start gap-2 h-auto py-2 transition-all duration-300 ease-in-out cursor-pointer {currentCaseKey ===
        c.id
          ? 'btn-primary text-white shadow-md shadow-primary/20 scale-[1.02]'
          : 'btn-ghost bg-base-100 hover:bg-base-200 text-base-content'}"
        onclick={() => onSelectCase && onSelectCase(c)}
      >
        <span class="text-base">{c.icon}</span>
        <span class="truncate">{c.name}</span>
      </button>
    {/each}
  </div>
</div>
