#!/usr/bin/env python3
"""Reconstruct the latest active SAI primary from durable repo state."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import sai_auth as a
from sai_auth_saul_identity import (
    INVALID_READY_STATE_NONQUALIFYING_SAUL, merge_viable_saul,
)
from sai_auth_watchdog import HEARTBEAT_SECONDS_DEFAULT, active_primary_count, load_programs

TERMINAL = {"READY_FOR_HUMAN_REVIEW"}
NONTERMINAL = {
    "ACTIVE", "WAITING_WORKER", "WAITING_EXTERNAL", "SUSPENDED",
    "TOKEN_EXHAUSTED", "STALE", "LOST", "REPLACEMENT_REQUIRED", "BLOCKED_HUMAN",
}
FALSE_TERMINAL = {"DONE", "COMPLETE", "TERMINAL", "FULFILLED", "READY"}
PASS_ST = {"PASSED_BY_SAUL", "PASSED_BY_SAI", "PASSED"}
CONTRACT = "20260813-pr62-saul-smoke"


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def find_coordinator_states(root) -> list[tuple[Path, dict]]:
    runs = Path(root) / ".ai" / "runs"
    found = []
    if not runs.is_dir():
        return found
    for d in sorted(runs.iterdir()):
        p = d / "coordinator-state.json"
        if p.is_file():
            data = _load_json(p)
            if isinstance(data, dict) and data.get("primary_logical_id"):
                found.append((p, data))
    return found


def pick_active(states: list[tuple[Path, dict]]):
    """Prefer nonterminal liveness. Do not treat empty worker lists as done."""
    ranked = []
    for path, row in states:
        live = row.get("liveness") or ""
        if live in TERMINAL:
            continue
        rank = 0 if live in ("ACTIVE", "WAITING_WORKER", "WAITING_EXTERNAL") else 1
        ranked.append((rank, path, row))
    if not ranked:
        return None, None
    ranked.sort(key=lambda x: (x[0], str(x[1])))
    return ranked[0][1], ranked[0][2]


def load_ledger(root, contract_id):
    if not contract_id:
        return None
    path = Path(root) / ".ai" / "contracts" / contract_id / "requirements" / "ledger.yaml"
    return a.read_yaml(path)


def live_revision(root, contract_id, fallback=None):
    """Contract tree pointer beats stale coordinator-state.json."""
    if not contract_id:
        return fallback
    try:
        return a.current_revision(root, contract_id) or fallback
    except Exception:
        return fallback


def open_required_blockers(root, contract_id=CONTRACT) -> list:
    try:
        from sai_auth_blockers import load_ledger as load_bl
        data, _ = load_bl(root)
    except Exception:
        return []
    open_rows = []
    for row in data.get("blockers") or []:
        st = str(row.get("status") or "")
        if st.startswith("SUPERSEDED") or st in PASS_ST:
            continue
        open_rows.append(row)
    return open_rows


def latest_saul(root, contract_id, *, prefer_head=None, state_saul=None):
    """Prefer compact state / reviews for the live HEAD. Never hide a newer BLOCKED."""
    def _head(row):
        if not isinstance(row, dict):
            return None
        return row.get("head") or row.get("implementation_head")

    if isinstance(state_saul, dict) and prefer_head and _head(state_saul) == prefer_head:
        return state_saul
    reviews = Path(root) / ".ai" / "contracts" / (contract_id or "") / "reviews"
    matching = []
    if reviews.is_dir():
        for p in reviews.glob("saul-*.yaml"):
            data = a.read_yaml(p) or {}
            if prefer_head and _head(data) == prefer_head:
                matching.append((p.stat().st_mtime, data))
    if matching:
        matching.sort(key=lambda x: x[0], reverse=True)
        return matching[0][1]
    if isinstance(state_saul, dict) and (not prefer_head or _head(state_saul) == prefer_head):
        return state_saul
    return None


def exit_satisfied(state: dict, head: str, saul, sai_disp, *, root=None,
                   pub_pem=None) -> bool:
    """READY_FOR_HUMAN_REVIEW requires merge-viable attested Saul, not YAML claims."""
    if not saul:
        return False
    rev = live_revision(root, state.get("contract_id"), state.get("contract_revision")) if root else state.get("contract_revision")
    viable, _ = merge_viable_saul(saul, head, rev, pub_pem=pub_pem, root=root)
    if not viable:
        return False
    saul_head = saul.get("head") or saul.get("implementation_head") or saul.get("implementation_sha")
    sai_ok = str(sai_disp or "").upper() == "APPROVE"
    if not (sai_ok and saul_head == head and not state.get("open_findings_digest")):
        return False
    if root and open_required_blockers(root, state.get("contract_id") or CONTRACT):
        return False
    return True


def _claimed_false_terminal(state: dict, compact: dict) -> bool:
    for src in (state, compact):
        if not isinstance(src, dict):
            continue
        for key in ("liveness", "expected_next_state", "program_status", "status"):
            val = str(src.get(key) or "")
            if val in FALSE_TERMINAL:
                return True
    return False


def enforced_rejects(root, compact=None, state=None) -> list:
    """Repo-enforced Decision 0009 rejects. Never mint READY."""
    compact = compact or {}
    state = state or {}
    reasons = []
    ready = bool(compact.get("exit_predicate_satisfied"))
    live = str(compact.get("liveness") or state.get("liveness") or "")
    if not ready and (_claimed_false_terminal(state, compact) or live in FALSE_TERMINAL):
        reasons.append("ready_false_and_program_terminal")
    open_b = open_required_blockers(root, compact.get("contract_id") or CONTRACT)
    if open_b and (ready or live in TERMINAL or live in FALSE_TERMINAL):
        reasons.append("required_blocker_and_program_terminal")
    return reasons


def reconstruct(root) -> dict:
    head = a.head_sha(root) or ""
    branch = a.current_branch(root)
    states = find_coordinator_states(root)
    path, state = pick_active(states)
    if not state:
        claimed = [(p, r) for p, r in states
                   if (r.get("liveness") or "") == "READY_FOR_HUMAN_REVIEW"]
        if claimed:
            path, state = claimed[0]
        else:
            return {
                "status": "NO_ACTIVE_PRIMARY",
                "current_head": head,
                "branch": branch,
                "playbook": "none",
                "do_not_redo": True,
            }
    live_head = head or state.get("current_head")
    contract_id = state.get("contract_id")
    rev = live_revision(root, contract_id, state.get("contract_revision"))
    ledger = load_ledger(root, contract_id)
    saul = latest_saul(
        root, contract_id, prefer_head=live_head, state_saul=state.get("saul")
    )
    programs, _ = load_programs(root)
    workers = state.get("workers") or state.get("active_workers") or []
    liveness = state.get("liveness")
    viable, _ = merge_viable_saul(
        saul or {}, live_head, rev, root=root,
    )
    invalid_ready = liveness == "READY_FOR_HUMAN_REVIEW" and not viable
    if invalid_ready:
        liveness = "WAITING_EXTERNAL"
    predicate_false = not exit_satisfied(
        dict(state, contract_revision=rev), live_head, saul,
        state.get("sai_disposition"), root=root,
    )
    if liveness in FALSE_TERMINAL and predicate_false:
        liveness = "ACTIVE"
        invalid_ready = True
    playbook = "session-pickup"
    if liveness == "WAITING_WORKER":
        playbook = "orchestrate-drain-workers"
    elif liveness == "WAITING_EXTERNAL":
        playbook = "orchestrate-waiting-external"
    elif liveness == "ACTIVE":
        playbook = "poteto-continue-frontier"
    if state.get("physical_runtime_continuity") is False and liveness in (
        "ACTIVE", "REPLACEMENT_REQUIRED",
    ):
        playbook = "poteto-continue-frontier"
    compact = {
        "status": "RECONSTRUCTED",
        "primary_logical_id": state.get("primary_logical_id"),
        "last_physical_bcId": state.get("physical_runtime_id"),
        "repo": state.get("repo"),
        "primary_pr": state.get("pr"),
        "branch": branch or state.get("branch"),
        "head_sha": live_head,
        "state_file_head": state.get("current_head"),
        "head_refreshed": live_head != state.get("current_head"),
        "contract_id": contract_id,
        "contract_revision": rev,
        "requirement_ledger": {
            "path": f".ai/contracts/{contract_id}/requirements/ledger.yaml" if contract_id else None,
            "count": len((ledger or {}).get("requirements") or []) if ledger else 0,
            "ids": [r.get("requirement_id") for r in ((ledger or {}).get("requirements") or [])],
        },
        "cora_admin_state": state.get("cora_admin_state") or "see-revision",
        "contractor_state": state.get("contractor_state") or workers,
        "worker_tree": workers,
        "latest_saul": saul,
        "latest_sai": {
            "disposition": state.get("sai_disposition") or "pending",
            "head": state.get("sai_reviewed_sha"),
        },
        "ci": state.get("ci") or "unknown",
        "event_inbox": state.get("pending_events") or [],
        "expected_next_state": state.get("expected_next_state"),
        "last_material_transition": state.get("last_material_transition"),
        "exit_predicate": state.get("exit_predicate"),
        "exit_predicate_satisfied": (
            False if invalid_ready else (not predicate_false and liveness in TERMINAL)
        ),
        "liveness": liveness,
        "physical_runtime_continuity": state.get("physical_runtime_continuity"),
        "logical_runtime_continuity": True,
        "heartbeat_seconds": state.get("heartbeat_seconds") or HEARTBEAT_SECONDS_DEFAULT,
        "active_primary_programs": active_primary_count(programs.get("programs") or []),
        "coordinator_state_path": str(path) if path else None,
        "playbook": playbook,
        "do_not_redo": True,
        "empty_todo_is_not_exit": True,
        "continue": True if invalid_ready else (predicate_false or liveness not in TERMINAL),
        "reassess_blockers": playbook == "poteto-continue-frontier",
        "physical_runtime_replacement_nonterminal": state.get("physical_runtime_continuity") is False,
    }
    if invalid_ready:
        compact["invalid_ready_state"] = INVALID_READY_STATE_NONQUALIFYING_SAUL
    rejects = enforced_rejects(root, compact, state)
    if rejects:
        compact["enforced_rejects"] = rejects
        compact["continue"] = True
        compact["exit_predicate_satisfied"] = False
        if compact.get("liveness") in TERMINAL or compact.get("liveness") in FALSE_TERMINAL:
            compact["liveness"] = "ACTIVE"
            compact["playbook"] = "poteto-continue-frontier"
    return compact


def cmd(argv=None):
    p = argparse.ArgumentParser(prog="sai-resume")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args(argv)
    if args.self_test:
        from sai_auth_resume_test import run_resume_fixtures
        n = run_resume_fixtures()
        print(f"sai-resume self-test: {len(n)} fixtures executed")
        return 0
    compact = reconstruct(a.toplevel())
    print(json.dumps(compact, indent=2, default=str))
    return 0 if compact.get("status") in ("RECONSTRUCTED", "NO_ACTIVE_PRIMARY") else 1


if __name__ == "__main__":
    raise SystemExit(cmd())
