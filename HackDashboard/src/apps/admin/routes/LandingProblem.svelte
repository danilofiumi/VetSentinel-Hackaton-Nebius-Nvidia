<script>
  import { cubicInOut } from "svelte/easing";
  import { fly } from "svelte/transition";
  import Image from "./Image.svelte";
  import { t } from "$lib";

  let speciesHazards = $derived([
    {
      id: "feline",
      name: t("landing.problem.felineTitle"),
      image: "/images/vector/hazard_cat_lily.jpg",
      mass: "4.0 kg",
      hazard: t("landing.problem.felineHazard"),
      badgeColor: "badge-error",
      physiology: t("landing.problem.felinePhysiology"),
      clinicalRule: t("landing.problem.felineClinicalRule"),
    },
    {
      id: "canine",
      name: t("landing.problem.canineTitle"),
      image: "/images/vector/hazard_dog_choco.jpg",
      mass: "15.0 kg",
      hazard: t("landing.problem.canineHazard"),
      badgeColor: "badge-warning",
      physiology: t("landing.problem.caninePhysiology"),
      clinicalRule: t("landing.problem.canineClinicalRule"),
    },
    {
      id: "exotic",
      name: t("landing.problem.exoticTitle"),
      image: "/images/vector/hazard_ferret_dose.jpg",
      mass: "1.0 kg",
      hazard: t("landing.problem.exoticHazard"),
      badgeColor: "badge-accent",
      physiology: t("landing.problem.exoticPhysiology"),
      clinicalRule: t("landing.problem.exoticClinicalRule"),
    },
  ]);
</script>

<section
  id="story"
  class="py-16 sm:py-20 border-b border-base-content/10 relative bg-white from-base-100 via-base-300/60 to-base-200 overflow-hidden"
>
  <!-- Fancy Corner Aurora Emergency Gradients -->

  <div
    class="absolute -bottom-36 -right-36 w-[550px] h-[550px] bg-[radial-gradient(circle,rgba(245,158,11,0.12)_0%,transparent_70%)] blur-3xl pointer-events-none -z-10"
    aria-hidden="true"
  ></div>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 space-y-12">
    <!-- Header -->
    <div class="text-center max-w-3xl mx-auto space-y-3">
      <div
        class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-error/10 border border-error/20 text-error font-mono text-xs font-bold uppercase tracking-wider"
      >
        <span>⏱️</span>
        <span>{t("landing.problem.badge")}</span>
      </div>
      <h2
        class="text-3xl sm:text-4xl lg:text-5xl font-black font-display tracking-tight text-base-content"
      >
        {t("landing.problem.title")}
      </h2>
      <p class="text-sm sm:text-base text-base-content/70 font-sans">
        {t("landing.problem.subtitle")}
      </p>
    </div>

    <!-- Night-Shift ER Clinician Visual Narrative Split with Gradient Shell -->
    <div
      class="p-[1.5px] rounded-3xl bg-gradient-to-r from-error/40 via-base-content/10 to-warning/35 shadow-xl"
    >
      <div
        class="card bg-gradient-to-br from-base-100/95 via-base-100/90 to-base-200/80 rounded-[calc(1.5rem-1.5px)] overflow-hidden backdrop-blur-xl"
      >
        <div class="grid grid-cols-1 lg:grid-cols-12 items-center">
          <!-- Visual: The Night Shift Vet -->
          <div
            class="lg:col-span-6 relative aspect-video sm:aspect-[4/3] lg:aspect-auto h-full min-h-[340px] bg-slate-950"
          >
            <Image
              src="/images/vector/vet_night_shift.jpg"
              alt="Stylized 2D vector illustration of emergency veterinarian at clinical telemetry workstation in acute ICU at 11:43 PM analyzing toxicology protocols"
              class="w-full h-full object-cover"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-slate-950/85 via-transparent to-transparent pointer-events-none"
            ></div>

            <div class="absolute bottom-4 left-4 right-4 text-white">
              <span
                class="badge badge-error font-mono text-[10px] font-bold uppercase tracking-wider mb-1.5"
              >
                {t("landing.problem.timeBadge")}
              </span>
              <p class="font-display font-bold text-base sm:text-lg">
                {t("landing.problem.soloTitle")}
              </p>
              <p class="text-xs text-white/80 font-sans mt-0.5">
                {t("landing.problem.soloDesc")}
              </p>
            </div>
          </div>

          <!-- Clinical Contrast Copy -->
          <div class="lg:col-span-6 p-6 sm:p-8 space-y-5">
            <div>
              <h3
                class="text-xl sm:text-2xl font-bold font-display text-base-content"
              >
                {t("landing.problem.nightmareTitle")}
              </h3>
              <p
                class="text-xs sm:text-sm text-base-content/75 font-sans mt-1 leading-relaxed"
              >
                {t("landing.problem.nightmareDesc")}
              </p>
            </div>

            <div class="space-y-3">
              <div
                class="p-3.5 rounded-2xl bg-error/5 border border-error/20 flex items-start gap-3"
              >
                <span class="text-error text-base">✕</span>
                <div>
                  <p class="text-xs font-bold text-base-content font-display">
                    {t("landing.problem.pain1Title")}
                  </p>
                  <p class="text-[11px] text-base-content/70 mt-0.5">
                    {t("landing.problem.pain1Desc")}
                  </p>
                </div>
              </div>

              <div
                class="p-3.5 rounded-2xl bg-error/5 border border-error/20 flex items-start gap-3"
              >
                <span class="text-error text-base">✕</span>
                <div>
                  <p class="text-xs font-bold text-base-content font-display">
                    {t("landing.problem.pain2Title")}
                  </p>
                  <p class="text-[11px] text-base-content/70 mt-0.5">
                    {t("landing.problem.pain2Desc")}
                  </p>
                </div>
              </div>

              <div
                class="p-3.5 rounded-2xl bg-success/10 border border-success/30 flex items-start gap-3"
              >
                <span class="text-success text-base">✓</span>
                <div>
                  <p class="text-xs font-bold text-success font-display">
                    {t("landing.problem.solTitle")}
                  </p>
                  <p class="text-[11px] text-base-content/80 mt-0.5">
                    {t("landing.problem.solDesc")}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 3 Species Hazard Cards with Real Animal Photos -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      {#each speciesHazards as item}
        <div
          class="card bg-gradient-to-b from-base-100 via-base-100/95 to-base-200/50 border border-base-content/10 shadow-md hover:shadow-2xl rounded-3xl overflow-hidden hover:border-primary/50 transition-all duration-500 ease-out hover:-translate-y-1.5 flex flex-col justify-between group"
        >
          <div>
            <div class="relative h-48 overflow-hidden bg-slate-950">
              <Image
                src={item.image}
                alt={item.name}
                class="w-full h-full object-cover hover:scale-105 transition-transform duration-500"
              />
              <div
                class="absolute inset-0 bg-gradient-to-t from-base-100/90 via-transparent to-transparent pointer-events-none"
              ></div>
              <div class="absolute top-3 right-3">
                <span
                  class="badge {item.badgeColor} font-mono font-bold text-[10px] text-white py-2 px-2.5 shadow-sm"
                >
                  {item.hazard}
                </span>
              </div>
              <div class="absolute bottom-2 left-4">
                <span
                  class="badge badge-neutral badge-xs font-mono font-bold text-white"
                >
                  {t("landing.problem.massLabel")} {item.mass}
                </span>
              </div>
            </div>

            <div class="p-5 pt-3">
              <h3 class="text-base font-bold font-display text-base-content">
                {item.name}
              </h3>
              <p
                class="text-xs text-base-content/70 mt-2 font-sans leading-relaxed"
              >
                {item.physiology}
              </p>
            </div>
          </div>

          <div class="p-4 bg-base-200/50 border-t border-base-content/10">
            <p class="text-[11px] text-base-content/85 font-sans">
              <strong class="text-primary font-bold">{t("landing.problem.priorityLabel")}</strong>
              {item.clinicalRule}
            </p>
          </div>
        </div>
      {/each}
    </div>
  </div>
</section>
