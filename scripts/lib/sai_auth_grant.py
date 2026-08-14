#!/usr/bin/env python3
"""Tracked officer grants and bootstrap closed-range checks (CTO-009 / CTO-011)."""
from __future__ import annotations

from pathlib import Path

import sai_auth as a

GRANTS_REL = ".ai/authorizations/grants"
SHA_BOUND_REL = ".ai/authorizations/sha-bound-authorization.yaml"
PIN_ISSUERS = ("ceo", "ctr-admin")


def bootstrap_until_ok(cfg, task_id, root=None, sha=None) -> bool:
    """False when the bootstrap task is closed for this commit/sha."""
    boot = cfg.get("bootstrap") or {}
    bindings = boot.get("task_bindings") or {}
    until = (bindings.get(task_id) or {}).get("until_sha")
    if not until:
        return True
    if not sha or not root:
        return False
    if sha == until:
        return True
    p = a.git(root, "merge-base", "--is-ancestor", sha, until)
    return p.returncode == 0


def officer_grant_required(cfg, root=None, sha=None) -> bool:
    og = cfg.get("officer_grants") or {}
    if not og.get("required"):
        return False
    after = og.get("required_after_sha")
    if not after or not sha or not root:
        return True
    if sha == after:
        return False
    p = a.git(root, "merge-base", "--is-ancestor", sha, after)
    return p.returncode != 0


def list_grants(root, sha=None):
    if sha:
        p = a.git(root, "ls-tree", "--name-only", sha, GRANTS_REL + "/")
        names = [Path(x).name for x in p.stdout.splitlines() if x.endswith(".yaml")]
        out = []
        for n in names:
            text = a.git_show(root, sha, f"{GRANTS_REL}/{n}")
            if text:
                doc = a.load_yaml(text)
                if isinstance(doc, dict):
                    out.append(doc)
        return out
    d = Path(root) / GRANTS_REL
    if not d.is_dir():
        return []
    out = []
    for p in sorted(d.glob("*.yaml")):
        doc = a.read_yaml(p)
        if isinstance(doc, dict):
            out.append(doc)
    return out


def bound_task_ids(*docs):
    """Union of task_id and task_ids[] on the given docs only (commit-time)."""
    out = []
    for doc in docs:
        if not isinstance(doc, dict):
            continue
        out.extend(x for x in (doc.get("task_ids") or []) if x)
        tid = doc.get("task_id")
        if tid:
            out.append(tid)
    return out


def _issuer_ok(cfg, issuer):
    return issuer in PIN_ISSUERS and issuer in (cfg.get("officers") or {})


def _issuer_grant_ok(root, grant_id, issuer):
    if not grant_id or not issuer:
        return False
    for g in list_grants(root, sha="HEAD"):
        if g.get("id") == grant_id and g.get("principal") == issuer:
            return True
    return False


def sha_bound_rows(root, cfg=None):
    """Officer SHA-bound pins from git show HEAD, never working tree or _config."""
    text = a.git_show(root, "HEAD", SHA_BOUND_REL)
    if not text:
        return []
    doc = a.load_yaml(text)
    if not isinstance(doc, dict):
        return []
    cfg = cfg or a.load_config(root)
    file_issuer = doc.get("issuer")
    file_grant = doc.get("issuer_grant")
    rows = doc.get("pins") or []
    out = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        issuer = r.get("issuer") or file_issuer
        grant_id = r.get("issuer_grant") or file_grant
        if not _issuer_ok(cfg, issuer) or not _issuer_grant_ok(root, grant_id, issuer):
            continue
        row = dict(r)
        row["issuer"] = issuer
        row["issuer_grant"] = grant_id
        out.append(row)
    return out


def sha_bound_task_ids(root, sha, agent_id, authorization_id):
    """Task-IDs pinned to this exact SHA + agent + authorization_id at HEAD."""
    extra = []
    if not sha or not agent_id or not authorization_id:
        return extra
    for row in sha_bound_rows(root):
        if (
            row.get("sha") == sha
            and row.get("agent_id") == agent_id
            and row.get("authorization_id") == authorization_id
            and row.get("task_id")
        ):
            extra.append(row["task_id"])
    return extra


def grant_covers(grant, agent_id, task_id, paths, runtime=None, extra_task_ids=None) -> bool:
    if not grant or grant.get("principal") != agent_id:
        return False
    tids = bound_task_ids(grant)
    if extra_task_ids:
        tids.extend(extra_task_ids)
    if task_id not in tids:
        return False
    grt = grant.get("runtime")
    if runtime and grt and grt != runtime:
        return False
    allowed = grant.get("paths") or []
    denied = grant.get("denied_paths") or []
    for p in paths or []:
        if not a.path_allowed(p, allowed, denied):
            return False
    return True


def matching_grant(root, agent_id, task_id, paths, *, sha=None, grant_id=None, runtime=None):
    for g in list_grants(root, sha=sha):
        if grant_id and g.get("id") != grant_id:
            continue
        extra = sha_bound_task_ids(root, sha, agent_id, g.get("id")) if sha else []
        if grant_covers(g, agent_id, task_id, paths, runtime=runtime, extra_task_ids=extra):
            return g
    return None


def lease_task_id_bound(root, cid, lease, task_id, agent_id, sha=None) -> bool:
    """True when task_id is on the commit-time lease or a SHA-bound HEAD pin."""
    tids = bound_task_ids(lease)
    if sha and lease:
        tids = list(tids) + sha_bound_task_ids(
            root, sha, agent_id, lease.get("lease_id")
        )
    if not tids:
        return True
    return task_id in tids


def register_grant_fixtures(one, _commit):
    """Extra synthetic fixtures for CTO-009 / CTO-011. Called from sai_auth_test."""

    def forged(d):
        _commit(d, {".ai/notes.md": "forged\n"}, "forged ceo trailer", {
            "Task-ID": "20260813-9999-auth-test-ctr-code-auth1",
            "Agent": "ceo",
        })

    one("authorization-forged-officer-trailer-bad", forged, True)

    def granted(d):
        _commit(d, {
            ".ai/authorizations/grants/grant-ceo-test.yaml": (
                "id: grant-ceo-test\n"
                "principal: ceo\n"
                "runtime: cursor-cloud-vm\n"
                "task_id: 20260813-9999-ceo-grant-test\n"
                "paths: [\".ai/**\"]\n"
                "actions: [write]\n"
                "issued_by: test\n"
            ),
            ".ai/runs/grant-note.md": "ok\n",
        }, "ceo with tracked grant", {
            "Task-ID": "20260813-9999-ceo-grant-test",
            "Agent": "ceo",
            "Authorization-ID": "grant-ceo-test",
            "Runtime": "cursor-cloud-vm",
        })

    one("authorization-officer-grant-good", granted, False)

    def expired(d):
        sha1 = a.head_sha(d)
        cfg = a.load_config(d)
        boot = cfg.setdefault("bootstrap", {})
        boot.setdefault("task_bindings", {})["20260813-1517-auth-loop-cursor-cloud"] = {
            "until_sha": sha1,
        }
        _commit(d, {
            ".ai/_config/authorization.yaml": a.dump_yaml(cfg),
            "scripts/after-boot.sh": "echo no\n",
        }, "reuse closed bootstrap", {
            "Task-ID": "20260813-1517-auth-loop-cursor-cloud",
            "Agent": "cursor-cloud",
        })

    one("authorization-bootstrap-expired-bad", expired, True)
