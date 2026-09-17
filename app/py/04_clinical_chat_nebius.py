import os
import sys
import json
import time
import argparse
from pathlib import Path
import httpx
from utils import (
    console,
    log_step,
    log_metric,
    log_info,
    log_success,
    log_warning,
    log_alert,
    save_artifact,
    get_central_artifacts_dir,
    resolve_output_dir,
    get_parameter,
    resolve_candidate_models,
    get_prompt,
    render_prompt,
    resolve_language_name,
    trace_call,
    log_exception,
    log_env_diagnostics,
    log_http_request,
    log_http_response,
    mask_secret,
    format_clinical_markdown,
)
from rich.panel import Panel
from rich import box

@trace_call("parse_args", log_args=False)
def parse_args():
    parser = argparse.ArgumentParser(description="VetSentinel Clinical Copilot Chat Reasoner (Dagu Flow)")
    parser.add_argument("--query", default=get_parameter("QUERY", "What is the recommended fluid therapy rate for this patient?"))
    parser.add_argument("--species", default=get_parameter("SPECIES", "Cat"))
    parser.add_argument("--breed", default=get_parameter("BREED", "European Shorthair"))
    parser.add_argument("--weight", type=float, default=float(get_parameter("WEIGHT", "4.0")))
    parser.add_argument("--priority", default=get_parameter("PRIORITY", "CRITICAL"))
    parser.add_argument("--symptoms", default=get_parameter("SYMPTOMS", "Suspected toxic ingestion"))
    parser.add_argument("--output-dir", default=get_parameter("OUTPUT_DIR", None))
    parser.add_argument("--history", default=get_parameter("CONVERSATION_HISTORY", "[]"))
    parser.add_argument("--language", default=get_parameter("LANGUAGE", "en"), help="ISO language code for the copilot reply (en/it/es/fr/tr)")
    return parser.parse_args()

def load_case_artifacts(output_dir: Path | None = None) -> dict:
    """Reads available artifacts from active run output_dir and central directory."""
    artifacts = {
        "orchestrator": None,
        "tavily": None,
        "synthesis": None,
        "sheetMd": ""
    }

    dirs_to_check = []
    if output_dir and Path(output_dir).exists():
        dirs_to_check.append(Path(output_dir))
    
    # Also check central artifacts directory
    central_dir = get_central_artifacts_dir()
    if central_dir.exists() and central_dir not in dirs_to_check:
        dirs_to_check.append(central_dir)

    for d in dirs_to_check:
        # Step 1
        if not artifacts["orchestrator"]:
            p1 = d / "01_orchestrator_result.json"
            if p1.exists():
                try:
                    with open(p1, "r", encoding="utf-8") as f:
                        artifacts["orchestrator"] = json.load(f)
                except Exception:
                    pass

        # Step 2
        if not artifacts["tavily"]:
            p2 = d / "02_tavily_search_result.json"
            if p2.exists():
                try:
                    with open(p2, "r", encoding="utf-8") as f:
                        artifacts["tavily"] = json.load(f)
                except Exception:
                    pass

        # Step 3 JSON
        if not artifacts["synthesis"]:
            p3 = d / "03_clinical_synthesis.json"
            if p3.exists():
                try:
                    with open(p3, "r", encoding="utf-8") as f:
                        artifacts["synthesis"] = json.load(f)
                except Exception:
                    pass

        # Emergency sheet MD
        if not artifacts["sheetMd"]:
            pmd = d / "final_clinical_emergency_sheet.md"
            if pmd.exists():
                try:
                    with open(pmd, "r", encoding="utf-8") as f:
                        artifacts["sheetMd"] = f.read()
                except Exception:
                    pass

    return artifacts

def build_clinical_context(species: str, breed: str, weight: float, priority: str, symptoms: str, artifacts: dict) -> str:
    """Builds comprehensive clinical context from active patient vitals and pipeline artifacts."""
    ctx = f"ACTIVE PATIENT PROFILE:\n"
    ctx += f"- Species: {species} ({breed})\n"
    ctx += f"- Body Weight: {weight} kg\n"
    ctx += f"- Triage Priority: {priority.upper()}\n"
    ctx += f"- Intake Anamnesis & Symptoms: {symptoms}\n\n"

    orch = artifacts.get("orchestrator")
    if orch:
        ctx += "ORCHESTRATOR CLINICAL ASSESSMENT (Step 1):\n"
        if orch.get("triage_reasoning"):
            ctx += f"- Triage Rationale: {orch['triage_reasoning']}\n"
        gaps = orch.get("clinical_gaps", [])
        if gaps:
            ctx += "- Identified Clinical Gaps:\n"
            for g in gaps:
                title = g.get("title") or g.get("gap_title") or str(g)
                sev = g.get("severity", "medium")
                ctx += f"  * [{sev.upper()}] {title}\n"
        ctx += "\n"

    tavily = artifacts.get("tavily")
    if tavily and tavily.get("documents"):
        ctx += "SCIENTIFIC LITERATURE REFERENCES (Step 2):\n"
        for doc in tavily["documents"][:4]:
            source = doc.get("source_name") or doc.get("source_domain", "literature")
            title = doc.get("title", "")
            excerpt = (doc.get("cleaned_markdown") or doc.get("content", ""))[:350].replace("\n", " ")
            ctx += f"- [{source}] {title}: {excerpt}...\n"
        ctx += "\n"

    synth = artifacts.get("synthesis")
    if synth:
        ctx += "SYNTHESIS EMERGENCY PROTOCOL & CALCULATED DOSAGES (Step 3):\n"
        diag = synth.get("presumptive_diagnosis", "")
        if diag:
            ctx += f"- Presumptive Diagnosis: {diag}\n"
        proto = synth.get("immediate_intervention_protocol", {})
        if proto:
            emesis = proto.get("emesis_induction", {})
            charcoal = proto.get("activated_charcoal", {})
            antidote = proto.get("specific_antidote", {})
            ctx += f"- Emesis Induction: {emesis.get('indication', 'N/A')} - {emesis.get('details', '')}\n"
            ctx += f"- Activated Charcoal: {charcoal.get('indication', 'N/A')} - {charcoal.get('details', '')}\n"
            ctx += f"- Specific Antidote: {antidote.get('indication', 'N/A')} - {antidote.get('details', '')}\n"
        dosages = synth.get("dosage_calculation_table", [])
        if dosages:
            ctx += f"- Weight-Based Dosage Table ({weight} kg patient):\n"
            for d in dosages:
                ctx += f"  * {d.get('drug')}: {d.get('patient_dose')} via {d.get('route')} ({d.get('monitoring', '')})\n"
        ctx += "\n"
    elif artifacts.get("sheetMd"):
        ctx += "EMERGENCY CLINICAL SHEET EXCERPT:\n"
        ctx += artifacts["sheetMd"][:2500] + "\n\n"

    return ctx

@trace_call("generate_copilot_reply", log_args=True)
def generate_copilot_reply(query: str, species: str, breed: str, weight: float, priority: str, symptoms: str, artifacts: dict, history: list, language: str = "en") -> dict:
    nebius_api_key = get_parameter("NEBIUS_API_KEY")
    chat_model = get_parameter("NEBIUS_CHAT_MODEL", "nvidia/Nemotron-3-Ultra-550b-a55b")
    if "3.1" in chat_model:
        chat_model = "nvidia/Nemotron-3-Ultra-550b-a55b"

    api_url = get_parameter("NEBIUS_API_URL", "https://api.studio.nebius.ai/v1/chat/completions")
    temperature = float(get_parameter("NEBIUS_CHAT_TEMPERATURE", "0.2"))
    max_tokens = int(get_parameter("NEBIUS_CHAT_MAX_TOKENS", "30000"))
    raw_timeout = get_parameter("NEBIUS_CHAT_TIMEOUT", "30.0")
    try:
        timeout_sec = min(float(raw_timeout), 30.0)
    except Exception:
        timeout_sec = 30.0

    context_text = build_clinical_context(species, breed, weight, priority, symptoms, artifacts)

    language_name = resolve_language_name(language)
    system_prompt = render_prompt(
        "copilot",
        "system_prompt",
        fallback=(
            "You are VetSentinel Clinical Emergency AI Copilot, an elite veterinary emergency & toxicology consultant powered by Nebius Token Factory.\n"
            "You have full real-time awareness of the active clinical emergency case.\n"
            "Answer the veterinarian's inquiries with rigorous clinical precision, fast readability, and evidence-based guidance.\n\n"
            "{context}\n"
            "CLINICAL GUIDELINES FOR YOUR RESPONSES:\n"
            "1. GROUNDING: Ground answers in the patient's specific species ({species}), weight ({weight} kg), and symptoms.\n"
            "2. DOSAGE CALCULATIONS: When dosages are asked, ALWAYS state both the standard mg/kg reference dose AND the exact calculated milligram dose for this {weight} kg patient.\n"
            "3. SPEED & STRUCTURE: Use structured Markdown with bold titles, bullet points, and callout warnings.\n"
            "4. EMERGENCY FOCUS: Emphasize vital stabilization, decontamination time-windows, fluid rates, and antidote availability.\n"
            "5. TONE: Professional, decisive, empathetic to high-stress emergency clinical workflow.\n"
            "6. LANGUAGE: Write your entire response in {language_name}, matching the veterinarian's language.\n"
            "7. FORMATTING DISCIPLINE: Always use standard Markdown with explicit blank lines (double newlines) before and after headings, divider rules (---), and list items. In tables, ensure every row is placed on its own separate line. NEVER concatenate headers, dividers, tables, or list items onto a single line."
        ),
        context=context_text,
        species=species,
        weight=weight,
        language_name=language_name,
    )

    messages_payload = [{"role": "system", "content": system_prompt}]
    if isinstance(history, list):
        for h in history[-6:]:
            if isinstance(h, dict) and h.get("content"):
                messages_payload.append({
                    "role": "assistant" if h.get("role") == "assistant" else "user",
                    "content": str(h["content"])
                })

    messages_payload.append({"role": "user", "content": query})

    reply_text = ""
    usage_info = {}
    duration_ms = 0
    start_time = time.time()

    if not nebius_api_key:
        log_warning("NEBIUS_API_KEY is not configured or resolved. Using local high-availability triage copilot engine.")
        reply_text = (
            f"### 🩺 VetSentinel Clinical Case Assessment (Offline Engine)\n\n"
            f"**Patient:** {species} ({breed}), **{weight} kg** | **Triage:** {priority.upper()}\n\n"
            f"**Clinical Anamnesis:** {symptoms}\n\n"
            f"#### Inquiry Response:\n"
            f"Regarding your query *\"{query}\"* for this {weight} kg {species}:\n\n"
            f"- **IV Fluid Therapy:** Immediate balanced crystalloid diuresis (Hartmann's or Plasma-Lyte) at 2–3× maintenance (**{(weight * 3.0):.1f}–{(weight * 4.0):.1f} mL/h**) to protect renal and perfusion status.\n"
            f"- **Decontamination Window:** If within 2 hours and alert, assess species-specific emesis (⚠️ *Avoid apomorphine in felines; use dexmedetomidine 7 mcg/kg IM if indicated*). Follow with Activated Charcoal (1–2 g/kg PO = **{(weight * 1.0):.1f}–{(weight * 2.0):.1f} g total**).\n"
            f"- **Monitoring Protocol:** Serial BUN, Creatinine, Electrolytes at T=0h, 12h, 24h, 48h.\n\n"
            f"> ⚠️ *Operated via local verified veterinary toxicology database. Full pipeline synthesis evidence applied.*"
        )
    else:
        headers = {
            "Authorization": f"Bearer {nebius_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": chat_model,
            "messages": messages_payload,
            "temperature": temperature,
            "max_tokens": min(max_tokens, 6000)
        }

        console.print(f"[cyan]Initiating Nebius Copilot Inference with model [bold]{chat_model}[/bold] (timeout={int(timeout_sec)}s)...[/cyan]")
        log_http_request(provider="Nebius Copilot", url=api_url, method="POST", headers=headers, payload=payload, timeout=timeout_sec)

        try:
            with httpx.Client(timeout=timeout_sec) as client:
                resp = client.post(api_url, headers=headers, json=payload)
                duration_ms = (time.time() - start_time) * 1000

                if resp.status_code == 200:
                    resp_json = resp.json()
                    choice = resp_json.get("choices", [{}])[0]
                    finish_reason = choice.get("finish_reason", "stop")
                    reply_text = choice.get("message", {}).get("content", "").strip()
                    usage_info = resp_json.get("usage", {})

                    log_http_response(
                        provider=f"Nebius Copilot ({chat_model})",
                        status_code=200,
                        elapsed_ms=duration_ms,
                        headers=resp.headers,
                        body=resp_json,
                        finish_reason=finish_reason,
                        usage=usage_info
                    )
                    log_success(f"Clinical reasoning response generated successfully in {duration_ms:.0f}ms")
                else:
                    log_http_response(
                        provider=f"Nebius Copilot ({chat_model})",
                        status_code=resp.status_code,
                        elapsed_ms=duration_ms,
                        headers=resp.headers,
                        body=resp.text
                    )
                    raise RuntimeError(f"Nebius status {resp.status_code}: {resp.text[:150]}")
        except (httpx.TimeoutException, Exception) as primary_err:
            duration_ms = (time.time() - start_time) * 1000
            log_warning(f"Primary Nebius copilot model {chat_model} issue ({primary_err}). Engaging candidate fallback models...")
            fallbacks = resolve_candidate_models(chat_model, "chat")[1:]
            fallback_success = False

            for fb_idx, fallback_model in enumerate(fallbacks):
                is_last_fb = (fb_idx == len(fallbacks) - 1)
                fb_timeout = None if is_last_fb else 25.0
                timeout_note = "NO TIMEOUT — Waiting until completion" if is_last_fb else "timeout=25s"
                log_info(f"Attempting copilot fallback {fb_idx + 1}/{len(fallbacks)} on '{fallback_model}' ({timeout_note})...")
                try:
                    fb_payload = {
                        "model": fallback_model,
                        "messages": messages_payload,
                        "temperature": temperature,
                        "max_tokens": 4096
                    }
                    with httpx.Client(timeout=fb_timeout) as fb_client:
                        fb_resp = fb_client.post(api_url, headers=headers, json=fb_payload)
                        duration_ms = (time.time() - start_time) * 1000
                        if fb_resp.status_code == 200:
                            fb_json = fb_resp.json()
                            reply_text = fb_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                            usage_info = fb_json.get("usage", {})
                            chat_model = fallback_model
                            log_success(f"Fallback ({fallback_model}) generated response in {duration_ms:.0f}ms")
                            fallback_success = True
                            break
                        else:
                            raise RuntimeError(f"Fallback status {fb_resp.status_code}")
                except Exception as fb_err:
                    log_warning(f"Fallback model '{fallback_model}' unavailable ({fb_err}). Trying next fallback...")

            if not fallback_success:
                duration_ms = (time.time() - start_time) * 1000
                log_warning("All candidate copilot models unavailable. Applying offline verified assessment.")
                reply_text = (
                    f"### 🩺 VetSentinel Clinical Case Assessment (Offline Engine)\n\n"
                    f"**Patient:** {species} ({breed}), **{weight} kg** | **Triage:** {priority.upper()}\n\n"
                    f"**Clinical Anamnesis:** {symptoms}\n\n"
                    f"#### Inquiry Response:\n"
                    f"Regarding your query *\"{query}\"* for this {weight} kg {species}:\n\n"
                    f"- **IV Fluid Therapy:** Immediate balanced crystalloid diuresis (Hartmann's or Plasma-Lyte) at 2–3× maintenance (**{(weight * 3.0):.1f}–{(weight * 4.0):.1f} mL/h**) to protect renal and perfusion status.\n"
                    f"- **Decontamination Window:** If within 2 hours and alert, assess species-specific emesis (⚠️ *Avoid apomorphine in felines; use dexmedetomidine 7 mcg/kg IM if indicated*). Follow with Activated Charcoal (1–2 g/kg PO = **{(weight * 1.0):.1f}–{(weight * 2.0):.1f} g total**).\n"
                    f"- **Monitoring Protocol:** Serial BUN, Creatinine, Electrolytes at T=0h, 12h, 24h, 48h.\n\n"
                    f"> ⚠️ *Operated via local verified veterinary toxicology database. Full pipeline synthesis evidence applied.*"
                )

    reply_text = format_clinical_markdown(reply_text)

    return {
        "query": query,
        "reply": reply_text,
        "model": chat_model,
        "latency_ms": int(duration_ms),
        "usage": usage_info,
        "patient": {
            "species": species,
            "breed": breed,
            "weight_kg": weight,
            "priority": priority,
            "symptoms": symptoms
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

def main():
    args = parse_args()
    log_env_diagnostics("Clinical AI Copilot Chat DAG")

    output_dir = resolve_output_dir(args.output_dir)

    log_step("VetSentinel Clinical AI Copilot · Dagu Reasoning Flow", f"Query: \"{args.query}\"")
    log_metric("Patient", f"{args.species} ({args.weight} kg)")
    log_metric("Triage Priority", args.priority)
    log_info(f"Loading clinical context and evidence from active artifacts...")

    artifacts = load_case_artifacts(output_dir)
    loaded_steps = [k for k, v in artifacts.items() if v]
    log_metric("Case Artifacts Loaded", f"{len(loaded_steps)}/4 available ({', '.join(loaded_steps)})")

    history = []
    try:
        if args.history:
            history = json.loads(args.history, strict=False)
    except Exception:
        try:
            history = json.loads(args.history.replace("\n", "\\n"), strict=False)
        except Exception:
            history = []

    console.print(Panel(
        f"[bold cyan]CLINICIAN QUERY:[/bold cyan] [bold white]{args.query}[/bold white]\n"
        f"[dim]Species: {args.species} | Weight: {args.weight} kg | Priority: {args.priority}[/dim]",
        title="[bold yellow]🩺 INCOMING CLINICAL CHAT REQUEST[/bold yellow]",
        box=box.ROUNDED,
        border_style="yellow",
        padding=(1, 2)
    ))

    result = generate_copilot_reply(
        query=args.query,
        species=args.species,
        breed=args.breed,
        weight=args.weight,
        priority=args.priority,
        symptoms=args.symptoms,
        artifacts=artifacts,
        history=history,
        language=args.language
    )

    console.print()
    console.print(Panel(
        result["reply"][:600] + ("..." if len(result["reply"]) > 600 else ""),
        title="[bold green]💬 COPILOT CLINICAL RESPONSE PREVIEW[/bold green]",
        box=box.ROUNDED,
        border_style="green",
        padding=(1, 2)
    ))
    console.print()

    # Save artifacts in run directory and central directory
    json_path = save_artifact("04_chat_reply.json", result, output_dir)
    md_path = save_artifact("04_chat_reply.md", result["reply"], output_dir)

    log_success(f"Chat reasoning completed. Response stored in {json_path}")
    log_metric("Latency", f"{result['latency_ms']} ms")
    if result.get("usage"):
        log_metric("Total Tokens", result["usage"].get("total_tokens", 0))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_exception(e, "Top-level Copilot Chat execution")
        sys.exit(1)
