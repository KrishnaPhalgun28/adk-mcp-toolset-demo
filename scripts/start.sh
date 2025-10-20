#!/usr/bin/env bash
set -euo pipefail

# In container: ensure CA bundle for TLS sanity
export SSL_CERT_FILE="$(python -c 'import certifi; print(certifi.where())')"
export REQUESTS_CA_BUNDLE="$SSL_CERT_FILE"
echo "Using CA bundle: $SSL_CERT_FILE"

# Require API key
if [[ -z "${GOOGLE_API_KEY:-}" ]]; then
  echo "ERROR: GOOGLE_API_KEY is not set." >&2
  exit 1
fi

# MCP server paths must exist in the container FS
if [[ ! -f "${TWITTER_MCP_SERVER_PATH:-}" ]]; then
  echo "ERROR: Missing TWITTER_MCP_SERVER_PATH: ${TWITTER_MCP_SERVER_PATH:-unset}" >&2
  exit 1
fi
if [[ ! -f "${GITHUB_MCP_SERVER_PATH:-}" ]]; then
  echo "ERROR: Missing GITHUB_MCP_SERVER_PATH: ${GITHUB_MCP_SERVER_PATH:-unset}" >&2
  exit 1
fi

PORT="${ADK_PORT:-8888}"
HOST="${ADK_HOST:-0.0.0.0}"

AGENTS_DIR="/app"
echo "Launching ADK Web on ${HOST}:${PORT} using agents dir: ${AGENTS_DIR} with model: ${GEMINI_MODEL:-gemini-2.5-flash}"
exec adk web --host "$HOST" --port "$PORT" "${AGENTS_DIR}"