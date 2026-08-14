#!/usr/bin/env python3
"""Durable blocker ledger. Discovery != clearance. Never delete history."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import sai_auth as a

STATUSES = (
    "DISCOVERED", "TRIAGED", "CLAIMED", "IMPLEMENTING", "IMPLEMENTED",
    "VERIFYING", "AWAITING_SAUL", "AWAITING_SAI", "PASSED_BY_SAUL",
    "PASSED_BY_SAI", "SUPERSEDED_BY_EXACT_STATE", "BLOCKED_EXTERNAL",
    "IMPLEMENTED_AWAITING_SAUL",
)
TECHNICAL_CLEARANCE = "saul"
GOVERNANCE_CLEARANCE = "ceo"
LEDGER_REL = ".ai/contracts/20260813-pr62-saul-smoke/blockers/ledger.yaml"


def load_ledger(root, rel=LEDGER_REL):
    path = Path(root) / rel
    data = a.read_yaml(path) or {}
    data.setdefault("blockers", [])
    return data, path


def save_ledger(path, data):
    data["updated_at"] = a.utcnow()
    a.write_yaml(path, data)


def append_blocker(root, blocker: dict, *, rel=LEDGER_REL):
    data, path = load_ledger(root, rel)
    bid = blocker.get("blocker_id")
    if not bid:
        raise ValueError("blocker_id required")
    for row in data["blockers"]:
        if row.get("blocker_id") == bid:
            return "exists", row
    blocker.setdefault("status", "DISCOVERED")
    blocker.setdefault("created_at", a.utcnow())
    blocker.setdefault("implementation_state", "open")
    blocker.setdefault("verification_state", "unverified")
    blocker.setdefault("clearance_review_id", None)
    blocker.setdefault("clearance_head", None)
    data["blockers"].append(blocker)
    save_ledger(path, data)
    return "appended", blocker


def attempt_clear(root, blocker_id, actor, *, review_id=None, head=None,
                  rel=LEDGER_REL):
    """Mechanical reject: discoverer/implementer cannot self-certify PASS."""
    data, path = load_ledger(root, rel)
    row = next((b for b in data["blockers"] if b.get("blocker_id") == blocker_id), None)
    if not row:
        return {"status": "REJECT", "reason": "UNKNOWN_BLOCKER"}
    cat = row.get("category") or "technical"
    auth = row.get("clearance_authority") or (
        GOVERNANCE_CLEARANCE if cat == "governance" else TECHNICAL_CLEARANCE
    )
    if cat != "governance" and actor != TECHNICAL_CLEARANCE:
        return {
            "status": "REJECT",
            "reason": "TECHNICAL_CLEARANCE_REQUIRES_SAUL",
            "actor": actor,
            "blocker_id": blocker_id,
        }
    if cat == "governance" and actor != GOVERNANCE_CLEARANCE:
        return {
            "status": "REJECT",
            "reason": "GOVERNANCE_CLEARANCE_REQUIRES_SAI",
            "actor": actor,
            "blocker_id": blocker_id,
        }
    if not review_id or not head:
        return {"status": "REJECT", "reason": "CLEARANCE_REQUIRES_REVIEW_AND_HEAD"}
    row["status"] = "PASSED_BY_SAUL" if actor == TECHNICAL_CLEARANCE else "PASSED_BY_SAI"
    row["clearance_review_id"] = review_id
    row["clearance_head"] = head
    row["clearance_at"] = a.utcnow()
    save_ledger(path, data)
    return {"status": row["status"], "blocker_id": blocker_id, "clearance_head": head}


def set_status(root, blocker_id, status, *, actor=None, rel=LEDGER_REL):
    if status in ("PASSED_BY_SAUL", "PASSED_BY_SAI", "PASSED"):
        return attempt_clear(root, blocker_id, actor or "unknown", rel=rel)
    if status not in STATUSES:
        return {"status": "REJECT", "reason": "UNKNOWN_STATUS"}
    data, path = load_ledger(root, rel)
    row = next((b for b in data["blockers"] if b.get("blocker_id") == blocker_id), None)
    if not row:
        return {"status": "REJECT", "reason": "UNKNOWN_BLOCKER"}
    row["status"] = status
    row["updated_at"] = a.utcnow()
    save_ledger(path, data)
    return {"status": status, "blocker_id": blocker_id}


def cmd(argv=None):
    p = argparse.ArgumentParser(prog="sai-blockers")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--clear", default=None)
    p.add_argument("--actor", default="cursor")
    p.add_argument("--review-id", default=None)
    p.add_argument("--head", default=None)
    args = p.parse_args(argv)
    if args.self_test:
        from sai_auth_blockers_test import run_blocker_fixtures
        n = run_blocker_fixtures()
        print(f"sai-blockers self-test: {len(n)} fixtures executed")
        return 0
    if args.clear:
        print(json.dumps(attempt_clear(
            a.toplevel(), args.clear, args.actor,
            review_id=args.review_id, head=args.head,
        ), indent=2))
        return 0
    data, _ = load_ledger(a.toplevel())
    open_rows = [b for b in data["blockers"] if not str(b.get("status") or "").startswith("PASSED")]
    print(json.dumps({"open": len(open_rows), "total": len(data["blockers"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(cmd())
