/**
 * version_gate.ts - CI helper for ChromaDB TypeScript client
 *
 * The JS/TS client communicates with the ChromaDB server over HTTP/gRPC
 * and has no Pydantic dependency. It is NOT affected by the Python 3.14
 * compatibility issue (#5996).
 *
 * This utility is provided for CI pipelines that need to conditionally
 * skip or run JS client integration tests based on the Python server version.
 */

interface ServerVersionInfo {
  pythonVersion: string;
  chromaVersion: string;
  compatible: boolean;
}

/**
 * Query the ChromaDB server's version endpoint and determine
 * if the server is running on Python 3.14+.
 *
 * @param serverUrl - Base URL of the ChromaDB server (e.g., "http://localhost:8000")
 * @returns Version info including compatibility status
 */
export async function checkServerPythonVersion(
  serverUrl: string
): Promise<ServerVersionInfo> {
  const response = await fetch(`${serverUrl}/api/v2/heartbeat`);
  if (!response.ok) {
    throw new Error(
      `Failed to reach ChromaDB server at ${serverUrl}: ${response.status}`
    );
  }

  // The heartbeat endpoint returns nanosecond timestamp.
  // To get version info, use the version endpoint.
  const versionResponse = await fetch(`${serverUrl}/api/v2/version`);
  const chromaVersion = await versionResponse.text();

  // Server Python version is not directly exposed via API.
  // For CI, this is typically passed via environment variable.
  const pythonVersion = process.env.CHROMA_SERVER_PYTHON_VERSION ?? "unknown";

  const [major, minor] = pythonVersion.split(".").map(Number);
  const compatible = !(major === 3 && minor >= 14);

  return {
    pythonVersion,
    chromaVersion: chromaVersion.replace(/"/g, ""),
    compatible,
  };
}

/**
 * CI entry point: exits with code 0 if tests should run, 1 if skipped.
 */
async function main() {
  const serverUrl = process.env.CHROMA_SERVER_URL ?? "http://localhost:8000";

  try {
    const info = await checkServerPythonVersion(serverUrl);
    console.log(`ChromaDB server version: ${info.chromaVersion}`);
    console.log(`Python version: ${info.pythonVersion}`);

    if (!info.compatible) {
      console.log(
        "WARNING: Server running on Python 3.14+. " +
          "Ensure the pydantic-settings patch is applied."
      );
    }

    console.log("JS/TS client is compatible regardless of server Python version.");
    process.exit(0);
  } catch (error) {
    console.error(`Server check failed: ${error}`);
    process.exit(1);
  }
}

// Run if executed directly (tsx/ts-node)
main();
