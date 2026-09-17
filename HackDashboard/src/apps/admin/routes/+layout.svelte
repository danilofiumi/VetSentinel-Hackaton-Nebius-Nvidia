<script>
  import "$css";
  import { onMount } from "svelte";
  import { beforeNavigate, afterNavigate, onNavigate } from "$app/navigation";
  import { page, navigating } from "$app/state";
  import ClinicalVitalsBanner from "./ClinicalVitalsBanner.svelte";
  import EmergencyProtocolModal from "./EmergencyProtocolModal.svelte";
  import ClinicalFooter from "./ClinicalFooter.svelte";
  import VetSentinelLogo from "./VetSentinelLogo.svelte";
  import LanguageSelector from "./LanguageSelector.svelte";
  import { t } from "$lib";

  let { children } = $props();
  let isDashboard = $derived(page?.url?.pathname?.startsWith("/dashboard"));

  onNavigate((navigation) => {
    // @ts-ignore <-- This is a private API so we need to ignore the TS error
    if (!document.startViewTransition) return;
    // Add a class to the main content container for the animation
    const content = document.querySelector(".content");
    content?.classList.add("swipe-left"); // Add swipe-left class

    return new Promise((resolve) => {
      // @ts-ignore <-- This is a private API so we need to ignore the TS error
      document.startViewTransition(async () => {
        resolve();
        await navigation.complete;

        // Remove the class after transition ends
        content?.classList.remove("swipe-left");
      });
    });
  });

  beforeNavigate(({ cancel }) => {
    console.log("Navigation is about to happen");

    // You can cancel navigation like this:
    // cancel();
  });
  () => {
    // Disable smooth scrolling during route transitions to prevent SvelteKit conflicts
    if (typeof document !== "undefined") {
      document.documentElement.style.scrollBehavior = "auto";
    }
  };

  afterNavigate(() => {
    // Re-enable smooth scrolling after SvelteKit has finished transitioning the page
    setTimeout(() => {
      if (typeof document !== "undefined") {
        document.documentElement.style.scrollBehavior = "smooth";
      }
    }, 50);
  });

  const clinicalThemes = [
    { id: "emerald", label: "Surgical Emerald", icon: "🩺", ward: "Surgery" },
    { id: "forest", label: "ICU Forest", icon: "🌲", ward: "Critical Care" },
    { id: "night", label: "Trauma Night", icon: "🌌", ward: "Trauma Unit" },
    { id: "dark", label: "Clinical Dark", icon: "🌙", ward: "Inpatient" },
    { id: "luxury", label: "Executive Clinic", icon: "👑", ward: "Specialist" },
    { id: "dim", label: "Diagnostic Dim", icon: "🌒", ward: "Radiology" },
    { id: "synthwave", label: "Telemetry Neon", icon: "🪩", ward: "Telemetry" },
    { id: "dracula", label: "Toxicology Red", icon: "🧛", ward: "Toxicology" },
    { id: "nord", label: "Sterile Ward", icon: "❄️", ward: "Sterile" },
    { id: "sunset", label: "Emergency Sunset", icon: "🌅", ward: "Triage" },
    {
      id: "coffee",
      label: "On-Call Coffee",
      icon: "☕",
      ward: "Doctor Lounge",
    },
    { id: "lofi", label: "Pathology Lab", icon: "⚪", ward: "Diagnostics" },
  ];

  let currentTheme = $state("emerald");
  let isEmergencyModalOpen = $state(false);

  onMount(() => {
    try {
      const savedTheme = localStorage.getItem("vetsentinel-theme");
      if (savedTheme && clinicalThemes.some((t) => t.id === savedTheme)) {
        currentTheme = savedTheme;
      }
      document.documentElement.setAttribute("data-theme", currentTheme);
    } catch {
      // Ignore localStorage access restrictions
    }
  });

  function setTheme(themeId) {
    currentTheme = themeId;
    if (typeof document !== "undefined") {
      document.documentElement.setAttribute("data-theme", themeId);
      try {
        localStorage.setItem("vetsentinel-theme", themeId);
      } catch {
        // Ignore
      }
      if (
        document.activeElement &&
        typeof document.activeElement.blur === "function"
      ) {
        document.activeElement.blur();
      }
    }
  }

  function openEmergencyModal() {
    isEmergencyModalOpen = true;
  }

  function closeEmergencyModal() {
    isEmergencyModalOpen = false;
  }
</script>

<div
  class="min-h-screen bg-base-300 text-base-content flex flex-col font-sans transition-colors duration-300 relative selection:bg-primary/30"
  data-sveltekit-preload-data="tap"
  data-sveltekit-preload-code="viewport"
>
  <!-- High-Precision Real-Time Navigation Telemetry Bar -->
  {#if navigating.to}
    <div
      class="fixed top-0 left-0 right-0 z-[9999] h-1 bg-gradient-to-r from-primary via-emerald-400 to-cyan-400 shadow-[0_0_12px_rgba(16,185,129,0.9)] animate-pulse"
      role="progressbar"
      aria-label="Navigating route"
    >
      <div class="h-full w-full bg-white/40 animate-pulse"></div>
    </div>
  {/if}

  <!-- Top Emergency Clinic Navbar -->
  <header
    class="navbar bg-base-100/90 border-b border-base-content/10 backdrop-blur-xl sticky top-0 z-5 px-3 sm:px-6 lg:px-8 shadow-sm transition-all duration-300"
  >
    <!-- Brand / Clinic Identity -->
    <div class="navbar-start gap-3">
      <a
        href="/"
        class="flex items-center gap-3 hover:opacity-90 transition-opacity"
      >
        <VetSentinelLogo size="md" withPulse={true} />

        <div>
          <div class="flex items-center gap-2">
            <span
              class="text-base sm:text-lg font-black tracking-tight font-display text-base-content leading-none"
            >
              VetSentinel
            </span>
            <span
              class="badge badge-sm badge-primary font-bold font-mono text-[10px] tracking-wider uppercase shadow-xs"
            >
              {t("nav.badge")}
            </span>
          </div>
          <p
            class="text-[10px] text-base-content/60 font-mono tracking-tight hidden lg:block mt-0.5"
          >
            {t("nav.tagline")}
          </p>
        </div>
      </a>
    </div>

    <!-- Center / Right Telemetry Status Badges & Quick Tools -->
    <div class="navbar-end gap-2 sm:gap-3">
      <!-- Evidence Databases Badge -->
      <div
        class="hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-full bg-base-200/80 border border-base-300 text-xs shadow-inner"
      >
        <span class="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
        <span class="font-bold text-base-content/70"
          >{t("nav.evidenceLabel")}</span
        >
        <span class="text-accent font-mono font-bold text-[11px]">
          {t("nav.evidenceSources")}
        </span>
      </div>

      <!-- Language Selector -->
      <LanguageSelector />

      <!-- Emergency Quick Call & Protocol Modal Launcher -->
      <button
        type="button"
        onclick={openEmergencyModal}
        class="btn btn-error btn-sm text-white font-bold gap-1.5 shadow-[0_0_15px_rgba(239,68,68,0.35)] hover:scale-105 transition-all duration-300 ease-in-out cursor-pointer rounded-xl border-none"
        title={t("hotlineModal.title")}
      >
        <span class="">🚨</span>
        <span class="font-mono text-xs">{t("nav.hotlineBtn")}</span>
        <span class="hidden md:inline badge badge-xs badge-ghost text-black"
          >{t("nav.hotlineBadge")}</span
        >
      </button>
    </div>
  </header>

  <!-- Live Clinical Vitals & Telemetry Rhythm Banner (Dashboard only) -->
  {#if isDashboard}
    <ClinicalVitalsBanner onOpenEmergency={openEmergencyModal} />
  {/if}

  <!-- Main Content Area -->
  <main class="flex-1 flex flex-col relative z-3">
    {@render children()}
  </main>

  <!-- Professional Clinical Telemetry Footer (Excluded on dashboard) -->
  {#if !isDashboard}
    <ClinicalFooter onOpenEmergency={openEmergencyModal} />
  {/if}

  <!-- Dedicated Emergency Clinical Protocol Modal -->
  <EmergencyProtocolModal
    isOpen={isEmergencyModalOpen}
    onClose={closeEmergencyModal}
  />
</div>

<style>
  :global(::view-transition-old(root)) {
    animation: 140ms cubic-bezier(0.4, 0, 0.2, 1) both fade-out;
  }
  :global(::view-transition-new(root)) {
    animation: 180ms cubic-bezier(0.4, 0, 0.2, 1) both fade-in;
  }
  @keyframes fade-in {
    from {
      opacity: 0;
      transform: translateY(4px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  @keyframes fade-out {
    from {
      opacity: 1;
      transform: translateY(0);
    }
    to {
      opacity: 0;
      transform: translateY(-4px);
    }
  }
</style>
