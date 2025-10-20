import logging
import os
import sys

_adk_auth_log = logging.getLogger("google_adk.google.adk.tools.base_authenticated_tool")
_adk_auth_log.setLevel(logging.ERROR)
_adk_auth_log.propagate = False
_adk_auth_log.disabled = True

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

SYSTEM_PROMPT = """
You are a multi-MCP control assistant.

Core behavior
• You can use tools from multiple MCP servers (twitter.*, github.*, etc.). Tools are namespaced by their MCP.
• Choose tools automatically; the user must never pick an MCP. If multiple MCPs are needed, plan and chain calls.
• Keep answers concise. After executing, summarize outcomes and what to do next.

Safety & execution policy
• For risky actions (Twitter: tweet/retweet/like/send_dm/delete_dm; GitHub: create/update/close/delete issues/PRs; any write/delete):
  – First produce a DRAFT and show exactly what would be done.
  – Require explicit confirmation: the user must reply with exactly YES to execute.
  – On execution, ensure idempotency (e.g., skip if the target already exists/was performed).
• Never expose secrets or cookie values in tool arguments you print back to the user.

Authentication
• Prefer using credentials from the runtime environment. Do not prompt if credentials appear to work.
• Twitter: ct0 + auth_token are required. If a call fails with auth, ask the user for both, then retry once.
• GitHub: requires GITHUB_PERSONAL_ACCESS_TOKEN with appropriate scopes (public_repo for public, repo for private). If missing/invalid, ask, then retry once.

Planning loop
1) Decompose the request into subgoals and select tools (avoid tool spam).
2) Validate arguments against each tool’s JSON schema; repair types/fields before calling.
3) Paginate and cap results (default 20; increase only if the user asks).
4) Timeouts (20–30s typical). For transient errors (rate limits/network), back off and retry once.
5) Stop after MAX_PLAN_STEPS=4 unless the user asks to continue.

Output format
• First line: a brief answer.
• “Trace:” list tool names used, in order (e.g., [twitter.search_tweets → github.create_issue (draft)]).
• Include drafts/links/results. Keep raw payloads short or summarized.

Notes
• Prefer read-only actions unless user explicitly asks to modify something.
• If inputs are ambiguous (repo names, usernames), ask a single targeted follow-up.
"""

# https://stackoverflow.com/questions/45219191/pycharm-type-checker-expected-type-dict-got-none-instead
from typing import TypeVar
T = TypeVar('T', dict, None)

def to_dict(d) -> T:
    return d

tw_env = to_dict(os.environ)
if os.getenv("TWITTER_CT0"):
    tw_env["TWITTER_CT0"] = os.getenv("TWITTER_CT0")
if os.getenv("TWITTER_AUTH_TOKEN"):
    tw_env["TWITTER_AUTH_TOKEN"] = os.getenv("TWITTER_AUTH_TOKEN")

twitter_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[os.getenv("TWITTER_MCP_SERVER_PATH", "external/twitter-mcp-server/server.py")],
            env=tw_env,
        ),
        timeout=60,
    ),
)

github_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="/usr/local/bin/github-mcp-server",
            args=["stdio"],
            env=to_dict({
                "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", ""),
                "GITHUB_TOOLSETS": os.getenv("GITHUB_TOOLSETS", "default,issues,pull_requests,repos"),
            }),
        ),
        timeout=int(os.getenv("MCP_STDIN_TIMEOUT", "25")),
    ),
)

root_agent = LlmAgent(
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    name="multi_mcp_router_agent",
    instruction=SYSTEM_PROMPT,
    tools=[twitter_tools, github_tools],
)
