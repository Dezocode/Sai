#!/usr/bin/env python3
"""Non-model primary wait. Chunked sleep; early wake on digest change."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

import sai_auth as a

DEFAULT_SECONDS = 900
BRANCH = "cursor/codebase-health-90ba"


def _run(cmd, timeout=20):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if p.returncode != 0:
        return ""
    return (p.stdout or "").strip()[:2000]


def remote_snapshot() -> str:
    """Cheap GitHub/git inspection. No model. Fail-open if gh/git unavailable."""
    return "\n".join(filter(None, [
        _run(["git", "ls-remote", "origin", f"refs/heads/{BRANCH}"]),
        _run([
            "gh", "run", "list", "--workflow=saul-review.yml",
            "--branch", BRANCH, "--limit", "1",
            "--json", "databaseId,conclusion,headSha,status",
        ]),
        _run([
            "gh", "run", "list", "--workflow=trusted-reviewer-provision.yml",
            "--limit", "1",
            "--json", "databaseId,conclusion,headSha,status,event",
        ], timeout=30),
        _run([
            "gh", "pr", "view", "62", "--json", "headRefOid,isDraft",
        ]),
    ]))


def cheap_digest(root, *, include_remote=True) -> str:
    head = a.head_sha(root) or ""
    parts = [head]
    if include_remote:
        parts.append(remote_snapshot())
    for rel in (
        ".ai/runs/20260813-2015-pr62-queue-ceo/coordinator-state.json",
        ".ai/contracts/20260813-pr62-saul-smoke/blockers/ledger.yaml",
        ".git/sai-last-material-event.json",
    ):
        p = Path(root) / rel
        if p.is_file():
            parts.append(p.read_text(encoding="utf-8")[:4000])
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()[:16]


def wait_loop(root, seconds, *, chunk=30, digest=None, include_remote=True):
    """Sleep up to `seconds`. Return early if cheap_digest changes. No model."""
    start = time.time()
    baseline = digest or cheap_digest(root, include_remote=include_remote)
    remaining = max(0.0, float(seconds))
    chunk = max(0.05, float(chunk))
    woke_early = False
    while remaining > 0:
        step = min(chunk, remaining)
        time.sleep(step)
        remaining -= step
        now = cheap_digest(root, include_remote=include_remote)
        if now != baseline:
            woke_early = True
            break
    return {
        "waited_seconds": round(time.time() - start, 3),
        "requested_seconds": seconds,
        "woke_early": woke_early,
        "model_invoked": False,
        "baseline_digest": baseline,
        "end_digest": cheap_digest(root, include_remote=include_remote),
        "same_process": True,
        "include_remote": include_remote,
    }


def cmd(argv=None):
    p = argparse.ArgumentParser(prog="sai-wait")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--seconds", type=int, default=DEFAULT_SECONDS)
    p.add_argument("--chunk", type=int, default=30)
    args = p.parse_args(argv)
    if args.self_test:
        from sai_auth_wait_test import run_wait_fixtures
        n = run_wait_fixtures()
        print(f"sai-wait self-test: {len(n)} fixtures executed")
        return 0
    result = wait_loop(a.toplevel(), args.seconds, chunk=args.chunk)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(cmd())
