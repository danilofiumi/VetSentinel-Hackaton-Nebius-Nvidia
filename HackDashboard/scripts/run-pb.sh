#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check if PocketBase is already running (port 8090 occupied or process active)
if lsof -i :8090 >/dev/null 2>&1 || pgrep -f "pocketbase" >/dev/null; then
    echo "ℹ️ PocketBase is already running. Skipping startup..."
    while true; do sleep 3600; done
else
    # Change to the PocketBase directory relative to this script and serve
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "${SCRIPT_DIR}/../../app/pb" && ./pocketbase serve
fi
