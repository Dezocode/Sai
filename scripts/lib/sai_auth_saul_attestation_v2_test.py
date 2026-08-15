#!/usr/bin/env python3
"""Attestation v2 authenticity fixtures. Keys: openssl tempfile only. Never commit."""
from __future__ import annotations

import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from sai_auth_saul_attestation_v2 import (
    CANDIDATE_KEY_SUBSTITUTION, HISTORICAL_V1_NOT_MERGE_VIABLE, QUALIFY_OK,
    STALE_REVIEW, architecture_pass_ok, make_signed_review_v2, shard_pass_ok,
    verify_attestation_v2,
)
from sai_auth_saul_check import (
    CHECK_NAME, ZERO_AUTHORITY, check_name_is_proof, evaluate_check,
    fake_named_check_has_authority,
)
from sai_auth_saul_identity import (
    make_signed_review, merge_viable_saul, qualifying_saul_review,
)

HEAD_A = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
HEAD_B = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
BASE_A = "cccccccccccccccccccccccccccccccccccccccc"
BASE_B = "dddddddddddddddddddddddddddddddddddddddd"
REV = 12

REQUIRED = (
    "cursor-fake-saul-bad",
    "fake-github-check-bad",
    "candidate-key-substitution-bad",
    "wrong-public-key-bad",
    "tampered-shard-digest-bad",
    "tampered-architecture-digest-bad",
    "historical-v1-not-merge-viable-bad",
    "exact-state-v2-fixture-good",
    "unsigned-bad",
    "synthetic-review-bad",
    "codex-not-invoked-bad",
    "wrong-head-bad",
    "wrong-base-bad",
    "stale-review-bad",
    "primary-unique-good",
    "primary-none-bad",
    "primary-ambiguous-bad",
    "primary-no-cross-contam-good",
)


def _keys(td: Path):
    priv, pub = td / "fix.pem", td / "fix.pub"
    subprocess.run(
        ["openssl", "genpkey", "-algorithm", "Ed25519", "-out", str(priv)],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["openssl", "pkey", "-in", str(priv), "-pubout", "-out", str(pub)],
        check=True, capture_output=True,
    )
    return priv, pub


def _v2(priv, pub, **kw):
    kw.setdefault("implementation_head", HEAD_A)
    kw.setdefault("base_sha", BASE_A)
    kw.setdefault("contract_revision", REV)
    return make_signed_review_v2(str(priv), str(pub), **kw)


def _fail(ok, reason, label, executed, want=None):
    if ok:
        raise RuntimeError((label, ok, reason))
    if want and reason != want:
        raise RuntimeError((label, reason, want))
    executed.add(label)
    print(f"SELFTEST PASS  {label}")


def run_authenticity_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        priv, pub = _keys(td)
        good = _v2(priv, pub)

        ok, reason = verify_attestation_v2(
            good, exact_head=HEAD_A, exact_rev=REV, exact_base=BASE_A, pub_pem=str(pub),
        )
        mv, mreason = merge_viable_saul(good, HEAD_A, REV, pub_pem=str(pub))
        sp, _ = shard_pass_ok(
            good, exact_head=HEAD_A, exact_rev=REV, exact_base=BASE_A, pub_pem=str(pub),
        )
        ap, _ = architecture_pass_ok(
            good, exact_head=HEAD_A, exact_rev=REV, exact_base=BASE_A, pub_pem=str(pub),
        )
        if not ok or reason != QUALIFY_OK or not mv or mreason != QUALIFY_OK or not sp or not ap:
            raise RuntimeError((ok, reason, mv, mreason, sp, ap))
        executed.add("exact-state-v2-fixture-good")
        print("SELFTEST PASS  exact-state-v2-fixture-good")

        fake = _v2(priv, pub, attestation={"source": "cursor"})
        ok, reason = verify_attestation_v2(
            fake, exact_head=HEAD_A, exact_rev=REV, pub_pem=str(pub),
        )
        _fail(ok, reason, "cursor-fake-saul-bad", executed)

        ev = evaluate_check(
            {"name": CHECK_NAME, "actor": "cursor"},
            good, exact_head=HEAD_A, exact_rev=REV, pub_pem=str(pub),
        )
        if ev.get("authority") != ZERO_AUTHORITY or check_name_is_proof(CHECK_NAME):
            raise RuntimeError(ev)
        if fake_named_check_has_authority({"name": CHECK_NAME, "actor": "cursor"}):
            raise RuntimeError("named check must have zero authority")
        executed.add("fake-github-check-bad")
        print("SELFTEST PASS  fake-github-check-bad")

        cand = td / "candidate"
        auth = cand / ".ai" / "authorizations"
        auth.mkdir(parents=True)
        cand_pub = auth / "saul-attestation-ed25519.pub"
        cand_pub.write_bytes(pub.read_bytes())
        subst = _v2(priv, cand_pub)
        ok, reason = verify_attestation_v2(
            subst, exact_head=HEAD_A, exact_rev=REV,
            pub_pem=str(cand_pub), root=str(cand),
        )
        _fail(ok, reason, "candidate-key-substitution-bad", executed,
              want=CANDIDATE_KEY_SUBSTITUTION)

        priv2, pub2 = td / "b.pem", td / "b.pub"
        subprocess.run(
            ["openssl", "genpkey", "-algorithm", "Ed25519", "-out", str(priv2)],
            check=True, capture_output=True,
        )
        subprocess.run(
            ["openssl", "pkey", "-in", str(priv2), "-pubout", "-out", str(pub2)],
            check=True, capture_output=True,
        )
        signed_a = _v2(priv, pub)
        ok, reason = verify_attestation_v2(
            signed_a, exact_head=HEAD_A, exact_rev=REV, pub_pem=str(pub2),
        )
        _fail(ok, reason, "wrong-public-key-bad", executed)

        tam_s = dict(good)
        tam_s["shard_input_digest"] = "f" * 64
        ok, reason = verify_attestation_v2(
            tam_s, exact_head=HEAD_A, exact_rev=REV, pub_pem=str(pub),
        )
        _fail(ok, reason, "tampered-shard-digest-bad", executed)

        tam_a = dict(good)
        tam_a["architecture_proof_digest"] = "f" * 64
        ok, reason = verify_attestation_v2(
            tam_a, exact_head=HEAD_A, exact_rev=REV, pub_pem=str(pub),
        )
        _fail(ok, reason, "tampered-architecture-digest-bad", executed)

        v1 = make_signed_review(
            str(priv), str(pub), implementation_head=HEAD_A, contract_revision=REV,
        )
        qok, _ = qualifying_saul_review(v1, HEAD_A, REV, pub_pem=str(pub))
        mv, mreason = merge_viable_saul(v1, HEAD_A, REV, pub_pem=str(pub))
        if not qok or mv or mreason != HISTORICAL_V1_NOT_MERGE_VIABLE:
            raise RuntimeError((qok, mv, mreason))
        executed.add("historical-v1-not-merge-viable-bad")
        print("SELFTEST PASS  historical-v1-not-merge-viable-bad")

        nosig = dict(good)
        nosig["attestation"] = dict(good.get("attestation") or {})
        nosig["attestation"].pop("sig", None)
        ok, reason = verify_attestation_v2(
            nosig, exact_head=HEAD_A, exact_rev=REV, pub_pem=str(pub),
        )
        _fail(ok, reason, "unsigned-bad", executed)

        syn = _v2(priv, pub, synthetic=True)
        ok, reason = verify_attestation_v2(
            syn, exact_head=HEAD_A, exact_rev=REV, pub_pem=str(pub),
        )
        _fail(ok, reason, "synthetic-review-bad", executed)

        noc = _v2(priv, pub, codex_invoked=False)
        ok, reason = verify_attestation_v2(
            noc, exact_head=HEAD_A, exact_rev=REV, pub_pem=str(pub),
        )
        _fail(ok, reason, "codex-not-invoked-bad", executed)

        ok, reason = verify_attestation_v2(
            good, exact_head=HEAD_B, exact_rev=REV, pub_pem=str(pub),
        )
        _fail(ok, reason, "wrong-head-bad", executed)

        ok, reason = verify_attestation_v2(
            good, exact_head=HEAD_A, exact_rev=REV, exact_base=BASE_B, pub_pem=str(pub),
        )
        _fail(ok, reason, "wrong-base-bad", executed)

        stale = _v2(priv, pub, ts="2020-01-01T00:00:00Z")
        ok, reason = verify_attestation_v2(
            stale, exact_head=HEAD_A, exact_rev=REV, pub_pem=str(pub),
            now=datetime.now(timezone.utc),
        )
        _fail(ok, reason, "stale-review-bad", executed, want=STALE_REVIEW)

    return executed


def run_authenticity_selftest():
    executed = run_authenticity_fixtures()
    from sai_auth_primary_context_test import run_primary_fixtures
    executed |= run_primary_fixtures()
    missing = [n for n in REQUIRED if n not in executed]
    if missing:
        raise RuntimeError(("missing fixtures", missing))
    return executed


if __name__ == "__main__":
    run_authenticity_selftest()
    print("sai_auth_saul_attestation_v2_test: OK")
