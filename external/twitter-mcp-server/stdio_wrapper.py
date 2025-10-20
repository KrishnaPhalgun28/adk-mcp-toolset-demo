#!/usr/bin/env python3

"""A thin shim that runs the Twitter MCP server and forwards ONLY valid JSON-RPC lines to stdout (everything else to stderr),
so accidental prints/logs cannot corrupt the stdio protocol and crash the client."""

import asyncio, json, os, sys

SERVER_CMD = [sys.executable, "-u", os.path.join(os.path.dirname(__file__), "server.py")]

def _looks_like_jsonrpc(line: bytes) -> bool:
    try:
        obj = json.loads(line.decode("utf-8").strip())
        return isinstance(obj, dict) and obj.get("jsonrpc") == "2.0"
    except Exception:
        return False

async def main():
    proc = await asyncio.create_subprocess_exec(
        *SERVER_CMD,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    async def pump_stdin():
        while True:
            chunk = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.buffer.readline)
            if not chunk:
                try:
                    proc.stdin.close()
                except Exception:
                    pass
                return
            proc.stdin.write(chunk)
            await proc.stdin.drain()

    async def pump_stdout():
        while True:
            line = await proc.stdout.readline()
            if not line:
                return
            if _looks_like_jsonrpc(line):
                sys.stdout.buffer.write(line)
                sys.stdout.buffer.flush()
            else:
                sys.stderr.buffer.write(line)
                sys.stderr.buffer.flush()

    async def pump_stderr():
        while True:
            line = await proc.stderr.readline()
            if not line:
                return
            sys.stderr.buffer.write(line)
            sys.stderr.buffer.flush()

    await asyncio.gather(pump_stdin(), pump_stdout(), pump_stderr())
    await proc.wait()

if __name__ == "__main__":
    asyncio.run(main())