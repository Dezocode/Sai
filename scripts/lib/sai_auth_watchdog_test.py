#!/usr/bin/env python3
"""Watchdog: healthy NOOP, complete queues, stale queues; two-primary cap."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile

from sai_auth_watchdog import (
    MAX_ACTIVE_PRIMARY_PROGRAMS, admit_primary, heartbeat, inspect_worker,
)


def _ts(now, seconds_ago):
    return (now - timedelta(seconds=seconds_ago)).isoformat().replace("+00:00", "Z")


def run_watchdog_fixtures():
    executed = set()
    now = datetime(2026, 8, 13, 23, 0, tzinfo=timezone.utc)

    healthy = {"agent_id": "ctr-code-pr62smoke", "state": "RUNNING",
               "last_seen": _ts(now, 60), "base_sha": "a" * 40, "task_id": "t"}
    a, r = inspect_worker(healthy, now=now)
    executed.add("watchdog-healthy-noop")
    if a != "NOOP" or r != "healthy":
        raise RuntimeError((a, r))
    print("SELFTEST PASS  watchdog-healthy-noop")

    done = {"agent_id": "ctr-admin", "state": "COMPLETE", "base_sha": "a" * 40,
            "task_id": "t"}
    a, r = inspect_worker(done, now=now)
    executed.add("watchdog-complete-event")
    if a != "SUBAGENT_COMPLETE":
        raise RuntimeError((a, r))
    print("SELFTEST PASS  watchdog-complete-event")

    stale = {"agent_id": "w", "state": "RUNNING", "last_seen": _ts(now, 4000),
             "base_sha": "a" * 40, "task_id": "t"}
    a, r = inspect_worker(stale, now=now)
    executed.add("watchdog-stale-event")
    if a != "STALE_WORKER":
        raise RuntimeError((a, r))
    print("SELFTEST PASS  watchdog-stale-event")

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        events = heartbeat(d, [healthy, done, stale], now=now)
        executed.add("watchdog-heartbeat-no-model")
        statuses = [(e.get("status") or e.get("type"), e.get("reason") or e.get("watchdog_reason")) for e in events]
        if events[0]["status"] != "NOOP":
            raise RuntimeError(events[0])
        if events[1].get("type") != "SUBAGENT_COMPLETE" and events[1].get("status") != "MATERIAL":
            raise RuntimeError(events[1])
        if events[2].get("type") != "STALE_WORKER" and events[2].get("status") != "MATERIAL":
            raise RuntimeError(events[2])
        if any(e.get("cora_wake") for e in events):
            raise RuntimeError("Cora must not wake on watchdog worker events")
        print("SELFTEST PASS  watchdog-heartbeat-no-model")

    p1 = {"logical_id": "pr62-primary", "pr": 62, "kind": "primary_implementation", "status": "active"}
    p2 = {"logical_id": "pr63-init", "pr": 63, "kind": "primary_implementation", "status": "active"}
    third = {"logical_id": "pr99-third", "pr": 99, "kind": "primary_implementation", "status": "active"}
    ri = {"logical_id": "pr64-ri", "pr": 64, "kind": "runtime_intelligence", "status": "active"}
    stacked = {"logical_id": "pr64-stack", "pr": 64, "kind": "stacked", "status": "active"}
    executed.add("two-primary-cap-parks-third")
    decision, reason = admit_primary([p1, p2], third)
    if decision != "park" or reason != "concentration_gate":
        raise RuntimeError((decision, reason, MAX_ACTIVE_PRIMARY_PROGRAMS))
    print("SELFTEST PASS  two-primary-cap-parks-third")

    executed.add("ri-stacked-does-not-consume-slot")
    d2, r2 = admit_primary([p1, p2], ri)
    d3, r3 = admit_primary([p1, p2], stacked)
    if d2 != "admit" or d3 != "admit":
        raise RuntimeError((d2, r2, d3, r3))
    print("SELFTEST PASS  ri-stacked-does-not-consume-slot")

    executed.add("dezocode-override-admits-third")
    d4, r4 = admit_primary([p1, p2], third, override={"principal": "dezocode"})
    if d4 != "admit":
        raise RuntimeError((d4, r4))
    print("SELFTEST PASS  dezocode-override-admits-third")
    return executed


if __name__ == "__main__":
    run_watchdog_fixtures()
    print("sai_auth_watchdog_test: OK")
