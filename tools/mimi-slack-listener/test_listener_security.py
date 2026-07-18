#!/usr/bin/env python3
"""Adversarial security tests for the @mimi Slack listener (Saul P1).

Runs offline — no Slack, no Claude CLI. Stubs the env + slack_bolt so the
module imports, then asserts the fail-closed and explicit-agent-selection
properties. Exit 0 = all pass.

  python tools/mimi-slack-listener/test_listener_security.py
"""
import importlib
import os
import sys
import types


def _stub_slack_bolt():
    mod = types.ModuleType("slack_bolt")
    adapter = types.ModuleType("slack_bolt.adapter")
    sm = types.ModuleType("slack_bolt.adapter.socket_mode")

    class _App:
        def __init__(self, *a, **k): pass
        def event(self, *a, **k):
            def deco(fn): return fn
            return deco

    class _Handler:
        def __init__(self, *a, **k): pass
        def start(self): raise AssertionError("start() must not run in tests")

    mod.App = _App
    sm.SocketModeHandler = _Handler
    sys.modules["slack_bolt"] = mod
    sys.modules["slack_bolt.adapter"] = adapter
    sys.modules["slack_bolt.adapter.socket_mode"] = sm


def load(env):
    for k in ("MIMI_ALLOWED_CHANNELS", "SLACK_BOT_TOKEN", "SLACK_APP_TOKEN",
              "MIMI_DISPATCH_AGENT"):
        os.environ.pop(k, None)
    os.environ.update(env)
    _stub_slack_bolt()
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, here)
    sys.modules.pop("listener", None)
    return importlib.import_module("listener")


def main() -> int:
    fails = []

    # 1. Empty allowlist → module loads but ALLOWED_CHANNELS is empty (guarded
    #    at __main__, and every mention is ignored).
    m = load({"SLACK_BOT_TOKEN": "x", "SLACK_APP_TOKEN": "y"})
    if m.ALLOWED_CHANNELS:
        fails.append("empty MIMI_ALLOWED_CHANNELS should yield empty set")

    # 2. A mention in a non-allowlisted channel is dropped (fail-closed): the
    #    handler returns before doing any work when channel not in allowlist.
    m = load({"SLACK_BOT_TOKEN": "x", "SLACK_APP_TOKEN": "y",
              "MIMI_ALLOWED_CHANNELS": "C0BH15HDN2Z"})
    if "C0BH15HDN2Z" not in m.ALLOWED_CHANNELS:
        fails.append("configured channel missing from allowlist")
    if "C_EVIL" in m.ALLOWED_CHANNELS:
        fails.append("un-configured channel leaked into allowlist")

    # 3. Explicit agent selection is wired to mimi-dispatcher by default and
    #    the spawn passes --agent (grep the source, since we don't run claude).
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "listener.py")).read()
    if m.DISPATCH_AGENT != "mimi-dispatcher":
        fails.append(f"DISPATCH_AGENT default is {m.DISPATCH_AGENT!r}, not mimi-dispatcher")
    if '"--agent", DISPATCH_AGENT' not in src:
        fails.append("spawn does not pass --agent DISPATCH_AGENT explicitly")
    if 'if not ALLOWED_CHANNELS:' not in src or "refusing to start" not in src:
        fails.append("__main__ does not fail-closed on empty allowlist")
    if 'if channel not in ALLOWED_CHANNELS:' not in src:
        fails.append("handler does not enforce allowlist unconditionally")

    if fails:
        for f in fails:
            print("FAIL:", f)
        print(f"SECURITY TESTS: {len(fails)} FAILURE(S)")
        return 1
    print("SECURITY TESTS: ALL PASS (fail-closed allowlist + explicit mimi-dispatcher selection)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
