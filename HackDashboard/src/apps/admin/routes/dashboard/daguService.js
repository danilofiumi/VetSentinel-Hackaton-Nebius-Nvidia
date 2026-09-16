// Standalone Dagu service functions for VetSentinel Emergency Pipeline

function sanitizeParam(str) {
  if (str === undefined || str === null) return "";
  return String(str).replace(/"/g, '\\"').trim();
}

export function buildDaguParams(patient, language = "en") {
  const species = sanitizeParam(patient.specie || "Cat");
  const breed = sanitizeParam(patient.razza || "European Shorthair");
  const weight = sanitizeParam(patient.peso || "4.0");
  const priority = sanitizeParam(patient.priorita || "auto");
  const symptoms = sanitizeParam(patient.sintomi || "Unidentified toxic ingestion");
  const lang = sanitizeParam(language || "en");

  return `SPECIES="${species}" BREED="${breed}" WEIGHT="${weight}" PRIORITY="${priority}" SYMPTOMS="${symptoms}" LANGUAGE="${lang}"`;
}

export async function startDaguPipeline(patient, language = "en") {
  const paramsStr = buildDaguParams(patient, language);

  const res = await fetch("/api/dagu/dags/vetsentinel-emergency-flow/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ params: paramsStr })
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Dagu start failed (${res.status}): ${errorText}`);
  }

  const data = await res.json();
  return data.dagRunId;
}

export async function fetchDagRunStatus(dagRunId) {
  const res = await fetch(`/api/dagu/dags/vetsentinel-emergency-flow/dag-runs/${dagRunId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch DAG run ${dagRunId}: ${res.status}`);
  }
  const data = await res.json();
  return data.dagRun;
}

export async function fetchLatestDagRun() {
  try {
    const res = await fetch("/api/dagu/dags", { signal: AbortSignal.timeout(2000) });
    if (!res.ok) return null;
    const data = await res.json();
    const dags = data.dags || [];
    const vetDag = dags.find(d => d.dag && d.dag.name === "vetsentinel-emergency-flow");
    return vetDag ? vetDag.latestDAGRun : null;
  } catch {
    return null;
  }
}

export async function fetchAllArtifacts(runId = null) {
  const url = runId
    ? `/api/artifacts?run_id=${encodeURIComponent(runId)}`
    : "/api/artifacts";
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to load artifacts: ${res.status}`);
  }
  return await res.json();
}

export async function fetchArtifactByName(fileName, runId = null) {
  let url = `/api/artifacts?name=${encodeURIComponent(fileName)}`;
  if (runId) {
    url += `&run_id=${encodeURIComponent(runId)}`;
  }
  const res = await fetch(url);
  if (!res.ok) return null;
  if (fileName.endsWith(".json")) {
    return await res.json();
  }
  return await res.text();
}

export async function fetchRecentDagRuns() {
  try {
    const res = await fetch("/api/dagu/dags/vetsentinel-emergency-flow/dag-runs", { signal: AbortSignal.timeout(2000) });
    if (!res.ok) return [];
    const data = await res.json();
    return data.dagRuns || [];
  } catch {
    return [];
  }
}

export async function fetchNodeLog(stdoutPath) {
  if (!stdoutPath) return "";
  try {
    const res = await fetch(`/api/dag-logs?path=${encodeURIComponent(stdoutPath)}`);
    if (!res.ok) return "";
    return await res.text();
  } catch {
    return "";
  }
}

export async function stopDaguPipeline(dagRunId = null) {
  try {
    let res = null;
    if (dagRunId) {
      try {
        res = await fetch(
          `/api/dagu/dag-runs/vetsentinel-emergency-flow/${encodeURIComponent(dagRunId)}/stop`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
          }
        );
      } catch (e) {}
    }
    const resAll = await fetch(
      "/api/dagu/dags/vetsentinel-emergency-flow/stop-all",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      }
    );
    return (res && res.ok) || resAll.ok;
  } catch (err) {
    console.error("Failed to stop Dagu pipeline:", err);
    return false;
  }
}

export function buildChatDaguParams({ patient, query, history, language = "en" }) {
  const species = sanitizeParam(patient?.specie || "Cat");
  const breed = sanitizeParam(patient?.razza || "European Shorthair");
  const weight = sanitizeParam(patient?.peso || "4.0");
  const priority = sanitizeParam(patient?.priorita || "CRITICAL");
  const symptoms = sanitizeParam(
    (patient?.sintomi || "Suspected toxic ingestion").replace(/[\r\n]+/g, " ")
  );
  const lang = sanitizeParam(language || "en");
  const cleanQuery = sanitizeParam((query || "").replace(/[\r\n]+/g, " "));

  const trimmedHistory = (history || []).slice(-6).map((m) => ({
    role: m.role,
    content: (m.content || "")
      .replace(/[\r\n]+/g, " ")
      .replace(/"/g, "'")
      .slice(0, 400),
  }));
  const historyStr = sanitizeParam(JSON.stringify(trimmedHistory));

  return `SPECIES="${species}" BREED="${breed}" WEIGHT="${weight}" PRIORITY="${priority}" SYMPTOMS="${symptoms}" QUERY="${cleanQuery}" CONVERSATION_HISTORY="${historyStr}" LANGUAGE="${lang}"`;
}

export async function startChatDaguPipeline({ patient, query, history, language = "en" }) {
  const paramsStr = buildChatDaguParams({ patient, query, history, language });

  const res = await fetch("/api/dagu/dags/vetsentinel-chat-flow/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ params: paramsStr }),
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Dagu chat start failed (${res.status}): ${errorText}`);
  }

  const data = await res.json();
  return data.dagRunId;
}

export async function fetchChatDagRunStatus(dagRunId) {
  const res = await fetch(
    `/api/dagu/dags/vetsentinel-chat-flow/dag-runs/${encodeURIComponent(dagRunId)}`
  );
  if (!res.ok) {
    throw new Error(`Failed to fetch Chat DAG run ${dagRunId}: ${res.status}`);
  }
  const data = await res.json();
  return data.dagRun;
}

export async function fetchChatReplyArtifact(dagRunId = null) {
  if (dagRunId) {
    try {
      const art = await fetchArtifactByName("04_chat_reply.json", dagRunId);
      if (art && art.reply) return art;
    } catch (e) {}
  }
  try {
    const centralArt = await fetchArtifactByName("04_chat_reply.json");
    if (centralArt && centralArt.reply) return centralArt;
  } catch (e) {}
  return null;
}
