<script>
  import { onMount } from "svelte";
  import { preloadCode, preloadData } from "$app/navigation";
  import { cubicInOut } from "svelte/easing";
  import { fly, fade } from "svelte/transition";
  import LandingHero from "./LandingHero.svelte";
  import LandingProblem from "./LandingProblem.svelte";
  import LandingSpecialists from "./LandingSpecialists.svelte";
  import LandingInteractiveDemo from "./LandingInteractiveDemo.svelte";
  import LandingDonate from "./LandingDonate.svelte";
  import LandingVetFaq from "./LandingVetFaq.svelte";
  import LandingCta from "./LandingCta.svelte";
  import EmergencyProtocolModal from "./EmergencyProtocolModal.svelte";
  import { t } from "$lib";

  // Eagerly preload both code & data for dashboard route so navigation is instant
  onMount(() => {
    preloadCode("/dashboard");
    preloadData("/dashboard");
  });

  let isHotlineOpen = $state(false);

  function openHotline() {
    isHotlineOpen = true;
  }

  function closeHotline() {
    isHotlineOpen = false;
  }

  const seoTitle = "VetSentinel · Veterinary Emergency & Toxicology Triage System";
  const seoDescription =
    "Turn toxic ER panic into calibrated, weight-based protocols in under 60 seconds. 0% dosage error, species-specific contraindications, and ASPCA & Merck peer-reviewed veterinary guidance.";
  const canonicalUrl = "https://vetsentinel.app/";
  const imageUrl = "https://vetsentinel.app/images/vector/hero_cat_lily.jpg";

  const keywords = [
    "veterinary emergency",
    "veterinary toxicology",
    "vet triage copilot",
    "animal poison control",
    "weight-based veterinary dosing",
    "feline lily nephrotoxicity",
    "canine theobromine chocolate toxicity",
    "ASPCA APCC",
    "Merck Veterinary Manual",
    "BSAVA small animal formulary",
    "veterinary clinical decision support",
    "vet ICU calculator",
    "veterinary SOAP export",
    "emergency vet workflow",
    "pet poison triage",
    "species pharmacology",
  ].join(", ");

  const jsonLdSchema = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "WebSite",
        "@id": "https://vetsentinel.app/#website",
        url: "https://vetsentinel.app/",
        name: "VetSentinel",
        description:
          "Veterinary Emergency & Toxicology Triage Decision-Support System.",
        publisher: {
          "@id": "https://vetsentinel.app/#organization",
        },
        inLanguage: "en-US",
      },
      {
        "@type": "Organization",
        "@id": "https://vetsentinel.app/#organization",
        name: "VetSentinel",
        url: "https://vetsentinel.app/",
        logo: {
          "@type": "ImageObject",
          url: "https://vetsentinel.app/logo.png",
          caption: "VetSentinel Logo",
        },
        sameAs: ["https://github.com/danilofiumi/Hackaton"],
      },
      {
        "@type": "MedicalWebPage",
        "@id": "https://vetsentinel.app/#webpage",
        url: "https://vetsentinel.app/",
        name: seoTitle,
        description: seoDescription,
        isPartOf: {
          "@id": "https://vetsentinel.app/#website",
        },
        about: [
          {
            "@type": "MedicalSpecialty",
            name: "Veterinary Emergency and Critical Care",
          },
          {
            "@type": "MedicalSpecialty",
            name: "Veterinary Clinical Toxicology",
          },
        ],
        audience: {
          "@type": "MedicalAudience",
          audienceType:
            "Clinician, Emergency Veterinarian, Veterinary Technician, Critical Care Specialist",
        },
        specialty: "Veterinary Emergency Medicine",
        primaryImageOfPage: {
          "@type": "ImageObject",
          url: imageUrl,
        },
      },
      {
        "@type": "SoftwareApplication",
        "@id": "https://vetsentinel.app/#software",
        name: "VetSentinel ER Copilot",
        applicationCategory: "HealthApplication",
        applicationSubCategory: "Veterinary Clinical Decision Support System",
        operatingSystem: "Web, macOS, Windows, Linux",
        offers: {
          "@type": "Offer",
          price: "0",
          priceCurrency: "USD",
        },
        featureList: [
          "Sub-10 second veterinary emergency triage hazard isolation",
          "Deterministic 0% math error weight-based dosage calculator",
          "Species-specific contraindication screening (canine, feline, ferret, rabbit, exotic)",
          "Verified medical references from ASPCA APCC, Merck Veterinary Manual & BSAVA",
          "1-Click SOAP medical record export for ezyVet, IDEXX, Cornerstone & Shepherd",
        ],
      },
      {
        "@type": "FAQPage",
        "@id": "https://vetsentinel.app/#faq",
        mainEntity: [
          {
            "@type": "Question",
            name: "How does VetSentinel determine whether inducing emesis is safe vs. contraindicated?",
            acceptedAnswer: {
              "@type": "Answer",
              text: "VetSentinel evaluates critical physiological risk factors before suggesting emesis. If the patient presents with severe lethargy, stupor, loss of protective gag reflex, or seizure activity, emesis is strictly flagged with a RED ALERT to prevent fatal aspiration pneumonia. Additionally, for caustic agents (acids, alkalis, batteries) or volatile hydrocarbons, emesis is contraindicated due to esophageal re-injury risks. When emesis is safe, exact apomorphine or ropinirole ophthalmic dosages are calculated.",
            },
          },
          {
            "@type": "Question",
            name: "What medical formularies and clinical authorities back these drug calculations?",
            acceptedAnswer: {
              "@type": "Answer",
              text: "All calculated dosages, fluid rates, and antidote schedules are referenced directly from certified veterinary toxicology authorities: the ASPCA Animal Poison Control Center (APCC) guidelines, the Merck Veterinary Manual (11th Ed.), the BSAVA Small Animal Formulary, and Plumb's Veterinary Drug Handbook. Every recommendation displays its formal bibliographic source.",
            },
          },
          {
            "@type": "Question",
            name: "Can I trust the dosage math for extreme patient masses (e.g. 1 kg ferret vs. 65 kg Mastiff)?",
            acceptedAnswer: {
              "@type": "Answer",
              text: "Yes. Veterinary pharmacokinetics demand strict milligram-per-kilogram scaling rather than standard adult doses. VetSentinel applies deterministic mathematical calculations (mg/kg × exact body weight) and automatically enforces species-specific infusion caps. For example, it prevents fluid volume overload in oliguric feline kidneys while computing appropriate aggressive diuresis rates for large canines.",
            },
          },
          {
            "@type": "Question",
            name: "What if the owner does not know the exact plant or household toxin ingested?",
            acceptedAnswer: {
              "@type": "Answer",
              text: "The triage intake accepts descriptive clinical observations (e.g., 'orange-spotted cut flower, orange pollen on face'). VetSentinel highlights differential identification criteria—such as distinguishing highly nephrotoxic true lilies (Lilium and Hemerocallis spp.) from non-nephrotoxic lookalikes like the Peace Lily (Spathiphyllum)—and defaults to aggressive renal-protective protocols until true lily exposure is definitively excluded.",
            },
          },
          {
            "@type": "Question",
            name: "How does the system handle time-delayed toxicities like rodenticides or lilies?",
            acceptedAnswer: {
              "@type": "Answer",
              text: "For toxicants with delayed clinical onset, VetSentinel generates a multi-stage monitoring roadmap. For anticoagulant rodenticides, it recommends baseline and 48-hour PT/PTT coagulopathy testing. For feline lily ingestion, it outlines serial BUN, Creatinine, and SDMA panels alongside 48 hours of continuous IV fluid diuresis.",
            },
          },
          {
            "@type": "Question",
            name: "How easily can I copy the treatment protocol into our clinic's PIMS (ezyVet, Cornerstone, IDEXX)?",
            acceptedAnswer: {
              "@type": "Answer",
              text: "With one click, the generated emergency protocol is formatted into standard clinical SOAP medical record text. You can paste it directly into ezyVet, Cornerstone, IDEXX Neo, Covetrus Pulse, or Shepherd—complete with fluid rates, drug administration timing, diagnostic orders, and client discharge warnings.",
            },
          },
          {
            "@type": "Question",
            name: "Does VetSentinel replace veterinary clinical judgment or malpractice coverage?",
            acceptedAnswer: {
              "@type": "Answer",
              text: "No. VetSentinel is strictly an emergency clinical decision-support tool. It eliminates stressful mental math, cross-references toxicological literature in seconds, and highlights red-flag contraindications under time pressure. However, the attending licensed veterinarian always retains sole clinical judgment, verification, and therapeutic authority for every patient.",
            },
          },
        ],
      },
    ],
  };

  const schemaScript = `<script type="application/ld+json">${JSON.stringify(jsonLdSchema)}<\/script>`;
</script>

<svelte:head>
  <!-- Primary Document Meta -->
  <title>{seoTitle}</title>
  <meta name="title" content={seoTitle} />
  <meta name="description" content={seoDescription} />
  <meta name="keywords" content={keywords} />
  <meta name="author" content="Danilo Fiumi, VetSentinel Clinical Systems" />
  <meta name="publisher" content="VetSentinel" />
  <meta
    name="robots"
    content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
  />
  <meta
    name="googlebot"
    content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
  />
  <link rel="canonical" href={canonicalUrl} />
  <link rel="alternate" hreflang="x-default" href={canonicalUrl} />
  <link rel="alternate" hreflang="en" href={canonicalUrl} />

  <!-- Open Graph / Facebook / LinkedIn -->
  <meta property="og:site_name" content="VetSentinel" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content={canonicalUrl} />
  <meta property="og:title" content={seoTitle} />
  <meta property="og:description" content={seoDescription} />
  <meta property="og:image" content={imageUrl} />
  <meta property="og:image:secure_url" content={imageUrl} />
  <meta property="og:image:type" content="image/jpeg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta
    property="og:image:alt"
    content="VetSentinel Veterinary Emergency ICU Telemetry and Toxicology Copilot Interface"
  />
  <meta property="og:locale" content="en_US" />
  <meta property="og:locale:alternate" content="en_GB" />

  <!-- Twitter / X Cards -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:site" content="@VetSentinel" />
  <meta name="twitter:creator" content="@VetSentinel" />
  <meta name="twitter:title" content={seoTitle} />
  <meta name="twitter:description" content={seoDescription} />
  <meta name="twitter:image" content={imageUrl} />
  <meta
    name="twitter:image:alt"
    content="VetSentinel Veterinary Emergency ICU Telemetry and Toxicology Copilot Interface"
  />

  <!-- Mobile, PWA & UX -->
  <meta
    name="theme-color"
    content="#10b981"
    media="(prefers-color-scheme: light)"
  />
  <meta
    name="theme-color"
    content="#064e3b"
    media="(prefers-color-scheme: dark)"
  />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta
    name="apple-mobile-web-app-status-bar-style"
    content="black-translucent"
  />
  <meta name="apple-mobile-web-app-title" content="VetSentinel" />
  <meta name="application-name" content="VetSentinel" />
  <meta name="mobile-web-app-capable" content="yes" />
  <meta name="format-detection" content="telephone=no, address=no, email=no" />

  <!-- Clinical & Academic Classification (Dublin Core & Medical) -->
  <meta name="DC.title" content={seoTitle} />
  <meta
    name="DC.creator"
    content="Danilo Fiumi, VetSentinel Clinical Systems"
  />
  <meta
    name="DC.subject"
    content="Veterinary Emergency Medicine; Clinical Toxicology; Decision Support Systems; Species Dosing"
  />
  <meta name="DC.description" content={seoDescription} />
  <meta name="DC.publisher" content="VetSentinel" />
  <meta name="DC.type" content="InteractiveResource" />
  <meta name="DC.format" content="text/html" />
  <meta name="DC.language" content="en" />
  <meta
    name="medical-specialty"
    content="Veterinary Emergency and Critical Care, Veterinary Clinical Pharmacology"
  />

  <!-- JSON-LD Structured Data Schema -->
  {@html schemaScript}
</svelte:head>

<div class="min-h-screen relative flex flex-col">
  <!-- Sticky Clinician & Hackathon Quickbar -->
  <div
    class="sticky top-16 z-30 bg-base-100/85 backdrop-blur-md border-b border-base-content/10 hidden md:block py-2.5 transition-all duration-300"
  >
    <div
      class="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between"
    >
      <div class="flex items-center gap-1.5 font-mono text-xs">
        <span class="text-base-content/50 font-bold">{t("landing.quickbar.story")}</span>
        <a
          href="#story"
          class="btn btn-ghost btn-xs rounded-lg font-mono hover:text-blue-600 transition-colors"
        >
          {t("landing.quickbar.dilemma")}
        </a>
        <span class="text-base-content/20">/</span>
        <a
          href="#solution"
          class="btn btn-ghost btn-xs rounded-lg font-mono hover:text-blue-600 transition-colors"
        >
          {t("landing.quickbar.shield")}
        </a>
        <span class="text-base-content/20">/</span>
        <a
          href="#demo"
          class="btn btn-ghost btn-xs rounded-lg font-mono hover:text-blue-600 transition-colors"
        >
          {t("landing.quickbar.demo")}
        </a>
        <span class="text-base-content/20">/</span>
        <a
          href="#donate"
          class="btn btn-ghost btn-xs rounded-lg font-mono hover:text-rose-500 transition-colors"
        >
          {t("landing.quickbar.donate")}
        </a>
        <span class="text-base-content/20">/</span>
        <a
          href="#vet-faq"
          class="btn btn-ghost btn-xs rounded-lg font-mono hover:text-blue-600 transition-colors"
        >
          {t("landing.quickbar.faq")}
        </a>
        <span class="text-base-content/20">/</span>
        <a
          href="/hackathon"
          class="btn btn-sm btn-outline btn-primary rounded-xl font-mono text-xs gap-1.5 ml-2 shadow-xs hover:scale-105 transition-all"
        >
          <span>🏆</span>
          <span>{t("landing.quickbar.hackathon")}</span>
        </a>
      </div>

      <div class="flex items-center gap-3">
        <a
          href="/dashboard"
          data-sveltekit-preload-code="eager"
          data-sveltekit-preload-data="tap"
          class="btn btn-primary btn-xs sm:btn-sm rounded-xl font-bold font-display shadow-xs gap-1.5 hover:scale-105 active:scale-95 transition-all duration-200"
        >
          <span>⚡ {t("landing.quickbar.launch")}</span>
          <span>→</span>
        </a>
      </div>
    </div>
  </div>

  <!-- Hero Section (Visual Cat/Lily Story & Hook) -->
  <LandingHero onOpenHotline={openHotline} />

  <!-- ER Dilemma & Night Shift Reality (Veterinarian Photo & Species Pharmacology) -->
  <LandingProblem />

  <!-- Clinical Safety Shield (Precision Dosing Photo & Safeguards) -->
  <LandingSpecialists />

  <!-- Interactive Demo Simulator (Walkthrough for Clinicians) -->
  <LandingInteractiveDemo />

  <!-- Support & Donations (Ko-fi & Buy Me a Coffee) -->
  <LandingDonate />

  <!-- Clinical Q&A for Veterinarians -->
  <LandingVetFaq />

  <!-- Clinical Impact & Patient Recovery (Emotional Closing & Recovered Dog Photo) -->
  <LandingCta onOpenHotline={openHotline} />

  <!-- 24/7 Emergency Poison Hotline Modal -->
  <EmergencyProtocolModal isOpen={isHotlineOpen} onClose={closeHotline} />
</div>
