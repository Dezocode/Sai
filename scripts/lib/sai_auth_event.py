#!/usr/bin/env python3
"""Compact material-event adapter. Digest-compare before any model wake."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import sai_auth as a


EVENT_TYPES = (
    "SUBAGENT_COMPLETE", "SUBAGENT_FAILED", "CORA_CONTRACT_CHANGED",
    "CONTRACTOR_COMPLETE", "NEW_SHA", "CI_COMPLETE", "CI_FAILED",
    "SAUL_REQUEST_CHANGES", "SAUL_APPROVE", "SAI_REQUEST_CHANGES",
    "SAI_APPROVE", "HUMAN_DECISION", "AUTHORITY_REQUIRED",
)


def state_digest(payload: dict) -> str:
    raw = json.dumps({
        "head": payload.get("head") or payload.get("new_head") or "",
        "contract_revision": payload.get("contract_revision"),
        "disposition": payload.get("disposition"),
        "findings_digest": payload.get("findings_digest") or "",
        "requirement_digest": payload.get("requirement_digest") or "",
        "ci": payload.get("ci"),
        "event_type": payload.get("event_type") or payload.get("type"),
    }, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def ingest(root, payload: dict, *, store_rel=".ai/runs/_coordinator/last-material-event.json"):
    """Return (action, event). Duplicate digest => NOOP, no model."""
    et = payload.get("event_type") or payload.get("type")
    if et not in EVENT_TYPES:
        return "reject", {"status": "REJECT", "reason": "unknown_event_type", "event_type": et}
    digest = state_digest(payload)
    store = Path(root) / store_rel
    prev = {}
    if store.is_file():
        try:
            prev = json.loads(store.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            prev = {}
    if prev.get("new_state_digest") == digest:
        return "noop", {
            "status": "NOOP",
            "reason": "duplicate_material_state",
            "event_type": et,
            "new_state_digest": digest,
        }
    event = {
        "status": "MATERIAL",
        "event_id": digest,
        "task_id": payload.get("task_id") or "",
        "type": et,
        "source": payload.get("source") or "github",
        "old_state_digest": prev.get("new_state_digest"),
        "new_state_digest": digest,
        "head": payload.get("head") or payload.get("new_head"),
        "contract_revision": payload.get("contract_revision"),
        "artifact_pointers": payload.get("artifact_pointers") or [],
        "recommended_next_transition": payload.get("recommended_next_transition"),
        "timestamp": a.utcnow(),
    }
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps(event, indent=2) + "\n", encoding="utf-8")
    return "material", event


def cmd(argv=None):
    p = argparse.ArgumentParser(prog="sai-event-adapter")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--from-json", default=None)
    args = p.parse_args(argv)
    if args.self_test:
        from sai_auth_event_test import run_event_fixtures
        n = run_event_fixtures()
        print(f"sai-event-adapter self-test: {n} fixtures executed")
        return 0
    payload = json.loads(Path(args.from_json).read_text(encoding="utf-8")) if args.from_json else json.load(sys.stdin)
    action, event = ingest(a.toplevel(), payload)
    print(json.dumps({"action": action, **event}, indent=2))
    return 0 if action in ("noop", "material") else 1


if __name__ == "__main__":
    raise SystemExit(cmd())
