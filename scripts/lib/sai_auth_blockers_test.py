#!/usr/bin/env python3
"""Blocker authority: anyone may append; only Saul/Sai may PASS in their plane."""
from __future__ import annotations

import tempfile
from pathlib import Path

import sai_auth as a
from sai_auth_blockers import (
    LEDGER_REL, PASS_STATUSES, REQUIRED_HISTORY, STATUSES, append_blocker,
    attempt_clear, item_path, load_ledger, save_ledger, set_status,
)

LIVE_REQUIRED = REQUIRED_HISTORY + (
    "CTO-021", "B-BLOAT-001", "CTO-024", "CTO-025", "CTO-026", "CTO-027",
    "B-META-P0-001", "B-QUALITY-001", "B-MERGE-PKG-001",
)
NON_SAUL_ACTORS = ("cursor", "contractor", "ctr-admin", "ctr-code-pr62smoke", "ceo")


def run_blocker_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        rel = "ledger.yaml"
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        a.write_yaml(root / rel, {"blockers": [], "policy": {"never_delete_history": True}})
        row = {
            "blocker_id": "B-001",
            "source": "cursor-primary",
            "source_actor": "ceo",
            "category": "technical",
            "severity": "PROVISIONAL-P0",
            "description": "stale Saul pickup: head mismatch",
            "clearance_authority": "saul",
            "status": "DISCOVERED",
        }
        action, stored = append_blocker(root, row, rel=rel)
        executed.add("cursor-may-append")
        if action != "appended":
            raise RuntimeError((action, stored))
        print("SELFTEST PASS  cursor-may-append")

        executed.add("sharded-item-written")
        data, path = load_ledger(root, rel)
        ip = item_path(path, "B-001")
        if not ip.is_file():
            raise RuntimeError("missing item file")
        item_text = ip.read_text(encoding="utf-8")
        if "stale Saul pickup" not in item_text:
            raise RuntimeError(item_text)
        if '"description"' not in item_text and "description:" not in item_text:
            raise RuntimeError(item_text)
        desc = (a.read_yaml(ip) or {}).get("description", "")
        if ":" in desc and '"' not in item_text:
            raise RuntimeError("description with colon must be quoted")
        print("SELFTEST PASS  sharded-item-written")

        executed.add("cursor-self-pass-rejected")
        r = attempt_clear(root, "B-001", "ceo", review_id="fake", head="a" * 40, rel=rel)
        if r["status"] != "REJECT" or r["reason"] != "TECHNICAL_CLEARANCE_REQUIRES_SAUL":
            raise RuntimeError(r)
        print("SELFTEST PASS  cursor-self-pass-rejected")

        executed.add("contractor-self-pass-rejected")
        r = attempt_clear(root, "B-001", "ctr-code-pr62smoke", review_id="x", head="a" * 40, rel=rel)
        if r["status"] != "REJECT":
            raise RuntimeError(r)
        print("SELFTEST PASS  contractor-self-pass-rejected")

        executed.add("saul-can-pass-technical")
        r = attempt_clear(root, "B-001", "saul", review_id="3175", head="b" * 40, rel=rel)
        if r["status"] != "PASSED_BY_SAUL":
            raise RuntimeError(r)
        print("SELFTEST PASS  saul-can-pass-technical")

        executed.add("history-not-deleted")
        data, _ = load_ledger(root, rel)
        if len(data["blockers"]) != 1 or data["blockers"][0]["status"] != "PASSED_BY_SAUL":
            raise RuntimeError(data["blockers"])
        if not item_path(Path(root) / rel, "B-001").is_file():
            raise RuntimeError("item deleted after pass")
        print("SELFTEST PASS  history-not-deleted")

        gov = {
            "blocker_id": "G-001",
            "category": "governance",
            "clearance_authority": "ceo",
            "status": "DISCOVERED",
            "description": "identity",
        }
        append_blocker(root, gov, rel=rel)
        executed.add("saul-cannot-pass-governance")
        r = attempt_clear(root, "G-001", "saul", review_id="1", head="c" * 40, rel=rel)
        if r["status"] != "REJECT":
            raise RuntimeError(r)
        r = attempt_clear(root, "G-001", "ceo", review_id="sai-1", head="c" * 40, rel=rel)
        if r["status"] != "PASSED_BY_SAI":
            raise RuntimeError(r)
        print("SELFTEST PASS  saul-cannot-pass-governance")

        executed.add("implemented-is-not-passed")
        row2 = {"blocker_id": "B-002", "category": "technical", "status": "IMPLEMENTED"}
        append_blocker(root, row2, rel=rel)
        r = set_status(root, "B-002", "IMPLEMENTED_AWAITING_SAUL", actor="cursor", rel=rel)
        if r["status"] != "IMPLEMENTED_AWAITING_SAUL":
            raise RuntimeError(r)
        data, _ = load_ledger(root, rel)
        b2 = next(b for b in data["blockers"] if b["blocker_id"] == "B-002")
        if b2["status"].startswith("PASSED"):
            raise RuntimeError("IMPLEMENTED must not be PASSED")
        print("SELFTEST PASS  implemented-is-not-passed")

        executed.add("never-delete-dropped-item")
        data, path = load_ledger(root, rel)
        data["blockers"] = [b for b in data["blockers"] if b.get("blocker_id") != "B-002"]
        save_ledger(path, data)
        data2, _ = load_ledger(root, rel)
        ids = {b.get("blocker_id") for b in data2["blockers"]}
        if "B-002" not in ids:
            raise RuntimeError("dropped blocker vanished")
        print("SELFTEST PASS  never-delete-dropped-item")

    executed.add("repo-blocker-ledger-parses")
    repo = Path(__file__).resolve().parents[2]
    live_path = repo / LEDGER_REL
    parsed = a.read_yaml(live_path)
    if not parsed or not parsed.get("blockers"):
        raise RuntimeError("live blocker ledger missing")
    if parsed.get("layout") != "sharded":
        raise RuntimeError("live ledger must be sharded index")
    nlines = len(live_path.read_text(encoding="utf-8").splitlines())
    if nlines > 300:
        raise RuntimeError(f"index bloat {nlines} > 300")
    data, path = load_ledger(repo)
    ids = {b.get("blocker_id") for b in data["blockers"]}
    missing = [i for i in LIVE_REQUIRED if i not in ids]
    if missing:
        raise RuntimeError(f"missing historical blockers: {missing}")
    for bid in LIVE_REQUIRED:
        ip = item_path(path, bid)
        if not ip.is_file():
            raise RuntimeError(f"missing item {bid}")
        rec = a.read_yaml(ip)
        if not rec:
            raise RuntimeError(f"unreadable {bid}")
        desc = rec.get("description") or ""
        raw = ip.read_text(encoding="utf-8")
        if ":" in desc:
            quoted = ('"description"' in raw) or ("description: \"" in raw) or ("description: '" in raw)
            if not quoted:
                raise RuntimeError(f"unquoted description {bid}")
    print("SELFTEST PASS  repo-blocker-ledger-parses")

    executed.add("live-cora-todo-non-saul-cannot-clear")
    for actor in NON_SAUL_ACTORS:
        r = attempt_clear(
            repo, "B-CORA-TODO-001", actor,
            review_id="fake", head="a" * 40,
        )
        if r.get("status") != "REJECT" or r.get("reason") != "TECHNICAL_CLEARANCE_REQUIRES_SAUL":
            raise RuntimeError((actor, r))
    print("SELFTEST PASS  live-cora-todo-non-saul-cannot-clear")

    executed.add("live-no-self-pass")
    for b in data["blockers"]:
        st = str(b.get("status") or "")
        if st in ("PASSED", "PASSED_BY_SAUL", "PASSED_BY_SAI") and b.get("blocker_id") in (
            "CTO-015", "CTO-016", "CTO-017", "CTO-018", "CTO-019", "CTO-020",
            "CTO-021", "CTO-024", "CTO-025", "CTO-026", "CTO-027", "B-BLOAT-001",
            "B-META-P0-001", "B-QUALITY-001", "B-MERGE-PKG-001",
        ):
            raise RuntimeError(f"contractor must not PASS {b.get('blocker_id')}")
    print("SELFTEST PASS  live-no-self-pass")

    executed.add("conditional-pass-not-pass-status")
    if "CONDITIONAL_PASS_ON_HUMAN_MERGE" not in STATUSES:
        raise RuntimeError("STATUSES must list CONDITIONAL_PASS_ON_HUMAN_MERGE")
    if "CONDITIONAL_PASS_ON_HUMAN_MERGE" in PASS_STATUSES:
        raise RuntimeError("CONDITIONAL_PASS_ON_HUMAN_MERGE must not be a PASS_STATUS")
    print("SELFTEST PASS  conditional-pass-not-pass-status")
    return executed


if __name__ == "__main__":
    run_blocker_fixtures()
    print("sai_auth_blockers_test: OK")
