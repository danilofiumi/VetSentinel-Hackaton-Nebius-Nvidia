# Parameters & Static Configuration

This directory contains static, non-secret parameters and environment defaults for **VetSentinel**.

## Files

- **`parameters.json`**: Primary static configuration file. Contains model identifiers, API endpoint URLs (`NEBIUS_API_URL`), per-step execution parameters (temperatures, token limits, timeouts, response format for Orchestrator, Clinical Synthesis, and Copilot Chat), service URLs, and internal filesystem paths.

## Precedence Order

Parameters are loaded following this precedence hierarchy:
1. **Explicit Environment Variable** (OS environment or command-line export)
2. **`.env` file** (reserved for sensitive credentials like `TAVILY_API_KEY` and `NEBIUS_API_KEY`)
3. **`static/parameters.json`** (static baseline defaults)

## Modifying Parameters

You can edit `parameters.json` directly at any time. Changes take effect on the next script run or service start without needing to modify your `.env` secret file.
