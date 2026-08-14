#!/usr/bin/env python3
"""Trusted-root provisioner refuses candidate HEAD unless independently confirmed."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile

import sai_auth as a
from sai_auth_trust_root import ARCHIVE_PATHS, provision


def _repo_with_scripts():
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "scripts" / "lib").mkdir(parents=True)
    (root / ".ai" / "_config").mkdir(parents=True)
    (root / ".ai" / "shared" / "schemas").mkdir(parents=True)
    (root / ".ai" / "shared" / "memory" / "decisions").mkdir(parents=True)
    (root / "scripts" / "invoke-saul-review").write_text("#!/bin/sh\necho ok\n")
    (root / "scripts" / "sai-dispatch-transition").write_text("#!/bin/sh\necho d\n")
    (root / "scripts" / "lib" / "sai_auth.py").write_text("x=1\n")
    (root / "CODEX.md").write_text("codex\n")
    (root / ".ai" / "_config" / "authorization.yaml").write_text("version: 1\n")
    (root / ".ai" / "shared" / "schemas" / "contract-review.schema.json").write_text("{}\n")
    (root / ".ai" / "shared" / "memory" / "decisions" / "0006-agent-authorization-loop.md").write_text("# 0006\n")
    a.git(root, "init")
    a.git(root, "config", "user.email", "t@example.com")
    a.git(root, "config", "user.name", "t")
    a.git(root, "add", "-A")
    a.git(root, "commit", "-m", "trusted")
    return tmp, root


def run_trust_root_fixtures():
    executed = set()
    tmp, root = _repo_with_scripts()
    try:
        head = a.head_sha(root)
        dest = root / "opt-trusted"
        executed.add("refuse-symbolic-head")
        r = provision(root, dest, "HEAD")
        if r["status"] != "REJECT" or r["reason"] != "SYMBOLIC_HEAD_REFUSED":
            raise RuntimeError(r)
        print("SELFTEST PASS  refuse-symbolic-head")

        executed.add("refuse-candidate-head")
        r = provision(root, dest, head)
        if r["status"] != "REJECT" or r["reason"] != "CANDIDATE_HEAD_REFUSED":
            raise RuntimeError(r)
        print("SELFTEST PASS  refuse-candidate-head")

        executed.add("confirm-trust-provisions")
        r = provision(root, dest, head, confirm_trust=True, actor="dezocode")
        if r["status"] != "PROVISIONED":
            raise RuntimeError(r)
        if not (dest / "scripts" / "invoke-saul-review").is_file():
            raise RuntimeError("missing invoke")
        man = json.loads((dest / "MANIFEST.json").read_text())
        if man["from_sha"] != head:
            raise RuntimeError(man)
        print("SELFTEST PASS  confirm-trust-provisions")

        executed.add("already-provisioned-refuses-overwrite")
        invoke = dest / "scripts" / "invoke-saul-review"
        pinned = invoke.read_text()
        r = provision(root, dest, head, confirm_trust=True, actor="attacker")
        if r["status"] != "ALREADY_PROVISIONED":
            raise RuntimeError(r)
        if invoke.read_text() != pinned:
            raise RuntimeError("overwrite of frozen root")
        print("SELFTEST PASS  already-provisioned-refuses-overwrite")
        executed.add("archive-paths-documented")
        if "scripts/invoke-saul-review" not in ARCHIVE_PATHS:
            raise RuntimeError(ARCHIVE_PATHS)
        print("SELFTEST PASS  archive-paths-documented")

        executed.add("candidate-mutation-does-not-change-root")
        invoke = dest / "scripts" / "invoke-saul-review"
        pinned = invoke.read_text()
        (root / "scripts" / "invoke-saul-review").write_text("#!/bin/sh\necho pwned\n")
        if invoke.read_text() != pinned:
            raise RuntimeError("trusted root mutated with candidate")
        if "pwned" not in (root / "scripts" / "invoke-saul-review").read_text():
            raise RuntimeError("candidate not mutated")
        print("SELFTEST PASS  candidate-mutation-does-not-change-root")

        executed.add("freeze-once-skips-symbolic")
        from sai_auth_trust_root import freeze_once
        r = freeze_once(root, "HEAD")
        if r["status"] != "SKIP":
            raise RuntimeError(r)
        print("SELFTEST PASS  freeze-once-skips-symbolic")
    finally:
        tmp.cleanup()
    return executed


if __name__ == "__main__":
    run_trust_root_fixtures()
    print("sai_auth_trust_root_test: OK")
