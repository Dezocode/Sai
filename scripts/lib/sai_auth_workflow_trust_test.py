#!/usr/bin/env python3
"""CTO-021/030 regression: candidate saul-review.yml cannot acquire Hostinger.

A-012: saul-review.yml absent OR cannot acquire self-hosted. Trusted file MUST
declare pull_request_target (not pull_request). Evil-run isolation. origin/main
must not be faked. Hermetic job-if: dispatch from a non-default ref must not
match the acquire predicate (evaluated before runner assignment).
"""
from __future__ import annotations

from sai_auth_workflow_trust import (
    CANDIDATE_WF, EVIL_RUN, TRUSTED_WF, assert_candidate_cannot_acquire,
    assert_trusted_workflow, git_path_exists, job_if, load_workflow,
    run_commands, would_acquire, workflow_on,
)


def run_workflow_trust_fixtures():
    executed = set()
    trusted_text = TRUSTED_WF.read_text(encoding="utf-8")
    trusted_doc = load_workflow(trusted_text)

    executed.add("trusted-workflow-constraints")
    fails = assert_trusted_workflow(trusted_text)
    if fails:
        raise RuntimeError(fails)
    print("SELFTEST PASS  trusted-workflow-constraints")

    executed.add("candidate-path-removed")
    cand_fails = assert_candidate_cannot_acquire(CANDIDATE_WF)
    if cand_fails:
        raise RuntimeError(cand_fails)
    if CANDIDATE_WF.is_file():
        print("SELFTEST PASS  candidate-path-removed (present but cannot acquire self-hosted)")
    else:
        print("SELFTEST PASS  candidate-path-removed (absent)")

    executed.add("candidate-evil-run-ignored")
    synthetic = (
        "name: evil\non:\n  pull_request:\njobs:\n  x:\n"
        "    runs-on: ubuntu-latest\n    steps:\n      - run: echo ok\n"
    )
    mutated = synthetic + (
        "\n      - name: pwn-from-candidate\n"
        f"        run: {EVIL_RUN}\n"
    )
    trusted_cmds = run_commands(trusted_doc)
    trusted_blob = "\n".join(trusted_cmds)
    if EVIL_RUN in trusted_text or EVIL_RUN in trusted_blob:
        raise RuntimeError("evil candidate run leaked into trusted workflow")
    mutated_cmds = run_commands(load_workflow(mutated))
    if EVIL_RUN not in "\n".join(mutated_cmds):
        raise RuntimeError("negative fixture did not inject evil run into candidate YAML")
    if EVIL_RUN in trusted_blob:
        raise RuntimeError("trusted executed commands include candidate evil run")
    print("SELFTEST PASS  candidate-evil-run-ignored")

    executed.add("trusted-still-pull-request-target")
    trust_on = workflow_on(trusted_doc)
    if not isinstance(trust_on, dict) or "pull_request_target" not in trust_on:
        raise RuntimeError("trusted file must declare pull_request_target")
    if "pull_request" in trust_on:
        raise RuntimeError("trusted file must not declare on: pull_request")
    if "allow-unsafe-pr-checkout: true" in trusted_text:
        raise RuntimeError("must not add allow-unsafe-pr-checkout: true")
    blob = "\n".join(trusted_cmds)
    if "candidate-data/scripts/" in blob or "$SAI_CANDIDATE_TREE/scripts/" in blob:
        raise RuntimeError("trusted run blob must not execute candidate scripts")
    print("SELFTEST PASS  trusted-still-pull-request-target")

    executed.add("hermetic-job-if-dispatch-ref")
    pred = job_if(trusted_doc, "invoke-saul")
    if "github.ref" not in pred:
        raise RuntimeError("job if: missing github.ref dispatch guard")
    if would_acquire(
        "workflow_dispatch",
        ref="refs/heads/cursor/codebase-health-90ba",
        default_branch="main",
    ):
        raise RuntimeError("dispatch from non-default ref must not acquire Hostinger")
    if not would_acquire(
        "workflow_dispatch", ref="refs/heads/main", default_branch="main",
    ):
        raise RuntimeError("dispatch from default branch must match acquire predicate")
    if not would_acquire(
        "pull_request_target",
        head_repo="Dezocode/Sai",
        repository="Dezocode/Sai",
    ):
        raise RuntimeError("same-repo pull_request_target must acquire")
    if would_acquire(
        "pull_request_target",
        head_repo="evil/Sai",
        repository="Dezocode/Sai",
    ):
        raise RuntimeError("fork pull_request_target must not acquire")
    if would_acquire(
        "pull_request",
        head_repo="Dezocode/Sai",
        repository="Dezocode/Sai",
    ):
        raise RuntimeError("on: pull_request must not acquire on the trusted file")
    print("SELFTEST PASS  hermetic-job-if-dispatch-ref")

    executed.add("cto021-not-faked-on-main")
    on_main = git_path_exists("origin/main:.github/workflows/saul-cto-review.default-branch.yml")
    on_main_old = git_path_exists("origin/main:.github/workflows/saul-review.yml")
    print(f"SELFTEST INFO  cto021_activation_on_main={str(on_main).lower()}")
    print(f"SELFTEST INFO  origin_main_has_saul_review_yml={str(on_main_old).lower()}")
    if on_main:
        raise RuntimeError("do not fake saul-cto-review.default-branch.yml onto origin/main")
    print("SELFTEST PASS  cto021-not-faked-on-main")

    executed.add("trusted-check-publish-from-trusted-tree-good")
    perms = trusted_doc.get("permissions") or {}
    if perms.get("checks") != "write":
        raise RuntimeError("trusted workflow must grant checks: write")
    if "Saul / Product Quality" not in trusted_text:
        raise RuntimeError("Check name must be exactly Saul / Product Quality")
    pub = trusted_text.split("- name: Publish Saul Product Quality Check", 1)
    if len(pub) < 2:
        raise RuntimeError("missing Publish Saul Product Quality Check step")
    chunk = pub[1].split("\n      - name:", 1)[0]
    if "SAI_TRUSTED_TREE" not in chunk:
        raise RuntimeError("publisher must resolve SAI_TRUSTED_TREE")
    if "saul-publish-check" not in chunk and "sai_auth_saul_check.py" not in chunk:
        raise RuntimeError("publisher must run saul-publish-check or python equivalent")
    if "candidate-data/scripts/" in chunk or "$SAI_CANDIDATE_TREE/scripts/" in chunk:
        raise RuntimeError("publisher must not execute candidate-data")
    if "GH_TOKEN:" not in chunk:
        raise RuntimeError("publisher step must keep GH_TOKEN")
    if "TRUSTED_PUBLISHER_MISSING" not in chunk:
        raise RuntimeError("missing trusted publisher must fail closed")
    if "--publish" not in chunk:
        raise RuntimeError("publisher must pass --publish")
    print("SELFTEST PASS  trusted-check-publish-from-trusted-tree-good")

    executed.add("unsigned-check-not-pass-bad")
    from sai_auth_saul_check import (
        CHECK_NAME, ZERO_AUTHORITY, build_publish_payload,
    )
    blocked = {
        "disposition": "BLOCKED", "reason": "NO_ARTIFACT",
        "codex_invoked": False, "synthetic": False, "findings": [],
    }
    payload = build_publish_payload(blocked, exact_head="a" * 40)
    if payload.get("name") != CHECK_NAME or payload.get("conclusion") != "failure":
        raise RuntimeError(payload)
    if payload.get("authority") != ZERO_AUTHORITY:
        raise RuntimeError("unsigned BLOCKED must not be ATTESTATION_V2")
    fake = build_publish_payload(blocked, exact_head="a" * 40,
                                 conclusion_override="success")
    if fake.get("conclusion") != "failure":
        raise RuntimeError("unsigned must not fake PASS")
    print("SELFTEST PASS  unsigned-check-not-pass-bad")
    return executed


if __name__ == "__main__":
    run_workflow_trust_fixtures()
    print("sai_auth_workflow_trust_test: OK")
