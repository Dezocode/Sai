#!/usr/bin/env python3
"""Named SAI worker identity. Task title is not organizational identity."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import sai_auth as a

IDENTITY_FIELDS = (
    "agent_id", "name", "role",
    "parent_logical_runtime", "parent_physical_runtime",
    "contract_id", "contract_revision",
    "authorization_id", "authorization_kind",
    "work_item", "base_sha", "model", "state",
)
WORKER_STATES = (
    "PENDING", "RUNNING", "WAITING", "COMPLETE", "FAILED",
    "STALE", "PARKED", "BLOCKED", "NOOP",
)
CORA_WAKE_EVENTS = (
    "CORA_CONTRACT_CHANGED", "AUTHORITY_REQUIRED",
)
# Cora does not wake on healthy worker progress or ordinary CI/Saul noise.


def validate_identity(row: dict) -> list[str]:
    missing = [k for k in IDENTITY_FIELDS if not row.get(k)]
    if row.get("state") and row["state"] not in WORKER_STATES:
        missing.append("state_invalid")
    if row.get("task_title") and row.get("task_title") == row.get("agent_id"):
        missing.append("task_title_equals_agent_id")
    return missing


def display_identity(row: dict) -> str:
    """Human line: organizational identity first, task title last."""
    title = row.get("task_title") or row.get("work_item") or ""
    return (
        f"{row.get('name')} ({row.get('agent_id')}) "
        f"role={row.get('role')} "
        f"parent={row.get('parent_logical_runtime')}/"
        f"{row.get('parent_physical_runtime')} "
        f"contract={row.get('contract_id')}@{row.get('contract_revision')} "
        f"{row.get('authorization_kind')}={row.get('authorization_id')} "
        f"work_item={row.get('work_item')} "
        f"base={str(row.get('base_sha') or '')[:12]} "
        f"model={row.get('model')} "
        f"state={row.get('state')} "
        f"task_title={title!r}"
    )


def cora_should_wake(event_type: str) -> bool:
    """Silent supervision: no model for ordinary healthy progress."""
    return event_type in CORA_WAKE_EVENTS


def named_cora(*, parent_logical, parent_physical, contract_id, revision,
               work_item, base_sha, model, grant_id="grant-pr62-queue-cora"):
    return {
        "agent_id": "ctr-admin",
        "name": "Cora",
        "role": "Contract Administration",
        "parent_logical_runtime": parent_logical,
        "parent_physical_runtime": parent_physical,
        "contract_id": contract_id,
        "contract_revision": revision,
        "authorization_id": grant_id,
        "authorization_kind": "grant",
        "work_item": work_item,
        "base_sha": base_sha,
        "model": model,
        "state": "RUNNING",
        "task_title": work_item,
        "implements": False,
    }


def persist_workers(root, workers, rel=".ai/_config/runtime-workers.json"):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated_at": a.utcnow(),
        "workers": workers,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def load_workers(root, rel=".ai/_config/runtime-workers.json"):
    path = Path(root) / rel
    if not path.is_file():
        return []
    try:
        return (json.loads(path.read_text(encoding="utf-8")) or {}).get("workers") or []
    except (json.JSONDecodeError, OSError):
        return []


def cmd(argv=None):
    p = argparse.ArgumentParser(prog="sai-runtime-registry")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--list", action="store_true")
    args = p.parse_args(argv)
    if args.self_test:
        from sai_auth_runtime_test import run_runtime_fixtures
        n = run_runtime_fixtures()
        print(f"sai-runtime-registry self-test: {len(n)} fixtures executed")
        return 0
    root = a.toplevel()
    rows = load_workers(root)
    if args.list:
        for row in rows:
            print(display_identity(row))
        print(json.dumps({"count": len(rows)}, indent=2))
        return 0
    print(json.dumps({"workers": rows}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(cmd())
