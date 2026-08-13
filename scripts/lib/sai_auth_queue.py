#!/usr/bin/env python3
"""Idempotent remediation queue. Observing the same blocker is not progress."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sai_auth as a  # noqa: E402
import sai_auth_review as review  # noqa: E402


ACTIVE = ("queued", "claimed", "working", "waiting_external")
TERMINAL = ("completed", "failed", "superseded")


def findings_digest(findings) -> str:
    rows = []
    for f in findings or []:
        rows.append("|".join([
            str(f.get("id") or ""),
            str(f.get("severity") or ""),
            str(f.get("contract_field") or ""),
            str(f.get("action") or ""),
            str(f.get("requested_change") or ""),
        ]))
    raw = "\n".join(sorted(rows))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def transition_key(task_id, contract_id, revision, head, reviewer, review_type, digest):
    raw = "|".join([
        str(task_id or ""),
        str(contract_id or ""),
        str(a.revision_int(revision) if revision is not None else ""),
        str(head or ""),
        str(reviewer or "saul"),
        str(review_type or "implementation"),
        str(digest or ""),
    ])
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def queue_dir(root, cid):
    d = a.contract_dir(root, cid) / "queue"
    d.mkdir(parents=True, exist_ok=True)
    return d


def item_path(root, cid, key):
    return queue_dir(root, cid) / f"{key}.yaml"


def load_item(root, cid, key):
    p = item_path(root, cid, key)
    return a.read_yaml(p) if p.is_file() else None


def list_items(root, cid):
    d = a.contract_dir(root, cid) / "queue"
    if not d.is_dir():
        return []
    return [a.read_yaml(p) for p in sorted(d.glob("*.yaml")) if a.read_yaml(p)]


def classify_owner(cfg, findings):
    """Return (owner, case) for a REQUEST_CHANGES finding set."""
    expanding = [f for f in findings or [] if review._expanding(cfg, f)]
    if expanding:
        return "human", "C"
    ordinary = [f for f in findings or [] if not review._expanding(cfg, f)]
    if not ordinary:
        return "sai", "noop"
    needs_contract = False
    for f in ordinary:
        field = f.get("contract_field") or ""
        act = f.get("action") or ""
        req = str(f.get("requested_change") or "").lower()
        if "authority-expanding" in req or "human-approved" in req:
            return "human", "C"
        if field == "allowed_paths" and act in ("add", "expand"):
            return "human", "C"
        if field == "allowed_paths" and act in ("narrow", "change"):
            needs_contract = True
    if needs_contract:
        return "cora", "B"
    return "contractor", "A"


def expected_next(owner, case):
    if owner == "human":
        return "HUMAN_AUTHORITY_REQUIRED"
    if owner == "cora":
        return "CORA_CLAIM_THEN_CONTRACTOR_REMEDIATE"
    if owner == "contractor":
        return "CONTRACTOR_REMEDIATE"
    return "SAI_EVAL"


def new_item(review_doc, *, task_id, owner, case, attempt=1):
    findings = review_doc.get("findings") or []
    digest = findings_digest(findings)
    cid = review_doc.get("contract_id")
    rev = review_doc.get("contract_revision")
    head = review_doc.get("implementation_head")
    key = transition_key(
        task_id, cid, rev, head,
        review_doc.get("reviewer") or "saul",
        review_doc.get("review_type") or "implementation",
        digest,
    )
    return {
        "work_item_id": key,
        "task_id": task_id,
        "source_event_id": review_doc.get("idempotency_key") or review_doc.get("github_run_id"),
        "source_reviewer": review_doc.get("reviewer") or "saul",
        "source_review_id": review_doc.get("idempotency_key"),
        "source_github_run": str(review_doc.get("github_run_id") or ""),
        "source_head": head,
        "source_contract_revision": rev,
        "contract_id": cid,
        "findings": [f.get("id") for f in findings],
        "findings_digest": digest,
        "owner": owner,
        "routing_case": case,
        "state": "queued",
        "expected_next_state": expected_next(owner, case),
        "claimed_by_runtime": None,
        "claim_generation": 1,
        "attempt": attempt,
        "max_attempts": 5,
        "created_at": a.utcnow(),
        "claimed_at": None,
        "last_material_progress_at": None,
        "completed_at": None,
        "result_contract_revision": None,
        "result_head_sha": None,
        "result_artifacts": [],
    }


def claim_or_noop(root, item, *, runtime=None):
    """First writer wins. Duplicate eval of the same key is a cheap NOOP."""
    cid = item.get("contract_id")
    key = item.get("work_item_id")
    if not cid or not key:
        return "error", None, "missing contract_id or work_item_id"
    existing = load_item(root, cid, key)
    if existing:
        st = existing.get("state")
        owner = existing.get("owner")
        if st in ACTIVE or st in TERMINAL:
            return "noop", existing, (
                f"NOOP remediation already owned by {owner} "
                f"state={st} key={key}"
            )
    item = dict(item)
    item["state"] = "claimed"
    item["claimed_at"] = a.utcnow()
    item["claimed_by_runtime"] = runtime or a.detect_runtime()
    item["last_material_progress_at"] = item["claimed_at"]
    a.write_yaml(item_path(root, cid, key), item)
    return "claimed", item, f"CLAIMED owner={item.get('owner')} key={key}"


def eval_review(root, review_doc, *, task_id=None, runtime=None):
    """Cheap state evaluation. Does not invoke an LLM."""
    cfg = a.load_config(root)
    disp = review_doc.get("disposition")
    cid = review_doc.get("contract_id")
    if disp == "APPROVE":
        return "noop", None, "NOOP Saul APPROVE; no remediation dispatch"
    if disp == "BLOCKED":
        return "noop", None, f"NOOP Saul BLOCKED ({review_doc.get('reason')}); no auto-dispatch"
    if disp != "REQUEST_CHANGES":
        return "noop", None, f"NOOP unhandled disposition {disp}"
    if not cid:
        return "error", None, "FAIL review missing contract_id"
    task_id = (task_id or os.environ.get("SAI_TASK_ID") or "").strip()
    ptr = a.load_pointer(root, cid) or {}
    rev = a.load_revision(
        root, cid, ptr.get("current_revision") or review_doc.get("contract_revision"),
    )
    if not task_id:
        task_id = str((rev or {}).get("requested_task") or cid)
    owner, case = classify_owner(cfg, review_doc.get("findings") or [])
    item = new_item(review_doc, task_id=task_id, owner=owner, case=case)
    # Same digest+head already claimed?
    for prev in list_items(root, cid):
        if (prev.get("findings_digest") == item["findings_digest"]
                and prev.get("source_head") == item["source_head"]
                and prev.get("state") in ACTIVE + TERMINAL):
            return "noop", prev, (
                f"NOOP remediation already owned by {prev.get('owner')} "
                f"state={prev.get('state')} key={prev.get('work_item_id')}"
            )
    return claim_or_noop(root, item, runtime=runtime)


def metrics(root, cid):
    items = list_items(root, cid)
    claimed = [i for i in items if i.get("state") != "queued"]
    return {
        "items": len(items),
        "active": len([i for i in items if i.get("state") in ACTIVE]),
        "claimed_or_beyond": len(claimed),
        "unique_digests": len({i.get("findings_digest") for i in items}),
    }


def self_test() -> int:
    errors = []
    findings = [
        {"id": "CTO-010", "severity": "P0", "contract_field": "saul_review_workflow",
         "action": "narrow", "requested_change": "trusted ref", "authority_expanding": False},
        {"id": "CTO-009", "severity": "P0", "contract_field": "authorization",
         "action": "add", "requested_change": "grant", "authority_expanding": False},
    ]
    d1 = findings_digest(findings)
    d2 = findings_digest(list(reversed(findings)))
    if d1 != d2:
        errors.append("digest must be order-independent")
    with a.NamedTemp() if False else _tmp() as tmp:
        root = tmp
        (root / ".ai/_config").mkdir(parents=True)
        (root / ".ai/contracts/demo/revisions").mkdir(parents=True)
        a.write_yaml(root / ".ai/_config/authorization.yaml", a.load_yaml(
            "authority_expanding_actions: [expand, grant-capability, remove-denied-path]\n"
            "officers: {}\n"
        ))
        a.write_json(root / ".ai/contracts/demo/contract.json", {
            "contract_id": "demo", "current_revision": "v1",
        })
        a.write_yaml(root / ".ai/contracts/demo/revisions/v1.yaml", {
            "contract_id": "demo", "revision": 1, "revision_label": "v1",
            "requested_task": "20260813-demo-task",
            "agent_id": "ctr-code-demo",
        })
        doc = {
            "reviewer": "saul", "disposition": "REQUEST_CHANGES",
            "contract_id": "demo", "contract_revision": 1,
            "implementation_head": "abc123", "review_type": "implementation",
            "idempotency_key": "k1", "github_run_id": "1",
            "findings": findings,
        }
        st, item, msg = eval_review(root, doc, task_id="20260813-demo-task")
        if st != "claimed":
            errors.append(f"first eval should claim, got {st} {msg}")
        st2, item2, msg2 = eval_review(root, doc, task_id="20260813-demo-task")
        if st2 != "noop":
            errors.append(f"second eval should noop, got {st2} {msg2}")
        # ten duplicate evals, still one item
        for _ in range(8):
            eval_review(root, doc, task_id="20260813-demo-task")
        items = list_items(root, "demo")
        if len(items) != 1:
            errors.append(f"expected 1 work item after 10 evals, got {len(items)}")
        # expanding finding -> human
        exp = dict(doc)
        exp["findings"] = [{
            "id": "CTO-X", "severity": "P0", "contract_field": "allowed_paths",
            "action": "add", "requested_change": "src/**", "authority_expanding": True,
        }]
        exp["implementation_head"] = "def456"
        exp["idempotency_key"] = "k2"
        st3, item3, _ = eval_review(root, exp, task_id="20260813-demo-task")
        if st3 != "claimed" or (item3 or {}).get("owner") != "human":
            errors.append(f"expanding should claim human, got {st3} {item3}")
    if errors:
        print("sai-dispatch self-test FAIL:", file=sys.stderr)
        for e in errors:
            print(" ", e, file=sys.stderr)
        return 1
    print("sai-dispatch self-test: PASS (10 duplicate evals -> 1 claim; expanding -> human)")
    return 0


class _tmp:
    def __enter__(self):
        import tempfile
        self.d = Path(tempfile.mktemp(prefix="sai-q-"))
        self.d.mkdir()
        return self.d

    def __exit__(self, *exc):
        import shutil
        shutil.rmtree(self.d, ignore_errors=True)


def cmd(argv=None):
    import argparse
    p = argparse.ArgumentParser(prog="sai-dispatch-transition")
    p.add_argument("--from-file")
    p.add_argument("--eval-only", action="store_true")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--task-id")
    p.add_argument("--contract-id")
    p.add_argument("--pr", default=None)
    args = p.parse_args(argv)
    if args.self_test:
        return self_test()
    root = a.toplevel()
    if not args.from_file:
        print("FAIL --from-file required (or --self-test)", file=sys.stderr)
        return 2
    doc = a.read_yaml(Path(args.from_file))
    st, item, msg = eval_review(root, doc, task_id=args.task_id)
    print(msg)
    key = (item or {}).get("work_item_id")
    if args.pr and key:
        print(f"<!-- sai-transition:{key} -->")
    if item:
        print(json.dumps({
            "status": st,
            "key": item.get("work_item_id"),
            "owner": item.get("owner"),
            "state": item.get("state"),
            "case": item.get("routing_case"),
            "digest": item.get("findings_digest"),
            "expected_next": item.get("expected_next_state"),
        }, indent=2))
    return 0 if st in ("claimed", "noop") else 1


if __name__ == "__main__":
    raise SystemExit(cmd(sys.argv[1:]))
