#!/usr/bin/env python3
"""Resume reconstructs live HEAD and refuses to treat empty workers as exit."""
from __future__ import annotations

import json
from pathlib import Path
import os
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
    executed |= run_ralph_liveness_fixtures()
    return executed


def _ralph_root(tmp, name, state, extra=None):
    root = Path(tmp) / name
    run = root / ".ai" / "runs" / "20260813-2015-pr62-queue-ceo"
    run.mkdir(parents=True)
    (run / "coordinator-state.json").write_text(json.dumps(state), encoding="utf-8")
    (root / ".ai" / "_config").mkdir(parents=True)
    a.write_yaml(root / ".ai" / "_config" / "primary-programs.yaml", {
        "max_active": 2,
        "programs": [{
            "logical_id": "pr62-primary", "pr": 62,
            "kind": "primary_implementation", "status": "active",
        }],
    })
    cid = root / ".ai" / "contracts" / "20260813-pr62-saul-smoke"
    cid.mkdir(parents=True)
    (cid / "contract.json").write_text(json.dumps({
        "contract_id": "20260813-pr62-saul-smoke", "current_revision": "v12",
    }), encoding="utf-8")
    if extra:
        extra(root)
    a.git(root, "init")
    a.git(root, "config", "user.email", "t@example.com")
    a.git(root, "config", "user.name", "t")
    (root / "README").write_text("x\n", encoding="utf-8")
    a.git(root, "add", "README")
    a.git(root, "commit", "-m", "init")
    return root, a.head_sha(root)


def _base_state(**kw):
    row = {
        "task_id": "20260813-2015-pr62-queue-ceo",
        "repo": "Dezocode/Sai", "pr": 62,
        "branch": "cursor/codebase-health-90ba",
        "primary_logical_id": "pr62-primary",
        "physical_runtime_id": "bc-old",
        "current_head": "deadbeef" * 5,
        "contract_id": "20260813-pr62-saul-smoke",
        "contract_revision": "v4",
        "liveness": "ACTIVE",
        "exit_predicate": "READY_FOR_HUMAN_REVIEW requires Saul+Sai",
        "exit_predicate_satisfied": False,
        "sai_disposition": "pending",
        "physical_runtime_continuity": False,
        "active_workers": [],
        "workers": [{"agent_id": "ctr-code-pr62smoke", "state": "COMPLETE"}],
        "pending_events": ["B-SAUL-COMPTROLLER-READINESS-001"],
        "open_findings_digest": "B-SAUL-COMPTROLLER-READINESS-001",
    }
    row.update(kw)
    return row


def _ledger(root, status="DISCOVERED"):
    from sai_auth_blockers import save_ledger
    path = root / ".ai/contracts/20260813-pr62-saul-smoke/blockers/ledger.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    save_ledger(path, {
        "ledger_id": "t", "contract_id": "20260813-pr62-saul-smoke",
        "blockers": [{"blocker_id": "B-SAUL-COMPTROLLER-READINESS-001",
                      "category": "technical", "status": status}],
    })


def run_ralph_liveness_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as tmp:
        root, live = _ralph_root(tmp, "a", _base_state())
        _ledger(root)
        compact = reconstruct(root)
        if compact.get("primary_logical_id") != "pr62-primary":
            raise RuntimeError(compact)
        if compact.get("liveness") != "ACTIVE" or not compact.get("continue"):
            raise RuntimeError(compact)
        if compact.get("contract_revision") not in ("v12", 12, "12"):
            raise RuntimeError(compact.get("contract_revision"))
        executed.add("ralph-liveness-a-wave-complete-good")
        print("SELFTEST PASS  ralph-liveness-a-wave-complete-good")

        rootb, _ = _ralph_root(tmp, "b", _base_state(
            physical_runtime_id="bc-new", physical_runtime_continuity=False,
        ))
        _ledger(rootb)
        compact = reconstruct(rootb)
        if compact.get("primary_logical_id") != "pr62-primary":
            raise RuntimeError(compact)
        if compact.get("playbook") != "poteto-continue-frontier":
            raise RuntimeError(compact.get("playbook"))
        if not compact.get("continue"):
            raise RuntimeError(compact)
        executed.add("ralph-liveness-b-restart-reassess-good")
        print("SELFTEST PASS  ralph-liveness-b-restart-reassess-good")

        rootc, _ = _ralph_root(tmp, "c", _base_state(
            saul={"disposition": "REQUEST_CHANGES", "head": "aa"},
            current_frontier="machine-actionable-mapping",
        ))
        _ledger(rootc)
        compact = reconstruct(rootc)
        if not compact.get("continue") or compact.get("liveness") in ("READY_FOR_HUMAN_REVIEW",):
            raise RuntimeError(compact)
        executed.add("ralph-liveness-c-saul-pending-continue-good")
        print("SELFTEST PASS  ralph-liveness-c-saul-pending-continue-good")

        rootd, _ = _ralph_root(tmp, "d", _base_state(
            liveness="WAITING_EXTERNAL",
            pending_events=["WAITING_EXTERNAL:saul"],
            physical_runtime_continuity=True,
        ))
        compact = reconstruct(rootd)
        if compact.get("liveness") == "READY_FOR_HUMAN_REVIEW" or not compact.get("continue"):
            raise RuntimeError(compact)
        if not compact.get("reassess_blockers"):
            raise RuntimeError("D must reassess under WAITING_EXTERNAL + continuity")
        executed.add("ralph-liveness-d-external-frontier-good")
        print("SELFTEST PASS  ralph-liveness-d-external-frontier-good")

        rooth, _ = _ralph_root(tmp, "h", _base_state(
            liveness="WAITING_EXTERNAL",
            pending_events=["WAITING_EXTERNAL:saul"],
            physical_runtime_continuity=False,
            workers=[{"agent_id": "ctr-code-pr62smoke", "state": "COMPLETE"}],
        ))
        _ledger(rooth)
        compact = reconstruct(rooth)
        if compact.get("primary_logical_id") != "pr62-primary":
            raise RuntimeError(compact)
        if not compact.get("reassess_blockers") or not compact.get("continue"):
            raise RuntimeError(compact)
        if compact.get("playbook") != "poteto-continue-frontier":
            raise RuntimeError(compact.get("playbook"))
        if compact.get("next_transition") != "REASSESS_BLOCKERS":
            raise RuntimeError(compact)
        if compact.get("exit_predicate_satisfied") or compact.get("program_complete"):
            raise RuntimeError(compact)
        executed.add("ralph-liveness-h-physical-wait-reassess-good")
        print("SELFTEST PASS  ralph-liveness-h-physical-wait-reassess-good")

        rooti, _ = _ralph_root(tmp, "i", _base_state(
            active_workers=[], workers=[], current_frontier="",
        ))
        _ledger(rooti)
        compact = reconstruct(rooti)
        if compact.get("exit_predicate_satisfied") or compact.get("program_complete"):
            raise RuntimeError("empty todo + blockers must not complete")
        executed.add("ralph-liveness-i-empty-todo-blockers-good")
        print("SELFTEST PASS  ralph-liveness-i-empty-todo-blockers-good")

        rootj, _ = _ralph_root(tmp, "j", _base_state(
            liveness="WAITING_EXTERNAL",
            saul={"disposition": "pending"},
            physical_runtime_continuity=True,
            workers=[], active_workers=[],
            pending_events=["WAITING_EXTERNAL:saul"],
        ))
        compact = reconstruct(rootj)
        if compact.get("liveness") not in ("WAITING_EXTERNAL", "ACTIVE_EXTERNAL_WAIT"):
            raise RuntimeError(compact)
        if compact.get("frontier_class") != "B":
            raise RuntimeError(compact)
        if not compact.get("continue") or not compact.get("reassess_blockers"):
            raise RuntimeError(compact)
        executed.add("ralph-liveness-j-saul-pending-external-good")
        print("SELFTEST PASS  ralph-liveness-j-saul-pending-external-good")

        rootk, _ = _ralph_root(tmp, "k", _base_state(
            saul={"disposition": "REQUEST_CHANGES", "head": "aa"},
            current_frontier="blocker",
        ))
        _ledger(rootk)
        compact = reconstruct(rootk)
        if not compact.get("continue") or compact.get("liveness") in (
            "READY_FOR_HUMAN_REVIEW", "DONE", "COMPLETE", "TERMINAL",
        ):
            raise RuntimeError(compact)
        executed.add("ralph-liveness-k-saul-fail-continue-good")
        print("SELFTEST PASS  ralph-liveness-k-saul-fail-continue-good")

        rootl, _ = _ralph_root(tmp, "l", _base_state(sai_disposition="REQUEST_CHANGES"))
        compact = reconstruct(rootl)
        if not compact.get("continue") or compact.get("exit_predicate_satisfied"):
            raise RuntimeError(compact)
        if compact.get("liveness") in ("READY_FOR_HUMAN_REVIEW", "DONE", "COMPLETE"):
            raise RuntimeError(compact)
        executed.add("ralph-liveness-l-sai-fail-nonterminal-good")
        print("SELFTEST PASS  ralph-liveness-l-sai-fail-nonterminal-good")

        from sai_auth_saul_attestation_v2 import make_signed_review_v2
        import subprocess as sp
        priv, pub = Path(tmp) / "g.pem", Path(tmp) / "g.pub"
        sp.run(["openssl", "genpkey", "-algorithm", "Ed25519", "-out", str(priv)],
               check=True, capture_output=True)
        sp.run(["openssl", "pkey", "-in", str(priv), "-pubout", "-out", str(pub)],
               check=True, capture_output=True)
        prev = os.environ.get("SAI_SAUL_ATTEST_PUB")
        os.environ["SAI_SAUL_ATTEST_PUB"] = str(pub)
        try:
            roote, live_e = _ralph_root(tmp, "e", _base_state(sai_disposition="pending"))
            review_e = make_signed_review_v2(
                str(priv), str(pub), implementation_head=live_e,
                contract_id="20260813-pr62-saul-smoke", contract_revision=12,
            )
            revdir = roote / ".ai/contracts/20260813-pr62-saul-smoke/reviews"
            revdir.mkdir(parents=True, exist_ok=True)
            a.write_yaml(revdir / "saul-e.yaml", review_e)
            compact = reconstruct(roote)
            if compact.get("exit_predicate_satisfied") or not compact.get("continue"):
                raise RuntimeError(compact)
            executed.add("ralph-liveness-e-saul-pass-sai-pending-good")
            print("SELFTEST PASS  ralph-liveness-e-saul-pass-sai-pending-good")

            rootf, live_f = _ralph_root(tmp, "f", _base_state(sai_disposition="APPROVE"))
            _ledger(rootf, status="DISCOVERED")
            review_f = make_signed_review_v2(
                str(priv), str(pub), implementation_head=live_f,
                contract_id="20260813-pr62-saul-smoke", contract_revision=12,
            )
            rdir = rootf / ".ai/contracts/20260813-pr62-saul-smoke/reviews"
            rdir.mkdir(parents=True, exist_ok=True)
            a.write_yaml(rdir / "saul-f.yaml", review_f)
            compact = reconstruct(rootf)
            if compact.get("exit_predicate_satisfied") or not compact.get("continue"):
                raise RuntimeError(compact)
            executed.add("ralph-liveness-f-sai-pass-blocker-remains-good")
            print("SELFTEST PASS  ralph-liveness-f-sai-pass-blocker-remains-good")

            rootg, live_g = _ralph_root(tmp, "g", _base_state(
                sai_disposition="APPROVE", liveness="READY_FOR_HUMAN_REVIEW",
                open_findings_digest="", pending_events=[],
            ))
            _ledger(rootg, status="PASSED_BY_SAUL")
            review_g = make_signed_review_v2(
                str(priv), str(pub), implementation_head=live_g,
                contract_id="20260813-pr62-saul-smoke", contract_revision=12,
            )
            gdir = rootg / ".ai/contracts/20260813-pr62-saul-smoke/reviews"
            gdir.mkdir(parents=True, exist_ok=True)
            a.write_yaml(gdir / "saul-g.yaml", review_g)
            compact = reconstruct(rootg)
            if not compact.get("exit_predicate_satisfied"):
                raise RuntimeError(compact)
            if compact.get("liveness") != "READY_FOR_HUMAN_REVIEW":
                raise RuntimeError(compact.get("liveness"))
            if compact.get("continue"):
                raise RuntimeError("G should be terminal")
            executed.add("ralph-liveness-g-predicates-ready-good")
            print("SELFTEST PASS  ralph-liveness-g-predicates-ready-good")
        finally:
            if prev is None:
                os.environ.pop("SAI_SAUL_ATTEST_PUB", None)
            else:
                os.environ["SAI_SAUL_ATTEST_PUB"] = prev

        from sai_auth_resume import enforced_rejects
        rootx, _ = _ralph_root(tmp, "x", _base_state(liveness="COMPLETE"))
        _ledger(rootx)
        compact = reconstruct(rootx)
        if "ready_false_and_program_terminal" not in (compact.get("enforced_rejects") or enforced_rejects(rootx, compact, _base_state(liveness="COMPLETE"))):
            if compact.get("liveness") in ("COMPLETE", "TERMINAL", "DONE"):
                raise RuntimeError(compact)
        executed.add("ralph-reject-false-terminal-bad")
        print("SELFTEST PASS  ralph-reject-false-terminal-bad")

        rooty, _ = _ralph_root(tmp, "y", _base_state(liveness="READY_FOR_HUMAN_REVIEW"))
        _ledger(rooty, status="DISCOVERED")
        compact = reconstruct(rooty)
        if compact.get("exit_predicate_satisfied"):
            raise RuntimeError(compact)
        if compact.get("liveness") == "READY_FOR_HUMAN_REVIEW" and not compact.get("continue"):
            raise RuntimeError("open blocker must keep program nonterminal")
        executed.add("ralph-reject-blocker-terminal-bad")
        print("SELFTEST PASS  ralph-reject-blocker-terminal-bad")

        from sai_auth_saul_gated import gates_missing, missing_ledger_projection
        miss = Path(tmp) / "nolegder"
        miss.mkdir()
        if not missing_ledger_projection(miss):
            raise RuntimeError("empty tree must miss P0 ledger rows")
        executed.add("ralph-reject-missing-ledger-bad")
        print("SELFTEST PASS  ralph-reject-missing-ledger-bad")
        if not gates_missing([{"blocker_id": "T-1", "check_name": "ci-green"}]):
            raise RuntimeError("ci-green is not a Saul blocker gate")
        executed.add("ralph-reject-missing-check-gate-bad")
        print("SELFTEST PASS  ralph-reject-missing-check-gate-bad")

        from sai_auth_resume import enforce
        skip = dict(compact)
        skip.update({
            "exit_predicate_satisfied": False,
            "reassess_blockers": False,
            "continue": True,
            "liveness": "WAITING_EXTERNAL",
            "status": "RECONSTRUCTED",
        })
        hits = enforce(rootd, skip, _base_state(
            liveness="WAITING_EXTERNAL", physical_runtime_continuity=True,
        ))
        if "ready_false_and_skip_reassess" not in hits:
            raise RuntimeError(hits)
        executed.add("ralph-enforce-skip-reassess-bad")
        print("SELFTEST PASS  ralph-enforce-skip-reassess-bad")
    return executed


if __name__ == "__main__":
    run_resume_fixtures()
    print("sai_auth_resume_test: OK")
