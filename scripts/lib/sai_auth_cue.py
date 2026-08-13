#!/usr/bin/env python3
"""Machine-actionable first-write identity cue. Deterministic; no model."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sai_auth as a  # noqa: E402
import sai_auth_flow as flow  # noqa: E402


def existing_assignment(root, branch):
    hint = flow.contractor_assignment(root, branch=branch)
    if not hint or not hint.get("contract_id"):
        return None
    rev = a.load_revision(root, hint["contract_id"], hint.get("revision") or "v1") or {}
    hint["allowed_paths"] = rev.get("allowed_paths") or []
    hint["denied_paths"] = rev.get("denied_paths") or []
    hint["task_id"] = hint.get("task_id") or rev.get("requested_task")
    return hint


def paths_in_assignment(assignment, paths) -> bool:
    if not assignment:
        return False
    allowed = assignment.get("allowed_paths") or []
    denied = list(assignment.get("denied_paths") or [])
    for p in paths or []:
        if not a.path_allowed(p, allowed, denied):
            return False
    return True


def build_cue(root, paths, *, session=None, branch=None, task_id=None):
    branch = branch or a.current_branch(root)
    session = session or {}
    assignment = existing_assignment(root, branch)
    identity = session.get("agent_id") or os.environ.get("SAI_AGENT_ID") or "unknown"
    task_id = (
        task_id
        or session.get("task_id")
        or os.environ.get("SAI_TASK_ID")
        or (assignment or {}).get("task_id")
        or ""
    )
    next_action = "CORA_ADMISSION"
    reason = "unknown_or_unauthorized_actor"
    if assignment and assignment.get("agent_id"):
        allowed = assignment.get("allowed_paths") or []
        if allowed and paths and not paths_in_assignment(assignment, paths):
            next_action = "HUMAN_AUTHORITY_REQUIRED"
            reason = "requested_paths_exceed_existing_assignment"
        else:
            next_action = "RESUME_CONTRACTOR"
            reason = "existing_contractor_assignment"
    cue = {
        "status": "SAI_IDENTITY_REQUIRED",
        "reason": reason,
        "task_id": task_id or "00000000-0000-unknown-identity",
        "repository": os.environ.get("SAI_REPOSITORY") or os.environ.get("GITHUB_REPOSITORY") or "Dezocode/Sai",
        "branch": branch,
        "current_identity": identity or "unknown",
        "requested_scope": list(paths or []),
        "next_action": next_action,
        "contract_hint": assignment,
        "allowed_read_only": True,
        "artifact_pointer": ".git/sai-identity-required.json",
        "orchestration_pointer": ".cursor/rules/sai-orchestration.mdc",
    }
    if next_action == "RESUME_CONTRACTOR" and assignment:
        cue["contract_id"] = assignment.get("contract_id")
        cue["revision"] = assignment.get("revision")
        cue["agent_id"] = assignment.get("agent_id")
    return cue


def emit_cue(payload, *, stream=None):
    stream = stream or sys.stderr
    print(json.dumps(payload, sort_keys=True), file=stream, flush=True)
    print(f"SAI_CUE {payload.get('next_action')}", file=stream, flush=True)
    return payload


def cmd(argv=None):
    p = argparse.ArgumentParser(prog="sai-identity-required")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--path", action="append", default=[])
    args = p.parse_args(argv)
    if args.self_test:
        from sai_auth_cue_test import run_cue_fixtures
        n = run_cue_fixtures()
        print(f"sai-identity-required self-test: {n} fixtures executed")
        return 0
    root = a.toplevel()
    payload = build_cue(root, args.path)
    emit_cue(payload, stream=sys.stdout)
    return 1


if __name__ == "__main__":
    raise SystemExit(cmd())
