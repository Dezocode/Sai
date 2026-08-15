#!/usr/bin/env python3
"""Synthetic FINDING_TO_CI fixtures. Prints SELFTEST PASS  <fixture>."""
from __future__ import annotations

from sai_auth_finding_guards import evaluate, finding_errors

REG = {
    "saul-finding-regression-guard",
    "code-health-self-test",
    "saul-sha-shard-quality",
}

# (fixture, expect_ok, finding)
CASES = (
    (
        "finding-deterministic-linked-good",
        True,
        {
            "blocking": True,
            "quality_guard": "DETERMINISTIC",
            "check_id": "saul-finding-regression-guard",
        },
    ),
    (
        "finding-heuristic-linked-good",
        True,
        {
            "blocking": True,
            "quality_guard": "HEURISTIC",
            "check_id": "code-health-self-test",
        },
    ),
    (
        "finding-semantic-rationale-good",
        True,
        {
            "blocking": True,
            "quality_guard": "SEMANTIC",
            "rationale": "Invariant requires Hostinger Saul architectural judgment.",
        },
    ),
    (
        "finding-missing-guard-bad",
        False,
        {"blocking": True},
    ),
    (
        "finding-semantic-silent-bad",
        False,
        {"blocking": True, "quality_guard": "SEMANTIC"},
    ),
    (
        "finding-unlinked-check-bad",
        False,
        {"blocking": True, "quality_guard": "DETERMINISTIC"},
    ),
    (
        "finding-unknown-check-id-bad",
        False,
        {
            "blocking": True,
            "quality_guard": "HEURISTIC",
            "check_id": "not-a-registered-check",
        },
    ),
    (
        "finding-recurring-creates-guard-good",
        True,
        {
            "blocking": True,
            "recurring": True,
            "quality_guard": "DETERMINISTIC",
            "check_id": "saul-sha-shard-quality",
        },
    ),
    (
        "finding-recurring-unlinked-bad",
        False,
        {
            "blocking": True,
            "recurring": True,
            "quality_guard": "DETERMINISTIC",
        },
    ),
    (
        "finding-defect-present-bad",
        False,
        {
            "blocking": True,
            "defect": "missing-guard",
        },
    ),
    (
        "finding-clean-good",
        True,
        {
            "blocking": True,
            "quality_guard": "DETERMINISTIC",
            "check_id": "saul-finding-regression-guard",
        },
    ),
)


def run_finding_guard_fixtures():
    executed = set()
    for name, expect_ok, finding in CASES:
        executed.add(name)
        ok = evaluate(finding, REG)
        if ok != expect_ok:
            raise RuntimeError((name, ok, expect_ok, finding_errors(finding, REG)))
        print(f"SELFTEST PASS  {name}")
    return executed


if __name__ == "__main__":
    run_finding_guard_fixtures()
    print("sai_auth_finding_guards_test: OK")
