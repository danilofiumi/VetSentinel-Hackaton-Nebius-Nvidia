#!/usr/bin/env bash
set -e

# Ensure Dagu home and artifact directories exist
mkdir -p "${DAGU_HOME:-/app/.dagu}/dags" \
         "${DAGU_HOME:-/app/.dagu}/logs" \
         "${DAGU_HOME:-/app/.dagu}/data/artifacts/vetsentinel"

exec "$@"
