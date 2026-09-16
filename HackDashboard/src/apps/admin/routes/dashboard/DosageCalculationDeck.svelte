<script>
  import { fade, fly } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";
  import { t } from "$lib";

  let { drugs = [], patient = {} } = $props();

  let viewMode = $state("table"); // "cards" | "table"
  let searchQuery = $state("");

  // Helper to categorize route and assign clear icons and badge styling
  function getRouteMeta(route = "") {
    const r = (route || "").toLowerCase();
    if (r.includes("iv") || r.includes("intravenous")) {
      return {
        icon: "💉",
        label: "IV",
        color: "bg-error/10 text-error border-error/30 dark:bg-error/20",
      };
    }
    if (r.includes("po") || r.includes("oral") || r.includes("mouth")) {
      return {
        icon: "💊",
        label: "PO",
        color:
          "bg-primary/10 text-primary border-primary/30 dark:bg-primary/20",
      };
    }
    if (
      r.includes("tube") ||
      r.includes("lavage") ||
      r.includes("slurry") ||
      r.includes("orogastric")
    ) {
      return {
        icon: "🧪",
        label: "Tube",
        color:
          "bg-warning/10 text-warning border-warning/30 dark:bg-warning/20",
      };
    }
    if (
      r.includes("fluid") ||
      r.includes("infusion") ||
      r.includes("cri") ||
      r.includes("ringer")
    ) {
      return {
        icon: "💧",
        label: "Infusion",
        color: "bg-info/10 text-info border-info/30 dark:bg-info/20",
      };
    }
    return {
      icon: "🩺",
      label: "Admin",
      color: "bg-base-200 text-base-content/80 border-base-300",
    };
  }

  // Helper to split raw dosage string into a prominent primary number and secondary titration/instructions
  function parseDose(doseStr = "") {
    if (!doseStr) return { main: "Standard dose", note: "" };

    const semiIdx = doseStr.indexOf(";");
    const parenIdx = doseStr.indexOf("(");

    let splitIdx = -1;
    if (semiIdx > 0) {
      splitIdx = semiIdx;
    } else if (parenIdx > 0) {
      const parenContent = doseStr.slice(parenIdx);
      if (
        parenContent.length > 14 ||
        parenContent.toLowerCase().includes("start") ||
        parenContent.toLowerCase().includes("repeat") ||
        parenContent.toLowerCase().includes("titrat") ||
        parenContent.toLowerCase().includes("recirculation") ||
        parenContent.toLowerCase().includes("maintenance")
      ) {
        splitIdx = parenIdx;
      }
    }

    if (splitIdx > 0) {
      const main = doseStr.slice(0, splitIdx).trim();
      let note = doseStr.slice(splitIdx).trim();
      if (note.startsWith(";") || note.startsWith(",")) {
        note = note.slice(1).trim();
      }
      if (note.startsWith("(") && note.endsWith(")")) {
        note = note.slice(1, -1).trim();
      }
      return { main, note };
    }

    return { main: doseStr, note: "" };
  }

  // Helper to split raw route into a primary route code (IV, PO, SC, etc.) and administration instructions/qualifiers
  function parseRoute(routeStr = "") {
    if (!routeStr) return { main: "Admin", note: "" };

    const semiIdx = routeStr.indexOf(";");
    const parenIdx = routeStr.indexOf("(");

    let splitIdx = -1;
    if (semiIdx > 0) {
      splitIdx = semiIdx;
    } else if (parenIdx > 0) {
      splitIdx = parenIdx;
    }

    if (splitIdx > 0) {
      const main = routeStr.slice(0, splitIdx).trim();
      let note = routeStr.slice(splitIdx).trim();
      if (note.startsWith(";") || note.startsWith(",")) {
        note = note.slice(1).trim();
      }
      if (note.startsWith("(") && note.endsWith(")")) {
        note = note.slice(1, -1).trim();
      }
      return { main: main || routeStr, note };
    }

    return { main: routeStr, note: "" };
  }

  let filteredDrugs = $derived.by(() => {
    if (!searchQuery.trim()) return drugs;
    const q = searchQuery.toLowerCase().trim();
    return drugs.filter(
      (d) =>
        (d.name || "").toLowerCase().includes(q) ||
        (d.route || "").toLowerCase().includes(q) ||
        (d.calculatedDose || "").toLowerCase().includes(q) ||
        (d.concentration || "").toLowerCase().includes(q),
    );
  });
</script>

<div class="space-y-3 pt-1">
  <!-- Section Header with Formula and View Switcher -->
  <div
    class="flex flex-col md:flex-row md:items-center justify-between gap-3 p-3 rounded-2xl bg-base-100/90 border border-base-300 shadow-sm"
  >
    <div class="space-y-1">
      <div class="flex items-center gap-2 flex-wrap">
        <span
          class="text-xs sm:text-sm font-black uppercase tracking-wider text-base-content font-display flex items-center gap-1.5"
        >
          <span>⚖️</span>
          <span>{t("protocol.dosagesTitle", { species: patient.specie || "Patient", weight: patient.peso || "?" })}</span>
        </span>
        <span
          class="badge badge-sm badge-primary font-mono font-bold shadow-xs"
        >
          {t("protocol.autoCalculated")}
        </span>
        {#if drugs.length > 0}
          <span
            class="badge badge-sm badge-ghost font-mono text-[10px] text-base-content/60"
          >
            {filteredDrugs.length}
            {filteredDrugs.length === 1 ? t("protocol.medication") : t("protocol.medications")}
          </span>
        {/if}
      </div>
      <p class="text-[11px] text-base-content/60 font-mono">
        {t("protocol.formulaPrefix")}
        <code
          class="font-bold text-primary bg-primary/10 px-1.5 py-0.5 rounded"
        >
          Dose = Rate/kg × {patient.peso || 0} kg
        </code>
      </p>
    </div>

    <!-- Controls: Search filter & Cards/Table View Switcher -->
    <div class="flex items-center gap-2 self-start md:self-auto flex-wrap">
      {#if drugs.length > 3}
        <div class="relative">
          <input
            type="text"
            placeholder={t("protocol.filterDrugsPlaceholder")}
            bind:value={searchQuery}
            class="input input-xs input-bordered rounded-xl w-32 sm:w-40 font-mono text-xs pl-6"
          />
          <span
            class="absolute left-2 top-1/2 -translate-y-1/2 text-[10px] text-base-content/50"
          >
            🔍
          </span>
          {#if searchQuery}
            <button
              type="button"
              class="absolute right-1.5 top-1/2 -translate-y-1/2 text-[10px] text-base-content/40 hover:text-base-content"
              onclick={() => (searchQuery = "")}
            >
              ✕
            </button>
          {/if}
        </div>
      {/if}

      <!-- Toggle View buttons -->
      <div class="join bg-base-200/80 p-0.5 rounded-xl border border-base-300">
        <button
          type="button"
          class="btn btn-xs join-item font-bold gap-1 transition-all {viewMode ===
          'cards'
            ? 'btn-primary shadow-xs'
            : 'btn-ghost text-base-content/70 hover:text-base-content'}"
          onclick={() => (viewMode = "cards")}
          title="Switch to detailed Medication Cards view"
        >
          <span>🎴</span>
          <span class="hidden sm:inline">{t("protocol.viewCards")}</span>
        </button>
        <button
          type="button"
          class="btn btn-xs join-item font-bold gap-1 transition-all {viewMode ===
          'table'
            ? 'btn-primary shadow-xs'
            : 'btn-ghost text-base-content/70 hover:text-base-content'}"
          onclick={() => (viewMode = "table")}
          title="Switch to compact Data Table view"
        >
          <span>📊</span>
          <span class="hidden sm:inline">{t("protocol.viewTable")}</span>
        </button>
      </div>
    </div>
  </div>

  {#if filteredDrugs.length === 0}
    <div
      class="p-8 text-center text-base-content/60 rounded-2xl border border-dashed border-base-300 bg-base-200/20 space-y-2"
    >
      <div class="text-3xl">💊</div>
      <div class="font-bold text-sm text-base-content/80">
        {t("protocol.noMedicationsMatched")}
      </div>
      <p class="text-xs text-base-content/50">
        {t("protocol.noMedicationsDesc")}
      </p>
    </div>
  {:else if viewMode === "cards"}
    <!-- ================================================================= -->
    <!-- VISUAL STRATEGY: CLINICAL DOSAGE CARDS (Zero Overflow, Legible)   -->
    <!-- ================================================================= -->
    <div
      class="grid grid-cols-1 lg:grid-cols-2 gap-3.5"
      in:fade={{ duration: 250, easing: cubicInOut }}
    >
      {#each filteredDrugs as d, i}
        {@const routeMeta = getRouteMeta(d.route)}
        {@const dose = parseDose(d.calculatedDose)}
        {@const parsedRoute = parseRoute(d.route)}
        <div
          class="card bg-base-100/95 border border-base-300 hover:border-primary/40 shadow-sm hover:shadow-md rounded-2xl transition-all duration-300 p-4 flex flex-col justify-between gap-3 relative overflow-hidden group"
          in:fly={{ y: 12, duration: 250, delay: i * 35, easing: cubicInOut }}
        >
          <!-- Accent line indicator -->
          <div
            class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary/30 via-primary to-primary/30 opacity-70 group-hover:opacity-100 transition-opacity"
          ></div>

          <!-- Card Header: Name, Route & Standard Rate -->
          <div class="flex items-start justify-between gap-3 pt-1">
            <div class="flex items-start gap-2.5 min-w-0">
              <div
                class="w-9 h-9 rounded-xl shrink-0 flex items-center justify-center text-lg bg-base-200 border border-base-300 shadow-inner group-hover:scale-105 transition-transform"
              >
                {routeMeta.icon}
              </div>
              <div class="min-w-0">
                <h4
                  class="text-sm sm:text-base font-black text-base-content font-display tracking-tight leading-tight whitespace-normal break-words"
                >
                  {d.name}
                </h4>
                <div class="flex items-center gap-1.5 mt-1 flex-wrap">
                  <span class="text-[11px] font-mono text-base-content/60">
                    {t("protocol.standardRate")}
                  </span>
                  <span
                    class="font-mono text-[11px] font-bold text-base-content/80 bg-base-200/80 px-1.5 py-0.5 rounded border border-base-300/60"
                  >
                    {d.standardDose}
                  </span>
                </div>
              </div>
            </div>

            <!-- Route Tag -->
            <div class="shrink-0 text-right">
              <span
                class="inline-flex items-center gap-1 font-mono text-[11px] font-bold uppercase px-2.5 py-1 rounded-xl border {routeMeta.color} shadow-xs whitespace-normal max-w-[140px] leading-tight"
              >
                <span>{routeMeta.icon}</span>
                <span class="min-w-0 break-words [overflow-wrap:anywhere]">{parsedRoute.main}</span>
              </span>
              {#if parsedRoute.note}
                <div
                  class="text-[10px] text-base-content/80 font-mono mt-1 text-right max-w-[150px] break-words leading-tight flex items-center justify-end gap-1 ml-auto"
                >
                  <span class="text-primary font-bold shrink-0">ℹ️</span>
                  <span>{parsedRoute.note}</span>
                </div>
              {/if}
            </div>
          </div>

          <!-- Hero Calculated Patient Dose Box -->
          <div
            class="p-3.5 rounded-xl bg-gradient-to-br from-primary/10 via-primary/5 to-transparent border border-primary/25 space-y-1.5 shadow-xs"
          >
            <div
              class="flex items-center justify-between text-[10px] uppercase font-bold text-primary font-mono tracking-wider"
            >
              <span class="flex items-center gap-1">
                <span>🎯</span>
                <span>{t("protocol.calculatedPatientDose")}</span>
              </span>
              <span
                class="badge badge-xs badge-primary font-mono font-bold text-[9px] text-primary-content uppercase px-1.5 py-0.5"
              >
                {t("protocol.patientDoseLabel", { weight: patient.peso })}
              </span>
            </div>

            <!-- Primary Dose Callout -->
            <div
              class="font-mono text-base sm:text-lg font-black text-primary whitespace-normal break-words leading-tight"
            >
              {dose.main}
            </div>

            <!-- Titration / Clinical Administration Instructions -->
            {#if dose.note}
              <div
                class="text-[11px] text-base-content/85 leading-relaxed pt-2 mt-1 border-t border-primary/20 flex items-start gap-1.5 bg-primary/5 -mx-1.5 -mb-1.5 p-2 rounded-b-lg"
              >
                <span class="text-primary font-bold shrink-0 text-xs mt-0.5"
                  >ℹ️</span
                >
                <span class="font-medium whitespace-normal break-words">
                  {dose.note}
                </span>
              </div>
            {/if}
          </div>

          <!-- Card Footer: Formulation & Monitoring in 2 neat blocks -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-0.5">
            <!-- Formulation / Concentration -->
            <div
              class="p-2.5 rounded-xl bg-base-200/50 border border-base-200/80 text-xs flex items-start gap-2"
            >
              <span class="text-sm shrink-0">📦</span>
              <div class="min-w-0 flex-1">
                <span
                  class="text-[10px] uppercase font-bold text-base-content/50 block font-label tracking-wider"
                >
                  {t("protocol.formulationSupply")}
                </span>
                <span
                  class="font-mono text-[11px] text-base-content/90 font-medium whitespace-normal break-words block mt-0.5"
                >
                  {d.concentration || t("protocol.standardClinicalStock")}
                </span>
              </div>
            </div>

            <!-- Safety & Monitoring Notes -->
            <div
              class="p-2.5 rounded-xl bg-warning/5 border border-warning/20 text-xs flex items-start gap-2"
            >
              <span class="text-sm shrink-0">🛡️</span>
              <div class="min-w-0 flex-1">
                <span
                  class="text-[10px] uppercase font-bold text-warning/90 dark:text-warning block font-label tracking-wider"
                >
                  {t("protocol.monitoringSafety")}
                </span>
                <span
                  class="text-[11px] text-base-content/80 leading-relaxed whitespace-normal break-words block mt-0.5"
                >
                  {d.notes || "Monitor patient vitals continually."}
                </span>
              </div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <!-- ================================================================= -->
    <!-- VISUAL STRATEGY: REDESIGNED DATA TABLE (Zero Overflow, Responsive) -->
    <!-- ================================================================= -->
    <div
      class="overflow-x-auto rounded-2xl border border-base-300 shadow-sm bg-base-100"
      in:fade={{ duration: 250, easing: cubicInOut }}
    >
      <table class="table table-zebra table-sm w-full">
        <thead>
          <tr
            class="bg-base-200/80 text-base-content/70 text-[11px] uppercase font-bold tracking-wider font-label"
          >
            <th class="min-w-[180px]">{t("protocol.thDrug")}</th>
            <th class="min-w-[140px]">{t("protocol.thStandardRate")}</th>
            <th class="min-w-[240px]">{t("protocol.thCalculatedDose", { weight: patient.peso })}</th>
            <th class="min-w-[110px]">{t("protocol.thRoute")}</th>
            <th class="min-w-[150px]">{t("protocol.thFormulation")}</th>
            <th class="min-w-[220px]">{t("protocol.thSafetyNotes")}</th>
          </tr>
        </thead>
        <tbody class="text-xs">
          {#each filteredDrugs as d}
            {@const routeMeta = getRouteMeta(d.route)}
            {@const dose = parseDose(d.calculatedDose)}
            {@const parsedRoute = parseRoute(d.route)}
            <tr class="hover:bg-primary/5 transition-colors align-top">
              <!-- Drug Name -->
              <td
                class="font-black text-base-content font-display whitespace-normal break-words"
              >
                <div class="flex items-center gap-1.5">
                  <span class="text-sm">{routeMeta.icon}</span>
                  <span>{d.name}</span>
                </div>
              </td>

              <!-- Standard Rate -->
              <td
                class="font-mono text-base-content/70 whitespace-normal break-words"
              >
                {d.standardDose}
              </td>

              <!-- Calculated Patient Dose (No rigid badge, wraps cleanly) -->
              <td>
                <div
                  class="p-2.5 rounded-xl bg-primary/10 border border-primary/25 text-primary space-y-1 whitespace-normal break-words max-w-sm"
                >
                  <div
                    class="font-mono font-bold text-xs sm:text-[13px] leading-snug"
                  >
                    {dose.main}
                  </div>
                  {#if dose.note}
                    <div
                      class="text-[10px] font-normal text-base-content/75 pt-1 border-t border-primary/20 leading-relaxed"
                    >
                      <span class="font-semibold text-primary"
                        >{t("protocol.instructionsLabel")}</span
                      >
                      {dose.note}
                    </div>
                  {/if}
                </div>
              </td>

              <!-- Route (No rigid badge, custom pill with wrap & instructions) -->
              <td>
                <div class="space-y-1">
                  <span
                    class="inline-flex items-center gap-1 font-mono text-[11px] font-bold uppercase px-2 py-1 rounded-lg border {routeMeta.color} whitespace-normal max-w-[130px] leading-tight"
                  >
                    <span>{routeMeta.icon}</span>
                    <span class="min-w-0 break-words [overflow-wrap:anywhere]">{parsedRoute.main}</span>
                  </span>
                  {#if parsedRoute.note}
                    <div
                      class="text-[10px] text-base-content/80 leading-tight flex items-start gap-1 max-w-[170px] break-words pt-0.5"
                    >
                      <span class="text-primary font-bold shrink-0 text-[10px]">ℹ️</span>
                      <span class="font-medium">{parsedRoute.note}</span>
                    </div>
                  {/if}
                </div>
              </td>

              <!-- Formulation -->
              <td
                class="text-base-content/70 font-mono text-[11px] whitespace-normal break-words"
              >
                {d.concentration || "—"}
              </td>

              <!-- Notes -->
              <td
                class="text-base-content/80 text-[11px] leading-relaxed whitespace-normal break-words max-w-xs"
              >
                {d.notes || "—"}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>
