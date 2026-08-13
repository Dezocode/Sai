#!/usr/bin/env python3
"""Unknown-identity write gate emits SAI_IDENTITY_REQUIRED and does not mutate."""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sai_auth as a  # noqa: E402
from sai_auth_verify import verify_pre_commit  # noqa: E402

POLICY = """
version: 1
enforcement: {mode: fail-closed, skip_commits_missing_policy: true, trust_session: false}
activation: {mode: lazy-first-write}
bootstrap:
  standing: true
  task_ids: []
  agent_trailers: [cursor-cloud]
officers: {}
path_classes: {}
"""


def _git(cwd, *args, check=True):
    p = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(p.stderr or p.stdout)
    return p


def _fingerprint(root: Path):
    files = []
    for p in sorted(root.rglob("*")):
        if ".git" in p.parts or not p.is_file():
            continue
        files.append((str(p.relative_to(root)), p.read_bytes()))
    index = _git(root, "diff", "--cached").stdout
    work = _git(root, "diff").stdout
    return files, index, work


def _init_repo(path: Path, branch="feat/cue-unknown"):
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-b", branch], cwd=path, capture_output=True, check=True)
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test Agent")
    (path / ".ai/_config").mkdir(parents=True, exist_ok=True)
    a.write_yaml(path / ".ai/_config/authorization.yaml", a.load_yaml(POLICY))
    _git(path, "add", "-A")
    _git(path, "commit", "-m", "policy\n\nTask-ID: 20260813-0000-cue-test\nAgent: cursor-cloud\n")
    return path


def _stage_payload(path: Path, rel="scripts/probe.sh", content="#!/bin/sh\necho probe\n"):
    fp = path / rel
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(content, encoding="utf-8")
    _git(path, "add", rel)
    return rel, content


def _run_pre_commit(root: Path):
    out, err = io.StringIO(), io.StringIO()
    env_drop = {}
    for key in ("SAI_TASK_ID", "SAI_AGENT_ID", "SAI_REPOSITORY", "GITHUB_REPOSITORY", "GITHUB_HEAD_REF"):
        if key in os.environ:
            env_drop[key] = os.environ.pop(key)
    try:
        with redirect_stdout(out), redirect_stderr(err):
            rc = verify_pre_commit(root)
    finally:
        os.environ.update(env_drop)
    return rc, out.getvalue(), err.getvalue()


def _parse_cue(stdout: str):
    lines = [ln for ln in stdout.splitlines() if ln.strip()]
    cue_line = next((ln for ln in lines if ln.startswith("{")), None)
    token = next((ln for ln in lines if ln.startswith("SAI_CUE ")), None)
    if not cue_line:
        raise AssertionError(f"missing JSON cue in stdout: {stdout!r}")
    return json.loads(cue_line), token, lines


def test_unknown_identity_cora_admission():
    with tempfile.TemporaryDirectory() as tmp:
        root = _init_repo(Path(tmp) / "unknown")
        rel, content = _stage_payload(root)
        before = _fingerprint(root)
        rc, stdout, stderr = _run_pre_commit(root)
        after = _fingerprint(root)
        cue, token, _ = _parse_cue(stdout)
        assert rc == 1, rc
        assert cue["status"] == "SAI_IDENTITY_REQUIRED"
        assert cue["reason"] == "unknown_or_unauthorized_actor"
        assert cue["next_action"] == "CORA_ADMISSION"
        assert cue["current_identity"] == "unknown"
        assert cue["allowed_read_only"] is True
        assert rel in cue["requested_scope"]
        assert cue["contract_hint"] is None
        assert token == "SAI_CUE CORA_ADMISSION"
        assert "FAIL no assumed identity" in stderr
        assert before == after, "write gate mutated the worktree"
        assert (root / rel).read_text(encoding="utf-8") == content
        artifact = root / ".git" / "sai-identity-required.json"
        assert artifact.is_file()
        disk = json.loads(artifact.read_text(encoding="utf-8"))
        assert disk["next_action"] == "CORA_ADMISSION"
        print("SELFTEST PASS  cue-unknown-cora-admission")


def test_existing_contract_resume_contractor():
    with tempfile.TemporaryDirectory() as tmp:
        branch = "feat/cue-resume"
        root = _init_repo(Path(tmp) / "resume", branch=branch)
        cid = "20260813-cue-fastpath"
        a.write_json(a.pointer_path(root, cid), {
            "contract_id": cid,
            "current_revision": "v1",
            "assigned_contractors": [
                {"agent_id": "ctr-code-cue1", "status": "provisional", "branch": branch},
            ],
        })
        a.save_revision(root, cid, {
            "contract_id": cid, "revision": 1, "revision_label": "v1",
            "agent_id": "ctr-code-cue1",
            "allowed_branch_or_worktree": branch,
        })
        rel, content = _stage_payload(root)
        before = _fingerprint(root)
        rc, stdout, stderr = _run_pre_commit(root)
        after = _fingerprint(root)
        cue, token, _ = _parse_cue(stdout)
        assert rc == 1, rc
        assert cue["next_action"] == "RESUME_CONTRACTOR"
        assert cue["contract_id"] == cid
        assert cue["revision"] == "v1"
        assert cue["agent_id"] == "ctr-code-cue1"
        assert cue["contract_hint"]["agent_id"] == "ctr-code-cue1"
        assert token == "SAI_CUE RESUME_CONTRACTOR"
        assert before == after, "write gate mutated the worktree"
        assert (root / rel).read_text(encoding="utf-8") == content
        print("SELFTEST PASS  cue-existing-contract-resume")


def run_cue_fixtures():
    test_unknown_identity_cora_admission()
    test_existing_contract_resume_contractor()
    return {"cue-unknown-cora-admission", "cue-existing-contract-resume"}


def main():
    run_cue_fixtures()
    print("sai_auth_cue_test: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
