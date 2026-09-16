// PocketBase JS Hook for VetSentinel Emergency Triage System
// Production-Ready & Multi-Environment (Docker Compose & Local Host)
// Serves Static SPA & Proxies Dagu Workflow Engine

console.log('[PocketBase Hook] Loading VetSentinel production handlers...');

const utils = require(__hooks + "/vetsentinel_utils.js");
const activeStaticDir = utils.resolveStaticDir();

console.log('[PocketBase Hook] Serving static SPA from: ' + activeStaticDir);

// ---------------------------------------------------------------------------
// 1. Static SPA Serving & Fallbacks
// ---------------------------------------------------------------------------

// Optional /manager sub-app route
try {
    const managerDir = activeStaticDir.replace(/\/admin$/, '/manager');
    const mgrFiles = $os.readDir(managerDir);
    if (mgrFiles && mgrFiles.length > 0) {
        routerAdd("GET", "/manager/{path...}", $apis.static(managerDir, true));
        console.log('[PocketBase Hook] Registered /manager SPA route: ' + managerDir);
    }
} catch (e) {}

// Main VetSentinel App at /
routerAdd("GET", "/{path...}", $apis.static(activeStaticDir, true));

// ---------------------------------------------------------------------------
// 2. API Endpoints
// ---------------------------------------------------------------------------

// System Status & Diagnostics
routerAdd("GET", "/api/status", (e) => {
    return require(__hooks + "/vetsentinel_utils.js").handleStatus(e);
});

// Artifacts API (Single file or aggregated clinical outputs)
routerAdd("GET", "/api/artifacts", (e) => {
    return require(__hooks + "/vetsentinel_utils.js").handleArtifacts(e);
});

// Execution Logs API (Secure reading with path sanitization)
routerAdd("GET", "/api/dag-logs", (e) => {
    return require(__hooks + "/vetsentinel_utils.js").handleDagLogs(e);
});

// Real-Time Context-Aware Clinical AI Copilot Chat
routerAdd("POST", "/api/clinical-chat", (e) => {
    return require(__hooks + "/vetsentinel_utils.js").handleClinicalChat(e);
});

// Universal Dagu Workflow Engine Proxy
routerAdd("GET", "/api/dagu/{path...}", (e) => {
    return require(__hooks + "/vetsentinel_utils.js").proxyDaguRequest(e, "GET");
});

routerAdd("POST", "/api/dagu/{path...}", (e) => {
    return require(__hooks + "/vetsentinel_utils.js").proxyDaguRequest(e, "POST");
});

routerAdd("PUT", "/api/dagu/{path...}", (e) => {
    return require(__hooks + "/vetsentinel_utils.js").proxyDaguRequest(e, "PUT");
});

routerAdd("DELETE", "/api/dagu/{path...}", (e) => {
    return require(__hooks + "/vetsentinel_utils.js").proxyDaguRequest(e, "DELETE");
});

routerAdd("PATCH", "/api/dagu/{path...}", (e) => {
    return require(__hooks + "/vetsentinel_utils.js").proxyDaguRequest(e, "PATCH");
});

console.log('[PocketBase Hook] ✓ VetSentinel production handlers registered successfully');
