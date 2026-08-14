#!/usr/bin/env python3
"""TPR-001/002 hermetic proofs. Called from workflow-trust and invoke --self-test."""
from __future__ import annotations

from pathlib import Path

from sai_auth_package import STRIP_FROM_CODEX, codex_exec_env
from sai_auth_workflow_trust import (
    CANDIDATE_WF, PROVISIONER_WF, TRUSTED_WF,
    assert_candidate_cannot_acquire, assert_provisioner_workflow,
    assert_trusted_workflow, load_workflow, run_commands,
)

ROOT = Path(__file__).resolve().parents[2]
AUDIT_WF = ROOT / ".github/workflows/agent-audit.yml"

CIRCULAR_PROVISIONER = """
name: circular-provision
on:
  workflow_dispatch:
    inputs:
      from_sha:
        required: true
jobs:
  provision:
    runs-on: [self-hosted]
    steps:
      - uses: actions/checkout@v4
        with:
          ref: "${{ github.event.inputs.from_sha }}"
      - run: scripts/provision-trusted-reviewer-root --from-sha x
"""

NON_CIRCULAR = """
name: trusted-review
on:
  pull_request_target:
jobs:
  invoke-saul:
    runs-on: [self-hosted]
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
          path: trusted-default-branch
      - run: '"$SAI_TRUSTED_TREE/scripts/invoke-saul-review"'
"""


def _step_chunk(text: str, name: str) -> str:
    needle = f"- name: {name}"
    if needle not in text:
        return ""
    return text.split(needle, 1)[1].split("\n      - name:", 1)[0]


def _blank(value) -> bool:
    if value is None:
        return True
    return isinstance(value, str) and not str(value).strip()


def _yaml_empty_override(chunk: str, key: str) -> bool:
    for line in chunk.splitlines():
        s = line.strip()
        if s == f'{key}: ""' or s == f"{key}: ''" or s == f"{key}:":
            return True
    return False


def _step_env(doc: dict, name: str) -> dict:
    jobs = doc.get("jobs") if isinstance(doc, dict) else None
    if not isinstance(jobs, dict):
        return {}
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        for step in job.get("steps") or []:
            if isinstance(step, dict) and step.get("name") == name:
                env = step.get("env") or {}
                return env if isinstance(env, dict) else {}
    return {}


def run_tpr_fixtures():
    executed = set()
    trusted_text = TRUSTED_WF.read_text(encoding="utf-8")
    trusted_doc = load_workflow(trusted_text)
    audit = AUDIT_WF.read_text(encoding="utf-8")

    executed.add("tpr-a-circular-provisioner-rejected")
    if PROVISIONER_WF.is_file():
        raise RuntimeError("live trusted-reviewer-provision.yml must be absent")
    if not assert_provisioner_workflow(CIRCULAR_PROVISIONER):
        raise RuntimeError("synthetic from_sha checkout+provisioner must be rejected")
    if assert_provisioner_workflow(NON_CIRCULAR):
        raise RuntimeError("non-circular workflow must not be rejected")
    print("SELFTEST PASS  tpr-a-circular-provisioner-rejected")

    executed.add("tpr-b-saul-review-yml-absent")
    cand_fails = assert_candidate_cannot_acquire(CANDIDATE_WF)
    if cand_fails:
        raise RuntimeError(cand_fails)
    if CANDIDATE_WF.is_file():
        raise RuntimeError("saul-review.yml must stay absent")
    print("SELFTEST PASS  tpr-b-saul-review-yml-absent")

    executed.add("tpr-c-no-candidate-scripts")
    trust_fails = assert_trusted_workflow(trusted_text)
    if trust_fails:
        raise RuntimeError(trust_fails)
    blob = "\n".join(run_commands(trusted_doc))
    if "candidate-data/scripts/" in blob:
        raise RuntimeError("trusted run blob must not execute candidate-data/scripts")
    print("SELFTEST PASS  tpr-c-no-candidate-scripts")

    executed.add("tpr-d-codex-env-no-github-token")
    isolated = codex_exec_env({
        "GITHUB_TOKEN": "ghs_x", "GH_TOKEN": "ghs_y",
        "OPENAI_API_KEY": "sk-test", "CODEX_API_KEY": "ck-test", "PATH": "/usr/bin",
    })
    if "GITHUB_TOKEN" in isolated or "GH_TOKEN" in isolated:
        raise RuntimeError(isolated)
    if not isolated.get("OPENAI_API_KEY") or not isolated.get("CODEX_API_KEY"):
        raise RuntimeError("model keys must remain")
    invoke_env = _step_env(trusted_doc, "Invoke Codex as Saul")
    chunk = _step_chunk(trusted_text, "Invoke Codex as Saul")
    for key in ("GITHUB_TOKEN", "GH_TOKEN"):
        if key not in invoke_env:
            raise RuntimeError(f"Invoke Codex env must explicitly override {key}")
        if not _blank(invoke_env.get(key)):
            raise RuntimeError(f"Invoke Codex {key} must be empty")
        if not _yaml_empty_override(chunk, key):
            raise RuntimeError(f'Invoke Codex must contain {key}: "" (or YAML empty)')
    post = _step_chunk(trusted_text, "Post review comment")
    status = _step_chunk(trusted_text, "Commit status")
    claim = _step_chunk(trusted_text, "Claim remediation transition")
    for pub, label in ((post, "Post review comment"), (status, "Commit status"), (claim, "Claim")):
        if "GH_TOKEN:" not in pub:
            raise RuntimeError(f"{label} must keep GH_TOKEN")
    print("SELFTEST PASS  tpr-d-codex-env-no-github-token")

    executed.add("tpr-e-codex-env-no-ssh-docker")
    isolated2 = codex_exec_env({
        "SSH_AUTH_SOCK": "/tmp/ssh", "DOCKER_HOST": "unix:///var/run/docker.sock",
        "OPENAI_API_KEY": "sk-test",
    })
    for k in ("SSH_AUTH_SOCK", "DOCKER_HOST"):
        if k in isolated2:
            raise RuntimeError(isolated2)
    if any(k not in STRIP_FROM_CODEX for k in ("SSH_AUTH_SOCK", "DOCKER_HOST")):
        raise RuntimeError(STRIP_FROM_CODEX)
    print("SELFTEST PASS  tpr-e-codex-env-no-ssh-docker")

    executed.add("tpr-f-publisher-disposition-not-candidate")
    status = _step_chunk(trusted_text, "Commit status")
    post = _step_chunk(trusted_text, "Post review comment")
    if "/tmp/saul/disposition" not in status:
        raise RuntimeError("commit-status must read /tmp/saul/disposition")
    if 'disp.strip()=="APPROVE"' not in status and 'DISP" = "APPROVE"' not in status:
        raise RuntimeError("APPROVE must come from trusted /tmp/saul/disposition")
    for chunk, label in ((status, "Commit status"), (post, "Post review comment")):
        if "candidate-data" in chunk or "SAI_CANDIDATE_TREE" in chunk:
            raise RuntimeError(f"{label} must not source candidate-data")
    print("SELFTEST PASS  tpr-f-publisher-disposition-not-candidate")

    executed.add("tpr-g-missing-review-yaml-no-artifact")
    if "NO_ARTIFACT" not in trusted_text:
        raise RuntimeError("missing review.yaml must BLOCKED/NO_ARTIFACT")
    if "if not yp.is_file()" not in trusted_text and "! -f /tmp/saul/review.yaml" not in trusted_text:
        raise RuntimeError("trusted workflow must handle missing review.yaml")
    print("SELFTEST PASS  tpr-g-missing-review-yaml-no-artifact")

    executed.add("tpr-h-ci-still-runs-auth-and-trust")
    if "verify-agent-authorization --self-test" not in audit:
        raise RuntimeError("agent-audit must keep verify-agent-authorization --self-test")
    if "verify-saul-workflow-trust --self-test" not in audit:
        raise RuntimeError("agent-audit must keep verify-saul-workflow-trust --self-test")
    print("SELFTEST PASS  tpr-h-ci-still-runs-auth-and-trust")
    return executed


if __name__ == "__main__":
    run_tpr_fixtures()
    print("sai_auth_tpr_test: OK")
