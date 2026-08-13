#!/usr/bin/env python3
"""Authorize-task, assume/release identity, Cora contract creation, amendments."""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sai_auth as a  # noqa: E402


PRODUCT_PREFIXES = ("openclaw-dashboard/", "scripts/", ".github/workflows/")


def _runtime(args):
    return getattr(args, "runtime", None) or os.environ.get("SAI_RUNTIME") or a.detect_runtime()


def cmd_authorize(argv=None):
    p = argparse.ArgumentParser(prog="sai-authorize-task")
    p.add_argument("--task-id", required=True)
    p.add_argument("--purpose", default="")
    p.add_argument("--requested-by", default="dezocode (U0BHYH0NMCY)")
    p.add_argument("--repository", default="Dezocode/Sai")
    p.add_argument("--runtime", default=None)
    p.add_argument("--required-role", default="contractor-coding")
    p.add_argument("--preferred-agent", default=None)
    p.add_argument("--create-contract", action="store_true")
    p.add_argument("--contract-id", default=None)
    p.add_argument("--contractor-id", default=None)
    p.add_argument("--contractor-name", default=None)
    p.add_argument("--branch", default=None)
    p.add_argument("--allowed-path", action="append", default=[])
    p.add_argument("--capability", action="append", default=[])
    args = p.parse_args(argv)
    root = a.toplevel()
    cfg = a.load_config(root)
    runtime = _runtime(args)
    req = a.load_request(root, args.task_id) or {
        "task_id": args.task_id,
        "requested_by": args.requested_by,
        "repository": args.repository,
        "runtime": runtime,
        "purpose": args.purpose,
        "required_role": args.required_role,
        "state": "REQUESTED",
        "resolved_agent": None,
        "contract_id": None,
    }
    if args.purpose:
        req["purpose"] = args.purpose
    req["state"] = "IDENTITY_RESOLUTION"
    reg = a.load_registry(root)
    agent = None
    if args.preferred_agent:
        agent = a.find_agent(reg, args.preferred_agent)
    if agent is None:
        agent = _resolve_impl_agent(cfg, reg, req, runtime)
    if agent is None:
        req["state"] = "CONTRACT_REQUIRED"
        req["resolved_agent"] = None
        a.save_request(root, args.task_id, req)
        print("CONTRACT_REQUIRED")
        print(f"request={a.request_path(root, args.task_id)}")
        print("Assume Cora: scripts/sai-assume-agent ctr-admin --task-id", args.task_id)
        if not args.create_contract:
            return 0
    if args.create_contract or req["state"] == "CONTRACT_REQUIRED":
        session = a.load_session(root) or {}
        if session.get("agent_id") != "ctr-admin":
            print("FAIL create-contract requires assumed identity ctr-admin (Cora)", file=sys.stderr)
            return 1
        return _create_contract(root, cfg, args, req, runtime)
    req["state"] = "AUTHORIZED"
    req["resolved_agent"] = agent.get("agent_id")
    a.save_request(root, args.task_id, req)
    print(f"AUTHORIZED agent={agent.get('agent_id')}")
    return 0


def _resolve_impl_agent(cfg, reg, req, runtime):
    role = req.get("required_role") or "contractor-coding"
    for ag in reg.get("agents") or []:
        if ag.get("status") not in ("active", "provisional"):
            continue
        aid = ag.get("agent_id") or ""
        if a.is_officer(cfg, aid):
            continue
        if role.startswith("contractor") and not aid.startswith("ctr-"):
            continue
        if not a.assume_allowed(cfg, ag, runtime):
            continue
        charter = ag.get("charter") or ""
        if "contractor-coding" in role and "contractor-coding" not in charter:
            continue
        return ag
    return None


def _create_contract(root, cfg, args, req, runtime):
    cid = args.contract_id or f"{args.task_id[:8]}-auth-{args.task_id.split('-')[-1]}"
    # contract.json schema wants YYYYMMDD-slug
    if not cid[0].isdigit():
        cid = f"{args.task_id[:8]}-{cid}"
    contractor = args.contractor_id or "ctr-code-auth1"
    name = args.contractor_name or contractor
    branch = args.branch or a.current_branch(root)
    paths = args.allowed_path or ["scripts/**", "tests/**", ".ai/runs/**"]
    caps = args.capability or ["git-commit", "git-push", "draft-pr"]
    denied = list((cfg.get("contractor") or {}).get("default_denied_paths") or [])
    rev = {
        "contract_id": cid,
        "revision": 1,
        "revision_label": "v1",
        "supersedes_revision": None,
        "agent_id": contractor,
        "contractor_name": name,
        "requested_task": args.task_id,
        "allowed_repository": req.get("repository") or "Dezocode/Sai",
        "allowed_branch_or_worktree": branch,
        "allowed_paths": paths,
        "denied_paths": denied,
        "capabilities": caps,
        "verification_requirements": [
            "scripts/verify-agent-authorization",
            "scripts/verify-contract-authorization",
        ],
        "execution_mode": "provisional",
        "amendment_ids": [],
        "review_state": {
            "saul": {"status": "pending", "reviewed_revision": None,
                     "reviewed_implementation_sha": None},
            "sai": {"status": "pending", "reviewed_revision": None,
                    "reviewed_implementation_sha": None},
        },
        "cora_admin_complete": False,
        "created_by": "ctr-admin",
        "created_at": a.utcnow(),
    }
    a.save_revision(root, cid, rev)
    ptr = {
        "contract_id": cid,
        "project_slug": cid.split("-", 1)[-1][:40],
        "project_name": req.get("purpose") or cid,
        "principal": req.get("requested_by") or "dezocode",
        "contractor_type": "coding",
        "isolation_mode": "prototype",
        "primary_runtime": runtime if runtime in (
            "cursor-cloud-vm", "cursor-desktop", "claude-code-cli",
            "codex-desktop", "openclaw-gateway-vps") else "cursor-cloud-vm",
        "compatibility_layer": "sai-mac-ios-android",
        "repository": req.get("repository") or "Dezocode/Sai",
        "branch_prefix": "proj/auth/",
        "status": "draft",
        "schema_version": 2,
        "current_revision": "v1",
        "execution_mode": "provisional",
        "created_by": "ctr-admin",
        "contract_admin_agent_id": "ctr-admin",
        "assigned_contractors": [
            {"agent_id": contractor, "status": "provisional", "branch": branch}
        ],
    }
    a.write_json(a.pointer_path(root, cid), ptr)
    profile = {
        "agent_id": contractor,
        "name": name,
        "role_title": "Coding Contractor",
        "status": "provisional",
        "primary_runtime": runtime,
        "contract_id": cid,
        "created_by": "ctr-admin",
        "created_at": a.utcnow(),
        "note": "Provisional identity; not a standing officer. Cora must not implement product code as this identity.",
    }
    a.write_yaml(a.contract_dir(root, cid) / "contractor-profile.yaml", profile)
    lease = _issue_lease(root, cid, 1, contractor, args.task_id, branch, paths, denied, caps)
    req["state"] = "CONTRACT_DRAFTED"
    req["contract_id"] = cid
    req["resolved_agent"] = contractor
    a.save_request(root, args.task_id, req)
    print(f"CONTRACT_DRAFTED id={cid} revision=v1 contractor={contractor}")
    print(f"lease={lease['lease_id']} execution_mode=provisional")
    print("Release Cora, then: scripts/sai-assume-agent", contractor, "--task-id", args.task_id)
    return 0


def _issue_lease(root, cid, rev, agent_id, task_id, branch, paths, denied, caps):
    lease = {
        "lease_id": f"lease-{uuid.uuid4().hex[:12]}",
        "contract_id": cid,
        "contract_revision": a.revision_label(rev),
        "agent_id": agent_id,
        "task_id": task_id,
        "repository": "Dezocode/Sai",
        "branch": branch,
        "worktree": str(root.name),
        "allowed_paths": paths,
        "denied_paths": denied,
        "capabilities": caps,
        "status": "active",
        "execution_mode": "provisional",
        "issued_at": a.utcnow(),
        "issued_by": "ctr-admin",
        "base_sha": a.head_sha(root),
    }
    a.save_lease(root, cid, lease)
    return lease


def cmd_assume(argv=None):
    p = argparse.ArgumentParser(prog="sai-assume-agent")
    p.add_argument("identity")
    p.add_argument("--task-id", required=True)
    p.add_argument("--runtime", default=None)
    p.add_argument("--contract-id", default=None)
    p.add_argument("--lease-id", default=None)
    args = p.parse_args(argv)
    root = a.toplevel()
    cfg = a.load_config(root)
    runtime = _runtime(args)
    cur = a.load_session(root)
    if cur and cur.get("agent_id") and cur.get("agent_id") != args.identity:
        print("FAIL release current identity first:", cur.get("agent_id"), file=sys.stderr)
        return 1
    ident = args.identity
    if ident.lower() in ("cora", "ctr-admin"):
        ident = "ctr-admin"
    if ident.lower() in ("sai", "ceo"):
        ident = "ceo"
    if ident.lower() == "saul" or ident == "dezo-sec-codex1":
        print("FAIL Saul is Codex-native; cannot assume Saul on", runtime, file=sys.stderr)
        return 1
    reg = a.load_registry(root)
    agent = a.find_agent(reg, ident)
    req = a.load_request(root, args.task_id)
    oc = a.officer_cfg(cfg, ident)
    if ident == "ceo":
        if runtime not in (oc or {}).get("assume_runtimes", []):
            print("FAIL Sai cannot be assumed on", runtime, file=sys.stderr)
            return 1
        from sai_auth_grant import matching_grant
        grant = matching_grant(
            root, "ceo", args.task_id, [".ai/**"],
            runtime=runtime,
        )
        session = {
            "agent_id": "ceo",
            "agent_name": "Sai",
            "runtime": runtime,
            "task_id": args.task_id,
            "contract_id": args.contract_id or (req or {}).get("contract_id"),
            "contract_revision": None,
            "lease_id": None,
            "grant_id": (grant or {}).get("id"),
            "assumed_at": a.utcnow(),
            "branch": a.current_branch(root),
            "worktree": str(Path(root)),
            "write_class": "governance",
        }
        a.save_session(root, session)
        print("ASSUMED ceo (Sai) runtime=", runtime, "grant=", session.get("grant_id"))
        print("Sai owns state-machine/governance writes only; not contractor or Cora.")
        return 0
    if ident == "ctr-admin":
        if runtime not in (oc or {}).get("assume_runtimes", []):
            print("FAIL Cora cannot be assumed on", runtime, file=sys.stderr)
            return 1
        if req and req.get("state") not in (
            "CONTRACT_REQUIRED", "CONTRACT_DRAFTED", "REQUESTED",
            "IDENTITY_RESOLUTION", None,
        ) and req.get("state") not in ("CONTRACT_REQUIRED", "CONTRACT_DRAFTED"):
            pass
        from sai_auth_grant import matching_grant
        grant = matching_grant(
            root, "ctr-admin", args.task_id,
            [".ai/contracts/**"], runtime=runtime,
        )
        session = {
            "agent_id": "ctr-admin",
            "agent_name": "Cora",
            "runtime": runtime,
            "task_id": args.task_id,
            "contract_id": args.contract_id or (req or {}).get("contract_id"),
            "contract_revision": None,
            "lease_id": None,
            "grant_id": (grant or {}).get("id"),
            "assumed_at": a.utcnow(),
            "branch": a.current_branch(root),
            "worktree": str(Path(root)),
            "write_class": "contract-admin",
        }
        a.save_session(root, session)
        print("ASSUMED ctr-admin (Cora) runtime=", runtime)
        print("Cora may write contract/agent-init/governance artifacts only.")
        return 0
    # contractor or other registered agent
    cid = args.contract_id or (req or {}).get("contract_id")
    if not cid:
        print("FAIL contractor assume requires --contract-id or request.contract_id", file=sys.stderr)
        return 1
    ptr = a.load_pointer(root, cid)
    if not ptr:
        print("FAIL contract not found", cid, file=sys.stderr)
        return 1
    rev_l = ptr.get("current_revision") or "v1"
    rev = a.load_revision(root, cid, rev_l)
    if not rev:
        print("FAIL missing revision", rev_l, file=sys.stderr)
        return 1
    agent_id = ident if not agent else agent.get("agent_id")
    if agent_id != rev.get("agent_id"):
        # allow profile-only contractors not yet in registry
        profile = a.read_yaml(a.contract_dir(root, cid) / "contractor-profile.yaml") or {}
        if profile.get("agent_id") != ident and ident != rev.get("agent_id"):
            print("FAIL identity", ident, "is not the contract agent", rev.get("agent_id"), file=sys.stderr)
            return 1
        agent_id = rev.get("agent_id")
    if agent and not a.assume_allowed(cfg, agent, runtime):
        print("FAIL runtime", runtime, "not allowed for", agent_id, file=sys.stderr)
        return 1
    leases = a.list_leases(root, cid)
    lease = None
    if args.lease_id:
        lease = a.load_lease(root, cid, args.lease_id)
    else:
        for L in leases:
            if (L.get("agent_id") == agent_id and L.get("status") == "active"
                    and L.get("contract_revision") == a.revision_label(rev_l)
                    and L.get("task_id") == args.task_id):
                lease = L
                break
    if not lease:
        print("FAIL no active lease for", agent_id, "revision", rev_l, file=sys.stderr)
        print("STALE_OR_MISSING_LEASE", file=sys.stderr)
        return 1
    if a.revision_label(lease.get("contract_revision")) != a.revision_label(rev_l):
        print("FAIL lease revision stale", lease.get("contract_revision"), "current", rev_l, file=sys.stderr)
        return 1
    session = {
        "agent_id": agent_id,
        "agent_name": (agent or {}).get("name") or agent_id,
        "runtime": runtime,
        "task_id": args.task_id,
        "contract_id": cid,
        "contract_revision": a.revision_label(rev_l),
        "lease_id": lease["lease_id"],
        "assumed_at": a.utcnow(),
        "branch": a.current_branch(root),
        "worktree": str(Path(root)),
        "execution_mode": lease.get("execution_mode"),
    }
    a.save_session(root, session)
    if req:
        req["state"] = "IMPLEMENTING"
        req["resolved_agent"] = agent_id
        a.save_request(root, args.task_id, req)
    print(f"ASSUMED {agent_id} contract={cid} revision={session['contract_revision']} lease={lease['lease_id']}")
    return 0


def cmd_release(argv=None):
    p = argparse.ArgumentParser(prog="sai-release-agent")
    p.add_argument("--keep-lease", action="store_true")
    args = p.parse_args(argv)
    root = a.toplevel()
    cur = a.load_session(root)
    if not cur:
        print("NO_SESSION")
        return 0
    aid = cur.get("agent_id")
    a.clear_session(root)
    print(f"RELEASED {aid}")
    return 0


def stale_leases(root, cid, current_rev):
    label = a.revision_label(current_rev)
    n = 0
    for L in a.list_leases(root, cid):
        if L.get("status") == "active" and a.revision_label(L.get("contract_revision")) != label:
            L["status"] = "stale"
            L["stale_reason"] = f"contract moved to {label}"
            a.save_lease(root, cid, L)
            n += 1
    return n


def cora_blocks_product(session, paths):
    if session.get("agent_id") != "ctr-admin":
        return None
    bad = [p for p in paths if any(p == pref or p.startswith(pref) for pref in PRODUCT_PREFIXES)]
    # allow tests/authorization and scripts/sai-*? Decision: Cora must not implement product.
    # Auth control-plane scripts are implementation — contractor, not Cora.
    return bad


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    rest = sys.argv[2:]
    if cmd == "authorize":
        raise SystemExit(cmd_authorize(rest))
    if cmd == "assume":
        raise SystemExit(cmd_assume(rest))
    if cmd == "release":
        raise SystemExit(cmd_release(rest))
    print("usage: sai_auth_flow.py authorize|assume|release", file=sys.stderr)
    raise SystemExit(2)
