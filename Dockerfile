FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates bash && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates bash tar && \
    rm -rf /var/lib/apt/lists/*

ENV GH_MCP_VERSION=v0.17.1
RUN set -eux; \
    PKG="github-mcp-server_Linux_x86_64.tar.gz"; \
    curl -fsSL -o "/tmp/${PKG}" "https://github.com/github/github-mcp-server/releases/download/${GH_MCP_VERSION}/${PKG}"; \
    tar -xzf "/tmp/${PKG}" -C /usr/local/bin; rm -f "/tmp/${PKG}"; chmod +x /usr/local/bin/github-mcp-server

COPY agent/ agent/
COPY scripts/ scripts/
COPY .env ./
COPY external/ external/

ENV PYTHONUNBUFFERED=1 PATH="/root/.local/bin:${PATH}"

EXPOSE 8888
ENTRYPOINT ["bash", "scripts/start.sh"]
