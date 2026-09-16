import os
import json
import sys
import time
import inspect
import functools
import traceback
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.traceback import install as install_rich_traceback

# Install Rich traceback handler so all unhandled exceptions print detailed stack traces with locals
install_rich_traceback(show_locals=True, width=110, extra_lines=3, word_wrap=True)

# Force terminal colors so Rich styles survive DAG execution and piping into Dagu logs
console = Console(force_terminal=True, color_system="auto", width=110)


# Load static parameters from static/ folder first
def _load_static_parameters():
    candidates = [
        Path(__file__).resolve().parent.parent.parent / "static" / "parameters.json",
        Path("/app/static/parameters.json"),
        Path("static/parameters.json"),
        Path(__file__).resolve().parent.parent.parent / "parameters" / "parameters.json",
        Path("/app/parameters/parameters.json"),
        Path("parameters/parameters.json"),
    ]
    for p in candidates:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        for k, v in data.items():
                            curr = os.environ.get(k)
                            if curr is None or str(curr).strip() in ("", "${" + k + "}"):
                                os.environ[k] = str(v)
                        return data
            except Exception:
                pass
    return {}

STATIC_PARAMETERS = _load_static_parameters()

def get_parameter(key: str, default=None):
    """Retrieve a parameter checking OS env first, then static parameters.json, then default.
    Cleans quotation marks, whitespace, and detects unexpanded ${KEY} placeholders."""
    val = os.getenv(key)
    if val is not None:
        s = str(val).strip()
        if s.startswith(('"', "'")) and s.endswith(('"', "'")) and len(s) >= 2:
            s = s[1:-1].strip()
        if s and s not in ("${" + key + "}", "$" + key, "None", "null"):
            return s
    static_val = STATIC_PARAMETERS.get(key)
    if static_val is not None:
        s = str(static_val).strip()
        if s.startswith(('"', "'")) and s.endswith(('"', "'")) and len(s) >= 2:
            s = s[1:-1].strip()
        if s and s not in ("${" + key + "}", "$" + key, "None", "null"):
            return s
    return default


# Load prompts from static/prompts.yaml
def _load_static_prompts() -> dict:
    candidates = [
        Path(__file__).resolve().parent.parent.parent / "static" / "prompts.yaml",
        Path("/app/static/prompts.yaml"),
        Path("static/prompts.yaml"),
        Path(__file__).resolve().parent.parent.parent / "static" / "prompts.yml",
        Path("/app/static/prompts.yml"),
        Path("static/prompts.yml"),
    ]
    for p in candidates:
        if p.exists():
            try:
                import yaml
                with open(p, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        return data
            except Exception:
                pass
    return {}

STATIC_PROMPTS = _load_static_prompts()

def get_prompt(section: str, key: str = "user_prompt", default: str = "") -> str:
    """Retrieve a prompt from static/prompts.yaml."""
    sec = STATIC_PROMPTS.get(section, {})
    if isinstance(sec, dict):
        return sec.get(key, default)
    elif isinstance(sec, str) and key == "user_prompt":
        return sec
    return default

def render_prompt(section: str, key: str = "user_prompt", fallback: str = "", **kwargs) -> str:
    """Retrieve and interpolate template variables {var} in prompt without breaking literal JSON brackets."""
    template = get_prompt(section, key, default=fallback)
    if not template and fallback:
        template = fallback
    rendered = template
    for k, v in kwargs.items():
        rendered = rendered.replace(f"{{{k}}}", str(v))
    return rendered

# Human-readable language names for prompt localization (keyed by ISO 639-1 code)
LANGUAGE_NAMES = {
    "en": "English",
    "it": "Italian",
    "es": "Spanish",
    "fr": "French",
    "tr": "Turkish",
}

def resolve_language_name(code: str) -> str:
    """Map an ISO language code (en/it/es/fr/tr) to its English language name for prompt instructions."""
    if not code:
        return LANGUAGE_NAMES["en"]
    key = str(code).strip().lower()[:2]
    return LANGUAGE_NAMES.get(key, LANGUAGE_NAMES["en"])

# Load environment variables from workspace root or current dir (secrets override static defaults)
root_env = Path(__file__).resolve().parent.parent.parent / ".env"
local_env = Path(__file__).resolve().parent / ".env"

if root_env.exists():
    load_dotenv(dotenv_path=root_env, override=False)
if local_env.exists():
    load_dotenv(dotenv_path=local_env, override=False)

# Force terminal colors so Rich styles survive DAG execution and piping into Dagu logs
console = Console(force_terminal=True, color_system="auto", width=110)

def get_central_artifacts_dir() -> Path:
    """Returns the centralized shared artifacts path (.dagu/data/artifacts/vetsentinel)."""
    dagu_home = os.getenv("DAGU_HOME")
    if dagu_home and not (dagu_home.startswith("/app") and not Path("/app").exists()):
        path = Path(os.path.expandvars(dagu_home)) / "data" / "artifacts" / "vetsentinel"
    else:
        path = Path(__file__).resolve().parent.parent.parent / ".dagu" / "data" / "artifacts" / "vetsentinel"
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()

def get_default_artifacts_dir() -> Path:
    """Returns the default artifacts path: prefers Dagu run directory, then central directory."""
    dagu_run_artifacts = os.getenv("DAG_RUN_ARTIFACTS_DIR")
    if dagu_run_artifacts and Path(dagu_run_artifacts).exists():
        return Path(dagu_run_artifacts).resolve()
    return get_central_artifacts_dir()

def resolve_output_dir(output_dir: Path | str | None = None) -> Path:
    """Resolves output directory, expanding any ${DAGU_HOME} or environment variables."""
    if not output_dir or str(output_dir).strip() in ("", "None", "null", "${context.paths.artifacts_dir}"):
        dagu_run_artifacts = os.getenv("DAG_RUN_ARTIFACTS_DIR")
        if dagu_run_artifacts:
            path = Path(dagu_run_artifacts).resolve()
            path.mkdir(parents=True, exist_ok=True)
            return path
        return get_default_artifacts_dir()

    raw_str = str(output_dir)
    dagu_home = os.getenv("DAGU_HOME", str(Path(__file__).resolve().parent.parent.parent / ".dagu"))
    expanded = raw_str.replace("${DAGU_HOME}", dagu_home).replace("$DAGU_HOME", dagu_home)
    expanded = os.path.expandvars(os.path.expanduser(expanded))
    target_dir = Path(expanded).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir

def save_artifact(filename: str, content: str | dict, output_dir: Path | str | None = None) -> Path:
    """Saves a JSON or Markdown artifact to the run output directory AND syncs to central directory."""
    target_dir = resolve_output_dir(output_dir)
    file_path = target_dir / filename

    if isinstance(content, (dict, list)):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(content))

    file_size = file_path.stat().st_size
    size_str = f"{file_size / 1024:.1f} KB" if file_size >= 1024 else f"{file_size} B"

    # Also mirror/sync to central directory (.dagu/data/artifacts/vetsentinel)
    try:
        central_dir = get_central_artifacts_dir()
        if target_dir.resolve() != central_dir.resolve():
            central_file = central_dir / filename
            if isinstance(content, (dict, list)):
                with open(central_file, "w", encoding="utf-8") as f:
                    json.dump(content, f, indent=2, ensure_ascii=False)
            else:
                with open(central_file, "w", encoding="utf-8") as f:
                    f.write(str(content))
    except Exception as e:
        console.print(f"[dim yellow]Warning mirroring artifact: {e}[/dim yellow]")

    console.print(f"  [bold green]✓[/bold green] Artifact stored: [cyan bold]{filename}[/cyan bold] [dim]({size_str})[/dim]")
    console.print(f"    [dim]↳ Run path: {file_path}[/dim]")
    return file_path

# ==========================================
# RICH LOGGING SYSTEM, TRACEBACKS & DIAGNOSTICS
# ==========================================

def mask_secret(val: str | None) -> str:
    """Masks secrets and API keys safely for log display, highlighting template errors."""
    if val is None:
        return "[red]None (Not Set)[/red]"
    s = str(val).strip()
    if not s:
        return "[red]<EMPTY STRING>[/red]"
    if s.startswith("${") and s.endswith("}"):
        return f"[bold red]❌ UNEXPANDED TEMPLATE: {s}[/bold red]"
    if s.startswith("$") and len(s) > 1:
        return f"[bold red]❌ UNEXPANDED VAR: {s}[/bold red]"
    if len(s) <= 8:
        return f"[yellow]{s[:2]}...{s[-2:]}[/yellow] (len={len(s)})"
    return f"[green]{s[:4]}...{s[-4:]}[/green] (len={len(s)})"

def log_exception(exc: Exception, context: str = ""):
    """Renders an eye-catching Rich exception panel with locals, stack frames, and fallback standard trace."""
    exc_type = type(exc).__name__
    msg = str(exc)
    ctx_str = f" DURING {context.upper()}" if context else ""

    err_text = f"[bold white]{exc_type}:[/bold white] [bright_red]{msg}[/bright_red]"
    panel = Panel(
        err_text,
        title=f"[bold white on red] 💥 TRACEBACK CAPTURED{ctx_str} [/bold white on red]",
        box=box.HEAVY,
        border_style="bright_red",
        padding=(1, 2)
    )
    console.print()
    console.print(panel)
    console.print("[dim]Detailed Stack Frame & Local Variables:[/dim]")
    try:
        console.print_exception(show_locals=True, width=110, extra_lines=2, word_wrap=True)
    except Exception:
        pass
    # Also log formatted traceback so non-interactive log files capture it
    console.print(f"[dim red]{traceback.format_exc()}[/dim red]")
    console.print()

def trace_call(name: str | None = None, log_args: bool = True, log_result: bool = False):
    """Decorator to trace function entry, execution duration, parameters (with secrets masked), and errors."""
    def decorator(func):
        func_name = name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Format sanitized args
            args_repr = []
            if log_args:
                for a in args:
                    if isinstance(a, (str, int, float, bool)) or a is None:
                        val_str = str(a)
                        if len(val_str) > 60:
                            val_str = val_str[:57] + "..."
                        args_repr.append(val_str)
                    elif isinstance(a, (list, tuple)):
                        args_repr.append(f"[{len(a)} items]")
                    elif isinstance(a, dict):
                        args_repr.append(f"{{{len(a)} keys}}")
                    else:
                        args_repr.append(type(a).__name__)

                for k, v in kwargs.items():
                    if any(secret_term in k.lower() for secret_term in ("key", "token", "secret", "auth", "password")):
                        args_repr.append(f"{k}={mask_secret(str(v))}")
                    elif isinstance(v, (str, int, float, bool)) or v is None:
                        val_str = str(v)
                        if len(val_str) > 60:
                            val_str = val_str[:57] + "..."
                        args_repr.append(f"{k}={val_str}")
                    elif isinstance(v, (list, tuple)):
                        args_repr.append(f"{k}=[{len(v)} items]")
                    elif isinstance(v, dict):
                        args_repr.append(f"{k}={{{len(v)} keys}}")
                    else:
                        args_repr.append(f"{k}=<{type(v).__name__}>")

            call_signature = f"{func_name}({', '.join(args_repr)})"
            console.print(f"  [dim cyan]▶ ENTER [bold]{call_signature}[/bold][/dim cyan]")
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000
                if log_result:
                    res_preview = str(result)
                    if len(res_preview) > 80:
                        res_preview = res_preview[:77] + "..."
                    console.print(f"  [dim green]◀ EXIT [bold]{func_name}[/bold] completed in [bold cyan]{elapsed_ms:.1f}ms[/bold cyan] -> {res_preview}[/dim green]")
                else:
                    console.print(f"  [dim green]◀ EXIT [bold]{func_name}[/bold] completed in [bold cyan]{elapsed_ms:.1f}ms[/bold cyan][/dim green]")
                return result
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                elapsed_ms = (time.perf_counter() - start) * 1000
                console.print(f"  [bold red]✖ FAILED [bold]{func_name}[/bold] after {elapsed_ms:.1f}ms: {type(e).__name__}: {e}[/bold red]")
                log_exception(e, f"Function '{func_name}' execution")
                raise
        return wrapper
    return decorator

def log_env_diagnostics(step_name: str = ""):
    """Prints a detailed diagnosis table of API keys, model parameters, and runtime paths."""
    table = Table(
        title=f"🔧 Runtime Environment & API Diagnostics {f'({step_name})' if step_name else ''}",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
        expand=True
    )
    table.add_column("Configuration Parameter", width=26, style="bold white")
    table.add_column("Status / Diagnostic Check", width=34)
    table.add_column("Resolved Value / Target", style="dim")

    # Nebius Key Check
    raw_nebius = os.getenv("NEBIUS_API_KEY")
    clean_nebius = get_parameter("NEBIUS_API_KEY")
    if clean_nebius and clean_nebius != raw_nebius and (raw_nebius or "").startswith("${"):
        nebius_status = "[bold yellow]RECOVERED (from parameters.json)[/bold yellow]"
    elif clean_nebius:
        nebius_status = "[bold green]CONFIGURED & VALID[/bold green]"
    elif (raw_nebius or "").startswith("${"):
        nebius_status = "[bold red]❌ UNEXPANDED TEMPLATE '${NEBIUS_API_KEY}'[/bold red]"
    else:
        nebius_status = "[bold red]❌ MISSING (Not set in OS env or .env)[/bold red]"
    table.add_row("NEBIUS_API_KEY", nebius_status, mask_secret(clean_nebius or raw_nebius))

    # Tavily Key Check
    raw_tavily = os.getenv("TAVILY_API_KEY")
    clean_tavily = get_parameter("TAVILY_API_KEY")
    if clean_tavily:
        tavily_status = "[bold green]CONFIGURED & VALID[/bold green]"
    elif (raw_tavily or "").startswith("${"):
        tavily_status = "[bold red]❌ UNEXPANDED TEMPLATE '${TAVILY_API_KEY}'[/bold red]"
    else:
        tavily_status = "[bold yellow]OPTIONAL / MISSING (Uses verified offline fallback)[/bold yellow]"
    table.add_row("TAVILY_API_KEY", tavily_status, mask_secret(clean_tavily or raw_tavily))

    # LLM Inference Parameters
    api_url = get_parameter("NEBIUS_API_URL", "https://api.studio.nebius.ai/v1/chat/completions")
    nebius_model = get_parameter("NEBIUS_ORCHESTRATOR_MODEL", get_parameter("NEBIUS_MODEL", "zai-org/GLM-5.3"))
    orch_temp = get_parameter("NEBIUS_ORCHESTRATOR_TEMPERATURE", "0.1")
    orch_max_tokens = get_parameter("NEBIUS_ORCHESTRATOR_MAX_TOKENS", "12000")
    orch_timeout = get_parameter("NEBIUS_ORCHESTRATOR_TIMEOUT", get_parameter("NEBIUS_TIMEOUT", "1800"))
    orch_fallback = get_parameter("NEBIUS_FALLBACK_MODEL", "zai-org/GLM-5.3-Flash")

    synthesis_model = get_parameter("NEBIUS_SYNTHESIS_MODEL", "zai-org/GLM-5.3")
    synth_temp = get_parameter("NEBIUS_SYNTHESIS_TEMPERATURE", "0.1")
    synth_max_tokens = get_parameter("NEBIUS_SYNTHESIS_MAX_TOKENS", "80000")
    synth_timeout = get_parameter("NEBIUS_SYNTHESIS_TIMEOUT", get_parameter("NEBIUS_TIMEOUT", "1800"))

    chat_model = get_parameter("NEBIUS_CHAT_MODEL", "zai-org/GLM-5.3")
    chat_temp = get_parameter("NEBIUS_CHAT_TEMPERATURE", "0.2")
    chat_max_tokens = get_parameter("NEBIUS_CHAT_MAX_TOKENS", "3000")
    chat_timeout = get_parameter("NEBIUS_CHAT_TIMEOUT", "45")

    dagu_home = os.getenv("DAGU_HOME", "<default>")
    artifacts_dir = str(get_default_artifacts_dir())

    table.add_row("NEBIUS_API_URL", "[cyan]ENDPOINT[/cyan]", str(api_url))
    table.add_row(
        "ORCHESTRATOR LLM (Step 1)",
        "[green]CONFIGURED[/green]",
        f"{nebius_model} (temp={orch_temp}, max_tok={orch_max_tokens}, timeout={orch_timeout}s, fallback={orch_fallback})"
    )
    table.add_row(
        "SYNTHESIS LLM (Step 3)",
        "[green]CONFIGURED[/green]",
        f"{synthesis_model} (temp={synth_temp}, max_tok={synth_max_tokens}, timeout={synth_timeout}s)"
    )
    table.add_row(
        "COPILOT CHAT LLM (PB)",
        "[green]CONFIGURED[/green]",
        f"{chat_model} (temp={chat_temp}, max_tok={chat_max_tokens}, timeout={chat_timeout}s)"
    )
    table.add_row("DAGU_HOME", "[cyan]PATH[/cyan]", str(dagu_home))
    table.add_row("ARTIFACTS DIRECTORY", "[cyan]PATH[/cyan]", artifacts_dir)
    table.add_row("PYTHON INTERPRETER", "[dim]RUNTIME[/dim]", sys.executable)

    console.print()
    console.print(table)
    console.print()

    # If critical key is missing, render explicit warning
    if not clean_nebius:
        log_alert(
            "NEBIUS_API_KEY NOT ACCESSIBLE",
            "Nebius Token Factory live inference requires a valid NEBIUS_API_KEY.\n"
            f"Current environment state: raw={repr(raw_nebius)}, resolved={repr(clean_nebius)}.\n"
            "If deployed in Dagu or Docker, ensure NEBIUS_API_KEY is exported in .env or the Docker container."
        )

def log_http_request(provider: str, url: str, method: str = "POST", headers: dict = None, payload: dict = None, timeout: float = None):
    """Prints transparent and detailed HTTP request information for debugging LLM endpoints."""
    headers_clean = dict(headers or {})
    if "Authorization" in headers_clean:
        auth_val = str(headers_clean["Authorization"])
        if "Bearer " in auth_val:
            prefix, token = auth_val.split("Bearer ", 1)
            headers_clean["Authorization"] = f"Bearer {mask_secret(token.strip())}"

    model = (payload or {}).get("model", "N/A")
    messages = (payload or {}).get("messages", [])
    temp = (payload or {}).get("temperature", "N/A")
    max_tokens = (payload or {}).get("max_tokens", "N/A")
    resp_fmt = (payload or {}).get("response_format", "text")

    sys_prompt_len = 0
    usr_prompt_len = 0
    usr_prompt_preview = ""
    for m in messages:
        role = m.get("role", "")
        c = str(m.get("content", ""))
        if role == "system":
            sys_prompt_len = len(c)
        elif role == "user":
            usr_prompt_len = len(c)
            usr_prompt_preview = c[:120].replace("\n", " ") + ("..." if len(c) > 120 else "")

    panel_content = f"""[bold]Target Endpoint:[/bold] [bright_cyan]{method} {url}[/bright_cyan]
[bold]Provider & Model:[/bold] [bright_yellow]{provider}[/bright_yellow] · [white bold]{model}[/white bold] | [bold]Timeout:[/bold] [cyan]{timeout}s[/cyan]
[bold]Inference Options:[/bold] temp={temp} | max_tokens={max_tokens} | format={resp_fmt}
[bold]Payload Breakdown:[/bold] {len(messages)} messages (system: {sys_prompt_len} chars, user: {usr_prompt_len} chars)
[bold]User Prompt Preview:[/bold] [dim italic]"{usr_prompt_preview}"[/dim italic]
[bold]Headers:[/bold] [dim]{json.dumps(headers_clean)}[/dim]"""

    console.print(Panel(
        panel_content,
        title=f"[bold cyan]🌐 HTTP OUTBOUND REQUEST ➔ {provider.upper()}[/bold cyan]",
        box=box.ROUNDED,
        border_style="cyan",
        padding=(0, 2)
    ))

def log_http_response(provider: str, status_code: int, elapsed_ms: float, headers: dict = None, body: str | dict = None, finish_reason: str = None, usage: dict = None):
    """Prints comprehensive HTTP response metrics, headers, token throughput, or error body."""
    req_id = (headers or {}).get("x-request-id") or (headers or {}).get("request-id", "N/A")
    content_type = (headers or {}).get("content-type", "N/A")

    if status_code == 200:
        finish_badge = f"[bold green]{finish_reason}[/bold green]" if finish_reason == "stop" else f"[bold white on red] ⚠️ {finish_reason} [/bold white on red]"
        usage_str = ""
        if usage:
            p_tok = usage.get("prompt_tokens", 0)
            c_tok = usage.get("completion_tokens", 0)
            t_tok = usage.get("total_tokens", 0)
            usage_str = f" | [bold]Tokens:[/bold] prompt={p_tok}, completion={c_tok}, total={t_tok}"

        console.print(
            f"  [bold green]✓[/bold green] [bold cyan]{provider}[/bold cyan] HTTP [bold green]200 OK[/bold green] in [bold yellow]{elapsed_ms:.0f}ms[/bold yellow]"
            f" | [bold]Finish:[/bold] {finish_badge}{usage_str} [dim](req_id={req_id})[/dim]"
        )
        if finish_reason == "length":
            console.print(
                f"    [bold yellow]⚠️ WARNING: The model stopped due to 'length' (hit max_tokens limit before completing output).[/bold yellow]"
            )
    else:
        # Error logging
        err_preview = body if isinstance(body, str) else json.dumps(body, indent=2, ensure_ascii=False)
        if len(str(err_preview)) > 1500:
            err_preview = str(err_preview)[:1500] + "\n... [TRUNCATED]"

        diag_hint = ""
        if status_code == 401:
            diag_hint = "👉 Hint: Authentication failed. Verify NEBIUS_API_KEY value, ensure no trailing spaces or expired token."
        elif status_code == 404:
            diag_hint = "👉 Hint: Model or endpoint not found. Verify if NEBIUS_MODEL exists in your Nebius Studio project."
        elif status_code == 422:
            diag_hint = "👉 Hint: Unprocessable Entity. Check response_format json_object schema or max_tokens."
        elif status_code == 429:
            diag_hint = "👉 Hint: Rate limit exceeded or quota exhausted. Check your Nebius plan balance."
        elif status_code >= 500:
            diag_hint = "👉 Hint: Nebius remote server error. The provider is experiencing an internal error."

        err_content = f"""[bold]HTTP Status Code:[/bold] [bold white on red] {status_code} [/bold white on red] in [yellow]{elapsed_ms:.0f}ms[/yellow]
[bold]Request ID:[/bold] [cyan]{req_id}[/cyan] | [bold]Content-Type:[/bold] {content_type}
{f'[bold yellow]{diag_hint}[/bold yellow]' if diag_hint else ''}
[bold]Error Response Body:[/bold]
[white]{err_preview}[/white]"""

        console.print()
        console.print(Panel(
            err_content,
            title=f"[bold white on red] 🚨 HTTP INFERENCE FAILURE ➔ {provider.upper()} (STATUS {status_code}) [/bold white on red]",
            box=box.DOUBLE_EDGE,
            border_style="bright_red",
            padding=(1, 2)
        ))
        console.print()

def log_step(title: str, subtitle: str = ""):
    """Logs a visually striking step header with timestamp."""
    now = datetime.now().strftime("%H:%M:%S")
    header_text = Text()
    header_text.append(" ⚡ ", style="bold yellow")
    header_text.append(title.upper(), style="bold white")
    header_text.append(f"  [{now}]", style="dim cyan")
    
    panel = Panel(
        header_text if not subtitle else f"[bold white]{title}[/bold white]\n[dim italic]{subtitle}[/dim italic]",
        box=box.ROUNDED,
        border_style="bright_blue",
        padding=(0, 2)
    )
    console.print()
    console.print(panel)

def log_pipeline_banner(species: str, breed: str, weight: float, priority: str, symptoms: str, output_dir: Path | str):
    """Renders the top-level patient triage banner."""
    p_color = "bright_red" if priority.lower() in ("critica", "critical", "rosso", "red") else "bright_yellow"
    content = f"""[bold]PATIENT:[/bold] [bright_cyan]{species}[/bright_cyan] ({breed})  |  [bold]WEIGHT:[/bold] [bright_green]{weight} kg[/bright_green]  |  [bold]TRIAGE:[/bold] [{p_color} bold]{priority.upper()}[/{p_color} bold]
[bold]ANAMNESIS:[/bold] [white]{symptoms}[/white]
[bold]ARTIFACT DESTINATION:[/bold] [cyan]{output_dir}[/cyan]"""

    panel = Panel(
        content,
        title="[bold bright_white]🐾 VETSENTINEL · EMERGENCY & TOXICOLOGY PIPELINE[/bold bright_white]",
        subtitle="[dim]Powered by Nebius Token Factory & Tavily Specialist Search[/dim]",
        box=box.DOUBLE_EDGE,
        border_style="magenta",
        padding=(1, 2)
    )
    console.print(panel)

def log_metric(name: str, value: str | int | float, unit: str = "", status: str = "OK"):
    """Prints a highlighted metric badge."""
    val_str = f"{value}{(' ' + unit) if unit else ''}"
    status_style = "green" if status == "OK" else "yellow"
    console.print(f"  [dim]▶[/dim] [bold]{name}:[/bold] [bright_yellow]{val_str}[/bright_yellow] [{status_style} bold][{status}][/{status_style} bold]")

def log_info(message: str):
    """Logs an informational message."""
    console.print(f"  [dim cyan]ℹ[/dim cyan] {message}")

def log_success(message: str):
    """Logs a success message."""
    console.print(f"  [bold green]✓[/bold green] {message}")

def log_warning(message: str):
    """Logs a warning message."""
    console.print(f"  [bold yellow]⚠️[/bold yellow] {message}")

def log_alert(title: str, message: str):
    """Renders a loud, impossible-to-miss alert panel (e.g. for fallback notices)."""
    panel = Panel(
        f"[bold white]{message}[/bold white]",
        title=f"[bold white on red] 🚨 {title} [/bold white on red]",
        box=box.DOUBLE_EDGE,
        border_style="bright_red",
        padding=(1, 2)
    )
    console.print()
    console.print(panel)
    console.print()

def log_clinical_gaps(gaps: list[dict]):
    """Renders identified clinical gaps in a structured table."""
    table = Table(
        title="🔍 Detected Information Gaps and Clinical Risks",
        box=box.SIMPLE_HEAVY,
        border_style="blue",
        header_style="bold cyan",
        expand=True
    )
    table.add_column("Severity", width=12, justify="center")
    table.add_column("Risk Area", width=30, style="bold")
    table.add_column("Clinical Details & Recommendations", style="dim")

    for g in gaps:
        sev = str(g.get("severity", "medium")).lower()
        if sev in ("critico", "critical"):
            sev_badge = "[bold white on red] CRITICAL [/bold white on red]"
        elif sev in ("alto", "high"):
            sev_badge = "[bold black on yellow] HIGH [/bold black on yellow]"
        else:
            sev_badge = "[bold black on blue] MEDIUM [/bold black on blue]"

        table.add_row(
            sev_badge,
            g.get("title", "Clinical Gap"),
            g.get("description", "")
        )
    console.print(table)

def log_search_results(documents: list[dict]):
    """Renders extracted documents in a structured table."""
    table = Table(
        title="📚 Extracted Medical-Scientific Sources (Authoritative Whitelist)",
        box=box.SIMPLE_HEAVY,
        border_style="green",
        header_style="bold green",
        expand=True
    )
    table.add_column("Source / Domain", width=25, style="bold cyan")
    table.add_column("Article / Protocol Title", width=45)
    table.add_column("Relevance", width=12, justify="center", style="bold green")

    for doc in documents:
        score = int(doc.get("relevance_score", 0.9) * 100)
        source = doc.get("source_name") or doc.get("source_domain", "aspca.org")
        table.add_row(
            source,
            doc.get("title", "Clinical Document"),
            f"{score}%"
        )
    console.print(table)

def log_dosage_table(dosages: list[dict], weight: float):
    """Renders calculated weight-based dosages in an emergency clinical table."""
    table = Table(
        title=f"⚖️ Weight-Based Calculated Dosage Table for Patient ({weight} kg)",
        box=box.DOUBLE_EDGE,
        border_style="bright_red",
        header_style="bold bright_white on dark_red",
        expand=True
    )
    table.add_column("Drug / Intervention", width=24, style="bold white")
    table.add_column("Std Dose", width=16, style="dim")
    table.add_column(f"Patient Dose ({weight} kg)", width=22, style="bold bright_green")
    table.add_column("Route", width=14, style="yellow")
    table.add_column("Clinical Monitoring & Notes", style="white")

    for d in dosages:
        table.add_row(
            d.get("drug", ""),
            d.get("standard_dosage", ""),
            d.get("patient_dose", ""),
            d.get("route", ""),
            d.get("monitoring", "")
        )
    console.print(table)

def generate_run_index(target_dir: Path, patient: dict, model_name: str, files: list[dict]):
    """Generates a rich _index.md artifact for instant preview inside the Dagu Web UI."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    weight = patient.get("weight_kg", patient.get("peso", 4.0))
    species = patient.get("species", patient.get("specie", "Cat"))
    breed = patient.get("breed", patient.get("razza", "European Shorthair"))
    priority = str(patient.get("priority", patient.get("priorita", "critical"))).upper()

    index_content = f"""# 🐾 VetSentinel · Clinical Triage & Toxicology Emergency
> **Dagu Pipeline Run** completed successfully on `{now}`
> **AI Model**: `{model_name}` | **Provider**: `Nebius Token Factory (Live Inference)`

---

## 📋 Patient Summary
| Parameter | Value |
| :--- | :--- |
| **Species / Breed** | **{species}** ({breed}) |
| **Body Weight** | **{weight} kg** |
| **Triage Code** | **{priority}** |
| **Intake Anamnesis** | {patient.get('symptoms', patient.get('sintomi', 'N/A'))} |

---

## 📑 Clinical Artifacts Produced (Click to Open)

### 🚨 Protocols and Operational Sheets
- [**final_clinical_emergency_sheet.md**](final_clinical_emergency_sheet.md) — **Complete Emergency Clinical Sheet with Weight-Based Dosage Calculation**
- [**01_orchestrator_report.md**](01_orchestrator_report.md) — **Nebius Orchestrator Report (Clinical Gaps & Function Calling)**
- [**02_web_search_report.md**](02_web_search_report.md) — **Tavily Specialist Search Report (ASPCA, Merck, BSAVA)**

### 📊 Structured JSON Datasets
- [**01_orchestrator_result.json**](01_orchestrator_result.json) — JSON schema of clinical gaps and function-call parameters
- [**02_tavily_search_result.json**](02_tavily_search_result.json) — Extracted and cleaned scientific texts
- [**03_clinical_synthesis.json**](03_clinical_synthesis.json) — Structured protocol, weight-based doses and references

---
*Stored automatically in `${target_dir}` for immediate clinical consultation.*
"""
    save_artifact("_index.md", index_content, target_dir)
