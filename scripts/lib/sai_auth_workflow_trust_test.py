#!/usr/bin/env python3
"""CTO-021 regression: candidate saul-review.yml cannot change trusted commands."""
from __future__ import annotations

from sai_auth_workflow_trust import (
    CANDIDATE_WF, EVIL_RUN, TRUSTED_WF, assert_trusted_workflow,
    git_path_exists, load_workflow, run_commands,
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

    executed.add("transitional-pr-trigger-kept")
    if "pull_request:" not in candidate_text:
        raise RuntimeError("transitional saul-review.yml must keep pull_request")
    if "freeze-trusted-reviewer-once" in candidate_text:
        raise RuntimeError("CTO-015: do not reintroduce candidate freeze")
    if "CTO-021" not in candidate_text:
        raise RuntimeError("transitional workflow must note CTO-021 remains open")
    print("SELFTEST PASS  transitional-pr-trigger-kept")

    executed.add("cto021-not-faked-on-main")
    on_main = git_path_exists("origin/main:.github/workflows/saul-cto-review.default-branch.yml")
    on_main_old = git_path_exists("origin/main:.github/workflows/saul-review.yml")
    print(f"SELFTEST INFO  cto021_activation_on_main={str(on_main).lower()}")
    print(f"SELFTEST INFO  origin_main_has_saul_review_yml={str(on_main_old).lower()}")
    if on_main:
        print("SELFTEST INFO  file exists on origin/main; activation is still a human gate")
    print("SELFTEST PASS  cto021-not-faked-on-main")
    return executed


if __name__ == "__main__":
    run_workflow_trust_fixtures()
    print("sai_auth_workflow_trust_test: OK")
