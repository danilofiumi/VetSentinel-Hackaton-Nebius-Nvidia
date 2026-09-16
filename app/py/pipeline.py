import os
import sys
import time
import argparse
import subprocess
from pathlib import Path
from utils import (
    console,
    log_step,
    log_info,
    log_success,
    log_alert,
    get_default_artifacts_dir,
    resolve_output_dir,
    get_parameter,
    trace_call,
    log_exception,
    log_env_diagnostics,
)

@trace_call("main", log_args=False)
def main():
    parser = argparse.ArgumentParser(description="VetSentinel Unified Pipeline")
    parser.add_argument("--species", default=get_parameter("SPECIES", "Cat"))
    parser.add_argument("--breed", default=get_parameter("BREED", "European Shorthair"))
    parser.add_argument("--weight", default=get_parameter("WEIGHT", "4.0"))
    parser.add_argument("--symptoms", default=get_parameter("SYMPTOMS", "4.0 kg European Shorthair cat, ingested an unidentified cut flower 2h ago, vomiting and lethargy."))
    parser.add_argument("--priority", default=get_parameter("PRIORITY", "auto"))
    parser.add_argument("--output-dir", default=get_parameter("OUTPUT_DIR", None))
    args = parser.parse_args()

    artifacts_dir = resolve_output_dir(args.output_dir)
    os.environ["SPECIES"] = args.species
    os.environ["BREED"] = args.breed
    os.environ["WEIGHT"] = str(args.weight)
    os.environ["SYMPTOMS"] = args.symptoms
    os.environ["PRIORITY"] = args.priority
    os.environ["OUTPUT_DIR"] = str(artifacts_dir)

    log_env_diagnostics("Unified Pipeline Runner")

    python_bin = sys.executable
    script_dir = Path(__file__).resolve().parent

    console.print(f"[bold green]🚀 Starting VetSentinel Pipeline for {args.species} ({args.weight} kg)...[/bold green]")
    total_start = time.perf_counter()

    steps = [
        ("Step 1 · Orchestrator (Nebius)", script_dir / "01_orchestrator_nebius.py"),
        ("Step 2 · Web Search Specialist (Tavily)", script_dir / "02_web_search_tavily.py"),
        ("Step 3 · Clinical Synthesis (Nebius)", script_dir / "03_clinical_synthesis_nebius.py"),
    ]

    for step_title, script_path in steps:
        step_start = time.perf_counter()
        console.print(f"\n[cyan bold]▶ RUNNING {step_title.upper()}[/cyan bold] ({script_path.name})...")
        try:
            res = subprocess.run([python_bin, str(script_path)], check=True)
            step_duration = (time.perf_counter() - step_start) * 1000
            console.print(f"[bold green]✓ {step_title} finished in {step_duration:.0f}ms (exit code 0)[/bold green]")
        except subprocess.CalledProcessError as cpe:
            step_duration = (time.perf_counter() - step_start) * 1000
            console.print(f"[bold red]✖ {step_title} FAILED with exit code {cpe.returncode} after {step_duration:.0f}ms[/bold red]")
            log_exception(cpe, f"Executing subprocess {script_path.name}")
            raise

    total_duration = time.perf_counter() - total_start
    console.print(f"\n[bold green]✨ VetSentinel Pipeline completed successfully in {total_duration:.1f}s![/bold green]")
    console.print(f"[cyan]📁 All artifacts are available in: {artifacts_dir}[/cyan]\n")

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        log_exception(e, "Top-level Unified Pipeline runner")
        sys.exit(1)

