#!/usr/bin/env python3
"""Human-principal SHA allowlist: skip Agent trailer only when all gates hold."""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

import sai_auth as a
from sai_auth_verify import verify_commit

EMAIL = "158269149+Dezocode@users.noreply.github.com"
POLICY = ".ai/_config/authorization.yaml"
CFG = """
version: 1
enforcement: {mode: fail-closed, skip_commits_missing_policy: true, trust_session: false}
bootstrap: {enabled: false, standing: true, task_ids: [], agent_trailers: []}
officers: {}
path_classes: {}
audit:
  preserve_human_principal_commits:
    principal_emails:
      - "158269149+Dezocode@users.noreply.github.com"
    commits: []
"""


def _git(cwd, *args, check=True, env=None):
    p = subprocess.run(
        ["git", "-C", str(cwd), *args], capture_output=True, text=True, env=env,
    )
    if check and p.returncode != 0:
        raise RuntimeError(p.stderr or p.stdout)
    return p


def _init(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-b", "feat/human"], cwd=path, capture_output=True, check=True)
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test Agent")
    (path / ".ai/_config").mkdir(parents=True, exist_ok=True)
    a.write_yaml(path / POLICY, a.load_yaml(CFG))
    _git(path, "add", "-A")
    _git(path, "commit", "-m", "policy\n\nTask-ID: 20260813-0000-human-test\nAgent: cursor-cloud\n")
    return path


def _commit_as(path: Path, rel, content, msg, email, trailers=None):
    fp = path / rel
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(content, encoding="utf-8")
    _git(path, "add", rel)
    body = msg
    if trailers:
        body += "\n\n" + "\n".join(f"{k}: {v}" for k, v in trailers.items()) + "\n"
    env = os.environ.copy()
    env["GIT_AUTHOR_EMAIL"] = email
    env["GIT_COMMITTER_EMAIL"] = email
    env["GIT_AUTHOR_NAME"] = "Dezocode"
    env["GIT_COMMITTER_NAME"] = "Dezocode"
    _git(path, "commit", "-m", body, env=env)
    return _git(path, "rev-parse", "HEAD").stdout.strip()


def _allow(path: Path, shas, emails=None):
    cfg = a.load_config(path)
    audit = cfg.setdefault("audit", {})
    audit["preserve_human_principal_commits"] = {
        "principal_emails": list(emails if emails is not None else [EMAIL]),
        "commits": [{"sha": s} for s in shas],
    }
    a.write_yaml(path / POLICY, cfg)
    return a.load_config(path)


def _expect(name, cond, detail=None):
    if not cond:
        raise RuntimeError(f"{name}: {detail}")
    print(f"SELFTEST PASS  {name}")


def run_human_commit_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        d = _init(tmp / "listed-good")
        sha = _commit_as(d, "docs/spec.md", "spec\n", "human spec", EMAIL)
        cfg = _allow(d, [sha])
        tr = a.parse_trailers(a.commit_message(d, sha))
        skip = a.human_principal_identity_skip(d, cfg, sha, tr)
        fails = verify_commit(d, cfg, sha)
        _expect("human-principal-listed-good", skip is True and fails == [], (skip, fails))
        executed.add("human-principal-listed-good")

        d = _init(tmp / "wrong-author")
        sha = _commit_as(d, "docs/spec.md", "spec\n", "human spec", "other@example.com")
        cfg = _allow(d, [sha])
        tr = a.parse_trailers(a.commit_message(d, sha))
        skip = a.human_principal_identity_skip(d, cfg, sha, tr)
        fails = verify_commit(d, cfg, sha)
        _expect(
            "human-principal-wrong-author-bad",
            skip is False and bool(fails),
            (skip, fails),
        )
        executed.add("human-principal-wrong-author-bad")

        d = _init(tmp / "unknown-sha")
        sha = _commit_as(d, "docs/spec.md", "spec\n", "human spec", EMAIL)
        other = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        cfg = _allow(d, [other])
        tr = a.parse_trailers(a.commit_message(d, sha))
        skip = a.human_principal_identity_skip(d, cfg, sha, tr)
        fails = verify_commit(d, cfg, sha)
        _expect(
            "human-principal-unknown-sha-bad",
            skip is False and bool(fails),
            (skip, fails),
        )
        executed.add("human-principal-unknown-sha-bad")

        d = _init(tmp / "agent-present")
        sha = _commit_as(
            d, "docs/spec.md", "spec\n", "agent authored", EMAIL,
            trailers={"Task-ID": "20260813-0000-human-test", "Agent": "ctr-code-forged"},
        )
        cfg = _allow(d, [sha])
        tr = a.parse_trailers(a.commit_message(d, sha))
        skip = a.human_principal_identity_skip(d, cfg, sha, tr)
        fails = verify_commit(d, cfg, sha)
        _expect(
            "agent-trailer-not-skipped-bad",
            skip is False and bool(fails) and tr.get("Agent") == "ctr-code-forged",
            (skip, fails, tr),
        )
        executed.add("agent-trailer-not-skipped-bad")

    return executed


if __name__ == "__main__":
    run_human_commit_fixtures()
    print("sai_auth_human_commit_test: OK")
