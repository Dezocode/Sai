#!/usr/bin/env python3
"""Blocker authority: anyone may append; only Saul/Sai may PASS in their plane."""
from __future__ import annotations

import tempfile
from pathlib import Path

import sai_auth as a
from sai_auth_blockers import append_blocker, attempt_clear, set_status


def run_blocker_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        rel = "ledger.yaml"
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        a.write_yaml(root / rel, {"blockers": []})
        row = {
            "blocker_id": "B-001",
            "source": "cursor-primary",
            "source_actor": "ceo",
            "category": "technical",
            "severity": "PROVISIONAL-P0",
            "description": "stale Saul pickup",
            "clearance_authority": "saul",
            "status": "DISCOVERED",
        }
        action, stored = append_blocker(root, row, rel=rel)
        executed.add("cursor-may-append")
        if action != "appended":
            raise RuntimeError((action, stored))
        print("SELFTEST PASS  cursor-may-append")

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
        data = a.read_yaml(root / rel)
        if len(data["blockers"]) != 1 or data["blockers"][0]["status"] != "PASSED_BY_SAUL":
            raise RuntimeError(data)
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
        data = a.read_yaml(root / rel)
        b2 = next(b for b in data["blockers"] if b["blocker_id"] == "B-002")
        if b2["status"].startswith("PASSED"):
            raise RuntimeError("IMPLEMENTED must not be PASSED")
        print("SELFTEST PASS  implemented-is-not-passed")
    return executed


if __name__ == "__main__":
    run_blocker_fixtures()
    print("sai_auth_blockers_test: OK")
