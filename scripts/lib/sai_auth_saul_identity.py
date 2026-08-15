#!/usr/bin/env python3
"""Canonical Saul identity: Hostinger Codex attestation, not actor strings."""
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

QUALIFY_OK = "OK"
INVALID_SAUL_IDENTITY = "INVALID_SAUL_IDENTITY"
TECHNICAL_CLEARANCE_REQUIRES_QUALIFYING_SAUL = (
    "TECHNICAL_CLEARANCE_REQUIRES_QUALIFYING_SAUL"
)
INVALID_READY_STATE_NONQUALIFYING_SAUL = (
    "INVALID_READY_STATE_NONQUALIFYING_SAUL"
)
DISPOSITIONS = ("APPROVE", "REQUEST_CHANGES", "BLOCKED")
REJECT_SOURCES = ("cursor", "contractor", "sai", "candidate")
PRIV_MARKERS = (
    "BEGIN PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY", "BEGIN ED25519 PRIVATE KEY",
)
DEFAULT_PUB_REL = ".ai/authorizations/saul-attestation-ed25519.pub"


def _rev(rev):
    if rev in (None, ""):
        return None
    try:
        return a.revision_int(rev)
    except (TypeError, ValueError):
        return None


def canonical_payload(review: dict) -> bytes:
    findings = review.get("findings") or []
    digest = hashlib.sha256(
        json.dumps(findings, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
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
        "contract_id": review.get("contract_id"),
        "contract_revision": ni if ni is not None else crev,
        "disposition": review.get("disposition"),
        "findings_digest": digest,
        "implementation_head": review.get("implementation_head"),
        "review_id": rid,
        "review_type": review.get("review_type"),
        "reviewer": review.get("reviewer"),
        "runtime": review.get("runtime"),
        "ts": ts,
    }
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_payload(payload: bytes, priv_pem_path: str) -> bytes:
    inf = tempfile.NamedTemporaryFile(delete=False)
    outf = tempfile.NamedTemporaryFile(delete=False)
    inf.close()
    outf.close()
    try:
        Path(inf.name).write_bytes(payload)
        subprocess.run(
            ["openssl", "pkeyutl", "-sign", "-inkey", str(priv_pem_path),
             "-rawin", "-in", inf.name, "-out", outf.name],
            check=True, capture_output=True,
        )
        return Path(outf.name).read_bytes()
    finally:
        Path(inf.name).unlink(missing_ok=True)
        Path(outf.name).unlink(missing_ok=True)


def _pub_file(pub_pem) -> Path | None:
    if pub_pem is None or pub_pem == "":
        return None
    if isinstance(pub_pem, Path):
        return pub_pem if pub_pem.is_file() else None
    text = str(pub_pem)
    if "BEGIN" in text:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pub")
        tmp.write(text.encode("utf-8"))
        tmp.close()
        return Path(tmp.name)
    p = Path(text)
    return p if p.is_file() else None


def verify_sig(payload: bytes, sig: bytes, pub_pem: str | Path) -> bool:
    pub = _pub_file(pub_pem)
    if pub is None:
        return False
    inf = tempfile.NamedTemporaryFile(delete=False)
    sigf = tempfile.NamedTemporaryFile(delete=False)
    inf.close()
    sigf.close()
    try:
        Path(inf.name).write_bytes(payload)
        Path(sigf.name).write_bytes(sig)
        r = subprocess.run(
            ["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(pub),
             "-rawin", "-in", inf.name, "-sigfile", sigf.name],
            capture_output=True,
        )
        return r.returncode == 0
    except OSError:
        return False
    finally:
        Path(inf.name).unlink(missing_ok=True)
        Path(sigf.name).unlink(missing_ok=True)


def resolve_pub_pem(pub_pem=None, root=None):
    got = _pub_file(pub_pem) if pub_pem else None
    if got is not None:
        return got
    env = os.environ.get("SAI_SAUL_ATTEST_PUB") or ""
    if env:
        got = _pub_file(env)
        if got is not None:
            return got
    root = Path(root) if root else Path(a.toplevel() or ".")
    default = root / DEFAULT_PUB_REL
    if default.is_file():
        return default
    return None


def _has_private_key(review: dict) -> bool:
    blob = json.dumps(review, default=str)
    return any(m in blob for m in PRIV_MARKERS)


def qualifying_saul_review(review, exact_head, exact_contract_revision, *,
                           pub_pem=None) -> tuple[bool, str]:
    """Fail closed. Returns (True, 'OK') or (False, INVALID_SAUL_IDENTITY)."""
    fail = (False, INVALID_SAUL_IDENTITY)
    if not isinstance(review, dict) or _has_private_key(review):
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
    if _rev(review.get("contract_revision")) != _rev(exact_contract_revision):
        return fail
    disp = str(review.get("disposition") or "").upper()
    if disp not in DISPOSITIONS:
        return fail
    att = review.get("attestation") if isinstance(review.get("attestation"), dict) else {}
    att = att or {}
    if att.get("source") in REJECT_SOURCES:
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
    pub = resolve_pub_pem(pub_pem)
    if pub is None:
        return fail
    try:
        payload = canonical_payload(review)
    except (TypeError, ValueError):
        return fail
    if not verify_sig(payload, sig, pub):
        return fail
    return True, QUALIFY_OK


def merge_viable_saul(review, exact_head, exact_rev, **kw) -> tuple[bool, str]:
    """Merge-viable requires attestation.version=2 + canonical v2 verify.

    v1 may still historically qualify via qualifying_saul_review; never merge_viable.
    """
    from sai_auth_saul_attestation_v2 import (
        HISTORICAL_V1_NOT_MERGE_VIABLE, att_version, verify_attestation_v2,
    )
    ver = att_version(review)
    if ver != 2:
        return False, HISTORICAL_V1_NOT_MERGE_VIABLE if ver == 1 else INVALID_SAUL_IDENTITY
    ok, reason = verify_attestation_v2(
        review, exact_head=exact_head, exact_rev=exact_rev,
        pub_pem=kw.get("pub_pem"), root=kw.get("root"),
        candidate_root=kw.get("candidate_root"),
        exact_base=kw.get("exact_base"), expected=kw.get("expected"),
        now=kw.get("now"),
    )
    if not ok:
        return False, reason
    disp = str(review.get("disposition") or "").upper()
    if disp == "APPROVE":
        return True, QUALIFY_OK
    return False, "NOT_MERGE_VIABLE"


def make_signed_review(priv_pem, pub_pem, **fields) -> dict:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    review = {
        "reviewer": fields.pop("reviewer", "saul"),
        "runtime": fields.pop("runtime", "codex"),
        "codex_invoked": fields.pop("codex_invoked", True),
        "synthetic": fields.pop("synthetic", False),
        "implementation_head": fields.pop("implementation_head", "a" * 40),
        "contract_id": fields.pop("contract_id", "20260813-pr62-saul-smoke"),
        "contract_revision": fields.pop("contract_revision", 12),
        "review_type": fields.pop("review_type", "implementation"),
        "disposition": fields.pop("disposition", "APPROVE"),
        "findings": fields.pop("findings", []),
        "idempotency_key": fields.pop("idempotency_key", "test-saul-id"),
    }
    review.update(fields)
    att = dict(review.get("attestation") or {})
    att.setdefault("alg", "ed25519")
    att.setdefault("ts", ts)
    att.setdefault("review_id", review.get("idempotency_key"))
    review["attestation"] = att
    sig = sign_payload(canonical_payload(review), str(priv_pem))
    att["sig"] = base64.b64encode(sig).decode("ascii")
    return review


def key_inside_worktree(key_path, root=None) -> bool:
    root = Path(root or a.toplevel() or ".").resolve()
    key = Path(key_path).resolve()
    try:
        key.relative_to(root)
        return True
    except ValueError:
        return False


def _cmd_sign(inp, out, key):
    root = a.toplevel() or os.getcwd()
    if key_inside_worktree(key, root):
        print("FAIL key must live outside the git worktree", file=sys.stderr)
        return 1
    review = a.read_yaml(Path(inp))
    if not isinstance(review, dict):
        print("FAIL missing review", file=sys.stderr)
        return 1
    att = dict(review.get("attestation") or {})
    att.setdefault("alg", "ed25519")
    att.setdefault("ts", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    att.setdefault(
        "review_id",
        review.get("saul_review_key") or review.get("idempotency_key")
        or review.get("github_run_id") or "",
    )
    review["attestation"] = att
    sig = sign_payload(canonical_payload(review), key)
    att["sig"] = base64.b64encode(sig).decode("ascii")
    a.write_yaml(Path(out), review)
    print("SIGNED", out)
    return 0


def _cmd_verify(inp, pub):
    review = a.read_yaml(Path(inp))
    ok, reason = qualifying_saul_review(
        review,
        (review or {}).get("implementation_head"),
        (review or {}).get("contract_revision"),
        pub_pem=pub,
    )
    print("VERIFY", "OK" if ok else reason)
    return 0 if ok else 1


def cmd(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        from sai_auth_saul_identity_test import run_identity_fixtures
        n = run_identity_fixtures()
        print(f"saul-attest self-test: {len(n)} fixtures executed")
        return 0
    p = argparse.ArgumentParser(prog="saul-attest")
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("sign")
    sp.add_argument("--in", dest="inp", required=True)
    sp.add_argument("--out", required=True)
    sp.add_argument("--key", required=True)
    vp = sub.add_parser("verify")
    vp.add_argument("--in", dest="inp", required=True)
    vp.add_argument("--pub", default=None)
    args = p.parse_args(argv)
    if args.cmd == "sign":
        return _cmd_sign(args.inp, args.out, args.key)
    if args.cmd == "verify":
        return _cmd_verify(args.inp, args.pub)
    return 2


if __name__ == "__main__":
    raise SystemExit(cmd())
