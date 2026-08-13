#!/usr/bin/env python3
"""Pre-commit / pre-push / CI authorization replay. Never trust session in CI."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sai_auth as a  # noqa: E402
import sai_auth_flow as flow  # noqa: E402


def _trailers_from_session(session):
    t = {
        "Task-ID": session.get("task_id") or "",
        "Agent": session.get("agent_id") or "",
        "Runtime": session.get("runtime") or "",
    }
    if session.get("lease_id"):
        t["Authorization-ID"] = session["lease_id"]
    if session.get("contract_id"):
        t["Contract-ID"] = session["contract_id"]
    if session.get("contract_revision"):
        t["Contract-Revision"] = session["contract_revision"]
    return t


def verify_paths(cfg, trailers, paths, *, root, sha=None, session=None, branch=None):
    fails = []
    agent_id = trailers.get("Agent")
    task_id = trailers.get("Task-ID")
    if not agent_id:
        fails.append("missing Agent trailer/identity")
        return fails
    if not task_id:
        fails.append("missing Task-ID")
        return fails
    if a.bootstrap_ok(cfg, trailers, paths):
        return fails
    if agent_id in (cfg.get("bootstrap") or {}).get("agent_trailers", []):
        fails.append("unbound runtime cannot commit without bootstrap or assumed identity")
        return fails
    oc = a.officer_cfg(cfg, agent_id)
    if oc:
        if oc.get("cursor_impersonation") == "forbidden":
            fails.append("Saul/Codex identity cannot author Cursor commits")
            return fails
        allowed = a.class_paths(cfg, oc.get("write_class"))
        denied = []
        if agent_id == "ctr-admin":
            denied = [".ai/agents/saul/**", "openclaw-dashboard/**"]
            bad = flow.cora_blocks_product({"agent_id": "ctr-admin"}, paths)
            if bad:
                fails.append("Cora must not implement product/control-plane code: " + ",".join(bad))
        for p in paths:
            if not a.path_allowed(p, allowed, denied):
                fails.append(f"officer {agent_id} path out of class: {p}")
        return fails
    # contractor
    cid = trailers.get("Contract-ID")
    if not cid:
        fails.append("contractor commit missing Contract-ID")
        return fails
    rev_l = trailers.get("Contract-Revision")
    ptr = a.load_pointer(root, cid, sha=sha)
    if not ptr:
        fails.append(f"contract {cid} not in tracked tree")
        return fails
    current = ptr.get("current_revision")
    if rev_l and current and a.revision_label(rev_l) != a.revision_label(current):
        fails.append(f"stale contract revision {rev_l} current is {current}")
        return fails
    rev = a.load_revision(root, cid, current or rev_l or "v1", sha=sha)
    if not rev:
        fails.append("contract revision file missing")
        return fails
    if rev.get("agent_id") != agent_id:
        fails.append(f"Agent {agent_id} != contract agent {rev.get('agent_id')}")
    br = trailers.get("Branch") or branch
    allowed_br = rev.get("allowed_branch_or_worktree") or ""
    if br and allowed_br and br != allowed_br and not br.startswith(str(allowed_br).rstrip("/")):
        fails.append(f"wrong branch {br} (allowed {allowed_br})")
    lid = trailers.get("Authorization-ID")
    lease = a.load_lease(root, cid, lid, sha=sha) if lid else None
    if not lease:
        for L in a.list_leases(root, cid, sha=sha):
            if L.get("agent_id") == agent_id and L.get("status") == "active":
                lease = L
                break
    if not lease:
        fails.append("no tracked authorization lease")
        return fails
    if lease.get("status") != "active":
        fails.append(f"lease {lease.get('lease_id')} status={lease.get('status')}")
    if a.revision_label(lease.get("contract_revision")) != a.revision_label(current or rev_l):
        fails.append("lease bound to stale contract revision")
    if lease.get("task_id") and lease.get("task_id") != task_id:
        fails.append("lease task_id mismatch")
    allowed = lease.get("allowed_paths") or rev.get("allowed_paths") or []
    denied = list(lease.get("denied_paths") or rev.get("denied_paths") or [])
    denied += list(cfg.get("protected_denied_for_contractors") or [])
    for p in paths:
        if not a.path_allowed(p, allowed, denied):
            fails.append(f"path out of scope: {p}")
    return fails


def verify_commit(root, cfg, sha, *, branch=None):
    if (cfg.get("enforcement") or {}).get("skip_commits_missing_policy") and not a.commit_has_policy(root, sha):
        return []
    msg = a.commit_message(root, sha)
    trailers = a.parse_trailers(msg)
    paths = a.commit_paths(root, sha)
    return verify_paths(cfg, trailers, paths, root=root, sha=sha, branch=branch)


def verify_range(root, spec, *, branch=None):
    cfg = a.load_config(root)
    fails = []
    shas = a.rev_list(root, spec)
    if not shas:
        print("verify-agent-authorization: no commits in range")
        return 0
    for sha in shas:
        fs = verify_commit(root, cfg, sha, branch=branch)
        if fs:
            for f in fs:
                print(f"FAIL {sha[:12]}: {f}", file=sys.stderr)
            fails.extend(fs)
        else:
            print(f"PASS {sha[:12]} authorization")
    if fails:
        print(f"verify-agent-authorization: FAILED ({len(fails)})", file=sys.stderr)
        return 1
    print("verify-agent-authorization: OK")
    return 0


def verify_pre_commit(root):
    cfg = a.load_config(root)
    session = a.load_session(root)
    paths = a.staged_paths(root)
    if not paths:
        print("verify-agent-authorization: nothing staged")
        return 0
    a.ensure_primary_runtime(root)
    if not session:
        reqs = list(Path(root).glob(".ai/requests/*/request.yaml"))
        # unbound: only allowed if CONTRACT_REQUIRED intake paths or bootstrap
        trailers = {
            "Task-ID": os.environ.get("SAI_TASK_ID") or "",
            "Agent": os.environ.get("SAI_AGENT_ID") or "cursor-cloud",
        }
        if a.bootstrap_ok(cfg, trailers, paths):
            print("PASS pre-commit bootstrap")
            return 0
        print("FAIL no assumed identity; run sai-authorize-task / sai-assume-agent", file=sys.stderr)
        print("CONTRACT_REQUIRED", file=sys.stderr)
        return 1
    trailers = _trailers_from_session(session)
    br = a.current_branch(root)
    if session.get("branch") and session["branch"] != br:
        print("FAIL session branch", session["branch"], "!=", br, file=sys.stderr)
        return 1
    fails = verify_paths(cfg, trailers, paths, root=root, session=session, branch=br)
    if session.get("agent_id") == "ctr-admin":
        extra = flow.cora_blocks_product(session, paths)
        if extra:
            fails.append("Cora product-code paths: " + ",".join(extra))
    if fails:
        for f in fails:
            print(f"FAIL {f}", file=sys.stderr)
        return 1
    print("PASS pre-commit authorization")
    return 0


def verify_commit_msg(root, msgfile):
    text = Path(msgfile).read_text(encoding="utf-8")
    t = a.parse_trailers(text)
    session = a.load_session(root)
    if session:
        if t.get("Agent") and t.get("Agent") != session.get("agent_id"):
            print("FAIL Agent trailer != assumed identity", file=sys.stderr)
            return 1
        if t.get("Task-ID") and t.get("Task-ID") != session.get("task_id"):
            print("FAIL Task-ID trailer != session task", file=sys.stderr)
            return 1
    if not t.get("Task-ID") or not t.get("Agent"):
        print("FAIL commit message missing Task-ID and/or Agent trailers", file=sys.stderr)
        return 1
    print("PASS commit-msg trailers")
    return 0


def append_trailers(root, msgfile):
    session = a.load_session(root)
    if not session:
        return 0
    path = Path(msgfile)
    text = path.read_text(encoding="utf-8")
    t = a.parse_trailers(text)
    lines = []
    if "Task-ID" not in t:
        lines.append(f"Task-ID: {session.get('task_id')}")
    if "Agent" not in t:
        lines.append(f"Agent: {session.get('agent_id')}")
    if session.get("lease_id") and "Authorization-ID" not in t:
        lines.append(f"Authorization-ID: {session['lease_id']}")
    if session.get("contract_id") and "Contract-ID" not in t:
        lines.append(f"Contract-ID: {session['contract_id']}")
    if session.get("contract_revision") and "Contract-Revision" not in t:
        lines.append(f"Contract-Revision: {session['contract_revision']}")
    rt = session.get("runtime")
    if rt and "Runtime" not in t:
        lines.append(f"Runtime: {rt}")
    if lines:
        if not text.endswith("\n"):
            text += "\n"
        path.write_text(text + "\n".join(lines) + "\n", encoding="utf-8")
    return 0


def latest_review(root, cid, reviewer, review_type, sha=None):
    d = a.reviews_dir(root, cid)
    if sha:
        p = a.git(root, "ls-tree", "--name-only", sha, f".ai/contracts/{cid}/reviews/")
        names = [Path(x).name for x in p.stdout.splitlines() if x.endswith(".yaml")]
        docs = []
        for n in names:
            text = a.git_show(root, sha, f".ai/contracts/{cid}/reviews/{n}")
            if text:
                docs.append(a.load_yaml(text))
    else:
        if not d.is_dir():
            return None
        docs = [a.read_yaml(p) for p in sorted(d.glob("*.yaml"))]
    docs = [x for x in docs if x and x.get("reviewer") == reviewer
            and x.get("review_type") == review_type]
    return docs[-1] if docs else None


def human_gate(root, cid=None, sha=None, ci_green=False):
    sha = sha or a.head_sha(root)
    if not cid:
        cid = _detect_contract(root)
    fails = []
    if not cid:
        fails.append("no contract for human gate")
        return fails, "BLOCKED"
    ptr = a.load_pointer(root, cid)
    rev_l = (ptr or {}).get("current_revision")
    rev = a.load_revision(root, cid, rev_l or "v1") if ptr else None
    if not rev:
        return ["missing current revision"], "BLOCKED"
    n = a.revision_int(rev_l)
    if not rev.get("cora_admin_complete"):
        fails.append("Cora administration not complete")
    saul_c = latest_review(root, cid, "saul", "contract")
    saul_i = latest_review(root, cid, "saul", "implementation")
    sai_c = latest_review(root, cid, "sai", "contract")
    sai_i = latest_review(root, cid, "sai", "implementation")

    def check(revw, kind, who):
        if not revw:
            fails.append(f"{who} {kind} review missing")
            return
        if revw.get("disposition") == "REQUEST_CHANGES":
            fails.append(f"{who} {kind} is REQUEST_CHANGES")
        if revw.get("disposition") == "BLOCKED":
            fails.append(f"{who} {kind} is BLOCKED ({revw.get('reason')})")
        if revw.get("disposition") != "APPROVE":
            fails.append(f"{who} {kind} not APPROVE")
            return
        if a.revision_int(revw.get("contract_revision")) != n:
            fails.append(f"{who} {kind} revision stale")
        if kind == "implementation":
            head = revw.get("implementation_head") or ""
            if not head or not sha.startswith(head) and not head.startswith(sha[:12]):
                if head != sha:
                    fails.append(f"{who} implementation SHA stale ({head} vs {sha})")
        if who == "saul":
            if revw.get("synthetic"):
                fails.append("Saul synthetic/fixture approval is not valid")
            if revw.get("runtime") != "codex":
                fails.append("Saul approval must have runtime: codex")

    check(saul_c, "contract", "saul")
    check(saul_i, "implementation", "saul")
    check(sai_c, "contract", "sai")
    check(sai_i, "implementation", "sai")
    if not ci_green:
        fails.append("CI not proven green on exact SHA")
    hap = a.contract_dir(root, cid) / "human-approval-required.yaml"
    if hap.is_file():
        doc = a.read_yaml(hap)
        if doc and not doc.get("resolved"):
            fails.append("authority-expanding human approval pending")
    if fails:
        return fails, "BLOCKED"
    return [], "READY"


def _detect_contract(root):
    session = a.load_session(root)
    if session and session.get("contract_id"):
        return session["contract_id"]
    base = Path(root) / ".ai/contracts"
    if not base.is_dir():
        return None
    br = a.current_branch(root)
    for d in sorted(base.iterdir()):
        if not d.is_dir():
            continue
        ptr = a.read_json(d / "contract.json") or {}
        if ptr.get("current_revision"):
            rev = a.read_yaml(d / "revisions" / f"{ptr['current_revision']}.yaml")
            if rev and rev.get("allowed_branch_or_worktree") == br:
                return d.name
    return None


def cmd_verify_agent(argv=None):
    p = argparse.ArgumentParser(prog="verify-agent-authorization")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--pre-commit", action="store_true")
    p.add_argument("--commit-msg", default=None)
    p.add_argument("--prepare-commit-msg", default=None)
    p.add_argument("--branch", default=None)
    args, extra = p.parse_known_args(argv)
    range_spec = " ".join(extra).strip() or os.environ.get("SAI_AUTH_RANGE") or "HEAD"
    if args.self_test:
        from sai_auth_test import run_synthetic_fixtures
        n = run_synthetic_fixtures()
        print(f"verify-agent-authorization self-test: {n} fixtures executed")
        return 0
    root = a.toplevel()
    if args.prepare_commit_msg:
        return append_trailers(root, args.prepare_commit_msg)
    if args.commit_msg:
        return verify_commit_msg(root, args.commit_msg)
    if args.pre_commit:
        return verify_pre_commit(root)
    if range_spec == "HEAD":
        range_spec = "-n 1 HEAD"
    return verify_range(root, range_spec, branch=args.branch or os.environ.get("GITHUB_HEAD_REF"))


def cmd_verify_contract(argv=None):
    p = argparse.ArgumentParser(prog="verify-contract-authorization")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--human-gate", action="store_true")
    p.add_argument("--contract-id", default=None)
    p.add_argument("--sha", default=None)
    p.add_argument("--ci-green", action="store_true")
    p.add_argument("--range", default=None)
    args = p.parse_args(argv)
    if args.self_test:
        from sai_auth_test import run_contract_fixtures
        n = run_contract_fixtures()
        print(f"verify-contract-authorization self-test: {n} fixtures executed")
        return 0
    root = a.toplevel()
    if args.range:
        return cmd_verify_agent([args.range])
    if args.human_gate:
        ci = args.ci_green and os.environ.get("GITHUB_ACTIONS") == "true"
        fails, state = human_gate(root, args.contract_id, args.sha, ci_green=ci)
        print(f"HUMAN_GATE {state}")
        for f in fails:
            print(f"FAIL {f}", file=sys.stderr)
        a.write_yaml(
            Path(root) / ".ai" / "contracts" / (args.contract_id or _detect_contract(root) or "unknown") / "human-gate.yaml",
            {"state": state, "sha": args.sha or a.head_sha(root), "fails": fails, "at": a.utcnow()},
        ) if (args.contract_id or _detect_contract(root)) else None
        return 0 if state == "READY" else 1
    cid = args.contract_id or _detect_contract(root)
    if not cid:
        print("FAIL no contract", file=sys.stderr)
        return 1
    ptr = a.load_pointer(root, cid)
    print("contract", cid, "revision", (ptr or {}).get("current_revision"))
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--contract"]:
        raise SystemExit(cmd_verify_contract(args[1:]))
    raise SystemExit(cmd_verify_agent(args))
