#!/usr/bin/env python3
"""HEAD task_id aliasing for grants/leases. Commit-time paths stay authoritative."""
from __future__ import annotations

import tempfile
from pathlib import Path

import sai_auth as a
from sai_auth_blockers import append_blocker, attempt_clear
from sai_auth_test import _commit, _contract, _init, _lease
from sai_auth_verify import verify_commit

CEO_OLD = "20260813-7777-ceo-grant-old"
CEO_NEW = "20260813-7778-ceo-grant-new"
CTR_OLD = "20260813-9999-auth-test-ctr-code-auth1"
CTR_NEW = "20260813-8888-rebind-wave-ctr-code-auth1"
GRANT_REL = ".ai/authorizations/grants/grant-ceo-rebind.yaml"
GRANT_ID = "grant-ceo-rebind"


def _fails(d, sha, branch="feat/auth"):
    return verify_commit(d, a.load_config(d), sha, branch=branch)


def _write_grant(d, **kw):
    doc = {
        "id": GRANT_ID,
        "principal": "ceo",
        "runtime": "cursor-cloud-vm",
        "task_id": CEO_OLD,
        "paths": [".ai/**"],
        "actions": ["write"],
        "issued_by": "test",
    }
    doc.update(kw)
    a.write_yaml(d / GRANT_REL, doc)
    return doc


def _ceo_tr(task):
    return {
        "Task-ID": task,
        "Agent": "ceo",
        "Authorization-ID": GRANT_ID,
        "Runtime": "cursor-cloud-vm",
    }


def _ctr_tr(cid, lid, task):
    return {
        "Task-ID": task,
        "Agent": "ctr-code-auth1",
        "Contract-ID": cid,
        "Contract-Revision": "v1",
        "Authorization-ID": lid,
        "Branch": "feat/auth",
    }


def _patch_lease(d, cid, lid="lease-test1", **kw):
    lease = a.load_lease(d, cid, lid) or {}
    for k, v in kw.items():
        if v is None:
            lease.pop(k, None)
        else:
            lease[k] = v
    a.save_lease(d, cid, lease)
    return lease


def _lease_rel(cid, lid="lease-test1"):
    return f".ai/contracts/{cid}/leases/{lid}.json"


def _expect(name, cond, detail=None):
    if not cond:
        raise RuntimeError(f"{name}: {detail}")
    print(f"SELFTEST PASS  {name}")


def run_rebind_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        d = _init(tmp / "grant-alias")
        _write_grant(d)
        _commit(d, {GRANT_REL: (d / GRANT_REL).read_text(), ".ai/runs/old.md": "a\n"},
                "grant old", _ceo_tr(CEO_OLD))
        sha = _commit(d, {".ai/runs/new.md": "b\n"}, "wave", _ceo_tr(CEO_NEW))
        pre = _fails(d, sha)
        _expect("grant-wave-fails-before-head-alias", bool(pre), pre)
        _write_grant(d, task_ids=[CEO_OLD, CEO_NEW])
        post = _fails(d, sha)
        _expect("grant-head-task-id-alias-good", post == [], post)
        executed.add("grant-head-task-id-alias-good")

        d = _init(tmp / "grant-principal")
        _write_grant(d)
        _commit(d, {GRANT_REL: (d / GRANT_REL).read_text(), ".ai/runs/old.md": "a\n"},
                "grant old", _ceo_tr(CEO_OLD))
        sha = _commit(d, {".ai/runs/new.md": "b\n"}, "wave", _ceo_tr(CEO_NEW))
        _write_grant(d, principal="ctr-admin", task_ids=[CEO_OLD, CEO_NEW])
        bad = _fails(d, sha)
        _expect(
            "grant-head-wrong-principal-bad",
            any("tracked grant" in x for x in bad),
            bad,
        )
        executed.add("grant-head-wrong-principal-bad")

        d = _init(tmp / "grant-paths")
        _write_grant(d, paths=[".ai/runs/**"])
        _commit(d, {GRANT_REL: (d / GRANT_REL).read_text(), ".ai/runs/old.md": "a\n"},
                "narrow grant", _ceo_tr(CEO_OLD))
        sha = _commit(d, {".ai/notes.md": "wide\n"}, "outside grant paths", _ceo_tr(CEO_NEW))
        _write_grant(d, paths=[".ai/**"], task_ids=[CEO_OLD, CEO_NEW])
        bad = _fails(d, sha)
        _expect("grant-head-path-expand-ignored", bool(bad), bad)
        executed.add("grant-head-path-expand-ignored")

        d = _init(tmp / "lease-alias")
        cid = _contract(d)
        lid = _lease(d, cid)
        sha = _commit(d, {"scripts/wave.sh": "echo w\n"}, "wave", _ctr_tr(cid, lid, CTR_NEW))
        pre = _fails(d, sha)
        _expect("lease-wave-fails-before-head-alias", any("task_id" in x for x in pre), pre)
        _patch_lease(d, cid, task_ids=[CTR_OLD, CTR_NEW])
        post = _fails(d, sha)
        _expect("lease-head-task-id-alias-good", post == [], post)
        executed.add("lease-head-task-id-alias-good")

        d = _init(tmp / "lease-ids-only")
        cid = _contract(d)
        lid = _lease(d, cid)
        _patch_lease(d, cid, task_id=None, task_ids=[CTR_NEW])
        rel = _lease_rel(cid, lid)
        _commit(d, {rel: (d / rel).read_text()}, "lease task_ids only", {
            "Task-ID": "20260813-1517-auth-loop-cursor-cloud",
            "Agent": "ctr-admin",
            "Authorization-ID": "grant-test-ctr-admin",
            "Runtime": "cursor-cloud-vm",
        })
        sha = _commit(d, {"scripts/ids.sh": "echo i\n"}, "ids only", _ctr_tr(cid, lid, CTR_NEW))
        post = _fails(d, sha)
        _expect("lease-task-ids-array-good", post == [], post)
        executed.add("lease-task-ids-array-good")

        d = _init(tmp / "lease-ids-mismatch")
        cid = _contract(d)
        lid = _lease(d, cid)
        _patch_lease(d, cid, task_id=None, task_ids=[CTR_OLD])
        rel = _lease_rel(cid, lid)
        _commit(d, {rel: (d / rel).read_text()}, "lease task_ids old", {
            "Task-ID": "20260813-1517-auth-loop-cursor-cloud",
            "Agent": "ctr-admin",
            "Authorization-ID": "grant-test-ctr-admin",
            "Runtime": "cursor-cloud-vm",
        })
        sha = _commit(d, {"scripts/mis.sh": "echo m\n"}, "mismatch", _ctr_tr(cid, lid, CTR_NEW))
        bad = _fails(d, sha)
        _expect("lease-task-ids-mismatch-bad", any("task_id" in x for x in bad), bad)
        executed.add("lease-task-ids-mismatch-bad")

        d = _init(tmp / "lease-paths")
        cid = _contract(d)
        lid = _lease(d, cid, paths=["scripts/**"])
        sha = _commit(
            d, {".ai/runs/out.md": "nope\n"}, "out of lease paths",
            _ctr_tr(cid, lid, CTR_NEW),
        )
        _patch_lease(
            d, cid,
            allowed_paths=["scripts/**", ".ai/runs/**"],
            task_ids=[CTR_OLD, CTR_NEW],
        )
        bad = _fails(d, sha)
        _expect(
            "lease-head-path-expand-ignored",
            any("path out of scope" in x for x in bad),
            bad,
        )
        executed.add("lease-head-path-expand-ignored")

        d = _init(tmp / "lease-agent")
        cid = _contract(d)
        lid = _lease(d, cid)
        sha = _commit(d, {"scripts/ag.sh": "echo a\n"}, "wave", _ctr_tr(cid, lid, CTR_NEW))
        _patch_lease(d, cid, agent_id="ctr-code-other", task_ids=[CTR_OLD, CTR_NEW])
        bad = _fails(d, sha)
        _expect("lease-head-wrong-agent-bad", any("task_id" in x for x in bad), bad)
        executed.add("lease-head-wrong-agent-bad")

        root = tmp / "self-pass"
        rel = "ledger.yaml"
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        a.write_yaml(root / rel, {"blockers": [], "policy": {"never_delete_history": True}})
        append_blocker(root, {
            "blocker_id": "B-REBIND",
            "source": "cursor-primary",
            "source_actor": "ctr-code-pr62smoke",
            "category": "technical",
            "severity": "PROVISIONAL-P0",
            "description": "rebind must not self-PASS",
            "clearance_authority": "saul",
            "status": "DISCOVERED",
        }, rel=rel)
        r = attempt_clear(
            root, "B-REBIND", "ctr-code-pr62smoke",
            review_id="self", head="c" * 40, rel=rel,
        )
        _expect("rebind-self-pass-rejected", r.get("status") == "REJECT", r)
        executed.add("rebind-self-pass-rejected")

    return executed


if __name__ == "__main__":
    run_rebind_fixtures()
    print("sai_auth_rebind_test: all fixtures passed")
