#!/usr/bin/env python3
"""Durable blocker ledger. Discovery != clearance. Never delete history.

Sharded layout: ledger.yaml is policy + short index (blocker_id, status).
Full records live in blockers/items/<blocker_id>.yaml with quoted descriptions.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import sai_auth as a

try:
    import yaml
except ImportError:
    yaml = None

STATUSES = (
    "DISCOVERED", "TRIAGED", "CLAIMED", "IMPLEMENTING", "IMPLEMENTED",
    "VERIFYING", "AWAITING_SAUL", "AWAITING_SAI", "PASSED_BY_SAUL",
    "PASSED_BY_SAI", "SUPERSEDED_BY_EXACT_STATE", "BLOCKED_EXTERNAL",
    "IMPLEMENTED_AWAITING_SAUL",
)
TECHNICAL_CLEARANCE = "saul"
GOVERNANCE_CLEARANCE = "ceo"
LEDGER_REL = ".ai/contracts/20260813-pr62-saul-smoke/blockers/ledger.yaml"
ITEMS_DIRNAME = "items"
PASS_STATUSES = ("PASSED_BY_SAUL", "PASSED_BY_SAI", "PASSED")
REQUIRED_HISTORY = (
    "B-TRUST-001", "B-RESUME-001", "B-ORCH-001",
    "CTO-015", "CTO-016", "CTO-017", "CTO-018", "CTO-019", "CTO-020",
    "B-CORA-TODO-001", "B-RALPH-001", "B-NO-IDLE-SAUL-001",
)


class _QuotedDumper(yaml.SafeDumper if yaml is not None else object):
    pass


if yaml is not None:
    def _quoted_str(dumper, data):
        style = '"' if isinstance(data, str) else None
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)

    _QuotedDumper.add_representer(str, _quoted_str)


def items_dir_for(ledger_path: Path) -> Path:
    return ledger_path.parent / ITEMS_DIRNAME


def item_path(ledger_path: Path, blocker_id: str) -> Path:
    return items_dir_for(ledger_path) / f"{blocker_id}.yaml"


def write_item(path: Path, row: dict) -> None:
    if yaml is None:
        raise RuntimeError("PyYAML is required")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.dump(
            row, Dumper=_QuotedDumper, sort_keys=False, allow_unicode=True, width=1000,
        ),
        encoding="utf-8",
    )


def _index_row(row: dict) -> dict:
    return {"blocker_id": row.get("blocker_id"), "status": row.get("status")}


def load_ledger(root, rel=LEDGER_REL):
    path = Path(root) / rel
    data = a.read_yaml(path) or {}
    data.setdefault("blockers", [])
    data.setdefault("policy", {})
    items = items_dir_for(path)
    full, seen = [], set()
    for row in data["blockers"]:
        bid = row.get("blocker_id")
        if not bid:
            continue
        ip = item_path(path, bid)
        if ip.is_file():
            rec = a.read_yaml(ip) or {}
            rec["blocker_id"] = bid
            if row.get("status"):
                rec["status"] = row["status"]
            full.append(rec)
        else:
            full.append(row)
        seen.add(bid)
    if items.is_dir():
        for p in sorted(items.glob("*.yaml")):
            rec = a.read_yaml(p) or {}
            bid = rec.get("blocker_id") or p.stem
            if bid in seen:
                continue
            rec["blocker_id"] = bid
            full.append(rec)
            seen.add(bid)
    data["blockers"] = full
    data["layout"] = "sharded"
    return data, path


def save_ledger(path, data):
    data = dict(data)
    data["updated_at"] = a.utcnow()
    items = items_dir_for(path)
    items.mkdir(parents=True, exist_ok=True)
    by_id, order, seen = {}, [], set()
    for row in data.get("blockers") or []:
        bid = row.get("blocker_id")
        if not bid:
            continue
        by_id[bid] = row
        write_item(item_path(path, bid), row)
        if bid not in seen:
            order.append(bid)
            seen.add(bid)
    for p in sorted(items.glob("*.yaml")):
        rec = a.read_yaml(p) or {}
        bid = rec.get("blocker_id") or p.stem
        if bid in seen:
            continue
        by_id[bid] = rec
        order.append(bid)
        seen.add(bid)
    index = {
        "ledger_id": data.get("ledger_id"),
        "contract_id": data.get("contract_id"),
        "updated_at": data["updated_at"],
        "policy": data.get("policy") or {},
        "layout": "sharded",
        "items_dir": ITEMS_DIRNAME,
        "blockers": [_index_row(by_id[b]) for b in order],
    }
    a.write_yaml(path, index)


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
    if status in PASS_STATUSES:
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
