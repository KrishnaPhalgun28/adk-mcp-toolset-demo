# ADK MCP Toolset: Integrating Twitter and GitHub

An ADK-based agent that unifies multiple MCPToolset backends including Twitter from https://github.com/gkydev/twitter-mcp-server and GitHub from https://github.com/github/github-mcp-server under a single conversational agent.

It works by using the MCPToolset framework to launch each stdio MCP server and expose their tools to one unified agent. The agent can plan, reason, and execute tasks seamlessly across both Twitter and GitHub environments.

## How to run?

1. Copy and configure the environment file  
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and fill the required variables:

   - **GOOGLE_API_KEY**: your Google API key for ADK.  
   - **TWITTER_CT0** and **TWITTER_AUTH_TOKEN**:  
     While logged into X/Twitter, extract these cookies using a browser extension such as **Cookie-Editor**,  
     or open **Chrome DevTools → Application → Storage → Cookies → https://x.com**.  
   - **GITHUB_PERSONAL_ACCESS_TOKEN**:  
     Create one here → https://github.com/settings/tokens  
     Use the **public_repo** scope for public repos or **repo** for both private and public repos.

2. Build and start  
   ```bash
   docker compose up --build
   ```

   To rebuild cleanly:  
   ```bash
   docker compose down --remove-orphans || true; docker compose build --no-cache --pull && docker compose up --force-recreate
   ```

3. Open the UI  
   http://localhost:8888/dev-ui/#/app?relative_path=./&app=agent

## ADK Web UI Screenshot

<img width="2560" height="1318" alt="screencapture-localhost-8888-dev-ui-2025-10-20-23_30_10" src="https://github.com/user-attachments/assets/36e2455e-3eda-4055-ae02-742f4b44c7ec" />
