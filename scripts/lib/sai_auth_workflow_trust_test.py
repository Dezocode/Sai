#!/usr/bin/env python3
"""CTO-021/025 regression: candidate saul-review.yml cannot change trusted commands.

A-011: candidate MUST declare pull_request AND workflow_dispatch, MUST contain
skip-guard TRANSITIONAL_RETIRED_TRUSTED_ON_MAIN plus trusted-file cat-file.
Trusted file MUST declare pull_request_target. origin/main must not be faked.
"""
from __future__ import annotations

from sai_auth_workflow_trust import (
    CANDIDATE_WF, EVIL_RUN, TRUSTED_WF, assert_trusted_workflow,
    git_path_exists, load_workflow, run_commands, should_skip_transitional,
    step_if, workflow_on,
)


def run_workflow_trust_fixtures():
    executed = set()
    trusted_text = TRUSTED_WF.read_text(encoding="utf-8")
    candidate_text = CANDIDATE_WF.read_text(encoding="utf-8")

    executed.add("trusted-workflow-constraints")
    fails = assert_trusted_workflow(trusted_text)
    if fails:
        raise RuntimeError(fails)
    print("SELFTEST PASS  trusted-workflow-constraints")

    executed.add("candidate-evil-run-ignored")
    mutated = candidate_text + (
        "\n      - name: pwn-from-candidate\n"
        f"        run: {EVIL_RUN}\n"
    )
    trusted_cmds = run_commands(load_workflow(trusted_text))
    trusted_blob = "\n".join(trusted_cmds)
    if EVIL_RUN in trusted_text or EVIL_RUN in trusted_blob:
        raise RuntimeError("evil candidate run leaked into trusted workflow")
    mutated_cmds = run_commands(load_workflow(mutated))
    if EVIL_RUN not in "\n".join(mutated_cmds):
        raise RuntimeError("negative fixture did not inject evil run into candidate YAML")
    if EVIL_RUN in trusted_blob:
        raise RuntimeError("trusted executed commands include candidate evil run")
    print("SELFTEST PASS  candidate-evil-run-ignored")

    executed.add("candidate-pr-trigger-retired")
    cand_doc = load_workflow(candidate_text)
    cand_on = workflow_on(cand_doc)
    if not isinstance(cand_on, dict):
        raise RuntimeError("candidate on: must be a mapping")
    if "pull_request" not in cand_on:
        raise RuntimeError("candidate saul-review.yml must declare pull_request")
    if "workflow_dispatch" not in cand_on:
        raise RuntimeError("candidate saul-review.yml must declare workflow_dispatch")
    if "TRANSITIONAL_RETIRED_TRUSTED_ON_MAIN" not in candidate_text:
        raise RuntimeError("candidate must contain skip-guard TRANSITIONAL_RETIRED_TRUSTED_ON_MAIN")
    if "saul-cto-review.default-branch.yml" not in candidate_text:
        raise RuntimeError("candidate skip-guard must cat-file saul-cto-review.default-branch.yml")
    if "git cat-file -e" not in candidate_text:
        raise RuntimeError("candidate skip-guard must git cat-file -e the trusted workflow")
    invoke_if = step_if(cand_doc, "saul")
    if "steps.retire.outputs.skip" not in invoke_if:
        raise RuntimeError("invoke step if: must mention steps.retire.outputs.skip")
    trust_on = workflow_on(load_workflow(trusted_text))
    if not isinstance(trust_on, dict) or "pull_request_target" not in trust_on:
        raise RuntimeError("trusted file must declare pull_request_target")
    if "freeze-trusted-reviewer-once" in candidate_text:
        raise RuntimeError("CTO-015: do not reintroduce candidate freeze")
    if "allow-unsafe-pr-checkout: true" in trusted_text:
        raise RuntimeError("must not add allow-unsafe-pr-checkout: true")
    blob = "\n".join(run_commands(load_workflow(trusted_text)))
    if "candidate-data/scripts/" in blob or "$SAI_CANDIDATE_TREE/scripts/" in blob:
        raise RuntimeError("trusted run blob must not execute candidate scripts")
    print("SELFTEST PASS  candidate-pr-trigger-retired")

    executed.add("hermetic-skip-guard")
    if not should_skip_transitional(True):
        raise RuntimeError("trusted_exists True must skip transitional Codex")
    if should_skip_transitional(False):
        raise RuntimeError("trusted_exists False must not skip (this PR still needs Codex)")
    print("SELFTEST PASS  hermetic-skip-guard")

    executed.add("cto021-not-faked-on-main")
    on_main = git_path_exists("origin/main:.github/workflows/saul-cto-review.default-branch.yml")
    on_main_old = git_path_exists("origin/main:.github/workflows/saul-review.yml")
    print(f"SELFTEST INFO  cto021_activation_on_main={str(on_main).lower()}")
    print(f"SELFTEST INFO  origin_main_has_saul_review_yml={str(on_main_old).lower()}")
    if on_main:
        raise RuntimeError("do not fake saul-cto-review.default-branch.yml onto origin/main")
    print("SELFTEST PASS  cto021-not-faked-on-main")
    return executed


if __name__ == "__main__":
    run_workflow_trust_fixtures()
    print("sai_auth_workflow_trust_test: OK")
