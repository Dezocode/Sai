#!/usr/bin/env python3
"""Resume reconstructs live HEAD and refuses to treat empty workers as exit."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile

import sai_auth as a
from sai_auth_resume import pick_active, reconstruct


def run_resume_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        run = root / ".ai" / "runs" / "20260813-2015-pr62-queue-ceo"
        run.mkdir(parents=True)
        state = {
            "task_id": "20260813-2015-pr62-queue-ceo",
            "repo": "Dezocode/Sai",
            "pr": 62,
            "branch": "cursor/codebase-health-90ba",
            "primary_logical_id": "pr62-primary",
            "physical_runtime_id": "bc-old",
            "current_head": "deadbeef" * 5,
            "contract_id": "20260813-pr62-saul-smoke",
            "contract_revision": "v3",
            "liveness": "WAITING_EXTERNAL",
            "exit_predicate": "READY_FOR_HUMAN_REVIEW requires Saul+Sai",
            "active_workers": [],
            "pending_events": ["WAITING_EXTERNAL:saul"],
            "expected_next_state": "WAITING_EXTERNAL",
            "last_material_transition": "workers-returned",
            "sai_disposition": "pending",
        }
        (run / "coordinator-state.json").write_text(json.dumps(state), encoding="utf-8")
        (root / ".ai" / "_config").mkdir(parents=True)
        a.write_yaml(root / ".ai" / "_config" / "primary-programs.yaml", {
            "max_active": 2,
            "programs": [{
                "logical_id": "pr62-primary", "pr": 62,
                "kind": "primary_implementation", "status": "active",
            }],
        })
        a.git(root, "init")
        a.git(root, "config", "user.email", "t@example.com")
        a.git(root, "config", "user.name", "t")
        (root / "README").write_text("x\n", encoding="utf-8")
        a.git(root, "add", "README")
        a.git(root, "commit", "-m", "init")
        live = a.head_sha(root)

        path, picked = pick_active([(run / "coordinator-state.json", state)])
        executed.add("resume-picks-nonterminal")
        if picked.get("primary_logical_id") != "pr62-primary":
            raise RuntimeError(picked)
        print("SELFTEST PASS  resume-picks-nonterminal")

        compact = reconstruct(root)
        executed.add("resume-refreshes-head")
        if compact["head_sha"] != live:
            raise RuntimeError(compact)
        if compact["state_file_head"] == live:
            raise RuntimeError("fixture head should differ from live")
        if compact["exit_predicate_satisfied"]:
            raise RuntimeError("empty workers must not satisfy exit")
        if not compact["continue"]:
            raise RuntimeError(compact)
        if compact["playbook"] != "orchestrate-waiting-external":
            raise RuntimeError(compact["playbook"])
        print("SELFTEST PASS  resume-refreshes-head")

        executed.add("resume-empty-todo-not-exit")
        if compact["empty_todo_is_not_exit"] is not True:
            raise RuntimeError(compact)
        print("SELFTEST PASS  resume-empty-todo-not-exit")

        ready = dict(state, liveness="READY_FOR_HUMAN_REVIEW")
        path2, picked2 = pick_active([(run / "coordinator-state.json", ready)])
        executed.add("resume-skips-terminal")
        if picked2 is not None:
            raise RuntimeError(picked2)
        print("SELFTEST PASS  resume-skips-terminal")

        from sai_auth_resume import latest_saul
        stale = {"disposition": "REQUEST_CHANGES", "implementation_head": "aa"}
        current = {"disposition": "BLOCKED", "head": live}
        reviews = root / ".ai" / "contracts" / "20260813-pr62-saul-smoke" / "reviews"
        reviews.mkdir(parents=True)
        a.write_yaml(reviews / "saul-implementation-old.yaml", stale)
        got = latest_saul(
            root, "20260813-pr62-saul-smoke", prefer_head=live, state_saul=current
        )
        executed.add("resume-prefers-live-head-saul")
        if got.get("disposition") != "BLOCKED" or got.get("head") != live:
            raise RuntimeError(got)
        print("SELFTEST PASS  resume-prefers-live-head-saul")
        executed.add("resume-rejects-mismatched-saul-snapshot")
        miss = latest_saul(
            root, "no-such-contract", prefer_head=live,
            state_saul={"head": "aa" * 20, "disposition": "APPROVE"},
        )
        if miss is not None:
            raise RuntimeError(miss)
        print("SELFTEST PASS  resume-rejects-mismatched-saul-snapshot")

        from sai_auth_resume import exit_satisfied
        spoof = {
            "reviewer": "saul", "disposition": "APPROVE", "head": live,
            "runtime": "cursor", "codex_invoked": False,
        }
        executed.add("resume-spoof-cursor-saul-not-exit")
        if exit_satisfied(
            dict(state, sai_disposition="APPROVE", contract_revision="v12"),
            live, spoof, "APPROVE",
        ):
            raise RuntimeError("spoof cursor Saul must not satisfy exit")
        print("SELFTEST PASS  resume-spoof-cursor-saul-not-exit")

        ready_spoof = dict(
            state, liveness="READY_FOR_HUMAN_REVIEW", sai_disposition="APPROVE",
            saul=spoof, current_head=live,
        )
        (run / "coordinator-state.json").write_text(json.dumps(ready_spoof), encoding="utf-8")
        compact2 = reconstruct(root)
        executed.add("resume-invalid-ready-nonqualifying-saul")
        if compact2.get("exit_predicate_satisfied"):
            raise RuntimeError(compact2)
        if compact2.get("invalid_ready_state") != "INVALID_READY_STATE_NONQUALIFYING_SAUL":
            raise RuntimeError(compact2)
        if compact2.get("liveness") == "READY_FOR_HUMAN_REVIEW":
            raise RuntimeError("invalid ready must not stay terminal")
        if not compact2.get("continue"):
            raise RuntimeError(compact2)
        print("SELFTEST PASS  resume-invalid-ready-nonqualifying-saul")
    return executed


if __name__ == "__main__":
    run_resume_fixtures()
    print("sai_auth_resume_test: OK")
