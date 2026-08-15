#!/usr/bin/env python3
"""Saul identity fixtures: Cursor/contractor/unsigned/forged never qualify."""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

import sai_auth as a
from sai_auth_blockers import attempt_clear, append_blocker
from sai_auth_saul_identity import (
    INVALID_SAUL_IDENTITY, QUALIFY_OK, canonical_payload,
    key_inside_worktree, make_signed_review, merge_viable_saul,
    qualifying_saul_review, sign_payload,
)

HEAD_A = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
HEAD_B = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
REV = 12
REPO = Path(__file__).resolve().parents[2]


def _keys(td: Path):
    priv, pub = td / "test.pem", td / "test.pub"
    subprocess.run(
        ["openssl", "genpkey", "-algorithm", "Ed25519", "-out", str(priv)],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["openssl", "pkey", "-in", str(priv), "-pubout", "-out", str(pub)],
        check=True, capture_output=True,
    )
    return priv, pub


def _fail(review, head, rev, pub, label, executed):
    ok, reason = qualifying_saul_review(review, head, rev, pub_pem=str(pub) if pub else None)
    if ok or reason != INVALID_SAUL_IDENTITY:
        raise RuntimeError((label, ok, reason))
    executed.add(label)
    print(f"SELFTEST PASS  {label}")


def _unsigned(**kw):
    d = {
        "reviewer": "saul", "runtime": "codex", "codex_invoked": True,
        "synthetic": False, "implementation_head": HEAD_A,
        "contract_id": "20260813-pr62-saul-smoke", "contract_revision": REV,
        "review_type": "implementation", "disposition": "APPROVE", "findings": [],
        "idempotency_key": "unsigned",
    }
    d.update(kw)
    return d


def _ledger(root: Path):
    rel = "ledger.yaml"
    a.write_yaml(root / rel, {"blockers": [], "policy": {"never_delete_history": True}})
    append_blocker(root, {
        "blocker_id": "B-001", "category": "technical",
        "clearance_authority": "saul", "status": "DISCOVERED",
        "description": "identity fixture",
    }, rel=rel)
    return rel


def run_identity_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        priv, pub = _keys(td)
        good = make_signed_review(
            str(priv), str(pub), implementation_head=HEAD_A, contract_revision=REV,
        )
        ok, reason = qualifying_saul_review(good, HEAD_A, REV, pub_pem=str(pub))
        executed.add("signed-codex-approve-qualifies")
        if not ok or reason != QUALIFY_OK:
            raise RuntimeError((ok, reason))
        print("SELFTEST PASS  signed-codex-approve-qualifies")

        _fail(_unsigned(
            reviewer="saul", runtime="cursor-cloud-named-subagent",
            codex_invoked=False,
        ), HEAD_A, REV, pub, "cursor-subagent-named-saul", executed)

        _fail(_unsigned(runtime="codex", codex_invoked=False),
              HEAD_A, REV, pub, "codex-invoked-false", executed)

        _fail(_unsigned(runtime="cursor"), HEAD_A, REV, pub,
              "runtime-cursor", executed)

        rel = _ledger(td)
        r = attempt_clear(td, "B-001", "saul", review_id="x", head=HEAD_A, rel=rel)
        executed.add("actor-saul-cli-spoof")
        if r.get("status") != "REJECT" or r.get("reason") != INVALID_SAUL_IDENTITY:
            raise RuntimeError(r)
        print("SELFTEST PASS  actor-saul-cli-spoof")

        syn = make_signed_review(
            str(priv), str(pub), implementation_head=HEAD_A,
            contract_revision=REV, synthetic=True,
        )
        _fail(syn, HEAD_A, REV, pub, "synthetic-true-signed", executed)

        nosig = dict(good)
        nosig["attestation"] = dict(good.get("attestation") or {})
        nosig["attestation"].pop("sig", None)
        _fail(nosig, HEAD_A, REV, pub, "correct-fields-no-signature", executed)

        forged = dict(good)
        att = dict(good.get("attestation") or {})
        raw = bytearray(__import__("base64").b64decode(att["sig"]))
        raw[0] ^= 0x01
        att["sig"] = __import__("base64").b64encode(bytes(raw)).decode("ascii")
        forged["attestation"] = att
        _fail(forged, HEAD_A, REV, pub, "forged-signature", executed)

        signed_a = make_signed_review(
            str(priv), str(pub), implementation_head=HEAD_A, contract_revision=REV,
        )
        _fail(signed_a, HEAD_B, REV, pub, "signed-head-a-verify-head-b", executed)
        _fail(signed_a, HEAD_A, 11, pub, "signed-rev-mismatch", executed)
        _fail(signed_a, HEAD_B, REV, pub, "stale-real-saul-old-head", executed)

        _fail(_unsigned(), HEAD_A, REV, pub, "candidate-authored-unsigned-yaml", executed)

        sai = make_signed_review(
            str(priv), str(pub), reviewer="sai", implementation_head=HEAD_A,
            contract_revision=REV,
        )
        _fail(sai, HEAD_A, REV, pub, "sai-authored-even-if-signed", executed)

        _fail(_unsigned(runtime="cursor"), HEAD_A, REV, pub,
              "contractor-authored-runtime-cursor", executed)
        r = attempt_clear(
            td, "B-001", "contractor", review_id="x", head=HEAD_A, rel=rel,
            review=_unsigned(runtime="cursor"),
        )
        executed.add("contractor-actor-with-cursor-review")
        if r.get("status") != "REJECT":
            raise RuntimeError(r)
        print("SELFTEST PASS  contractor-actor-with-cursor-review")

        yml = td / "signed.yaml"
        a.write_yaml(yml, good)
        old = os.environ.get("SAI_SAUL_ATTEST_PUB")
        os.environ["SAI_SAUL_ATTEST_PUB"] = str(pub)
        try:
            cid = "20260813-pr62-saul-smoke"
            (td / ".ai/contracts" / cid).mkdir(parents=True)
            a.write_json(td / ".ai/contracts" / cid / "contract.json", {
                "contract_id": cid, "current_revision": "v12",
            })
            stale = make_signed_review(
                str(priv), str(pub), implementation_head=HEAD_A,
                contract_revision=11,
            )
            r = attempt_clear(
                td, "B-001", "saul", review_id=None, head=HEAD_A, rel=rel,
                review=stale,
            )
            executed.add("signed-rev11-live-pointer-v12")
            if r.get("status") != "REJECT" or r.get("reason") != INVALID_SAUL_IDENTITY:
                raise RuntimeError(r)
            print("SELFTEST PASS  signed-rev11-live-pointer-v12")
            r = attempt_clear(
                td, "B-001", "cursor", review_id=None, head=HEAD_A, rel=rel,
                from_file=str(yml),
            )
            executed.add("saul-signed-artifact-can-pass")
            if r.get("status") != "PASSED_BY_SAUL":
                raise RuntimeError(r)
            if r.get("clearance_head") != HEAD_A:
                raise RuntimeError(r)
            if not r.get("blocker_id"):
                raise RuntimeError(r)
            print("SELFTEST PASS  saul-signed-artifact-can-pass")
        finally:
            if old is None:
                os.environ.pop("SAI_SAUL_ATTEST_PUB", None)
            else:
                os.environ["SAI_SAUL_ATTEST_PUB"] = old

        from sai_auth_saul_attestation_v2 import make_signed_review_v2
        v2good = make_signed_review_v2(
            str(priv), str(pub), implementation_head=HEAD_A, contract_revision=REV,
        )
        mv, mreason = merge_viable_saul(v2good, HEAD_A, REV, pub_pem=str(pub))
        executed.add("merge-viable-signed-approve")
        if not mv or mreason != QUALIFY_OK:
            raise RuntimeError((mv, mreason))
        print("SELFTEST PASS  merge-viable-signed-approve")

        rc_rev = make_signed_review(
            str(priv), str(pub), implementation_head=HEAD_A, contract_revision=REV,
            disposition="REQUEST_CHANGES",
        )
        qok, _ = qualifying_saul_review(rc_rev, HEAD_A, REV, pub_pem=str(pub))
        mv2, _ = merge_viable_saul(rc_rev, HEAD_A, REV, pub_pem=str(pub))
        executed.add("identity-ok-request-changes-not-merge-viable")
        if not qok or mv2:
            raise RuntimeError((qok, mv2))
        print("SELFTEST PASS  identity-ok-request-changes-not-merge-viable")

        inrepo = REPO / "scripts" / "lib" / ".tmp-saul-key-must-not-exist.pem"
        executed.add("refuse-in-tree-key-path")
        if not key_inside_worktree(inrepo, REPO):
            raise RuntimeError("repo-relative key must be inside worktree")
        if key_inside_worktree(priv, REPO):
            raise RuntimeError("temp key must be outside worktree")
        print("SELFTEST PASS  refuse-in-tree-key-path")

        payload = canonical_payload(good)
        executed.add("canonical-payload-stable")
        if payload != canonical_payload(good):
            raise RuntimeError("canonical payload must be stable")
        sign_payload(payload, str(priv))
        print("SELFTEST PASS  canonical-payload-stable")

    boot = REPO / "scripts" / "saul-hostinger-bootstrap-review"
    env = {k: v for k, v in os.environ.items()
           if k not in ("SAI_SAUL_BOOTSTRAP", "SAI_SAUL_ATTEST_KEY", "SAI_TRUSTED_TREE")}
    lib = str(REPO / "scripts" / "lib")
    prior = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = lib if not prior else lib + os.pathsep + prior
    proc = subprocess.run(
        [str(boot), "--self-test"], cwd=str(REPO), env=env, capture_output=True, text=True,
    )
    executed.add("bootstrap-not-hostinger-saul")
    text = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 2 or "NOT_HOSTINGER_SAUL" not in text:
        raise RuntimeError((proc.returncode, text))
    print("SELFTEST PASS  bootstrap-not-hostinger-saul")
    return executed


if __name__ == "__main__":
    run_identity_fixtures()
    print("sai_auth_saul_identity_test: OK")
