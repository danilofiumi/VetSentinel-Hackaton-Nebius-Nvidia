#!/usr/bin/env bash
# ==============================================================================
# Services Orchestration Script
# VetSentinel / Hackaton Workspace
# Concurrently manages PocketBase, Dagu Workflow Engine, and HackDashboard UI
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure binaries and wrapper scripts are executable
[ -f "$SCRIPT_DIR/app/pb/pocketbase" ] && chmod +x "$SCRIPT_DIR/app/pb/pocketbase"
[ -f "$SCRIPT_DIR/dagu" ] && chmod +x "$SCRIPT_DIR/dagu"

# Activate Python virtual environment if present (.venv)
if [ -d "$SCRIPT_DIR/.venv" ] && [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Load environment variables (.env in workspace root, then fallback HackDashboard/.env)
# Existing environment variables take precedence and will NOT be overwritten.
load_env_file() {
    local env_file="$1"
    if [ -f "$env_file" ]; then
        while IFS= read -r line || [ -n "$line" ]; do
            case "$line" in
                \#*|"") continue ;;
                *=*)
                    local var_name="${line%%=*}"
                    var_name="$(echo "$var_name" | xargs)"
                    if [ -z "${!var_name+x}" ]; then
                        eval "export $line"
                    fi
                    ;;
            esac
        done < "$env_file"
    fi
}

load_env_file "$SCRIPT_DIR/.env"
load_env_file "$SCRIPT_DIR/HackDashboard/.env"

# Default host and port configurations
PB_HOST="${PB_HOST:-127.0.0.1}"
PB_PORT="${PB_PORT:-8090}"
DAGU_HOST="${DAGU_HOST:-127.0.0.1}"
UI_HOST="${UI_HOST:-localhost}"
UI_PORT="${UI_PORT:-5173}"
# MANAGER_PORT="${MANAGER_PORT:-5174}"
# MARKETING_PORT="${MARKETING_PORT:-5175}"

# Read Dagu port from .dagu/config.yaml if not explicitly set
DAGU_PORT="${DAGU_PORT:-}"
if [ -z "$DAGU_PORT" ] && [ -f "$SCRIPT_DIR/.dagu/config.yaml" ]; then
    CONFIG_PORT=$(grep -E '^[[:space:]]*port:' "$SCRIPT_DIR/.dagu/config.yaml" | head -n1 | awk '{print $2}' | tr -d '"' | tr -d "'")
    if [ -n "$CONFIG_PORT" ]; then
        DAGU_PORT="$CONFIG_PORT"
    fi
fi
DAGU_PORT="${DAGU_PORT:-8075}"

# Service and target configuration
START_PB=true
START_DAGU=true
START_UI=true
UI_TARGET="${UI_TARGET:-admin}"

show_help() {
    cat << EOF
==============================================================================
VetSentinel / Hackaton Services Orchestrator
==============================================================================
Usage: ./start.sh [options]

Service Selection:
  --all                 Start PocketBase, Dagu, and Frontend UI (default)
  --no-ui, --backend    Start only backend services (PocketBase + Dagu)
  --pb-only             Start only PocketBase
  --dagu-only           Start only Dagu Workflow Engine
  --ui-only             Start only Frontend UI

Frontend Target Options (HackDashboard):
  --admin, --triage     Start VetSentinel Admin / Triage UI (default: port 5173)
  --manager             Start Console Manager UI (port 5174)
  --marketing           Start Marketing site (port 5175)
  --all-ui, --both-ui   Start both Admin (5173) and Manager (5174) concurrently
  --target <name>       Specify custom UI target (admin, manager, marketing, all)

Port Configuration:
  --port-pb <port>      Set PocketBase port (default: 8090)
  --port-dagu <port>    Set Dagu server port (default from .dagu/config.yaml or 8075)
  --port-ui <port>      Set Primary UI port (default: 5173)

Environment Overrides:
  PB_HOST, PB_PORT      PocketBase bind host and port
  DAGU_HOST, DAGU_PORT  Dagu bind host and port
  UI_PORT, UI_TARGET    Frontend port and build target
  -h, --help            Show this help message
==============================================================================
EOF
    exit 0
}

# Parse CLI arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --all)
            START_PB=true
            START_DAGU=true
            START_UI=true
            ;;
        --no-ui|--backend|--dagu-pb)
            START_PB=true
            START_DAGU=true
            START_UI=false
            ;;
        --pb-only)
            START_PB=true
            START_DAGU=false
            START_UI=false
            ;;
        --dagu-only)
            START_PB=false
            START_DAGU=true
            START_UI=false
            ;;
        --ui-only)
            START_PB=false
            START_DAGU=false
            START_UI=true
            ;;
        --admin|--triage)
            START_UI=true
            UI_TARGET="admin"
            ;;
        --manager)
            START_UI=true
            UI_TARGET="manager"
            ;;
        --marketing)
            START_UI=true
            UI_TARGET="marketing"
            ;;
        --all-ui|--both-ui)
            START_UI=true
            UI_TARGET="all"
            ;;
        --target|--ui-target)
            shift
            if [ $# -eq 0 ]; then
                echo "❌ Missing argument for target"
                exit 1
            fi
            UI_TARGET="$1"
            START_UI=true
            ;;
        --port-pb)
            shift
            PB_PORT="$1"
            ;;
        --port-dagu)
            shift
            DAGU_PORT="$1"
            ;;
        --port-ui)
            shift
            UI_PORT="$1"
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "❌ Unknown option: $1"
            echo "Run './start.sh --help' for available options."
            exit 1
            ;;
    esac
    shift
done

# If HackDashboard folder doesn't exist, disable UI automatically
if [ "$START_UI" = true ] && [ ! -d "$SCRIPT_DIR/HackDashboard" ]; then
    echo "⚠️  HackDashboard folder not found, skipping UI service."
    START_UI=false
fi

# Track spawned process IDs
PB_PID=""
DAGU_PID=""
UI_PIDS=()

# Helper function to kill a process and its child process tree
kill_tree() {
    local pid="$1"
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        # Find child PIDs
        local children
        children=$(pgrep -P "$pid" 2>/dev/null || true)
        for child in $children; do
            kill_tree "$child"
        done
        kill -TERM "$pid" 2>/dev/null || true
    fi
}

# Cleanup on exit or interruption
cleanup() {
    # Disable trap to avoid recursive calls
    trap - EXIT SIGINT SIGTERM SIGHUP
    echo ""
    echo "========================================================"
    echo "🛑 Shutting down services..."
    echo "========================================================"

    # Terminate UI processes
    for pid in "${UI_PIDS[@]}"; do
        if [ -n "$pid" ]; then
            kill_tree "$pid"
        fi
    done

    # Terminate Dagu process
    if [ -n "$DAGU_PID" ]; then
        kill_tree "$DAGU_PID"
    fi

    # Terminate PocketBase process
    if [ -n "$PB_PID" ]; then
        kill_tree "$PB_PID"
    fi

    # Give processes a brief moment to exit gracefully
    sleep 0.5

    # Force kill any lingering processes if still alive
    for pid in "${UI_PIDS[@]}"; do
        [ -n "$pid" ] && kill -9 "$pid" 2>/dev/null || true
    done
    [ -n "$DAGU_PID" ] && kill -9 "$DAGU_PID" 2>/dev/null || true
    [ -n "$PB_PID" ] && kill -9 "$PB_PID" 2>/dev/null || true

    wait 2>/dev/null || true
    echo "✓ All services stopped cleanly."
    exit 0
}

trap cleanup EXIT SIGINT SIGTERM SIGHUP

echo "========================================================"
echo "🚀 Initializing VetSentinel & Hackaton Workspace"
echo "========================================================"

# ------------------------------------------------------------------------------
# 1. Start PocketBase
# ------------------------------------------------------------------------------
if [ "$START_PB" = true ]; then
    PB_BIN="$SCRIPT_DIR/app/pb/pocketbase"
    if [ ! -f "$PB_BIN" ]; then
        echo "❌ PocketBase binary not found at $PB_BIN"
        exit 1
    fi

    if lsof -i :"$PB_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
        echo "⚠️  Port $PB_PORT is already in use. PocketBase is already running or port is occupied."
    else
        echo "📦 Starting PocketBase on http://${PB_HOST}:${PB_PORT}..."
        (cd "$SCRIPT_DIR/app/pb" && ./pocketbase serve --http="${PB_HOST}:${PB_PORT}") &
        PB_PID=$!
        sleep 1.2
    fi
fi

# ------------------------------------------------------------------------------
# 2. Start Dagu Dashboard & Workflow Server
# ------------------------------------------------------------------------------
if [ "$START_DAGU" = true ]; then
    DAGU_BIN="$SCRIPT_DIR/dagu"
    if [ ! -f "$DAGU_BIN" ]; then
        echo "❌ Dagu wrapper script not found at $DAGU_BIN"
        exit 1
    fi

    if lsof -i :"$DAGU_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
        echo "⚠️  Port $DAGU_PORT is already in use. Dagu server is already running or port is occupied."
    else
        echo "📊 Starting Dagu Dashboard on http://${DAGU_HOST}:${DAGU_PORT}..."
        "$DAGU_BIN" server --host="$DAGU_HOST" --port="$DAGU_PORT" &
        DAGU_PID=$!
        sleep 0.8
    fi
fi

# ------------------------------------------------------------------------------
# 3. Start Frontend (HackDashboard)
# ------------------------------------------------------------------------------
if [ "$START_UI" = true ]; then
    PKG_MGR="bun"
    if ! command -v bun >/dev/null 2>&1; then
        PKG_MGR="npx"
        echo "⚠️  'bun' command not found, using 'npx/npm' instead."
    fi

    case "$UI_TARGET" in
        all|both)
            echo "💻 Starting HackDashboard [Admin] (http://${UI_HOST}:${UI_PORT})..."
            if [ "$PKG_MGR" = "bun" ]; then
                (cd "$SCRIPT_DIR/HackDashboard" && bun x cross-env APP_TARGET=admin bun x vite dev --port "$UI_PORT") &
                UI_PIDS+=($!)
            else
                (cd "$SCRIPT_DIR/HackDashboard" && npx cross-env APP_TARGET=admin npx vite dev --port "$UI_PORT") &
                UI_PIDS+=($!)
                UI_PIDS+=($!)
            fi
            ;;
        manager)
            echo "💻 Starting HackDashboard [Manager] (http://${UI_HOST}:${UI_PORT})..."
            if [ "$PKG_MGR" = "bun" ]; then
                (cd "$SCRIPT_DIR/HackDashboard" && bun x cross-env APP_TARGET=manager bun x vite dev --port "$UI_PORT") &
                UI_PIDS+=($!)
            else
                (cd "$SCRIPT_DIR/HackDashboard" && npx cross-env APP_TARGET=manager npx vite dev --port "$UI_PORT") &
                UI_PIDS+=($!)
            fi
            ;;
        marketing)
            echo "💻 Starting HackDashboard [Marketing] (http://${UI_HOST}:${MARKETING_PORT})..."
            if [ "$PKG_MGR" = "bun" ]; then
                (cd "$SCRIPT_DIR/HackDashboard" && bun x cross-env APP_TARGET=marketing bun x vite dev --port "$MARKETING_PORT") &
                UI_PIDS+=($!)
            else
                (cd "$SCRIPT_DIR/HackDashboard" && npx cross-env APP_TARGET=marketing npx vite dev --port "$MARKETING_PORT") &
                UI_PIDS+=($!)
            fi
            ;;
        admin|*)
            echo "💻 Starting VetSentinel Admin UI (http://${UI_HOST}:${UI_PORT})..."
            if [ "$PKG_MGR" = "bun" ]; then
                (cd "$SCRIPT_DIR/HackDashboard" && bun x cross-env APP_TARGET=admin bun x vite dev --port "$UI_PORT") &
                UI_PIDS+=($!)
            else
                (cd "$SCRIPT_DIR/HackDashboard" && npx cross-env APP_TARGET=admin npx vite dev --port "$UI_PORT") &
                UI_PIDS+=($!)
            fi
            ;;
    esac
fi

# ------------------------------------------------------------------------------
# Summary Banner
# ------------------------------------------------------------------------------
echo ""
echo "========================================================"
echo "✨ Services Status:"
[ "$START_PB" = true ]   && echo "   🗄️  PocketBase:     http://${PB_HOST}:${PB_PORT} (Admin UI: http://${PB_HOST}:${PB_PORT}/_/)"
[ "$START_DAGU" = true ] && echo "   📊 Dagu Dashboard:  http://${DAGU_HOST}:${DAGU_PORT}"
if [ "$START_UI" = true ]; then
    if [ "$UI_TARGET" = "all" ] || [ "$UI_TARGET" = "both" ]; then
        echo "   💻 VetSentinel UI:  http://${UI_HOST}:${UI_PORT} (Target: admin)"
        echo "   💻 Console Manager: http://${UI_HOST}:${MANAGER_PORT} (Target: manager)"
    elif [ "$UI_TARGET" = "manager" ]; then
        echo "   💻 Console Manager: http://${UI_HOST}:${UI_PORT} (Target: manager)"
    elif [ "$UI_TARGET" = "marketing" ]; then
        echo "   💻 Marketing Site:  http://${UI_HOST}:${MARKETING_PORT} (Target: marketing)"
    else
        echo "   💻 VetSentinel UI:  http://${UI_HOST}:${UI_PORT} (Target: admin)"
    fi
fi
echo "========================================================"
echo "💡 Press Ctrl+C to stop all services cleanly."
echo "========================================================"

# Keep running and wait for background processes
set +e
wait
