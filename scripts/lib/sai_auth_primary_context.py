#!/usr/bin/env python3
"""Resolve unique current Primary from live git + primary-programs.yaml.

NO_UNDECLARED_OPERATIONAL_CONTEXT: no hardcoded PR/contract/branch/SHA
defaults in reusable production code. runtime_intelligence does not count.
Never silently select the first of multiple active primary_implementation rows.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sai_auth as a  # noqa: E402
from sai_auth_watchdog import PRIMARY_KIND, load_programs  # noqa: E402

NO_PRIMARY_CONTEXT = "NO_PRIMARY_CONTEXT"
AMBIGUOUS_PRIMARY_CONTEXT = "AMBIGUOUS_PRIMARY_CONTEXT"
NO_UNDECLARED_OPERATIONAL_CONTEXT = "NO_UNDECLARED_OPERATIONAL_CONTEXT"
PROGRAMS_REL = ".ai/_config/primary-programs.yaml"
LEDGER_REL = "requirements/ledger.yaml"
_GH_REMOTE = re.compile(
    r"(?:github\.com[:/]|git@github\.com:)(?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
    re.IGNORECASE,
)


def active_primary_implementation(programs: list) -> list[dict]:
    """kind=primary_implementation AND status=active. RI/stacked do not count."""
    out = []
    for row in programs or []:
        if not isinstance(row, dict):
            continue
        if (row.get("status") or "").lower() != "active":
            continue
        if (row.get("kind") or "") != PRIMARY_KIND:
            continue
        out.append(row)
    return out


def select_primary_program(programs: list, logical_id=None) -> tuple[dict | None, str | None]:
    active = active_primary_implementation(programs)
    if logical_id:
        match = [p for p in active if p.get("logical_id") == logical_id]
        if len(match) != 1:
            return None, NO_PRIMARY_CONTEXT
        return dict(match[0]), None
    if not active:
        return None, NO_PRIMARY_CONTEXT
    if len(active) > 1:
        return None, AMBIGUOUS_PRIMARY_CONTEXT
    return dict(active[0]), None


def _remote_repository(root) -> str | None:
    p = a.git(root, "remote", "get-url", "origin")
    url = (p.stdout or "").strip()
    if not url:
        return None
    m = _GH_REMOTE.search(url.replace("ssh://git@", "git@"))
    if m:
        return f"{m.group('owner')}/{m.group('repo')}"
    return None


def _live_base_sha(root, program: dict) -> str | None:
    """Resolve merge-base from live git. Program `base` is a ref name, never a SHA literal default."""
    refs = []
    base_ref = program.get("base")
    if base_ref:
        refs.append(str(base_ref))
    refs.extend(("origin/main", "main"))
    head = a.head_sha(root)
    if not head:
        return None
    for ref in refs:
        parsed = a.git(root, "rev-parse", "--verify", ref)
        if parsed.returncode != 0:
            continue
        mb = a.git(root, "merge-base", "HEAD", ref)
        if mb.returncode == 0 and mb.stdout.strip():
            return mb.stdout.strip()
    return None


def _contract_revision(root, contract_id):
    if not contract_id:
        return None
    ptr = a.load_pointer(root, contract_id) or {}
    return ptr.get("current_revision")


def _principal(root, contract_id, program: dict):
    if program.get("principal"):
        return program.get("principal")
    if not contract_id:
        return None
    ptr = a.load_pointer(root, contract_id) or {}
    return ptr.get("principal")


def _event_namespace(logical_id) -> str:
    return f"sai.primary.{logical_id}" if logical_id else "sai.primary"


def load_primary_context(root, *, logical_id=None) -> tuple[dict | None, str | None]:
    """Live git + yaml. Isolated dict per call (no shared mutable state)."""
    data, _path = load_programs(root, rel=PROGRAMS_REL)
    programs = data.get("programs") or []
    program, err = select_primary_program(programs, logical_id)
    if err:
        return None, err
    head = a.head_sha(root)
    branch = a.current_branch(root)
    repo = _remote_repository(root)
    if not head or not branch or branch in (None, ""):
        return None, NO_UNDECLARED_OPERATIONAL_CONTEXT
    if not repo:
        return None, NO_UNDECLARED_OPERATIONAL_CONTEXT
    cid = program.get("contract_id")
    if not cid:
        return None, NO_UNDECLARED_OPERATIONAL_CONTEXT
    base = _live_base_sha(root, program)
    if not base:
        return None, NO_UNDECLARED_OPERATIONAL_CONTEXT
    rev = _contract_revision(root, cid)
    ledger = str(a.contract_dir(root, cid) / LEDGER_REL)
    ctx = {
        "logical_id": program.get("logical_id"),
        "kind": PRIMARY_KIND,
        "repository": repo,
        "pr": program.get("pr"),
        "branch": branch,
        "head_sha": head,
        "base_sha": base,
        "contract_id": cid,
        "contract_revision": rev,
        "blocker_ledger": ledger,
        "event_namespace": _event_namespace(program.get("logical_id")),
        "principal": _principal(root, cid, program),
        "yaml_branch": program.get("branch"),
        "status": program.get("status"),
    }
    return dict(ctx), None


def cmd(argv=None):
    p = argparse.ArgumentParser(prog="sai-primary-context")
    p.add_argument("--logical-id", default=None)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args(argv)
    if args.self_test:
        from sai_auth_primary_context_test import run_primary_fixtures
        n = run_primary_fixtures()
        print(f"primary-context self-test: {len(n)} fixtures executed")
        return 0
    ctx, err = load_primary_context(a.toplevel(), logical_id=args.logical_id)
    if err:
        print(err, file=sys.stderr)
        return 1
    print(json.dumps(ctx, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(cmd())
