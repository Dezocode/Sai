#!/usr/bin/env python3
"""Tracked officer grants and bootstrap closed-range checks (CTO-009 / CTO-011)."""
from __future__ import annotations

from pathlib import Path

import sai_auth as a

GRANTS_REL = ".ai/authorizations/grants"


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


def grant_covers(grant, agent_id, task_id, paths, runtime=None, sha=None) -> bool:
    if not grant or grant.get("principal") != agent_id:
        return False
    tids = list(grant.get("task_ids") or [])
    if grant.get("task_id"):
        tids.append(grant.get("task_id"))
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
    covers = [str(x) for x in (grant.get("covers_shas") or [])]
    if covers and sha:
        full = str(sha)
        if not any(full == c or full.startswith(c) or c.startswith(full[:12]) for c in covers):
            return False
    return True


def _workdir_grants(root):
    d = Path(root) / GRANTS_REL
    if not d.is_dir():
        return []
    out = []
    for p in sorted(d.glob("*.yaml")):
        doc = a.read_yaml(p)
        if isinstance(doc, dict):
            out.append(doc)
    return out


def matching_grant(root, agent_id, task_id, paths, *, sha=None, grant_id=None, runtime=None):
    seen = set()
    candidates = list(list_grants(root, sha=sha))
    # SHA-bound ratification grants live in the current tree; historical
    # commits cannot contain them. Replay those only when covers_shas matches.
    if sha:
        for g in _workdir_grants(root):
            if g.get("covers_shas"):
                candidates.append(g)
    for g in candidates:
        gid = g.get("id")
        if gid and gid in seen:
            continue
        if gid:
            seen.add(gid)
        if grant_id and gid != grant_id:
            continue
        if grant_covers(g, agent_id, task_id, paths, runtime=runtime, sha=sha):
            return g
    return None


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
