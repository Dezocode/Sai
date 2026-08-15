#!/usr/bin/env python3
"""Architecture-review fixtures. Names include good or bad."""
from __future__ import annotations

import json
from pathlib import Path

from sai_auth_review_architecture import (
    ARCH_CLEARANCE_REASON, SCHEMA_ID, SCHEMA_REL, attempt_clear_arch_blocker,
    load_schema, review_architecture, validate_evidence,
)

ROOT = Path(__file__).resolve().parents[2]
PROD = Path(__file__).resolve().parent / "sai_auth_review_architecture.py"
IDENTITY_LEAKS = (
    "codebase-health-90ba",
    "20260813-pr62-saul-smoke",
    "lease-c3a003pr62q1",
    "pull/62",
)
BASE = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
HEAD = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
REPO = "example/repo"


def _base(**extra):
    inp = {
        "repository": REPO,
        "base_sha": BASE,
        "head_sha": HEAD,
        "changed_paths": extra.pop("changed_paths", ["tests/unit/leaf_ok.py"]),
        "untouched_paths": extra.pop("untouched_paths", []),
        "shard_coverage": extra.pop("shard_coverage", {
            "expected": ["s1"], "passed": ["s1"], "missing": [], "failed": [],
        }),
        "quality_policy_digest": "policy-v1",
    }
    inp.update(extra)
    return inp


def _full_shards():
    ids = [f"shard-{i}" for i in range(4)]
    return {"expected": ids, "passed": list(ids), "missing": [], "failed": []}


def _assert_schema(ev):
    fails = validate_evidence(ev)
    if fails:
        raise RuntimeError(fails)
    schema = load_schema(ROOT)
    if schema.get("$id") and SCHEMA_ID not in schema.get("$id", ""):
        raise RuntimeError("schema $id mismatch")
    if ev.get("schema_id") != SCHEMA_ID:
        raise RuntimeError("evidence schema_id")
    rel = ROOT / SCHEMA_REL
    json.loads(rel.read_text(encoding="utf-8"))


def _assert_no_identity_defaults():
    text = PROD.read_text(encoding="utf-8")
    for leak in IDENTITY_LEAKS:
        if leak in text:
            raise RuntimeError(f"production hardcoded identity default: {leak}")


def test_arch_local_impact_good():
    ev = review_architecture(_base(
        shard_coverage={"expected": [], "passed": [], "missing": [], "failed": []},
    ))
    _assert_schema(ev)
    if ev["local_arch"]["verdict"] != "PASS_CURRENT":
        raise RuntimeError(ev["local_arch"])
    if ev["impact_arch"]["verdict"] != "PASS_CURRENT":
        raise RuntimeError(ev["impact_arch"])
    if ev["system_arch_required_now"]:
        raise RuntimeError("bounded change must not set SYSTEM_ARCH_REQUIRED_NOW")
    print("SELFTEST PASS  arch-local-impact-good")


def test_arch_system_missing_bad():
    ev = review_architecture(_base(shard_coverage=_full_shards()))
    _assert_schema(ev)
    conv = ev["convergence"]
    if conv["converged"] is True:
        raise RuntimeError("full shards without SYSTEM_ARCH must not converge")
    if conv["reason"] != "NOT_CONVERGED_MISSING_SYSTEM_ARCH":
        raise RuntimeError(conv)
    if ev["system_arch"]["performed"] is True:
        raise RuntimeError(ev["system_arch"])
    print("SELFTEST PASS  arch-system-missing-bad")


def test_arch_shards_missing_bad():
    ev = review_architecture(_base(
        shard_coverage={
            "expected": ["shard-a", "shard-b"],
            "passed": ["shard-a"],
            "missing": ["shard-b"],
            "failed": [],
        },
        system_arch_proof={
            "performed": True,
            "verdict": "PASS_CURRENT",
            "head_sha": HEAD,
        },
    ))
    _assert_schema(ev)
    if ev["local_arch"]["verdict"] != "PASS_CURRENT":
        raise RuntimeError(ev["local_arch"])
    if ev["impact_arch"]["verdict"] != "PASS_CURRENT":
        raise RuntimeError(ev["impact_arch"])
    if ev["system_arch"]["verdict"] != "PASS_CURRENT":
        raise RuntimeError(ev["system_arch"])
    conv = ev["convergence"]
    if conv["converged"] is True:
        raise RuntimeError("architecture PASS with missing shard must not converge")
    if conv["reason"] != "NOT_CONVERGED_MISSING_SHARD":
        raise RuntimeError(conv)
    print("SELFTEST PASS  arch-shards-missing-bad")


def test_arch_domain_stale_bad():
    old = "cccccccccccccccccccccccccccccccccccccccc"
    ev = review_architecture(_base(
        changed_paths=["scripts/lib/sai_auth_blockers.py"],
        untouched_paths=[".ai/contracts/example/blockers/ledger.yaml"],
        component_graph={
            "scripts/lib/sai_auth_blockers.py": {"tests": [], "schemas": []},
        },
        prior_domain_proofs={
            "contractor_isolation": {
                "verdict": "PASS_CURRENT",
                "head_sha": old,
                "context_digest": "stale-digest",
            },
            "requirement_coherence": {
                "verdict": "PASS_CURRENT",
                "head_sha": HEAD,
                "context_digest": "stale-digest",
            },
        },
    ))
    _assert_schema(ev)
    iso = ev["domains"]["contractor_isolation"]
    if iso["verdict"] == "PASS_CURRENT":
        raise RuntimeError("untouched invalidated domain must not be PASS_CURRENT")
    if iso["verdict"] != "STALE":
        raise RuntimeError(iso)
    if not iso["impact"] or iso["local"]:
        raise RuntimeError(iso)
    if ".ai/contracts/example/blockers/ledger.yaml" not in iso["untouched_files"]:
        raise RuntimeError(iso)
    print("SELFTEST PASS  arch-domain-stale-bad")


def test_arch_fail_creates_blocker_good():
    ev = review_architecture(_base(
        changed_paths=["scripts/lib/sai_auth.py"],
        component_graph={"scripts/lib/sai_auth.py": {"tests": [], "schemas": []}},
        domain_findings={"authorization": "FAIL"},
    ))
    _assert_schema(ev)
    if ev["domains"]["authorization"]["verdict"] != "FAIL":
        raise RuntimeError(ev["domains"]["authorization"])
    blockers = ev["blockers"]
    if not blockers:
        raise RuntimeError("FAIL must append ARCH-* blocker payload")
    row = blockers[0]
    if not str(row.get("blocker_id") or "").startswith("ARCH-"):
        raise RuntimeError(row)
    if row.get("ledger_write") is not False:
        raise RuntimeError("must not write live ledger")
    if row.get("clearance_authority") != "saul":
        raise RuntimeError(row)
    for actor in ("cursor", "contractor", "ctr-code-pr62smoke", "self", "cora"):
        got = attempt_clear_arch_blocker(row, actor, proof={
            "reviewer": "saul", "runtime": "codex", "disposition": "APPROVE",
        })
        if got.get("status") != "REJECT" or got.get("reason") != ARCH_CLEARANCE_REASON:
            raise RuntimeError((actor, got))
    fake = {
        "reviewer": "saul",
        "runtime": "codex",
        "codex_invoked": True,
        "synthetic": False,
        "review_type": "SYSTEM_ARCH",
        "disposition": "APPROVE",
        "implementation_head": HEAD,
        "attestation": {"source": "cursor", "sig": "fakesig"},
    }
    got = attempt_clear_arch_blocker(row, "saul", proof=fake, exact_head=HEAD)
    if got.get("status") != "REJECT":
        raise RuntimeError(("cursor-sourced proof must not clear", got))
    unsigned = dict(fake)
    unsigned["attestation"] = {"sig": ""}
    got = attempt_clear_arch_blocker(row, "saul", proof=unsigned, exact_head=HEAD)
    if got.get("status") != "REJECT":
        raise RuntimeError(("unsigned must not clear", got))
    print("SELFTEST PASS  arch-fail-creates-blocker-good")


def test_arch_system_required_now_good():
    ev = review_architecture(_base(
        changed_paths=[
            ".ai/_config/authorization.yaml",
            ".github/workflows/agent-audit.yml",
            "scripts/lib/sai_auth.py",
            ".ai/agents/sai/AGENT.md",
            ".cursor/rules/sai-orchestration.mdc",
        ],
        component_graph={p: {"tests": [], "schemas": []} for p in (
            ".ai/_config/authorization.yaml",
            ".github/workflows/agent-audit.yml",
            "scripts/lib/sai_auth.py",
            ".ai/agents/sai/AGENT.md",
            ".cursor/rules/sai-orchestration.mdc",
        )},
    ))
    _assert_schema(ev)
    if not ev["system_arch_required_now"]:
        raise RuntimeError(ev["system_arch"])
    if not ev["system_arch"]["required_now"]:
        raise RuntimeError(ev["system_arch"])
    print("SELFTEST PASS  arch-system-required-now-good")


def run_architecture_fixtures():
    _assert_no_identity_defaults()
    test_arch_local_impact_good()
    test_arch_system_missing_bad()
    test_arch_shards_missing_bad()
    test_arch_domain_stale_bad()
    test_arch_fail_creates_blocker_good()
    test_arch_system_required_now_good()
    return {
        "arch-local-impact-good",
        "arch-system-missing-bad",
        "arch-shards-missing-bad",
        "arch-domain-stale-bad",
        "arch-fail-creates-blocker-good",
        "arch-system-required-now-good",
    }


if __name__ == "__main__":
    n = run_architecture_fixtures()
    print(f"sai_auth_review_architecture_test: OK ({len(n)} fixtures)")
