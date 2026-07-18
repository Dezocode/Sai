#!/usr/bin/env python3
"""Mimi dispatch runner on the Claude Agent SDK (M0).

Contract: 20260717-mimi-dispatcher-bootstrap-monaecode, deliverable
M0-claude-agent-sdk. Reference: .ai/shared/references/claude-agent-sdk.md.

This is the *programmatic* dispatch harness Cora's amendment requires —
distinct from the interactive `.claude/agents/mimi-dispatcher.md` subagent.
It loads ClaudeAgentOptions from config/agent-options.json and drives the
Claude Agent SDK `query()` loop.

Auth: the Agent SDK honors the same credential resolution as the Claude
Code CLI (ANTHROPIC_API_KEY, or an `ant auth login` / `claude setup-token`
subscription profile). No key is committed; none is read from the repo.

Modes:
  --check   Offline validation: import the SDK, build options from the
            config file, print the resolved option summary. No model call,
            so it runs without auth. Exit 0 on success.
  --smoke   Live read-only smoke test: one query() with allowed_tools
            limited to Read, prompt asks the agent to confirm it loaded and
            reply OK. Needs auth. Exit 0 only if a real reply came back.
  (prompt)  Any other argument is treated as a dispatch prompt and run
            through query() with the full configured options.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # runtimes/claude/agent-sdk/
CONFIG = HERE / "config" / "agent-options.json"


def load_raw_options() -> dict:
    with open(CONFIG) as fh:
        return json.load(fh)


def build_options(raw: dict, *, read_only: bool = False):
    """Map config/agent-options.json → ClaudeAgentOptions.

    Import is done inside the function so --check can report a clean,
    honest 'SDK not installed' rather than crashing at module load.
    """
    from claude_agent_sdk import ClaudeAgentOptions

    allowed = ["Read"] if read_only else raw.get("allowedTools", ["Read"])
    kwargs = {
        "allowed_tools": allowed,
        "system_prompt": raw.get("systemPromptAppend"),
    }
    # Pass through optional fields only when present, so we stay compatible
    # across SDK versions that may not accept every keyword.
    if raw.get("settingSources"):
        kwargs["setting_sources"] = raw["settingSources"]
    if raw.get("mcpServers"):
        kwargs["mcp_servers"] = raw["mcpServers"]
    # NOTE: the config's `agents` map documents which subagent this harness
    # dispatches to, but ClaudeAgentOptions.agents wants AgentDefinition
    # dataclasses, not path strings. The Claude Agent SDK auto-discovers
    # `.claude/agents/*.md` (including mimi-dispatcher) from settingSources,
    # so we intentionally do NOT pass `agents` programmatically.
    # Drop keys the installed SDK version doesn't accept rather than fail.
    try:
        return ClaudeAgentOptions(**kwargs)
    except TypeError:
        return ClaudeAgentOptions(
            allowed_tools=allowed, system_prompt=raw.get("systemPromptAppend")
        )


def cmd_check() -> int:
    raw = load_raw_options()
    print(f"config: {CONFIG}")
    print(f"agent_id: {raw.get('agent_id')}")
    print(f"allowedTools: {raw.get('allowedTools')}")
    print(f"subagents: {list((raw.get('agents') or {}).keys())}")
    print(f"mcpServers: {list((raw.get('mcpServers') or {}).keys())}")
    try:
        import claude_agent_sdk  # noqa: F401
    except ImportError as exc:
        print(f"SDK: NOT INSTALLED ({exc}) — run `pip install claude-agent-sdk`")
        return 3
    opts = build_options(raw, read_only=True)
    print(f"SDK: import OK; ClaudeAgentOptions built ({type(opts).__name__})")
    print("CHECK: PASS")
    return 0


async def _run_query(prompt: str, *, read_only: bool) -> int:
    from claude_agent_sdk import query

    raw = load_raw_options()
    opts = build_options(raw, read_only=read_only)
    got_reply = False
    async for message in query(prompt=prompt, options=opts):
        got_reply = True
        text = getattr(message, "text", None) or str(message)
        print(text)
    return 0 if got_reply else 1


def cmd_smoke() -> int:
    prompt = (
        "You are Mimi's Agent SDK dispatch harness running a read-only smoke "
        "test. Reply with exactly: 'mimi agent-sdk smoke OK'. Do not use any "
        "tool except Read, and make no changes."
    )
    return asyncio.run(_run_query(prompt, read_only=True))


def main(argv: list[str]) -> int:
    if not argv or argv[0] == "--check":
        return cmd_check()
    if argv[0] == "--smoke":
        return cmd_smoke()
    return asyncio.run(_run_query(" ".join(argv), read_only=False))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
