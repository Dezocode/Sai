#!/usr/bin/env python3
"""Hermetic Hostinger bootstrap guards. Never substitute candidate executables."""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

CANDIDATE_HEAD_MISMATCH = "CANDIDATE_HEAD_MISMATCH"
CANDIDATE_NOT_GIT = "CANDIDATE_NOT_GIT"
CANDIDATE_SHA_UNRESOLVED = "CANDIDATE_SHA_UNRESOLVED"
MUTABLE_REF = "MUTABLE_REF"
TRUSTED_REVIEWER_UNAVAILABLE = "TRUSTED_REVIEWER_UNAVAILABLE"

_SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")
_SYMBOLIC = frozenset({"HEAD", "@", "head", "Head"})


class BootstrapError(Exception):
    def __init__(self, code: str, **fields: str):
        self.code = code
        self.fields = fields
        extra = " ".join(f"{k}={v}" for k, v in fields.items() if v is not None)
        self.machine = f"{code} {extra}".strip() if extra else code
        super().__init__(self.machine)


def _git(tree: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(tree), *args],
        capture_output=True,
        text=True,
    )


def require_immutable_sha(head: str) -> str:
    """Accept only a full 40-char hex commit id. Never symbolic refs."""
    if head is None:
        raise BootstrapError(MUTABLE_REF, ref="empty")
    raw = str(head).strip()
    if not raw or raw in _SYMBOLIC or raw.startswith("refs/") or raw.startswith("refs"):
        raise BootstrapError(MUTABLE_REF, ref=raw or "empty")
    if raw.startswith("-") or "/" in raw or raw in ("main", "master", "HEAD"):
        raise BootstrapError(MUTABLE_REF, ref=raw)
    if not _SHA40.fullmatch(raw):
        raise BootstrapError(MUTABLE_REF, ref=raw)
    return raw.lower()


def assert_candidate_head(candidate: Path, expected_sha: str) -> str:
    """Fail closed unless candidate HEAD^{commit} equals the immutable --head."""
    cand = Path(candidate)
    if not cand.exists() or not cand.is_dir():
        raise BootstrapError(CANDIDATE_NOT_GIT, path=str(cand))
    inside = _git(cand, "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        raise BootstrapError(CANDIDATE_NOT_GIT, path=str(cand))
    expected = require_immutable_sha(expected_sha)
    actual_p = _git(cand, "rev-parse", "--verify", "HEAD^{commit}")
    if actual_p.returncode != 0:
        raise BootstrapError(CANDIDATE_NOT_GIT, path=str(cand))
    actual = actual_p.stdout.strip().lower()
    exp_p = _git(cand, "rev-parse", "--verify", f"{expected}^{{commit}}")
    if exp_p.returncode != 0:
        raise BootstrapError(CANDIDATE_SHA_UNRESOLVED, expected=expected)
    resolved = exp_p.stdout.strip().lower()
    if actual != resolved:
        raise BootstrapError(
            CANDIDATE_HEAD_MISMATCH, expected=resolved, actual=actual,
        )
    return actual


def _under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def require_trusted_executables(trusted: Path) -> tuple[Path, Path]:
    """Return realpaths of trusted invoke+attest. Never use candidate copies."""
    t = Path(trusted)
    if not t.exists() or not t.is_dir():
        raise BootstrapError(TRUSTED_REVIEWER_UNAVAILABLE, path=str(t))
    trusted_real = t.resolve()
    invoke = trusted_real / "scripts" / "invoke-saul-review"
    attest = trusted_real / "scripts" / "saul-attest"
    for p, name in ((invoke, "invoke-saul-review"), (attest, "saul-attest")):
        if not p.is_file() or not os.access(p, os.X_OK):
            raise BootstrapError(TRUSTED_REVIEWER_UNAVAILABLE, missing=name)
    invoke_real, attest_real = invoke.resolve(), attest.resolve()
    if not _under(invoke_real, trusted_real) or not _under(attest_real, trusted_real):
        raise BootstrapError(TRUSTED_REVIEWER_UNAVAILABLE, reason="escaped-trusted-tree")
    return invoke_real, attest_real
