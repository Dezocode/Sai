#!/usr/bin/env python3
"""Reconstruct the latest active SAI primary from durable repo state."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import sai_auth as a
from sai_auth_watchdog import HEARTBEAT_SECONDS_DEFAULT, active_primary_count, load_programs

TERMINAL = {"READY_FOR_HUMAN_REVIEW"}
NONTERMINAL = {
    "ACTIVE", "WAITING_WORKER", "WAITING_EXTERNAL", "SUSPENDED",
    "TOKEN_EXHAUSTED", "STALE", "LOST", "REPLACEMENT_REQUIRED", "BLOCKED_HUMAN",
}


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
    if isinstance(state_saul, dict):
        return state_saul
    return None


def exit_satisfied(state: dict, head: str, saul, sai_disp) -> bool:
    """READY_FOR_HUMAN_REVIEW is mechanical. Empty todos are not enough."""
    if (state.get("liveness") or "") == "READY_FOR_HUMAN_REVIEW":
        return False  # still require evidence fields below
    saul_ok = bool(saul) and str(saul.get("disposition") or "").upper() == "APPROVE"
    saul_head = (saul or {}).get("head") or (saul or {}).get("implementation_sha")
    sai_ok = str(sai_disp or "").upper() == "APPROVE"
    return bool(
        saul_ok and sai_ok and saul_head == head
        and not state.get("open_findings_digest")
    )


def reconstruct(root) -> dict:
    head = a.head_sha(root) or ""
    branch = a.current_branch(root)
    path, state = pick_active(find_coordinator_states(root))
    if not state:
        return {
            "status": "NO_ACTIVE_PRIMARY",
            "current_head": head,
            "branch": branch,
            "playbook": "none",
            "do_not_redo": True,
        }
    # Durable JSON may lag git. Pickup uses live HEAD, never a stale snapshot SHA.
    live_head = head or state.get("current_head")
    contract_id = state.get("contract_id")
    ledger = load_ledger(root, contract_id)
    saul = latest_saul(
        root, contract_id, prefer_head=live_head, state_saul=state.get("saul")
    )
    programs, _ = load_programs(root)
    workers = state.get("workers") or state.get("active_workers") or []
    liveness = state.get("liveness")
    predicate_false = not exit_satisfied(state, live_head, saul, state.get("sai_disposition"))
    playbook = "session-pickup"
    if liveness == "WAITING_WORKER":
        playbook = "orchestrate-drain-workers"
    elif liveness == "WAITING_EXTERNAL":
        playbook = "orchestrate-waiting-external"
    elif liveness == "ACTIVE":
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
        "contract_revision": state.get("contract_revision"),
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
        "exit_predicate_satisfied": not predicate_false and liveness in TERMINAL,
        "liveness": liveness,
        "physical_runtime_continuity": state.get("physical_runtime_continuity"),
        "logical_runtime_continuity": True,
        "heartbeat_seconds": state.get("heartbeat_seconds") or HEARTBEAT_SECONDS_DEFAULT,
        "active_primary_programs": active_primary_count(programs.get("programs") or []),
        "coordinator_state_path": str(path) if path else None,
        "playbook": playbook,
        "do_not_redo": True,
        "empty_todo_is_not_exit": True,
        "continue": predicate_false or liveness not in TERMINAL,
    }
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
