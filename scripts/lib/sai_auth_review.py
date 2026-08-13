#!/usr/bin/env python3
"""Invoke Codex/Saul and consume machine-readable CTO reviews. Never fake APPROVE."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sai_auth as a  # noqa: E402
import sai_auth_flow as flow  # noqa: E402
import sai_auth_verify as v  # noqa: E402

MARKER_B, MARKER_E = "---SAUL_REVIEW_YAML---", "---END_SAUL_REVIEW_YAML---"


def _codex_env():
    key = os.environ.get("OPENAI_API_KEY") or os.environ.get("CODEX_API_KEY")
    return key


def _codex_cmd():
    if shutil.which("codex"):
        return ["codex", "exec", "--ephemeral", "-"]
    if shutil.which("npx") and _codex_env():
        return ["npx", "--yes", "@openai/codex", "exec", "--ephemeral", "-"]
    return None


def _prompt(root, cid, rev, sha, review_type):
    parts = []
    for rel in [
        "CODEX.md",
        ".ai/agents/saul/AGENT.md",
        ".ai/agents/saul/runtimes/codex/automation/profile.md",
        ".ai/agents/saul/runtimes/codex/prompts/cto-review.md",
    ]:
        p = Path(root) / rel
        if p.is_file():
            parts.append(f"# {rel}\n{p.read_text(encoding='utf-8')[:12000]}")
    revdoc = a.load_revision(root, cid, rev) if cid else None
    if revdoc:
        parts.append("# contract revision\n" + a.dump_yaml(revdoc))
    if sha:
        msg = a.commit_message(root, sha)
        parts.append(f"# implementation HEAD {sha}\n{msg}")
        diff = a.git(root, "show", "--stat", sha).stdout
        parts.append(diff[:8000])
    parts.append(
        f"Review type: {review_type}. Emit YAML between {MARKER_B} and {MARKER_E}. "
        "disposition must be APPROVE, REQUEST_CHANGES, or BLOCKED. "
        "You are Saul (dezo-sec-codex1), Codex-native CTO. Do not impersonate Cora or Sai."
    )
    return "\n\n".join(parts)


def _parse_yaml_block(text):
    if MARKER_B in text and MARKER_E in text:
        body = text.split(MARKER_B, 1)[1].split(MARKER_E, 1)[0]
        return a.load_yaml(body)
    try:
        doc = a.load_yaml(text)
        if isinstance(doc, dict) and "disposition" in doc:
            return doc
    except Exception:
        return None
    return None


def invoke(root, cid, revision, sha, review_type, github_run_id=None, github_event=None,
           out=None, force=False, fixture=None):
    rev_n = a.revision_int(revision) if revision else None
    if not cid:
        cid = v._detect_contract(root)
    if not cid:
        print("FAIL no contract_id", file=sys.stderr)
        return 1, None
    ptr = a.load_pointer(root, cid)
    if ptr and not revision:
        revision = ptr.get("current_revision")
        rev_n = a.revision_int(revision)
    sha = sha or a.head_sha(root)
    key = a.review_key(cid, rev_n, sha, "saul", review_type)
    dest = a.reviews_dir(root, cid) / f"saul-{review_type}-{key}.yaml"
    if dest.is_file() and not force:
        existing = a.read_yaml(dest)
        print(f"IDEMPOTENT_SKIP key={key} disposition={existing.get('disposition')}")
        return 0, existing
    last = v.latest_review(root, cid, "saul", review_type)
    if (not force and last and last.get("disposition") == "REQUEST_CHANGES"
            and a.revision_int(last.get("contract_revision")) == rev_n
            and (last.get("implementation_head") or "") == (sha or "")
            and (a.load_config(root).get("idempotency") or {}).get("skip_if_unchanged_request_changes", True)):
        print("LOOP_PREVENTION skip re-invoke; revision and SHA unchanged after REQUEST_CHANGES")
        return 0, last

    doc = None
    reason = None
    if fixture:
        doc = a.read_yaml(Path(fixture)) if not isinstance(fixture, dict) else fixture
        if doc is not None:
            doc["synthetic"] = True
            doc["runtime"] = doc.get("runtime") or "test-fixture"
    elif not _codex_env() or not _codex_cmd():
        reason = "CODEX_UNAVAILABLE"
        doc = {
            "reviewer": "saul",
            "runtime": "codex",
            "contract_id": cid,
            "contract_revision": rev_n,
            "implementation_head": sha,
            "review_type": review_type,
            "disposition": "BLOCKED",
            "reason": reason,
            "findings": [],
            "synthetic": False,
            "codex_invoked": False,
        }
    else:
        prompt = _prompt(root, cid, revision, sha, review_type)
        env = os.environ.copy()
        if os.environ.get("CODEX_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
            env["OPENAI_API_KEY"] = os.environ["CODEX_API_KEY"]
        try:
            p = subprocess.run(
                _codex_cmd(), input=prompt, capture_output=True, text=True,
                env=env, timeout=600,
            )
            parsed = _parse_yaml_block(p.stdout + "\n" + p.stderr)
            if not parsed or parsed.get("disposition") not in ("APPROVE", "REQUEST_CHANGES", "BLOCKED"):
                doc = {
                    "reviewer": "saul", "runtime": "codex", "contract_id": cid,
                    "contract_revision": rev_n, "implementation_head": sha,
                    "review_type": review_type, "disposition": "BLOCKED",
                    "reason": "CODEX_OUTPUT_UNPARSEABLE", "codex_invoked": True,
                    "exit_code": p.returncode, "findings": [],
                }
            else:
                doc = parsed
                doc.setdefault("reviewer", "saul")
                doc["runtime"] = "codex"
                doc["codex_invoked"] = True
                doc["synthetic"] = False
                doc["contract_id"] = cid
                doc["contract_revision"] = rev_n
                doc["implementation_head"] = sha
                doc["review_type"] = review_type
        except Exception as e:
            doc = {
                "reviewer": "saul", "runtime": "codex", "contract_id": cid,
                "contract_revision": rev_n, "implementation_head": sha,
                "review_type": review_type, "disposition": "BLOCKED",
                "reason": f"CODEX_INVOKE_ERROR:{type(e).__name__}",
                "codex_invoked": False, "findings": [],
            }

    doc["idempotency_key"] = key
    if github_run_id:
        doc["github_run_id"] = github_run_id
    if github_event:
        doc["github_event"] = github_event
    doc.setdefault("findings", [])
    # Never allow fixture/missing-codex to become a valid APPROVE
    if doc.get("disposition") == "APPROVE":
        if doc.get("synthetic") or not doc.get("codex_invoked"):
            doc["disposition"] = "BLOCKED"
            doc["reason"] = "REFUSED_UNVERIFIED_APPROVE"
    a.write_yaml(dest, doc)
    if out:
        Path(out).write_text(a.dump_yaml(doc), encoding="utf-8")
    print(a.dump_yaml(doc))
    print(f"SAUL_DISPOSITION {doc.get('disposition')} key={key} file={dest}")
    rc = 0 if doc.get("disposition") == "APPROVE" else 1
    return rc, doc


def _expanding(cfg, finding):
    actions = set(cfg.get("authority_expanding_actions") or [])
    if finding.get("authority_expanding"):
        return True
    if finding.get("action") in actions:
        return True
    field = finding.get("contract_field") or ""
    act = finding.get("action") or ""
    if field in ("allowed_paths", "capabilities", "denied_paths", "allowed_repository") and act in (
        "expand", "add", "remove", "grant-capability", "remove-denied-path",
    ):
        if act == "add" and field == "verification_requirements":
            return False
        if act == "narrow":
            return False
        if act == "add" and field == "allowed_paths":
            return True
        if act == "add" and field == "capabilities":
            return True
        if act == "remove" and field == "denied_paths":
            return True
    return False


def consume(root, cid, src, session_ok=True):
    session = a.load_session(root) or {}
    if session.get("agent_id") != "ctr-admin":
        print("FAIL consume-saul-contract-review requires assumed Cora (ctr-admin)", file=sys.stderr)
        return 1
    review = a.read_yaml(Path(src)) if not isinstance(src, dict) else src
    if not review:
        print("FAIL missing review", file=sys.stderr)
        return 1
    cid = cid or review.get("contract_id")
    ptr = a.load_pointer(root, cid)
    current = a.revision_int(ptr.get("current_revision"))
    tracked = a.reviews_dir(root, cid) / f"consumed-{review.get('idempotency_key') or 'na'}.yaml"
    a.write_yaml(tracked, review)
    if review.get("disposition") == "APPROVE":
        rev = a.load_revision(root, cid, current)
        rs = rev.setdefault("review_state", {}).setdefault("saul", {})
        rs["status"] = "approved"
        rs["reviewed_revision"] = current
        if review.get("review_type") == "implementation":
            rs["reviewed_implementation_sha"] = review.get("implementation_head")
        a.save_revision(root, cid, rev)
        print("CONSUMED APPROVE; no amendment")
        return 0
    if review.get("disposition") == "BLOCKED":
        print("CONSUMED BLOCKED; no auto-amend", review.get("reason"))
        return 0
    cfg = a.load_config(root)
    ordinary, expanding = [], []
    for f in review.get("findings") or []:
        (expanding if _expanding(cfg, f) else ordinary).append(f)
    if expanding:
        hap = {
            "contract_id": cid,
            "from_review": review.get("idempotency_key"),
            "authority_expanding_findings": expanding,
            "resolved": False,
            "created_at": a.utcnow(),
            "created_by": "ctr-admin",
            "note": "Cora must not auto-grant authority-expanding Saul requests.",
        }
        a.write_yaml(a.contract_dir(root, cid) / "human-approval-required.yaml", hap)
        print("HUMAN_APPROVAL_REQUIRED authority-expanding findings; no auto-amend")
    if not ordinary:
        return 0 if expanding else 0
    new_n = current + 1
    old = a.load_revision(root, cid, current)
    new = json_clone(old)
    maps = []
    amd_id = f"A-{new_n:03d}"
    changes = []
    for f in ordinary:
        fid = f.get("id") or "CTO-unknown"
        field = f.get("contract_field")
        act = f.get("action")
        req_ch = f.get("requested_change")
        if field == "allowed_paths" and act == "narrow" and isinstance(req_ch, list):
            new["allowed_paths"] = req_ch
        elif field == "verification_requirements" and act == "add":
            vr = list(new.get("verification_requirements") or [])
            item = req_ch if isinstance(req_ch, str) else str(req_ch)
            if item not in vr:
                vr.append(item)
            new["verification_requirements"] = vr
        elif field and act == "add" and field in new and isinstance(new.get(field), list):
            item = req_ch if not isinstance(req_ch, list) else req_ch
            cur = list(new.get(field) or [])
            if isinstance(item, list):
                for x in item:
                    if x not in cur:
                        cur.append(x)
            elif item not in cur:
                cur.append(item)
            new[field] = cur
        changes.append({"finding_id": fid, "field": field, "action": act})
        maps.append(f"{fid} -> {amd_id} -> v{new_n}")
    new["revision"] = new_n
    new["revision_label"] = f"v{new_n}"
    new["supersedes_revision"] = current
    new["amendment_ids"] = list(old.get("amendment_ids") or []) + [amd_id]
    new["review_state"] = {
        "saul": {"status": "pending", "reviewed_revision": None,
                 "reviewed_implementation_sha": None},
        "sai": {"status": "pending", "reviewed_revision": None,
                "reviewed_implementation_sha": None},
    }
    a.save_revision(root, cid, new)
    amd = {
        "amendment_id": amd_id,
        "contract_id": cid,
        "from_revision": current,
        "to_revision": new_n,
        "finding_ids": [f.get("id") for f in ordinary],
        "authority_expanding": False,
        "human_approval_required": False,
        "summary": "; ".join(maps),
        "trace": maps,
        "changes": changes,
        "created_by": "ctr-admin",
        "created_at": a.utcnow(),
    }
    a.write_yaml(a.amendments_dir(root, cid) / f"{amd_id}.yaml", amd)
    ptr["current_revision"] = f"v{new_n}"
    a.write_json(a.pointer_path(root, cid), ptr)
    nstale = flow.stale_leases(root, cid, new_n)
    print(f"AMENDED {cid} v{current} -> v{new_n} stale_leases={nstale}")
    for m in maps:
        print("TRACE", m)
    return 0


def json_clone(obj):
    return json.loads(json.dumps(obj))


def cmd_invoke(argv=None):
    p = argparse.ArgumentParser(prog="invoke-saul-review")
    p.add_argument("--contract-id", default=None)
    p.add_argument("--revision", default=None)
    p.add_argument("--head", default=None)
    p.add_argument("--review-type", default="implementation",
                   choices=["contract", "implementation"])
    p.add_argument("--github-run-id", default=os.environ.get("GITHUB_RUN_ID"))
    p.add_argument("--github-event", default=os.environ.get("GITHUB_EVENT_NAME"))
    p.add_argument("--out", default=None)
    p.add_argument("--force", action="store_true")
    p.add_argument("--fixture", default=None)
    p.add_argument("--detect-contract", action="store_true")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args(argv)
    if args.self_test:
        from sai_auth_test import run_saul_fixtures
        n = run_saul_fixtures()
        print(f"invoke-saul-review self-test: {n} fixtures executed")
        return 0
    root = a.toplevel()
    if args.detect_contract:
        print(v._detect_contract(root) or "")
        return 0
    rc, _ = invoke(
        root, args.contract_id, args.revision, args.head, args.review_type,
        github_run_id=args.github_run_id, github_event=args.github_event,
        out=args.out, force=args.force, fixture=args.fixture,
    )
    return rc


def cmd_consume(argv=None):
    p = argparse.ArgumentParser(prog="consume-saul-contract-review")
    p.add_argument("--contract-id", default=None)
    p.add_argument("--from-file", required=False)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args(argv)
    if args.self_test:
        from sai_auth_test import run_consume_fixtures
        n = run_consume_fixtures()
        print(f"consume-saul-contract-review self-test: {n} fixtures executed")
        return 0
    if not args.from_file:
        print("FAIL --from-file required", file=sys.stderr)
        return 2
    return consume(a.toplevel(), args.contract_id, args.from_file)


def cmd_record_sai(argv=None):
    p = argparse.ArgumentParser(prog="record-sai-verification")
    p.add_argument("--contract-id", required=True)
    p.add_argument("--review-type", default="implementation",
                   choices=["contract", "implementation"])
    p.add_argument("--disposition", default="APPROVE",
                   choices=["APPROVE", "REQUEST_CHANGES", "BLOCKED"])
    p.add_argument("--head", default=None)
    p.add_argument("--note", default="")
    args = p.parse_args(argv)
    root = a.toplevel()
    session = a.load_session(root) or {}
    if session.get("agent_id") != "ceo":
        print("FAIL Sai verification requires assumed identity ceo", file=sys.stderr)
        return 1
    ptr = a.load_pointer(root, args.contract_id)
    rev_n = a.revision_int((ptr or {}).get("current_revision") or 1)
    sha = args.head or a.head_sha(root)
    key = a.review_key(args.contract_id, rev_n, sha, "sai", args.review_type)
    doc = {
        "reviewer": "sai",
        "runtime": session.get("runtime") or "cursor-cloud-vm",
        "contract_id": args.contract_id,
        "contract_revision": rev_n,
        "implementation_head": sha,
        "review_type": args.review_type,
        "disposition": args.disposition,
        "synthetic": False,
        "note": args.note,
        "idempotency_key": key,
        "recorded_by": "ceo",
        "recorded_at": a.utcnow(),
    }
    dest = a.reviews_dir(root, args.contract_id) / f"sai-{args.review_type}-{key}.yaml"
    a.write_yaml(dest, doc)
    print(f"SAI_DISPOSITION {args.disposition} {dest}")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0] if args else "invoke"
    rest = args[1:] if args else []
    if cmd == "consume":
        raise SystemExit(cmd_consume(rest))
    if cmd == "record-sai":
        raise SystemExit(cmd_record_sai(rest))
    if cmd == "invoke":
        raise SystemExit(cmd_invoke(rest))
    raise SystemExit(cmd_invoke(args))
