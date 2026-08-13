#!/usr/bin/env python3
"""Read-only liveness + two-primary concentration. No model invocation."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import sai_auth as a
from sai_auth_event import ingest
from sai_auth_runtime import cora_should_wake

# 25 minutes: inside the 20–30 minute principal window; configurable.
HEARTBEAT_SECONDS_DEFAULT = 1500
STALE_AFTER_SECONDS_DEFAULT = 1800
MAX_ACTIVE_PRIMARY_PROGRAMS = 2
PRIMARY_KIND = "primary_implementation"
EXEMPT_KINDS = (
    "stacked",
    "runtime_intelligence",
    "telemetry",
    "memory",
    "read_only_verification",
)


def _parse_ts(value):
    if not value:
        return None
    text = str(value).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def inspect_worker(worker: dict, *, now=None, stale_after=STALE_AFTER_SECONDS_DEFAULT):
    """Compare durable worker record only. Do not resume the worker."""
    now = now or datetime.now(timezone.utc)
    state = (worker.get("state") or "").upper()
    if state in ("COMPLETE", "FAILED"):
        if worker.get("completion_queued"):
            return "NOOP", "already_queued"
        return "SUBAGENT_COMPLETE", "worker_finished"
    last = _parse_ts(worker.get("last_seen") or worker.get("updated_at"))
    if state in ("RUNNING", "WAITING", "PENDING") and last:
        age = (now - last).total_seconds()
        if age <= stale_after:
            return "NOOP", "healthy"
        return "STALE_WORKER", "stale_last_seen"
    if state == "STALE":
        return "STALE_WORKER", "already_stale"
    if state == "PARKED":
        return "NOOP", "parked"
    return "NOOP", "no_liveness_signal"


def heartbeat(root, workers, *, now=None, stale_after=STALE_AFTER_SECONDS_DEFAULT,
              store_rel=".git/sai-last-material-event.json"):
    """One pass: NOOP / completion / stale. Never calls a model."""
    now = now or datetime.now(timezone.utc)
    events = []
    for worker in workers:
        action, reason = inspect_worker(worker, now=now, stale_after=stale_after)
        if action == "NOOP":
            events.append({
                "status": "NOOP",
                "reason": reason,
                "agent_id": worker.get("agent_id"),
                "cora_wake": False,
            })
            continue
        payload = {
            "event_type": action,
            "task_id": worker.get("task_id") or worker.get("work_item") or "",
            "head": worker.get("base_sha") or "",
            "source": "watchdog",
            "agent_id": worker.get("agent_id"),
            "recommended_next_transition": (
                "INTEGRATE_WORKER" if action == "SUBAGENT_COMPLETE" else "DIAGNOSE_STALE_WORKER"
            ),
        }
        kind, event = ingest(root, payload, store_rel=store_rel)
        event["watchdog_reason"] = reason
        event["cora_wake"] = cora_should_wake(action)
        event["action"] = kind
        events.append(event)
    return events


def active_primary_count(programs: list[dict]) -> int:
    n = 0
    for row in programs:
        if (row.get("status") or "").lower() != "active":
            continue
        kind = row.get("kind") or PRIMARY_KIND
        if kind in EXEMPT_KINDS:
            continue
        if kind == PRIMARY_KIND:
            n += 1
    return n


def admit_primary(programs: list[dict], candidate: dict, *,
                  max_active=MAX_ACTIVE_PRIMARY_PROGRAMS, override=None):
    """Park a third independent primary unless dezocode overrides."""
    kind = candidate.get("kind") or PRIMARY_KIND
    if kind in EXEMPT_KINDS:
        return "admit", "exempt_kind"
    cid = candidate.get("logical_id")
    existing = [p for p in programs if p.get("logical_id") == cid]
    if existing:
        return "admit", "already_registered"
    if override and override.get("principal") == "dezocode":
        return "admit", "dezocode_override"
    if active_primary_count(programs) >= max_active:
        return "park", "concentration_gate"
    return "admit", "under_cap"


def load_programs(root, rel=".ai/_config/primary-programs.yaml"):
    path = Path(root) / rel
    data = a.read_yaml(path) or {}
    return data, path


def cmd(argv=None):
    p = argparse.ArgumentParser(prog="sai-watchdog")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--heartbeat-seconds", type=int, default=HEARTBEAT_SECONDS_DEFAULT)
    p.add_argument("--stale-after-seconds", type=int, default=STALE_AFTER_SECONDS_DEFAULT)
    args = p.parse_args(argv)
    if args.self_test:
        from sai_auth_watchdog_test import run_watchdog_fixtures
        n = run_watchdog_fixtures()
        print(f"sai-watchdog self-test: {len(n)} fixtures executed")
        return 0
    root = a.toplevel()
    from sai_auth_runtime import load_workers
    from sai_auth_resume import find_coordinator_states, pick_active
    workers = load_workers(root)
    _, state = pick_active(find_coordinator_states(root))
    extra = (state or {}).get("workers") or []
    if extra and isinstance(extra[0], dict):
        workers = list(extra)
    events = heartbeat(root, workers, stale_after=args.stale_after_seconds)
    print(json.dumps({
        "heartbeat_seconds": args.heartbeat_seconds,
        "stale_after_seconds": args.stale_after_seconds,
        "model_invoked": False,
        "events": events,
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(cmd())
