<script>
  import { fly, fade } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";
  import { t } from "$lib";

  let { isOpen = false, onClose } = $props();

  const emergencyContacts = [
    {
      name: "ASPCA Animal Poison Control (APCC)",
      phone: "(888) 426-4435",
      tel: "+18884264435",
      availability: "24/7 / 365 Days",
      desc: "Premier veterinary toxicology resource for acute toxicoses and lethal ingestions.",
      badge: "Primary US / Int'l",
      badgeColor: "badge-error",
    },
    {
      name: "Pet Poison Helpline",
      phone: "(855) 764-7661",
      tel: "+18557647661",
      availability: "24/7 Dedicated",
      desc: "Comprehensive animal poison control for veterinary teams & pet owners.",
      badge: "24/7 Support",
      badgeColor: "badge-warning",
    },
    {
      name: "VPIS (Veterinary Poisons Info Service)",
      phone: "+44 (0) 20 7305 5055",
      tel: "+442073055055",
      availability: "UK & European Emergency",
      desc: "Specialized clinical toxicology guidance for veterinarians in Europe.",
      badge: "Europe / UK",
      badgeColor: "badge-info",
    },
  ];

  const rapidVitals = [
    {
      species: "Canine (Dog)",
      icon: "🐕",
      hr: "60 - 140 bpm",
      rr: "10 - 30 brpm",
      temp: "38.0 - 39.2 °C (100.4 - 102.5 °F)",
      crt: "< 2.0 sec",
      bp: "110 - 140 mmHg (Sys)",
    },
    {
      species: "Feline (Cat)",
      icon: "🐈",
      hr: "140 - 220 bpm",
      rr: "20 - 40 brpm",
      temp: "38.1 - 39.2 °C (100.5 - 102.5 °F)",
      crt: "< 2.0 sec",
      bp: "120 - 150 mmHg (Sys)",
    },
  ];

  const emergencyAntidotes = [
    {
      drug: "Naloxone",
      indication: "Opioid toxicity",
      route: "IV / IM / IN",
      dose: "0.02 - 0.04 mg/kg",
    },
    {
      drug: "Atropine",
      indication: "Organophosphate / Carbamates",
      route: "IV / IM",
      dose: "0.02 - 0.04 mg/kg (1/4 IV, rest IM/SC)",
    },
    {
      drug: "Vitamin K1 (Phytomenadione)",
      indication: "Anticoagulant rodenticides",
      route: "SC / PO with fatty meal",
      dose: "2.5 - 5.0 mg/kg/day",
    },
    {
      drug: "Intralipid 20%",
      indication: "Lipophilic toxins (Permethrin, Ivermectin, Baclofen, LAs)",
      route: "IV bolus + CRI",
      dose: "1.5 mL/kg over 15m, then 0.25 mL/kg/min",
    },
    {
      drug: "Apomorphine (Dogs only)",
      indication: "Recent non-corrosive ingestion (<2h)",
      route: "IV / Conjunctival",
      dose: "0.03 - 0.04 mg/kg IV",
    },
  ];

  let copiedText = $state("");

  function copyNumber(num) {
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(num);
      copiedText = num;
      setTimeout(() => {
        copiedText = "";
      }, 2000);
    }
  }
</script>

{#if isOpen}
  <div
    class="fixed inset-0 z-[500] flex items-center justify-center p-4 bg-black/75 backdrop-blur-md"
    transition:fade={{ duration: 250, easing: cubicInOut }}
  >
    <!-- Modal Card with fancy medical border & glow -->
    <div
      class="relative w-full max-w-3xl max-h-[90vh] overflow-y-auto bg-base-100 rounded-3xl border border-error/30 shadow-[0_0_50px_rgba(239,68,68,0.25)] flex flex-col transition-all duration-300"
      transition:fly={{ y: 30, duration: 350, easing: cubicInOut }}
    >
      <!-- Red emergency alert header -->
      <div
        class="sticky top-0 z-20 bg-base-100/95 backdrop-blur-md px-6 py-4 border-b border-error/20 flex items-center justify-between"
      >
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 rounded-2xl bg-error/20 border border-error/40 flex items-center justify-center text-error animate-pulse"
          >
            <svg
              class="w-6 h-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3
                class="text-base font-black tracking-tight text-base-content uppercase font-display"
              >
                {t("hotlineModal.title")}
              </h3>
              <span
                class="badge badge-error badge-sm text-white font-mono font-black"
                >CODE RED</span
              >
            </div>
            <p class="text-xs text-base-content/60 font-mono">
              {t("hotlineModal.subtitle")}
            </p>
          </div>
        </div>

        <button
          type="button"
          class="btn btn-ghost btn-circle btn-sm text-base-content/70 hover:bg-base-200 cursor-pointer"
          onclick={onClose}
          aria-label="Close emergency modal"
        >
          ✕
        </button>
      </div>

      <!-- Content Body -->
      <div class="p-6 space-y-6">
        <!-- 24/7 Poison Control Hotlines -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <span
              class="text-xs font-black uppercase tracking-wider text-error font-mono flex items-center gap-1.5"
            >
              <span>🚨</span> {t("hotlineModal.contactsTitle")}
            </span>
            <span class="text-[11px] text-base-content/50 font-mono"
              >Tap phone to dial or copy</span
            >
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            {#each emergencyContacts as contact}
              <div
                class="bg-base-200/70 border border-base-300 rounded-2xl p-4 flex flex-col justify-between hover:border-error/40 hover:bg-base-200 transition-all duration-300 ease-in-out group shadow-sm"
              >
                <div>
                  <div class="flex items-center flex-col justify-center mb-1.5">
                    <span
                      class="text-[10px] text-nowrap text-base-content/50 font-mono"
                      >{contact.availability}</span
                    >
                    <span
                      class="badge text-nowrap {contact.badgeColor} badge-xs font-mono font-bold"
                      >{contact.badge}</span
                    >
                  </div>
                  <h4
                    class="font-bold text-xs text-base-content leading-tight mb-1"
                  >
                    {contact.name}
                  </h4>
                  <p class="text-[11px] text-base-content/60 leading-snug mb-3">
                    {contact.desc}
                  </p>
                </div>

                <div
                  class="pt-2 border-t border-base-content/10 flex items-center gap-2"
                >
                  <a
                    href="tel:{contact.tel}"
                    class="btn text-nowrap btn-error btn-xs flex-1 text-white font-mono font-black gap-1 shadow-sm hover:scale-105 transition-transform duration-200"
                  >
                    <span>📞</span>
                    {contact.phone}
                  </a>
                  <button
                    type="button"
                    class="btn btn-ghost btn-xs text-base-content/60 hover:text-base-content px-2 cursor-pointer"
                    title="Copy number"
                    onclick={() => copyNumber(contact.phone)}
                  >
                    {#if copiedText === contact.phone}
                      <span class="text-success text-[10px] font-bold"
                        >Copied!</span
                      >
                    {:else}
                      <svg
                        class="w-3.5 h-3.5"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                        />
                      </svg>
                    {/if}
                  </button>
                </div>
              </div>
            {/each}
          </div>
        </div>

        <!-- Rapid Normal Vitals Reference (Canine vs Feline) -->
        <div>
          <span
            class="text-xs font-black uppercase tracking-wider text-primary font-mono flex items-center gap-1.5 mb-3"
          >
            <span>🩺</span> {t("hotlineModal.vitalsTitle")}
          </span>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            {#each rapidVitals as v}
              <div
                class="bg-base-200/50 border border-base-300 rounded-2xl p-4"
              >
                <div
                  class="flex items-center gap-2 mb-3 pb-2 border-b border-base-content/10"
                >
                  <span class="text-lg">{v.icon}</span>
                  <span
                    class="font-black text-xs text-base-content uppercase font-display"
                    >{v.species}</span
                  >
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div class="bg-base-100/70 p-2 rounded-xl">
                    <span
                      class="text-[10px] text-base-content/50 uppercase block"
                      >Heart Rate</span
                    >
                    <span class="font-black text-primary">{v.hr}</span>
                  </div>
                  <div class="bg-base-100/70 p-2 rounded-xl">
                    <span
                      class="text-[10px] text-base-content/50 uppercase block"
                      >Respiratory Rate</span
                    >
                    <span class="font-bold text-accent">{v.rr}</span>
                  </div>
                  <div class="bg-base-100/70 p-2 rounded-xl">
                    <span
                      class="text-[10px] text-base-content/50 uppercase block"
                      >Rectal Temp</span
                    >
                    <span class="font-bold text-base-content">{v.temp}</span>
                  </div>
                  <div class="bg-base-100/70 p-2 rounded-xl">
                    <span
                      class="text-[10px] text-base-content/50 uppercase block"
                      >CRT & Blood Press.</span
                    >
                    <span class="font-bold text-base-content"
                      >{v.crt} · {v.bp}</span
                    >
                  </div>
                </div>
              </div>
            {/each}
          </div>
        </div>

        <!-- Emergency Antidotes Fast Table -->
        <div>
          <span
            class="text-xs font-black uppercase tracking-wider text-warning font-mono flex items-center gap-1.5 mb-3"
          >
            <span>💉</span> {t("hotlineModal.antidotesTitle")}
          </span>
          <div
            class="overflow-x-auto rounded-2xl border border-base-300 bg-base-200/40"
          >
            <table class="table table-xs w-full">
              <thead>
                <tr
                  class="bg-base-300/50 text-base-content/60 font-mono text-[10px]"
                >
                  <th>{t("hotlineModal.drugCol")}</th>
                  <th>{t("hotlineModal.targetCol")}</th>
                  <th>{t("hotlineModal.routeCol")}</th>
                  <th>{t("hotlineModal.dosageCol")}</th>
                </tr>
              </thead>
              <tbody class="font-mono text-xs">
                {#each emergencyAntidotes as a}
                  <tr
                    class="hover:bg-base-100/50 border-b border-base-content/5"
                  >
                    <td class="font-bold text-primary">{a.drug}</td>
                    <td class="text-base-content/80">{a.indication}</td>
                    <td
                      ><span class="badge badge-ghost badge-xs font-mono"
                        >{a.route}</span
                      ></td
                    >
                    <td class="font-semibold text-warning">{a.dose}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div
        class="sticky bottom-0 bg-base-100/95 backdrop-blur-md px-6 py-3 border-t border-base-content/10 flex items-center justify-between text-xs font-mono text-base-content/50"
      >
        <span class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-success animate-pulse"></span>
          Emergency Protocol Active · ASPCA / BSAVA Verified
        </span>
        <button
          type="button"
          class="btn btn-sm btn-primary rounded-xl px-5 font-bold cursor-pointer"
          onclick={onClose}
        >
          {t("hotlineModal.closeBtn")}
        </button>
      </div>
    </div>
  </div>
{/if}
