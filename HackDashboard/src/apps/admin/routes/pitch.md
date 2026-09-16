"Imagine your cat nibbles on a flower from a vase in your living room. You don't realize it, but it’s a lily: in 18 hours, its kidneys will permanently fail. You rush to the vet in a complete panic. The veterinarian has just a few minutes to identify the plant, decide whether inducing vomiting is safe or could cause choking, and calculate the exact drug dosage down to the milligram to save an animal that weighs only 4 kilos.

That’s why we built VetSentinel: the emergency copilot that turns veterinary ER panic into a lifesaving, milligram-precise protocol in under 10 seconds."

⏱️ Minute-by-Minute Script (5 Minutes)

Minute 1: The Real Problem (The Emotional Hook)

⚬ Explain that pets are not "tiny humans":
  ⚬ Cats lack the liver enzymes needed to break down lily toxins.
  ⚬ Dogs cannot metabolize dark chocolate.
  ⚬ A rabbit or a ferret weighs only 1 kilo: being off by half a drop on a dosage can be fatal.
⚬ The night-shift vet's nightmare: thumbing through physical textbooks or searching Google burns precious minutes—and Google is flooded with ad-heavy blogs and bad advice.

Minute 2: The Solution – VetSentinel (ELI5)

"How does VetSentinel work? We built a team of 3 digital specialists coordinated by an orchestrator:"

1. The Fast Doctor (Nebius AI + GLM-5.3-Flash): reads the case intake ("Cat, 4 kg, ate a flower, vomiting and lethargic"). In a fraction of a second, it flags the hazards: "Warning: we must immediately confirm if this is a true lily and initiate renal protection before it’s too late!"
2. The Source Detective (Tavily Specialist Search): runs real-time searches exclusively across verified medical reference databases (ASPCA Animal Poison Control, Merck Veterinary Manual, BSAVA). Zero ads, zero misinformation.
3. The Mathematical Pharmacist (Clinical Synthesis): never guesses dosages. It multiplies official guidelines by the animal's exact weight (4.0 kg = 28 ml/hr IV fluids, 6 g activated charcoal) and flashes a clear red warning: "Do not induce vomiting if the cat is lethargic; high risk of aspiration pneumonia".

Minute 3: Live Demo (On Screen)

(Navigate the UI as you speak)

1. Screen 1 (Triage Input):
  ⚬ Highlight the quick-select presets: click "Cat · Unknown Lily Houseplant" (or "Dog · Dark Chocolate").
  ⚬ Show how the weight (4 kg) and symptoms are configured in a single click.
2. The Magic Click: Hit "Run Clinical Analysis / Execute Dagu Pipeline".
3. Dagu Modal Screen:
  ⚬ Explain: "Notice these green lights progressing in real time? This isn't a fake chat spinner; it’s a directed acyclic graph (DAG) pipeline running under the hood."
4. Synthesis & Dosages Screen:
  ⚬ Highlight the output table: dosages calculated in ml/hr, explicit contraindications on emesis and antidotes, and the one-click copy button to paste the clinical report directly into medical records.

Minute 4: Technical Architecture (Why Technical Judges Will Love It)

⚬ Modern Frontend: Built with Svelte 5 (Runes), TailwindCSS, and DaisyUI. Features hospital-grade telemetry with a real-time ECG trace, clinical theme switching, and smooth easing animations.
⚬ Backend Orchestrator (Dagu): Rather than relying on an unconstrained single chatbot call, execution is split into an independent, traceable, and reproducible task graph that auto-saves JSON artifacts and Markdown summaries.
⚬ Ultra-Low Latency Inference: Served via Nebius Token Factory using the high-throughput GLM-5.3-Flash model.
⚬ Evidence-Based & Hallucination-Free: The LLM does not invent active ingredients; all data is retrieved from verified veterinary domains via Tavily.

Minute 5: Impact and Closing

⚬ "In an emergency room, a 10-minute delay is often the difference between a pet going home or not surviving the night.
⚬ VetSentinel doesn't replace the veterinarian: it acts as an intelligent safety shield that saves critical minutes and eliminates dosage math errors under extreme pressure.
⚬ Thank you!"

💡 3 Winning Metaphors to Use

Technical Concept	ELI5 Pitch to Judges
Dagu Workflow Engine	"It works like an emergency assembly line: if doctor one doesn't finish the diagnosis, doctor two won't run searches, and doctor three won't prepare the medication. No compounding errors."
Tavily Whitelist Search	"We gave the AI a pair of focused glasses: it can only read peer-reviewed veterinary manuals, completely ignoring internet forums and random blogs."
Deterministic Weight-Based Dosing	"We don't let a chatbot do drug math: we compute exact volumes by applying strict mathematical formulas to official clinical guidelines, because medication dosing cannot rely on guesswork."

🛡️ Judge Q&A Prep

1. "Why not just use ChatGPT or a standard chat interface?"
   Answer: "In an ER scenario, a vet doesn't have time to prompt-engineer or parse walls of conversational text. They need three answers in under five seconds: Should I induce emesis? Yes or no? How much activated charcoal? What fluid rate? VetSentinel is an actionable, deterministic workflow tool, not a generic chatbot."
2. "How do you prevent the AI from hallucinating toxic dosages?"
   Answer: "Our architecture uses a two-stage guardrail: the LLM isolates clinical variables and search queries; Tavily fetches verified guidelines (ASPCA, Merck, BSAVA); then deterministic code calculates weight-based formulas (mg/kg) that strictly require source citations before display."
3. "What role does Dagu play here?"
   Answer: "Dagu provides enterprise-grade pipeline reliability: it visualizes every clinical stage in an explicit DAG, persists execution logs for medicolegal auditing, and writes structured artifacts to disk for direct integration into electronic health records."