#!/usr/bin/env python3
"""GitHub Check `Saul / Product Quality` plus generated blocker Checks.

Check name, GitHub actor, similarly named Cursor checks, and YAML reviewer
strings have zero clearance authority. Only verify_attestation_v2 is proof.
Publishes no secret material (no private keys, no PEM). One publisher emits
the aggregate Check and `Saul / Blocker / <ID>` from the canonical ledger.
IMPLEMENTED_AWAITING_SAUL / DISCOVERED / missing proof / Cursor actor = failure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sai_auth as a  # noqa: E402
from sai_auth_saul_attestation_v2 import QUALIFY_OK, verify_attestation_v2  # noqa: E402

CHECK_NAME = "Saul / Product Quality"
BLOCKER_CHECK_PREFIX = "Saul / Blocker / "
EXACT_STATE_SCHEMA = "saul-exact-state-review.schema.json"
ZERO_AUTHORITY = "ZERO_AUTHORITY"
ATTESTATION_V2 = "ATTESTATION_V2"
REJECT_ACTORS = ("cursor", "contractor", "sai", "cora", "candidate")
NON_SUCCESS_STATUS = frozenset({
    "IMPLEMENTED_AWAITING_SAUL", "DISCOVERED", "IMPLEMENTING", "TRIAGED",
    "CLAIMED", "OPEN", "BLOCKED_EXTERNAL", "AWAITING_SAUL", "AWAITING_SAI",
    "IMPLEMENTED", "VERIFYING",
})
PASS_STATUS = frozenset({"PASSED_BY_SAUL", "PASSED"})


def check_name_is_proof(_name=None) -> bool:
    """A Check name is never sufficient clearance."""
    return False


def blocker_check_name(blocker_id) -> str:
    return f"{BLOCKER_CHECK_PREFIX}{blocker_id}"


def is_canonical_check_name(name) -> bool:
    n = str(name or "")
    return n == CHECK_NAME or n.startswith(BLOCKER_CHECK_PREFIX)


def canonical_blockers(root=None) -> list:
    from sai_auth_blockers import load_ledger
    root = root or a.toplevel() or os.getcwd()
    try:
        data, _ = load_ledger(root)
    except Exception:
        return []
    out = []
    for row in data.get("blockers") or []:
        bid = row.get("blocker_id")
        if not bid:
            continue
        st = str(row.get("status") or "")
        if st.startswith("SUPERSEDED"):
            continue
        rec = dict(row)
        rec["check_name"] = blocker_check_name(bid)
        out.append(rec)
    return out


def _sig_digest(review: dict) -> str | None:
    att = review.get("attestation") if isinstance(review.get("attestation"), dict) else {}
    sig = (att or {}).get("sig") or ""
    if not sig:
        return None
    return hashlib.sha256(str(sig).encode("ascii", errors="replace")).hexdigest()


def evidence_surface(review: dict, *, verified: bool, reason: str | None = None,
                     check_name: str | None = None) -> dict:
    """Non-secret proof fields for the Check output. Never includes PEM/keys."""
    att = review.get("attestation") if isinstance(review.get("attestation"), dict) else {}
    att = att or {}
    blob = json.dumps(review, default=str)
    if any(m in blob for m in ("BEGIN PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY")):
        raise ValueError("refusing to publish private key material")
    return {
        "check_name": check_name or CHECK_NAME,
        "check_name_is_proof": False,
        "verified": bool(verified),
        "reason": reason,
        "base_sha": review.get("base_sha"),
        "implementation_head": review.get("implementation_head"),
        "key_id": att.get("key_id"),
        "shard_id": review.get("shard_id"),
        "shard_input_digest": review.get("shard_input_digest"),
        "coverage_manifest_digest": review.get("coverage_manifest_digest"),
        "reviewed_unit_digest_root": review.get("reviewed_unit_digest_root"),
        "architecture_domain": review.get("architecture_domain"),
        "architecture_proof_digest": review.get("architecture_proof_digest"),
        "findings_digest": review.get("findings_digest") or att.get("findings_digest"),
        "disposition": review.get("disposition"),
        "codex_invoked": review.get("codex_invoked"),
        "synthetic": review.get("synthetic"),
        "sig_digest": _sig_digest(review),
        "review_id": att.get("review_id"),
        "attestation_version": att.get("version"),
    }


def evaluate_check(check: dict, review, *, exact_head, exact_rev=None,
                   exact_base=None, pub_pem=None, root=None) -> dict:
    """Name match is not proof. Cursor/fake similarly named Checks: zero authority."""
    check = check if isinstance(check, dict) else {"name": check}
    name = check.get("name") or check.get("context") or ""
    actor = str(check.get("actor") or check.get("app") or "").lower()
    canonical = is_canonical_check_name(name)
    if actor in REJECT_ACTORS or not isinstance(review, dict):
        ev = evidence_surface(review if isinstance(review, dict) else {},
                              verified=False, reason=ZERO_AUTHORITY, check_name=name)
        ev.update({
            "canonical_name_match": canonical,
            "authority": ZERO_AUTHORITY,
            "actor": actor,
        })
        return ev
    ok, reason = verify_attestation_v2(
        review, exact_head=exact_head, exact_rev=exact_rev,
        exact_base=exact_base, pub_pem=pub_pem, root=root,
    )
    authority = ATTESTATION_V2 if ok else ZERO_AUTHORITY
    ev = evidence_surface(review, verified=ok, reason=reason, check_name=name)
    ev.update({
        "canonical_name_match": canonical,
        "authority": authority,
        "actor": actor,
        "check_name_observed": name,
    })
    return ev


def fake_named_check_has_authority(check: dict) -> bool:
    """Cursor (or any) similarly named Check never grants clearance by itself."""
    return False


def _payload(name, review, *, exact_head, exact_rev=None, pub_pem=None,
             root=None, extra_fail=False) -> dict:
    ok, reason = verify_attestation_v2(
        review or {}, exact_head=exact_head, exact_rev=exact_rev,
        pub_pem=pub_pem, root=root,
    )
    if extra_fail:
        ok = False
        reason = reason if reason != QUALIFY_OK else "BLOCKER_NOT_SAUL_PASS"
    ev = evidence_surface(review or {}, verified=ok, reason=reason, check_name=name)
    conclusion = "success" if ok else "failure"
    return {
        "name": name,
        "head_sha": exact_head,
        "status": "completed",
        "conclusion": conclusion,
        "output": {
            "title": name,
            "summary": json.dumps({
                "check_name_is_proof": False,
                "verified": ok,
                "reason": reason if reason != QUALIFY_OK else "OK",
                "evidence": ev,
            }, sort_keys=True),
        },
        "authority": ATTESTATION_V2 if ok else ZERO_AUTHORITY,
    }


def build_publish_payload(review, *, exact_head, exact_rev=None, pub_pem=None,
                          root=None, conclusion_override=None) -> dict:
    payload = _payload(
        CHECK_NAME, review, exact_head=exact_head, exact_rev=exact_rev,
        pub_pem=pub_pem, root=root,
    )
    if conclusion_override and payload.get("authority") == ATTESTATION_V2:
        payload["conclusion"] = conclusion_override
    if payload.get("authority") != ATTESTATION_V2:
        payload["conclusion"] = "failure"
    return payload


def blocker_extra_fail(blocker: dict, review, actor="") -> bool:
    if str(actor or "").lower() in REJECT_ACTORS:
        return True
    st = str((blocker or {}).get("status") or "")
    if st in NON_SUCCESS_STATUS or st not in PASS_STATUS:
        return True
    if not isinstance(review, dict):
        return True
    return False


def build_blocker_payloads(review, blockers, *, exact_head, exact_rev=None,
                           pub_pem=None, root=None, actor="") -> list:
    out = []
    for row in blockers or []:
        bid = row.get("blocker_id")
        if not bid:
            continue
        extra = blocker_extra_fail(row, review, actor=actor)
        out.append(_payload(
            blocker_check_name(bid), review, exact_head=exact_head,
            exact_rev=exact_rev, pub_pem=pub_pem, root=root, extra_fail=extra,
        ))
    return out


def check_run_body(payload: dict) -> dict:
    """GitHub Checks API body. Name from payload. No PEM/keys."""
    blob = json.dumps(payload, default=str)
    if any(m in blob for m in ("BEGIN PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY")):
        raise ValueError("refusing to publish private key material")
    name = payload.get("name") or CHECK_NAME
    return {
        "name": name,
        "head_sha": payload.get("head_sha"),
        "status": "completed",
        "conclusion": payload.get("conclusion") or "failure",
        "output": payload.get("output") or {
            "title": name,
            "summary": json.dumps({"check_name_is_proof": False, "verified": False}),
        },
    }


def publish_check_run(payload: dict, *, repo: str) -> int:
    """POST/update Check via gh. Requires GH_TOKEN. Fail closed if missing."""
    if not os.environ.get("GH_TOKEN"):
        print("BLOCKED GH_TOKEN_MISSING", file=sys.stderr)
        return 1
    if not repo:
        print("BLOCKED REPO_MISSING", file=sys.stderr)
        return 1
    body = json.dumps(check_run_body(payload))
    proc = subprocess.run(
        ["gh", "api", f"repos/{repo}/check-runs", "-X", "POST", "--input", "-"],
        input=body, capture_output=True, text=True,
    )
    if proc.stdout:
        print(proc.stdout, end="" if proc.stdout.endswith("\n") else "\n")
    if proc.returncode != 0:
        err = (proc.stderr or "").strip()
        print(f"BLOCKED CHECK_PUBLISH_FAILED {err[:200]}", file=sys.stderr)
        return 1
    return 0


def cmd(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    p = argparse.ArgumentParser(prog="saul-publish-check")
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--head", required=True)
    p.add_argument("--rev", default=None)
    p.add_argument("--pub", default=None)
    p.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY") or "")
    p.add_argument("--publish", action="store_true")
    p.add_argument("--dry-run", action="store_true", default=False)
    p.add_argument("--no-blockers", action="store_true")
    args = p.parse_args(argv)
    review = a.read_yaml(Path(args.inp)) or {}
    payload = build_publish_payload(
        review, exact_head=args.head, exact_rev=args.rev, pub_pem=args.pub,
    )
    extras = []
    if not args.no_blockers:
        extras = build_blocker_payloads(
            review, canonical_blockers(), exact_head=args.head,
            exact_rev=args.rev, pub_pem=args.pub,
        )
    print(json.dumps({"aggregate": payload, "blockers": extras}, indent=2, default=str)
          if extras else json.dumps(payload, indent=2, default=str))
    if args.publish and not args.dry_run:
        rc = publish_check_run(payload, repo=args.repo)
        if rc != 0:
            return rc
        for item in extras:
            rc = publish_check_run(item, repo=args.repo)
            if rc != 0:
                return rc
    return 0 if payload.get("authority") == ATTESTATION_V2 else 1


if __name__ == "__main__":
    raise SystemExit(cmd())
