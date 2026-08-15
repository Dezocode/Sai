#!/usr/bin/env python3
"""Gated-CI consumer fixtures. Cannot mint PASS. Prints SELFTEST PASS  <id>."""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile

import sai_auth as a
from sai_auth_saul_gated import consume, detect_substitute, missing_ledger_projection

P0 = "B-SAUL-COMPTROLLER-READINESS-001"


def _git(root: Path, files: dict):
    root.mkdir(parents=True, exist_ok=True)
    a.git(root, "init")
    a.git(root, "config", "user.email", "t@example.com")
    a.git(root, "config", "user.name", "t")
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body if isinstance(body, str) else json.dumps(body), encoding="utf-8")
        a.git(root, "add", rel)
    a.git(root, "commit", "-m", "init")
    return a.head_sha(root)


def _ledger(bids):
    rows = "\n".join(f"- blocker_id: {b}\n  status: DISCOVERED" for b in bids)
    return f"ledger_id: t\ncontract_id: 20260813-pr62-saul-smoke\nblockers:\n{rows}\n"


def _state(**kw):
    row = {
        "task_id": "t", "repo": "Dezocode/Sai", "pr": 62,
        "branch": "cursor/codebase-health-90ba",
        "primary_logical_id": "pr62-primary",
        "current_head": "0" * 40, "contract_id": "20260813-pr62-saul-smoke",
        "contract_revision": "v12", "liveness": "ACTIVE",
        "exit_predicate": "READY_FOR_HUMAN_REVIEW",
        "exit_predicate_satisfied": False, "sai_disposition": "pending",
    }
    row.update(kw)
    return json.dumps(row)


def run_gated_fixtures():
    executed = set()
    p0s = [
        "B-SAUL-COMPTROLLER-READINESS-001", "B-FRONTIER-QUALITY-ARCH-001",
        "B-QUALITY-ANTI-BALLOON-001", "B-RALPH-BLOCKER-CI-CONVERGENCE-001",
    ]
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "absent-good"
        _git(root, {
            ".ai/contracts/20260813-pr62-saul-smoke/blockers/ledger.yaml": _ledger(p0s),
            ".ai/contracts/20260813-pr62-saul-smoke/contract.json": json.dumps({
                "contract_id": "20260813-pr62-saul-smoke", "current_revision": "v12",
            }),
            ".ai/runs/t/coordinator-state.json": _state(),
            ".ai/_config/primary-programs.yaml": "max_active: 2\nprograms: []\n",
        })
        rep = consume(root)
        if rep.get("exit") != 0 or not rep.get("saul_gates", {}).get("checks_nonsuccess"):
            raise RuntimeError(rep)
        if rep.get("can_mint_pass"):
            raise RuntimeError("must not mint PASS")
        executed.add("gated-absent-proof-nonsuccess-good")
        print("SELFTEST PASS  gated-absent-proof-nonsuccess-good")

        bad = Path(tmp) / "terminal-bad"
        _git(bad, {
            ".ai/contracts/20260813-pr62-saul-smoke/blockers/ledger.yaml": _ledger(p0s),
            ".ai/contracts/20260813-pr62-saul-smoke/contract.json": json.dumps({
                "contract_id": "20260813-pr62-saul-smoke", "current_revision": "v12",
            }),
            ".ai/runs/t/coordinator-state.json": _state(liveness="COMPLETE"),
            ".ai/_config/primary-programs.yaml": "max_active: 2\nprograms: []\n",
        })
        rep = consume(bad)
        if rep.get("exit") != 1:
            raise RuntimeError(rep)
        executed.add("gated-false-terminal-bad")
        print("SELFTEST PASS  gated-false-terminal-bad")

        miss = Path(tmp) / "ledger-bad"
        _git(miss, {
            ".ai/contracts/20260813-pr62-saul-smoke/blockers/ledger.yaml": _ledger(["CTO-026"]),
            ".ai/contracts/20260813-pr62-saul-smoke/contract.json": json.dumps({
                "contract_id": "20260813-pr62-saul-smoke", "current_revision": "v12",
            }),
            ".ai/runs/t/coordinator-state.json": _state(),
            ".ai/_config/primary-programs.yaml": "max_active: 2\nprograms: []\n",
        })
        if not missing_ledger_projection(miss):
            raise RuntimeError("expected missing P0s")
        rep = consume(miss)
        if rep.get("exit") != 1:
            raise RuntimeError(rep)
        executed.add("gated-missing-ledger-blocker-bad")
        print("SELFTEST PASS  gated-missing-ledger-blocker-bad")

        sub = Path(tmp) / "sub-bad"
        head = _git(sub, {
            ".ai/contracts/20260813-pr62-saul-smoke/blockers/ledger.yaml": _ledger(p0s),
            ".ai/contracts/20260813-pr62-saul-smoke/contract.json": json.dumps({
                "contract_id": "20260813-pr62-saul-smoke", "current_revision": "v12",
            }),
            ".ai/runs/t/coordinator-state.json": _state(),
            ".ai/_config/primary-programs.yaml": "max_active: 2\nprograms: []\n",
            ".ai/contracts/20260813-pr62-saul-smoke/reviews/saul-fake.yaml": (
                "reviewer: saul\nruntime: cursor\ndisposition: APPROVE\n"
                "codex_invoked: false\nsynthetic: true\n"
            ),
        })
        # rewrite review with this head
        (sub / ".ai/contracts/20260813-pr62-saul-smoke/reviews/saul-fake.yaml").write_text(
            "reviewer: saul\nruntime: cursor\ndisposition: APPROVE\n"
            f"implementation_head: {head}\ncodex_invoked: false\nsynthetic: true\n",
            encoding="utf-8",
        )
        if not detect_substitute(sub):
            raise RuntimeError("cursor APPROVE must be substitute")
        rep = consume(sub)
        if rep.get("exit") != 1:
            raise RuntimeError(rep)
        executed.add("gated-substitute-evidence-bad")
        print("SELFTEST PASS  gated-substitute-evidence-bad")

        syn = Path(tmp) / "syn-bad"
        h2 = _git(syn, {
            ".ai/contracts/20260813-pr62-saul-smoke/blockers/ledger.yaml": _ledger(p0s),
            ".ai/contracts/20260813-pr62-saul-smoke/contract.json": json.dumps({
                "contract_id": "20260813-pr62-saul-smoke", "current_revision": "v12",
            }),
            ".ai/runs/t/coordinator-state.json": _state(),
            ".ai/_config/primary-programs.yaml": "max_active: 2\nprograms: []\n",
        })
        a.write_yaml(syn / ".ai/contracts/20260813-pr62-saul-smoke/reviews/saul-syn.yaml", {
            "reviewer": "saul", "runtime": "codex", "disposition": "APPROVE",
            "implementation_head": h2, "codex_invoked": True, "synthetic": True,
            "contract_revision": 12,
        })
        rep = consume(syn)
        if rep.get("exit") != 1:
            raise RuntimeError(rep)
        executed.add("gated-synthetic-review-bad")
        print("SELFTEST PASS  gated-synthetic-review-bad")

        unsigned = Path(tmp) / "unsigned-bad"
        h3 = _git(unsigned, {
            ".ai/contracts/20260813-pr62-saul-smoke/blockers/ledger.yaml": _ledger(p0s),
            ".ai/contracts/20260813-pr62-saul-smoke/contract.json": json.dumps({
                "contract_id": "20260813-pr62-saul-smoke", "current_revision": "v12",
            }),
            ".ai/runs/t/coordinator-state.json": _state(),
            ".ai/_config/primary-programs.yaml": "max_active: 2\nprograms: []\n",
        })
        a.write_yaml(unsigned / ".ai/contracts/20260813-pr62-saul-smoke/reviews/saul-u.yaml", {
            "reviewer": "saul", "runtime": "codex", "disposition": "APPROVE",
            "implementation_head": h3, "codex_invoked": True, "synthetic": False,
            "contract_revision": 12,
        })
        rep = consume(unsigned)
        if rep.get("exit") != 1:
            raise RuntimeError(rep)
        executed.add("gated-unsigned-exact-head-bad")
        print("SELFTEST PASS  gated-unsigned-exact-head-bad")

        from sai_auth_saul_gated import gates_missing
        miss_gates = gates_missing([
            {"blocker_id": P0, "category": "technical", "check_name": "ci-green"},
        ])
        if P0 not in miss_gates:
            raise RuntimeError(miss_gates)
        executed.add("gated-missing-check-gate-bad")
        print("SELFTEST PASS  gated-missing-check-gate-bad")
    return executed


if __name__ == "__main__":
    run_gated_fixtures()
    print("sai_auth_saul_gated_test: OK")
