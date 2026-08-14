#!/usr/bin/env python3
"""SHA-bound authorization pins. HEAD/working-tree task_ids must not rebind history."""
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
POLICY = ".ai/_config/authorization.yaml"
REASON = "wave used new Task-ID before grant/lease aliases existed; no history rewrite"


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


def _boot_tr():
    return {
        "Task-ID": "20260813-1517-auth-loop-cursor-cloud",
        "Agent": "cursor-cloud",
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


def _add_pin(cfg, sha, agent_id, task_id, auth_id):
    audit = cfg.setdefault("audit", {})
    rows = list(audit.get("sha_bound_authorization") or [])
    rows.append({
        "sha": sha,
        "agent_id": agent_id,
        "task_id": task_id,
        "authorization_id": auth_id,
        "reason": REASON,
    })
    audit["sha_bound_authorization"] = rows
    return cfg


def _commit_pin(d, sha, agent_id, task_id, auth_id):
    cfg = a.load_yaml(a.git_show(d, "HEAD", POLICY) or "")
    _add_pin(cfg, sha, agent_id, task_id, auth_id)
    return _commit(d, {POLICY: a.dump_yaml(cfg)}, "sha-bound pin", _boot_tr())


def run_rebind_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        d = _init(tmp / "wt-grant")
        _write_grant(d)
        _commit(d, {GRANT_REL: (d / GRANT_REL).read_text(), ".ai/runs/old.md": "a\n"},
                "grant old", _ceo_tr(CEO_OLD))
        sha = _commit(d, {".ai/runs/new.md": "b\n"}, "wave", _ceo_tr(CEO_NEW))
        _write_grant(d, task_ids=[CEO_OLD, CEO_NEW])
        cfg = a.read_yaml(d / POLICY)
        _add_pin(cfg, sha, "ceo", CEO_NEW, GRANT_ID)
        (d / POLICY).write_text(a.dump_yaml(cfg), encoding="utf-8")
        bad = _fails(d, sha)
        _expect("uncommitted-grant-task-ids-do-not-rebind", bool(bad), bad)
        executed.add("uncommitted-grant-task-ids-do-not-rebind")

        d = _init(tmp / "later-head")
        _write_grant(d)
        _commit(d, {GRANT_REL: (d / GRANT_REL).read_text(), ".ai/runs/old.md": "a\n"},
                "grant old", _ceo_tr(CEO_OLD))
        sha = _commit(d, {".ai/runs/new.md": "b\n"}, "wave", _ceo_tr(CEO_NEW))
        _write_grant(d, task_ids=[CEO_OLD, CEO_NEW])
        _commit(d, {GRANT_REL: (d / GRANT_REL).read_text()}, "later HEAD task_ids",
                _ceo_tr(CEO_OLD))
        bad = _fails(d, sha)
        _expect("later-head-grant-without-sha-bound-bad", bool(bad), bad)
        executed.add("later-head-grant-without-sha-bound-bad")

        d = _init(tmp / "sha-bound-good")
        _write_grant(d)
        _commit(d, {GRANT_REL: (d / GRANT_REL).read_text(), ".ai/runs/old.md": "a\n"},
                "grant old", _ceo_tr(CEO_OLD))
        sha = _commit(d, {".ai/runs/new.md": "b\n"}, "wave", _ceo_tr(CEO_NEW))
        _expect("sha-bound-needed-before-pin", bool(_fails(d, sha)))
        _commit_pin(d, sha, "ceo", CEO_NEW, GRANT_ID)
        post = _fails(d, sha)
        _expect("sha-bound-matching-sha-good", post == [], post)
        executed.add("sha-bound-matching-sha-good")

        d = _init(tmp / "sha-bound-other")
        _write_grant(d)
        _commit(d, {GRANT_REL: (d / GRANT_REL).read_text(), ".ai/runs/old.md": "a\n"},
                "grant old", _ceo_tr(CEO_OLD))
        sha_s = _commit(d, {".ai/runs/new.md": "b\n"}, "wave S", _ceo_tr(CEO_NEW))
        sha_t = _commit(d, {".ai/runs/other.md": "c\n"}, "wave T", _ceo_tr(CEO_NEW))
        _commit_pin(d, sha_s, "ceo", CEO_NEW, GRANT_ID)
        bad = _fails(d, sha_t)
        _expect("sha-bound-other-sha-bad", bool(bad), bad)
        ok_s = _fails(d, sha_s)
        _expect("sha-bound-pinned-sha-still-good", ok_s == [], ok_s)
        executed.add("sha-bound-other-sha-bad")

        d = _init(tmp / "principal")
        _write_grant(d)
        _commit(d, {GRANT_REL: (d / GRANT_REL).read_text(), ".ai/runs/old.md": "a\n"},
                "grant old", _ceo_tr(CEO_OLD))
        sha = _commit(d, {".ai/runs/new.md": "b\n"}, "wave", _ceo_tr(CEO_NEW))
        _commit_pin(d, sha, "ctr-admin", CEO_NEW, GRANT_ID)
        bad = _fails(d, sha)
        _expect(
            "sha-bound-wrong-principal-bad",
            any("tracked grant" in x for x in bad),
            bad,
        )
        executed.add("sha-bound-path-principal-fail-closed")

        d = _init(tmp / "paths")
        _write_grant(d, paths=[".ai/runs/**"])
        _commit(d, {GRANT_REL: (d / GRANT_REL).read_text(), ".ai/runs/old.md": "a\n"},
                "narrow grant", _ceo_tr(CEO_OLD))
        sha = _commit(d, {".ai/notes.md": "wide\n"}, "outside grant paths", _ceo_tr(CEO_NEW))
        _commit_pin(d, sha, "ceo", CEO_NEW, GRANT_ID)
        bad = _fails(d, sha)
        _expect("sha-bound-path-expand-ignored", bool(bad), bad)

        d = _init(tmp / "lease-ctime")
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
        _expect("lease-commit-time-task-ids-good", post == [], post)
        executed.add("lease-commit-time-task-ids-good")

        d = _init(tmp / "lease-later")
        cid = _contract(d)
        lid = _lease(d, cid)
        sha = _commit(d, {"scripts/wave.sh": "echo w\n"}, "wave", _ctr_tr(cid, lid, CTR_NEW))
        _patch_lease(d, cid, task_ids=[CTR_OLD, CTR_NEW])
        rel = _lease_rel(cid, lid)
        _commit(d, {rel: (d / rel).read_text()}, "later HEAD lease task_ids", {
            "Task-ID": "20260813-1517-auth-loop-cursor-cloud",
            "Agent": "ctr-admin",
            "Authorization-ID": "grant-test-ctr-admin",
            "Runtime": "cursor-cloud-vm",
        })
        bad = _fails(d, sha)
        _expect("later-head-lease-without-sha-bound-bad", any("task_id" in x for x in bad), bad)
        _commit_pin(d, sha, "ctr-code-auth1", CTR_NEW, lid)
        post = _fails(d, sha)
        _expect("sha-bound-lease-matching-sha-good", post == [], post)
        executed.add("sha-bound-lease-matching-sha-good")

        d = _init(tmp / "lease-paths")
        cid = _contract(d)
        lid = _lease(d, cid, paths=["scripts/**"])
        sha = _commit(
            d, {".ai/runs/out.md": "nope\n"}, "out of lease paths",
            _ctr_tr(cid, lid, CTR_NEW),
        )
        _commit_pin(d, sha, "ctr-code-auth1", CTR_NEW, lid)
        bad = _fails(d, sha)
        _expect(
            "sha-bound-lease-path-fail-closed",
            any("path out of scope" in x for x in bad),
            bad,
        )

        root = tmp / "self-pass"
        rel = "ledger.yaml"
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        a.write_yaml(root / rel, {"blockers": [], "policy": {"never_delete_history": True}})
        append_blocker(root, {
            "blocker_id": "CTO-024",
            "source": "saul",
            "source_actor": "saul",
            "category": "technical",
            "severity": "P0",
            "description": "rebind must not self-PASS",
            "clearance_authority": "saul",
            "status": "DISCOVERED",
        }, rel=rel)
        r = attempt_clear(
            root, "CTO-024", "cursor",
            review_id="self", head="c" * 40, rel=rel,
        )
        _expect("rebind-self-pass-rejected", r.get("status") == "REJECT", r)
        executed.add("rebind-self-pass-rejected")

    return executed


if __name__ == "__main__":
    run_rebind_fixtures()
    print("sai_auth_rebind_test: all fixtures passed")
