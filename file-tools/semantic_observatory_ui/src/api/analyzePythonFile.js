const DEFAULT_API_URL = "http://127.0.0.1:8765/api/analyze";

export async function analyzePythonFile(file) {
  if (!file) {
    throw new Error("No file selected.");
  }
  if (!file.name.endsWith(".py")) {
    throw new Error("Only .py files are supported.");
  }

  const source = await file.text();
  const response = await fetch(import.meta.env.VITE_OBSERVATORY_API_URL ?? DEFAULT_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      filename: file.name,
      source,
      includeStatements: false,
      includeBlocks: false,
    }),
  });

  const payload = await response.json();
  if (!response.ok || payload.success !== true) {
    throw new Error(payload.message || "Semantic analysis failed.");
  }

  return payload.result;
}
