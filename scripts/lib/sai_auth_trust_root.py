#!/usr/bin/env python3
"""Provision SAI_TRUSTED_REVIEWER_ROOT from an explicit trusted SHA. Never HEAD."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import sai_auth as a

DEFAULT_DEST = "/opt/sai/trusted-reviewer"
ARCHIVE_PATHS = (
    "scripts/invoke-saul-review",
    "scripts/sai-dispatch-transition",
    "scripts/lib",
    "CODEX.md",
    ".ai/_config/authorization.yaml",
    ".ai/shared/schemas/contract-review.schema.json",
    ".ai/shared/memory/decisions/0006-agent-authorization-loop.md",
)


def _rev_parse(root, rev):
    p = a.git(root, "rev-parse", rev)
    if p.returncode != 0:
        raise RuntimeError(p.stderr or p.stdout or f"unknown rev {rev}")
    return p.stdout.strip()


def provision(root, dest, from_sha, *, confirm_trust=False, actor="unknown"):
    if not from_sha or from_sha in ("HEAD", "head", "@"):
        return {"status": "REJECT", "reason": "SYMBOLIC_HEAD_REFUSED"}
    resolved = _rev_parse(root, from_sha)
    head = a.head_sha(root)
    on_main = False
    main = a.git(root, "rev-parse", "origin/main")
    if main.returncode == 0 and main.stdout.strip() == resolved:
        on_main = True
    if resolved == head and not confirm_trust and not on_main:
        return {
            "status": "REJECT",
            "reason": "CANDIDATE_HEAD_REFUSED",
            "from_sha": resolved,
            "hint": "pass --confirm-trust only after a human independently trusts this SHA",
        }
    dest_path = Path(dest)
    dest_path.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        cmd = ["git", "-C", str(root), "archive", resolved, *ARCHIVE_PATHS]
        proc = subprocess.run(cmd, capture_output=True)
        if proc.returncode != 0:
            return {
                "status": "REJECT",
                "reason": "ARCHIVE_FAILED",
                "detail": (proc.stderr or proc.stdout).decode("utf-8", "replace")[:400],
            }
        subprocess.run(["tar", "-x", "-C", tmp], input=proc.stdout, check=True)
        src = Path(tmp)
        if not (src / "scripts" / "invoke-saul-review").is_file():
            return {"status": "REJECT", "reason": "MISSING_INVOKE_SAUL"}
        for child in src.iterdir():
            target = dest_path / child.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            shutil.move(str(child), str(target))
        invoke = dest_path / "scripts" / "invoke-saul-review"
        invoke.chmod(invoke.stat().st_mode | 0o111)
    manifest = {
        "status": "PROVISIONED",
        "from_sha": resolved,
        "dest": str(dest_path),
        "actor": actor,
        "on_main": on_main,
        "confirm_trust": confirm_trust,
        "trust_mode": "runner-image",
        "timestamp": a.utcnow(),
    }
    (dest_path / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def cmd(argv=None):
    p = argparse.ArgumentParser(prog="provision-trusted-reviewer-root")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--from-sha", default=None)
    p.add_argument("--dest", default=os.environ.get("SAI_TRUSTED_REVIEWER_ROOT") or DEFAULT_DEST)
    p.add_argument("--confirm-trust", action="store_true")
    p.add_argument("--actor", default=os.environ.get("GITHUB_ACTOR") or "unknown")
    args = p.parse_args(argv)
    if args.self_test:
        from sai_auth_trust_root_test import run_trust_root_fixtures
        n = run_trust_root_fixtures()
        print(f"provision-trusted-reviewer-root self-test: {len(n)} fixtures executed")
        return 0
    if not args.from_sha:
        print(json.dumps({"status": "REJECT", "reason": "FROM_SHA_REQUIRED"}))
        return 2
    result = provision(a.toplevel(), args.dest, args.from_sha,
                       confirm_trust=args.confirm_trust, actor=args.actor)
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") == "PROVISIONED" else 1


if __name__ == "__main__":
    raise SystemExit(cmd())
