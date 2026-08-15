#!/usr/bin/env python3
"""Canonical Saul attestation v2: Ed25519 exact-state payload + verify.

ONE verifier for shard/architecture PASS, blocker clearance, merge_viable_saul,
technical convergence, sai-resume READY, READY_FOR_HUMAN_REVIEW.
Trust: SAI_SAUL_ATTEST_PUB or trusted-reviewer tree. Never candidate HEAD.
Fixture Ed25519 keys are TEST ONLY (tempfile + openssl). No production key.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sai_auth as a  # noqa: E402
from sai_auth_saul_identity import (  # noqa: E402
    DISPOSITIONS, INVALID_SAUL_IDENTITY, PRIV_MARKERS, QUALIFY_OK,
    REJECT_SOURCES, _has_private_key, _rev, sign_payload, verify_sig,
)

ALG = "ed25519"
VERSION = 2
STALE_AFTER_SECONDS = 7 * 24 * 3600
TRUST_PUB_REL = ".ai/authorizations/saul-attestation-ed25519.pub"
HISTORICAL_V1_NOT_MERGE_VIABLE = "HISTORICAL_V1_NOT_MERGE_VIABLE"
CANDIDATE_KEY_SUBSTITUTION = "CANDIDATE_KEY_SUBSTITUTION"
TRUST_ANCHOR_UNAVAILABLE = "TRUST_ANCHOR_UNAVAILABLE"
STALE_REVIEW = "STALE_REVIEW"

# Canonical signed field names (schema: saul-attestation-v2.schema.json).
CANONICAL_KEYS = (
    "alg", "architecture_domain", "architecture_proof_digest",
    "base_sha", "codex_invoked", "contract_id", "contract_revision",
    "coverage_manifest_digest", "diff_digest", "disposition",
    "findings_digest", "implementation_head", "key_id", "pr",
    "program_id", "repository", "review_id", "review_scope",
    "review_type", "reviewed_unit_digest_root", "shard_id",
    "shard_input_digest", "synthetic", "ts", "version",
)


def att_version(review) -> int | None:
    if not isinstance(review, dict):
        return None
    att = review.get("attestation") if isinstance(review.get("attestation"), dict) else {}
    v = (att or {}).get("version")
    if v is None:
        return 1
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def findings_digest(review: dict) -> str:
    findings = review.get("findings") or []
    return hashlib.sha256(
        json.dumps(findings, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pubkey_fingerprint(pub_pem) -> str | None:
    """SHA-256 of SPKI DER. pub_pem is a path or PEM text."""
    path, tmp = _materialize_pub(pub_pem)
    if path is None:
        return None
    try:
        r = subprocess.run(
            ["openssl", "pkey", "-pubin", "-in", str(path), "-outform", "DER"],
            capture_output=True, check=False,
        )
        if r.returncode != 0 or not r.stdout:
            return None
        return _sha256_bytes(r.stdout)
    except OSError:
        return None
    finally:
        if tmp:
            Path(tmp).unlink(missing_ok=True)


def _materialize_pub(pub_pem):
    if pub_pem is None or pub_pem == "":
        return None, None
    if isinstance(pub_pem, Path):
        return (pub_pem if pub_pem.is_file() else None), None
    text = str(pub_pem)
    if "BEGIN" in text:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pub")
        tmp.write(text.encode("utf-8"))
        tmp.close()
        return Path(tmp.name), tmp.name
    p = Path(text)
    return (p if p.is_file() else None), None


def _inside(path, root) -> bool:
    if path is None or root is None:
        return False
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except (ValueError, OSError):
        return False


def resolve_trusted_pub(pub_pem=None, *, root=None, candidate_root=None):
    """Non-candidate trust only. Missing production pub → fail closed."""
    cand = None
    if candidate_root is not None:
        cand = Path(candidate_root).resolve()
    elif root is not None:
        cand = Path(root).resolve()

    def take(src):
        if src is None or src == "":
            return None, None, None
        if "BEGIN" in str(src) and not Path(str(src)).exists():
            path, tmp = _materialize_pub(src)
            return path, None, tmp
        p = Path(str(src))
        if not p.is_file():
            return None, None, None
        if cand is not None and _inside(p, cand):
            return None, CANDIDATE_KEY_SUBSTITUTION, None
        return p, None, None

    got, why, tmp = take(pub_pem)
    if why:
        return None, why, None
    if got is not None:
        return got, None, tmp

    env = os.environ.get("SAI_SAUL_ATTEST_PUB") or ""
    if env:
        got, why, tmp = take(env)
        if why:
            return None, why, None
        if got is not None:
            return got, None, tmp

    trusted = os.environ.get("SAI_TRUSTED_REVIEWER_ROOT") or os.environ.get("SAI_TRUSTED_TREE") or ""
    if trusted:
        p = Path(trusted) / TRUST_PUB_REL
        if p.is_file():
            if cand is not None and _inside(p, cand):
                return None, CANDIDATE_KEY_SUBSTITUTION, None
            return p, None, None
    return None, TRUST_ANCHOR_UNAVAILABLE, None


def canonical_payload_v2(review: dict) -> bytes:
    att = review.get("attestation") if isinstance(review.get("attestation"), dict) else {}
    att = att or {}
    rid = (
        att.get("review_id") or review.get("saul_review_key")
        or review.get("idempotency_key") or review.get("github_run_id") or ""
    )
    ts = att.get("ts") or review.get("recorded_at") or ""
    crev = review.get("contract_revision")
    ni = _rev(crev)
    body = {
        "alg": att.get("alg") or ALG,
        "architecture_domain": review.get("architecture_domain"),
        "architecture_proof_digest": review.get("architecture_proof_digest"),
        "base_sha": review.get("base_sha"),
        "codex_invoked": review.get("codex_invoked"),
        "contract_id": review.get("contract_id"),
        "contract_revision": ni if ni is not None else crev,
        "coverage_manifest_digest": review.get("coverage_manifest_digest"),
        "diff_digest": review.get("diff_digest"),
        "disposition": review.get("disposition"),
        "findings_digest": findings_digest(review),
        "implementation_head": review.get("implementation_head"),
        "key_id": att.get("key_id") or review.get("key_id"),
        "pr": review.get("pr"),
        "program_id": review.get("program_id"),
        "repository": review.get("repository"),
        "review_id": rid,
        "review_scope": review.get("review_scope"),
        "review_type": review.get("review_type"),
        "reviewed_unit_digest_root": review.get("reviewed_unit_digest_root"),
        "shard_id": review.get("shard_id"),
        "shard_input_digest": review.get("shard_input_digest"),
        "synthetic": review.get("synthetic"),
        "ts": ts,
        "version": VERSION,
    }
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _parse_ts(value):
    if not value:
        return None
    text = str(value).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def verify_attestation_v2(
    review, *, exact_head, exact_rev=None, exact_base=None, expected=None,
    pub_pem=None, root=None, candidate_root=None, now=None,
    max_age_seconds=STALE_AFTER_SECONDS,
) -> tuple[bool, str]:
    """Fail closed. Returns (True, 'OK') or (False, reason)."""
    fail = (False, INVALID_SAUL_IDENTITY)
    if not isinstance(review, dict) or _has_private_key(review):
        return fail
    if att_version(review) != VERSION:
        return fail
    if review.get("reviewer") != "saul":
        return fail
    if review.get("runtime") != "codex":
        return fail
    if review.get("codex_invoked") is not True:
        return fail
    if review.get("synthetic") is not False:
        return fail
    if str(review.get("implementation_head") or "") != str(exact_head or ""):
        return fail
    if exact_rev is not None and _rev(review.get("contract_revision")) != _rev(exact_rev):
        return fail
    if exact_base is not None and str(review.get("base_sha") or "") != str(exact_base):
        return fail
    disp = str(review.get("disposition") or "").upper()
    if disp not in DISPOSITIONS:
        return fail
    att = review.get("attestation") if isinstance(review.get("attestation"), dict) else {}
    att = att or {}
    if att.get("source") in REJECT_SOURCES:
        return fail
    if (att.get("alg") or ALG) != ALG:
        return fail
    if att.get("public_key") or att.get("pub") or review.get("public_key"):
        return False, CANDIDATE_KEY_SUBSTITUTION
    ts = _parse_ts(att.get("ts") or review.get("recorded_at"))
    if ts is None:
        return fail
    now = now or datetime.now(timezone.utc)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    if (now - ts).total_seconds() > max_age_seconds:
        return False, STALE_REVIEW
    expected = expected or {}
    for key, val in expected.items():
        if str(review.get(key) or "") != str(val):
            return fail
    sig_b64 = att.get("sig")
    if not sig_b64:
        return fail
    try:
        sig = base64.b64decode(sig_b64, validate=False)
    except Exception:
        return fail
    if not sig:
        return fail
    pub, why, tmp = resolve_trusted_pub(
        pub_pem, root=root, candidate_root=candidate_root,
    )
    try:
        if pub is None:
            return False, why or TRUST_ANCHOR_UNAVAILABLE
        fp = pubkey_fingerprint(pub)
        if not fp or str(att.get("key_id") or "") != fp:
            return fail
        try:
            payload = canonical_payload_v2(review)
        except (TypeError, ValueError):
            return fail
        if not verify_sig(payload, sig, pub):
            return fail
        return True, QUALIFY_OK
    finally:
        if tmp:
            Path(tmp).unlink(missing_ok=True)


def shard_pass_ok(review, **kw) -> tuple[bool, str]:
    return verify_attestation_v2(review, **kw)


def architecture_pass_ok(review, **kw) -> tuple[bool, str]:
    return verify_attestation_v2(review, **kw)


def technical_clearance_ok(review, **kw) -> tuple[bool, str]:
    return verify_attestation_v2(review, **kw)


def make_signed_review_v2(priv_pem, pub_pem, **fields) -> dict:
    """Test/Hostinger helper. Defaults are placeholders, not live PR identity."""
    ts = fields.pop("ts", None) or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    fp = pubkey_fingerprint(pub_pem) or ""
    review = {
        "reviewer": fields.pop("reviewer", "saul"),
        "runtime": fields.pop("runtime", "codex"),
        "codex_invoked": fields.pop("codex_invoked", True),
        "synthetic": fields.pop("synthetic", False),
        "implementation_head": fields.pop("implementation_head", "0" * 40),
        "base_sha": fields.pop("base_sha", "1" * 40),
        "contract_id": fields.pop("contract_id", "test-contract"),
        "contract_revision": fields.pop("contract_revision", 1),
        "review_type": fields.pop("review_type", "implementation"),
        "review_scope": fields.pop("review_scope", "exact-state"),
        "disposition": fields.pop("disposition", "APPROVE"),
        "findings": fields.pop("findings", []),
        "idempotency_key": fields.pop("idempotency_key", "test-saul-v2"),
        "repository": fields.pop("repository", "example/test"),
        "pr": fields.pop("pr", None),
        "program_id": fields.pop("program_id", None),
        "diff_digest": fields.pop("diff_digest", "d" * 64),
        "shard_id": fields.pop("shard_id", "shard-exact"),
        "shard_input_digest": fields.pop("shard_input_digest", "a" * 64),
        "coverage_manifest_digest": fields.pop("coverage_manifest_digest", "b" * 64),
        "reviewed_unit_digest_root": fields.pop("reviewed_unit_digest_root", "c" * 64),
        "architecture_domain": fields.pop("architecture_domain", "authorization"),
        "architecture_proof_digest": fields.pop("architecture_proof_digest", "e" * 64),
    }
    review.update(fields)
    att = dict(review.get("attestation") or {})
    att["version"] = VERSION
    att["alg"] = ALG
    att["ts"] = ts
    att["review_id"] = att.get("review_id") or review.get("idempotency_key")
    att["key_id"] = fp
    review["attestation"] = att
    sig = sign_payload(canonical_payload_v2(review), str(priv_pem))
    att["sig"] = base64.b64encode(sig).decode("ascii")
    return review


def cmd(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        from sai_auth_saul_attestation_v2_test import run_authenticity_selftest
        n = run_authenticity_selftest()
        print(f"verify-saul-authenticity self-test: {len(n)} fixtures executed")
        return 0
    p = argparse.ArgumentParser(prog="verify-saul-authenticity")
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--head", required=True)
    p.add_argument("--rev", default=None)
    p.add_argument("--base", default=None)
    p.add_argument("--pub", default=None)
    args = p.parse_args(argv)
    review = a.read_yaml(Path(args.inp))
    ok, reason = verify_attestation_v2(
        review or {}, exact_head=args.head, exact_rev=args.rev,
        exact_base=args.base, pub_pem=args.pub,
    )
    print("VERIFY", "OK" if ok else reason)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(cmd())
