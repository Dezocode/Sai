#!/usr/bin/env python3
"""GitHub Check `Saul / Product Quality` — live evidence surface, NOT proof.

Check name, GitHub actor, similarly named Cursor checks, and YAML reviewer
strings have zero clearance authority. Only verify_attestation_v2 is proof.
Publishes no secret material (no private keys, no PEM).
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
ZERO_AUTHORITY = "ZERO_AUTHORITY"
ATTESTATION_V2 = "ATTESTATION_V2"
REJECT_ACTORS = ("cursor", "contractor", "sai", "cora", "candidate")


def check_name_is_proof(_name=None) -> bool:
    """A Check name is never sufficient clearance."""
    return False


def is_canonical_check_name(name) -> bool:
    return str(name or "") == CHECK_NAME


def _sig_digest(review: dict) -> str | None:
    att = review.get("attestation") if isinstance(review.get("attestation"), dict) else {}
    sig = (att or {}).get("sig") or ""
    if not sig:
        return None
    return hashlib.sha256(str(sig).encode("ascii", errors="replace")).hexdigest()


def evidence_surface(review: dict, *, verified: bool, reason: str | None = None) -> dict:
    """Non-secret proof fields for the Check output. Never includes PEM/keys."""
    att = review.get("attestation") if isinstance(review.get("attestation"), dict) else {}
    att = att or {}
    blob = json.dumps(review, default=str)
    if any(m in blob for m in ("BEGIN PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY")):
        raise ValueError("refusing to publish private key material")
    return {
        "check_name": CHECK_NAME,
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
                              verified=False, reason=ZERO_AUTHORITY)
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
    ev = evidence_surface(review, verified=ok, reason=reason)
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


def build_publish_payload(review, *, exact_head, exact_rev=None, pub_pem=None,
                          root=None, conclusion_override=None) -> dict:
    ok, reason = verify_attestation_v2(
        review or {}, exact_head=exact_head, exact_rev=exact_rev,
        pub_pem=pub_pem, root=root,
    )
    ev = evidence_surface(review or {}, verified=ok, reason=reason)
    # Never fake PASS: unsigned/BLOCKED/unverified → failure.
    conclusion = conclusion_override or ("success" if ok else "failure")
    if not ok:
        conclusion = "failure"
    return {
        "name": CHECK_NAME,
        "head_sha": exact_head,
        "status": "completed",
        "conclusion": conclusion,
        "output": {
            "title": CHECK_NAME,
            "summary": json.dumps({
                "check_name_is_proof": False,
                "verified": ok,
                "reason": reason if reason != QUALIFY_OK else "OK",
                "evidence": ev,
            }, sort_keys=True),
        },
        "authority": ATTESTATION_V2 if ok else ZERO_AUTHORITY,
    }


def check_run_body(payload: dict) -> dict:
    """GitHub Checks API body. Name exact. No PEM/keys."""
    blob = json.dumps(payload, default=str)
    if any(m in blob for m in ("BEGIN PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY")):
        raise ValueError("refusing to publish private key material")
    return {
        "name": CHECK_NAME,
        "head_sha": payload.get("head_sha"),
        "status": "completed",
        "conclusion": payload.get("conclusion") or "failure",
        "output": payload.get("output") or {
            "title": CHECK_NAME,
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
    args = p.parse_args(argv)
    review = a.read_yaml(Path(args.inp)) or {}
    payload = build_publish_payload(
        review, exact_head=args.head, exact_rev=args.rev, pub_pem=args.pub,
    )
    print(json.dumps(payload, indent=2, default=str))
    if args.publish and not args.dry_run:
        rc = publish_check_run(payload, repo=args.repo)
        if rc != 0:
            return rc
    return 0 if payload.get("authority") == ATTESTATION_V2 else 1


if __name__ == "__main__":
    raise SystemExit(cmd())
