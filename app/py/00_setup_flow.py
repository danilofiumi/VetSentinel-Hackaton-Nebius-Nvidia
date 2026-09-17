#!/usr/bin/env python3
import os
import sys
import json
import time
import argparse
import shutil
from pathlib import Path
from utils import (
    console,
    log_step,
    log_pipeline_banner,
    log_info,
    log_success,
    log_warning,
    log_alert,
    save_artifact,
    resolve_output_dir,
    get_central_artifacts_dir,
    get_parameter,
    get_parameter_list,
    resolve_candidate_models,
    log_env_diagnostics,
    trace_call,
    log_exception,
    STATIC_PARAMETERS,
)


@trace_call("parse_args", log_args=False)
def parse_args():
    parser = argparse.ArgumentParser(description="Step 0: Dagu Flow Python Initialization & Parameter Setup")
    parser.add_argument("--species", default=get_parameter("SPECIES", "Cat"))
    parser.add_argument("--breed", default=get_parameter("BREED", "European Shorthair"))
    parser.add_argument("--weight", type=float, default=float(get_parameter("WEIGHT", "4.0")))
    parser.add_argument(
        "--symptoms",
        default=get_parameter(
            "SYMPTOMS",
            "4.0 kg European Shorthair cat, ingested an unidentified cut flower 2h ago, vomiting and lethargy."
        )
    )
    parser.add_argument("--priority", default=get_parameter("PRIORITY", "auto"))
    parser.add_argument("--language", default=get_parameter("LANGUAGE", "en"))
    parser.add_argument("--output-dir", default=get_parameter("OUTPUT_DIR", None))
    return parser.parse_args()


@trace_call("main", log_args=False)
def main():
    args = parse_args()

    # 1. Resolve run and central artifacts directories
    run_artifacts_dir = resolve_output_dir(args.output_dir)
    central_artifacts_dir = get_central_artifacts_dir()

    run_artifacts_dir.mkdir(parents=True, exist_ok=True)
    central_artifacts_dir.mkdir(parents=True, exist_ok=True)

    # 2. Render Pipeline Initialization Banner
    log_pipeline_banner(
        species=args.species,
        breed=args.breed,
        weight=args.weight,
        priority=args.priority,
        symptoms=args.symptoms,
        output_dir=run_artifacts_dir,
    )

    log_step("Step 0 · Dagu Flow Python Init", "Loading static parameters & preparing artifacts")

    # 3. Print Rich Diagnostics for Runtime Environment & LLM Parameters
    log_env_diagnostics("Dagu Emergency Flow (Python Init)")

    # 4. Resolve active models and timeouts for this run
    orch_model = get_parameter("NEBIUS_ORCHESTRATOR_MODEL", get_parameter("NEBIUS_MODEL", "zai-org/GLM-5.3"))
    orch_timeout = float(get_parameter("NEBIUS_ORCHESTRATOR_TIMEOUT", get_parameter("NEBIUS_TIMEOUT", "15.0")))
    orch_candidates = resolve_candidate_models(orch_model, "orchestrator")

    synth_model = get_parameter("NEBIUS_SYNTHESIS_MODEL", get_parameter("NEBIUS_MODEL", "zai-org/GLM-5.3"))
    synth_timeout = float(get_parameter("NEBIUS_SYNTHESIS_TIMEOUT", get_parameter("NEBIUS_TIMEOUT", "60.0")))
    synth_candidates = resolve_candidate_models(synth_model, "synthesis")

    chat_model = get_parameter("NEBIUS_CHAT_MODEL", "nvidia/Nemotron-3-Ultra-550b-a55b")
    chat_timeout = float(get_parameter("NEBIUS_CHAT_TIMEOUT", "45.0"))
    chat_candidates = resolve_candidate_models(chat_model, "chat")

    # 5. Build Flow Configuration Manifest
    flow_config = {
        "flow_id": "vetsentinel-emergency-flow",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "initialized",
        "patient": {
            "species": args.species,
            "breed": args.breed,
            "weight_kg": args.weight,
            "symptoms": args.symptoms,
            "priority": args.priority,
            "language": args.language,
        },
        "resolved_pipeline_parameters": {
            "orchestrator": {
                "primary_model": orch_model,
                "timeout_sec": orch_timeout,
                "candidate_models": orch_candidates,
            },
            "synthesis": {
                "primary_model": synth_model,
                "timeout_sec": synth_timeout,
                "candidate_models": synth_candidates,
            },
            "chat": {
                "primary_model": chat_model,
                "timeout_sec": chat_timeout,
                "candidate_models": chat_candidates,
            },
        },
        "static_parameters_source": "static/parameters.json",
        "static_parameters_count": len(STATIC_PARAMETERS),
        "paths": {
            "run_artifacts_dir": str(run_artifacts_dir),
            "central_artifacts_dir": str(central_artifacts_dir),
        }
    }

    # 6. Save Flow Setup Manifests (JSON and Markdown)
    save_artifact(
        "00_flow_config.json",
        json.dumps(flow_config, indent=2),
        output_dir=run_artifacts_dir
    )

    setup_md = f"""# 🏥 VetSentinel Dagu Flow Initialized

- **Patient:** {args.species} ({args.breed}), **{args.weight} kg**
- **Priority:** `{args.priority.upper()}`
- **Anamnesis:** {args.symptoms}
- **Language:** `{args.language}`
- **Timestamp:** `{flow_config['timestamp']}`

## ⚙️ Model Pipeline Configuration (from static/parameters.json)

| Pipeline Step | Fast Initial Model | Timeout | Candidate Fallback Chain & Long-Tail Fallback |
|---|---|---|---|
| **Step 1: Orchestrator** | `{orch_model}` | **{int(orch_timeout)}s** | `{' ➔ '.join(orch_candidates[:-1])}` ({int(orch_timeout)}s) ➔ **{orch_candidates[-1]}** (⚠️ **NO TIMEOUT — Waiting until completion**) |
| **Step 3: Clinical Synthesis** | `{synth_model}` | **{int(synth_timeout)}s** | `{' ➔ '.join(synth_candidates[:-1])}` ({int(synth_timeout)}s) ➔ **{synth_candidates[-1]}** (⚠️ **NO TIMEOUT — Waiting until completion**) |
| **Interactive Copilot Chat** | `{chat_model}` | **{int(chat_timeout)}s** | `{' ➔ '.join(chat_candidates[:-1])}` (25s) ➔ **{chat_candidates[-1]}** (⚠️ **NO TIMEOUT — Waiting until completion**) |

*Run artifacts directory:* `{run_artifacts_dir}`  
*Central sync directory:* `{central_artifacts_dir}`
"""
    save_artifact(
        "00_flow_setup.md",
        setup_md,
        output_dir=run_artifacts_dir
    )

    # 7. Mirror early to central directory
    try:
        shutil.copy2(run_artifacts_dir / "00_flow_config.json", central_artifacts_dir / "00_flow_config.json")
        shutil.copy2(run_artifacts_dir / "00_flow_setup.md", central_artifacts_dir / "00_flow_setup.md")
    except Exception as copy_err:
        log_warning(f"Could not mirror 00_flow artifacts to central directory: {copy_err}")

    log_success(
        f"Dagu emergency flow initialized via Python ({len(STATIC_PARAMETERS)} parameters loaded from static/parameters.json)."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_exception(e, "Step 0 Dagu flow initialization")
        sys.exit(1)
