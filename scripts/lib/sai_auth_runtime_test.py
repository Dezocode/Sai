#!/usr/bin/env python3
"""Identity fixtures: named Cora/contractor tree; Cora silent on healthy progress."""
from __future__ import annotations

from sai_auth_runtime import (
    cora_should_wake, display_identity, named_cora, validate_identity,
)


def run_runtime_fixtures():
    executed = set()
    cora = named_cora(
        parent_logical="pr62-primary",
        parent_physical="bc-test",
        contract_id="20260813-pr62-saul-smoke",
        revision="v3",
        work_item="issue-lease",
        base_sha="a" * 40,
        model="cursor-grok-4.6-high",
    )
    missing = validate_identity(cora)
    executed.add("named-cora-identity")
    if missing or cora["agent_id"] != "ctr-admin" or cora["name"] != "Cora":
        raise RuntimeError(missing or cora)
    if cora.get("implements") is not False:
        raise RuntimeError("Cora must not implement")
    print("SELFTEST PASS  named-cora-identity")

    contractor = dict(cora)
    contractor.update({
        "agent_id": "ctr-code-pr62smoke",
        "name": "PR62 contractor",
        "role": "Implementation",
        "authorization_id": "lease-c3a003pr62q1",
        "authorization_kind": "lease",
        "work_item": "resume-sai-scripts",
        "task_title": "Implement /resume-sai",
        "implements": True,
        "parent_logical_runtime": "pr62-primary",
    })
    executed.add("named-contractor-distinct-from-title")
    line = display_identity(contractor)
    if "ctr-code-pr62smoke" not in line or "Implement /resume-sai" not in line:
        raise RuntimeError(line)
    if contractor["agent_id"] == contractor["task_title"]:
        raise RuntimeError("task title used as identity")
    print("SELFTEST PASS  named-contractor-distinct-from-title")

    executed.add("cora-silent-healthy-progress")
    if cora_should_wake("SUBAGENT_COMPLETE") or cora_should_wake("CI_COMPLETE"):
        raise RuntimeError("Cora must not wake on healthy progress")
    if not cora_should_wake("CORA_CONTRACT_CHANGED"):
        raise RuntimeError("Cora must wake on contract change")
    if not cora_should_wake("AUTHORITY_REQUIRED"):
        raise RuntimeError("Cora must wake on authority gate")
    print("SELFTEST PASS  cora-silent-healthy-progress")

    executed.add("parent-child-not-implicit-authority")
    if contractor["authorization_id"] == cora["authorization_id"]:
        raise RuntimeError("child must have explicit lease, not parent grant")
    print("SELFTEST PASS  parent-child-not-implicit-authority")
    return executed


if __name__ == "__main__":
    run_runtime_fixtures()
    print("sai_auth_runtime_test: OK")
