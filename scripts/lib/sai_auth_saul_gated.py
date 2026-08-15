#!/usr/bin/env python3
"""Ordinary CI consumer of Saul v2 evidence. Cannot mint PASS.

Validates public Ed25519 v2 if present. Fail closed on forged, unsigned
(for this head), wrong-head, synthetic, or substitute evidence. Absent proof
reports SAUL_GATES_NONSUCCESS and exits 0 unless the tree claims READY while
READY_FOR_HUMAN_REVIEW is false, a required blocker is missing from the
canonical ledger/Check projection, or substitute evidence was minted.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sai_auth as a  # noqa: E402
from sai_auth_saul_attestation_v2 import verify_attestation_v2  # noqa: E402
from sai_auth_saul_check import (  # noqa: E402
    BLOCKER_CHECK_PREFIX, REJECT_ACTORS, blocker_check_name, canonical_blockers,
)
from sai_auth_resume import enforced_rejects, reconstruct  # noqa: E402

PRIV = ("BEGIN PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY", "BEGIN ED25519 PRIVATE KEY")
P0 = (
    "B-SAUL-COMPTROLLER-READINESS-001",
    "B-FRONTIER-QUALITY-ARCH-001",
    "B-QUALITY-ANTI-BALLOON-001",
    "B-RALPH-BLOCKER-CI-CONVERGENCE-001",
)


def _reviews(root) -> list:
    out = []
    contracts = Path(root) / ".ai" / "contracts"
    if not contracts.is_dir():
        return out
    for p in contracts.glob("*/reviews/saul-*.yaml"):
        data = a.read_yaml(p) or {}
        if isinstance(data, dict):
            data["_path"] = str(p)
            out.append(data)
    return out


def _head_of(row: dict):
    return row.get("implementation_head") or row.get("head")


def evidence_for_head(root, head) -> list:
    return [r for r in _reviews(root) if _head_of(r) == head]


def detect_substitute(root) -> list:
    hits = []
    for row in _reviews(root):
        actor = str(row.get("runtime") or row.get("source") or "").lower()
        att = row.get("attestation") if isinstance(row.get("attestation"), dict) else {}
        src = str((att or {}).get("source") or "").lower()
        disp = str(row.get("disposition") or "").upper()
        blob = json.dumps(row, default=str)
        if any(m in blob for m in PRIV):
            hits.append("private_key_in_review")
        if disp == "APPROVE" and (actor in REJECT_ACTORS or src in REJECT_ACTORS):
            hits.append(f"substitute_actor:{actor or src}")
    exclude = (".ai/runs/", "scripts/lib/")
    try:
        files = a.git(root, "ls-files").stdout.splitlines()
    except Exception:
        files = []
    for rel in files:
        if any(rel.startswith(p) for p in exclude):
            continue
        if not rel.endswith((".pem", ".key", ".yaml", ".yml", ".json")):
            continue
        try:
            text = (Path(root) / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if any(m in text for m in PRIV):
            hits.append(f"private_key_file:{rel}")
    return hits


def missing_ledger_projection(root) -> list:
    from sai_auth_blockers import load_ledger
    try:
        data, _ = load_ledger(root)
    except Exception:
        return list(P0)
    ids = {r.get("blocker_id") for r in data.get("blockers") or []}
    return [b for b in P0 if b not in ids]


def gates_missing(rows) -> list:
    missing = []
    for row in rows or []:
        bid = row.get("blocker_id")
        cat = str(row.get("category") or "technical")
        if cat == "governance" or not bid:
            continue
        name = row.get("check_name") or blocker_check_name(bid)
        if not str(name).startswith(BLOCKER_CHECK_PREFIX) or not str(name).endswith(str(bid)):
            missing.append(bid)
    return missing


def missing_check_gates(root) -> list:
    return gates_missing(canonical_blockers(root))


def consume(root, *, pub_pem=None, head=None) -> dict:
    head = head or a.head_sha(root) or ""
    compact = reconstruct(root)
    ready = bool(compact.get("exit_predicate_satisfied"))
    live = str(compact.get("liveness") or "")
    substitutes = detect_substitute(root)
    ledger_miss = missing_ledger_projection(root)
    gate_miss = missing_check_gates(root)
    rejects = list(compact.get("enforced_rejects") or [])
    if not rejects:
        rejects = enforced_rejects(root, compact)
    evidence = evidence_for_head(root, head)
    gates = {"verified": False, "reason": "proof_absent", "checks_nonsuccess": True}
    hard = []
    if substitutes:
        hard.append("substitute_evidence")
        gates = {"verified": False, "reason": "substitute_evidence", "checks_nonsuccess": True}
    if ledger_miss:
        hard.append("required_blocker_missing_from_ledger")
    if gate_miss:
        hard.append("required_blocker_missing_check_gate")
    if rejects:
        hard.extend(rejects)
    if evidence and not substitutes:
        review = evidence[0]
        ok, reason = verify_attestation_v2(
            review, exact_head=head, pub_pem=pub_pem, root=root,
        )
        gates = {"verified": bool(ok), "reason": reason, "checks_nonsuccess": not ok}
        if not ok:
            hard.append(f"evidence_{reason}")
    report = {
        "head": head,
        "liveness": live,
        "exit_predicate_satisfied": ready,
        "saul_gates": gates,
        "hard_fail": hard,
        "can_mint_pass": False,
        "ordinary_ci_is_not_saul_pass": True,
    }
    if not evidence and not hard:
        report["saul_gates"]["reason"] = "proof_absent"
        report["exit"] = 0
        report["note"] = "SAUL_GATES_NONSUCCESS proof_absent"
    elif hard:
        report["exit"] = 1
    else:
        report["exit"] = 0
    return report


def cmd(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        from sai_auth_saul_gated_test import run_gated_fixtures
        n = run_gated_fixtures()
        print(f"verify-saul-gated-ci self-test: {len(n)} fixtures executed")
        return 0
    p = argparse.ArgumentParser(prog="verify-saul-gated-ci")
    p.add_argument("--pub", default=None)
    args = p.parse_args(argv)
    root = a.toplevel() or os.getcwd()
    report = consume(root, pub_pem=args.pub)
    print(json.dumps(report, indent=2, default=str))
    if report.get("note"):
        print(report["note"])
    return int(report.get("exit") or 0)


if __name__ == "__main__":
    raise SystemExit(cmd())
