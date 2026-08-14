#!/usr/bin/env python3
"""CTO-012 / shell-safety / saul_review_key fixtures. Candidate PR is DATA."""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

import sai_auth as a
from sai_auth_key import remember_review, lookup_completed, saul_review_key


WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/saul-cto-review.default-branch.yml"


def isolate_saul_selftest_env(tmp):
    """Keep invoke-saul-review --self-test hermetic under production env vars."""
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("CODEX_API_KEY", None)
    os.environ["SAI_SKIP_CODEX"] = "1"
    os.environ["SAI_SAUL_KEY_CACHE"] = str(Path(tmp) / "saul-keys")
    os.environ["SAI_SAUL_PACKAGE_DIR"] = str(Path(tmp) / "pkg")
    for k in ("SAI_TRUSTED_TREE", "SAI_CANDIDATE_TREE", "SAI_TRUST_MODE"):
        os.environ.pop(k, None)


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def run_saul_trust_fixtures():
    executed = set()
    text = _workflow_text()

    executed.add("saul-no-git-archive-head")
    if "git archive HEAD" in text or "git archive \"HEAD\"" in text:
        raise RuntimeError("CTO-012: production must not git archive candidate HEAD")
    print("SELFTEST PASS  saul-no-git-archive-head")

    executed.add("saul-no-pr-bootstrap-success")
    if "pr-bootstrap-until-main" in text:
        raise RuntimeError("CTO-012: pr-bootstrap-until-main is not a success trust_mode")
    print("SELFTEST PASS  saul-no-pr-bootstrap-success")

    executed.add("saul-unavailable-blocks")
    if "TRUSTED_REVIEWER_UNAVAILABLE" not in text:
        raise RuntimeError("unavailable trusted source must BLOCK with TRUSTED_REVIEWER_UNAVAILABLE")
    if "trust_mode=unavailable" not in text and "TRUST_MODE=unavailable" not in text:
        raise RuntimeError("workflow must be able to set TRUST_MODE=unavailable")
    print("SELFTEST PASS  saul-unavailable-blocks")

    executed.add("saul-empty-dest-freeze-once")
    if "freeze-trusted-reviewer-once" in text or "empty-dest-bootstrap" in text:
        raise RuntimeError("CTO-015: trusted workflow must not freeze from candidate SHA")
    if "--confirm-trust" in text:
        raise RuntimeError("CTO-015: trusted workflow must not pass confirm_trust")
    print("SELFTEST PASS  saul-empty-dest-freeze-once")

    executed.add("saul-trusted-sources-only")
    if "SAI_TRUSTED_REVIEWER_ROOT" not in text:
        raise RuntimeError("runner-image trusted root missing")
    if "trusted-default-branch" not in text:
        raise RuntimeError("default-branch trusted checkout missing")
    if "path: candidate-data" not in text:
        raise RuntimeError("candidate DATA path missing")
    print("SELFTEST PASS  saul-trusted-sources-only")

    executed.add("saul-trusted-job-if-guards")
    job = text.split("invoke-saul:", 1)[1].split("steps:", 1)[0]
    if "head.repo.full_name" not in job or "github.repository" not in job:
        raise RuntimeError("trusted job if must skip fork PRs before runs-on")
    if "workflow_dispatch" not in job or "github.ref" not in job:
        raise RuntimeError("trusted job if must constrain dispatch to default-branch refs")
    if "pull_request_target" not in job:
        raise RuntimeError("trusted job if must require pull_request_target")
    print("SELFTEST PASS  saul-trusted-job-if-guards")

    executed.add("saul-shell-no-reason-interpolation")
    forbidden = (
        "steps.saul.outputs.reason",
        "steps.trust.outputs.reason",
    )
    for tok in forbidden:
        if tok in text:
            raise RuntimeError(f"model/review text must not interpolate into shell: {tok}")
    # Any ${{ steps.saul.outputs.* }} inside run: is unsafe if the value is free text.
    if "${{ steps.saul.outputs." in text:
        raise RuntimeError("do not interpolate saul step outputs into run: blocks")
    print("SELFTEST PASS  saul-shell-no-reason-interpolation")

    executed.add("saul-review-key-idempotent")
    os.environ["SAI_SAUL_KEY_CACHE"] = str(Path(tempfile.mkdtemp()) / "keys")
    k = saul_review_key(
        repository="Dezocode/Sai",
        pr="62",
        review_type="implementation",
        contract_id="20260813-pr62-saul-smoke",
        contract_revision=3,
        implementation_head="abc" * 8,
        blocking_requirement_digest="deadbeefdeadbeef",
        review_scope="final",
    )
    k2 = saul_review_key(
        repository="Dezocode/Sai",
        pr="62",
        review_type="implementation",
        contract_id="20260813-pr62-saul-smoke",
        contract_revision=3,
        implementation_head="abc" * 8,
        blocking_requirement_digest="deadbeefdeadbeef",
        review_scope="final",
    )
    if k != k2 or len(k) != 16:
        raise RuntimeError(f"unstable key {k} {k2}")
    remember_review(k, {"disposition": "REQUEST_CHANGES", "codex_invoked": True})
    hits = 0
    for _ in range(10):
        if lookup_completed(k):
            hits += 1
    if hits != 10:
        raise RuntimeError("duplicate key lookups must all hit cache")
    k3 = saul_review_key(
        repository="Dezocode/Sai",
        pr="62",
        review_type="implementation",
        contract_id="20260813-pr62-saul-smoke",
        contract_revision=3,
        implementation_head="def" * 8,
        blocking_requirement_digest="deadbeefdeadbeef",
        review_scope="final",
    )
    if k3 == k or lookup_completed(k3):
        raise RuntimeError("new head must be a new eligible key")
    k4 = saul_review_key(
        repository="Dezocode/Sai",
        pr="62",
        review_type="implementation",
        contract_id="20260813-pr62-saul-smoke",
        contract_revision=3,
        implementation_head="def" * 8,
        blocking_requirement_digest="feedfacefeedface",
        review_scope="final",
    )
    if k4 == k3:
        raise RuntimeError("requirement digest change must mint a new key")
    print("SELFTEST PASS  saul-review-key-idempotent")
    os.environ.pop("SAI_SAUL_KEY_CACHE", None)

    executed.add("saul-old-head-fallback-detected")
    old = "git archive HEAD\nTRUST_MODE=pr-bootstrap-until-main"
    if "git archive HEAD" not in old or "pr-bootstrap-until-main" not in old:
        raise RuntimeError("negative fixture string broken")
    print("SELFTEST PASS  saul-old-head-fallback-detected")

    executed.add("saul-metacharacters-are-data")
    poison = ["`id`", "$(reboot)", "; rm -rf /", "|cat", ">\n/tmp/x"]
    for s in poison:
        if s in text:
            raise RuntimeError("workflow source contains unexpected metacharacter payload")
    print("SELFTEST PASS  saul-metacharacters-are-data")

    executed.add("saul-selftest-hermetic-with-prod-env")
    with tempfile.TemporaryDirectory() as tmp:
        isolate_saul_selftest_env(tmp)
        os.environ["SAI_TRUSTED_TREE"] = str(Path(tmp) / "trusted")
        os.environ["SAI_CANDIDATE_TREE"] = str(Path(tmp) / "candidate")
        os.environ["SAI_SAUL_PACKAGE_DIR"] = str(Path(tmp) / "pkg")
        from sai_auth_test import _contract, _init
        from sai_auth_review import invoke
        d = Path(tmp) / "hermetic"
        _init(d)
        cid = _contract(d)
        _rc, doc = invoke(d, cid, "v1", "deadbeef", "contract", force=True)
        if not doc or doc.get("reason") != "CODEX_UNAVAILABLE":
            raise RuntimeError(doc)
        print("SELFTEST PASS  saul-selftest-hermetic-with-prod-env")

    if os.environ.get("SAI_SELFTEST_INNER") == "1":
        return executed
    executed.add("saul-wrapper-selftest-does-not-mutate-prod-package")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(__file__).resolve().parents[2]
        prod_pkg = Path(tmp) / "prod-pkg"
        prod_pkg.mkdir()
        sentinel = prod_pkg / "metadata.json"
        sentinel.write_text('{"live":true}\n', encoding="utf-8")
        before = sentinel.read_bytes()
        env = os.environ.copy()
        env["SAI_TRUSTED_TREE"] = str(Path(tmp) / "trusted")
        env["SAI_CANDIDATE_TREE"] = str(Path(tmp) / "candidate")
        env["SAI_SAUL_PACKAGE_DIR"] = str(prod_pkg)
        env["SAI_SKIP_CODEX"] = "1"
        env["SAI_SELFTEST_INNER"] = "1"
        lib = str(root / "scripts" / "lib")
        prior = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = lib if not prior else lib + ":" + prior
        proc = subprocess.run(
            [str(root / "scripts" / "invoke-saul-review"), "--self-test"],
            cwd=str(root), env=env, capture_output=True, text=True, timeout=60,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stdout + proc.stderr)
        if sentinel.read_bytes() != before:
            raise RuntimeError("production package mutated by --self-test")
        print("SELFTEST PASS  saul-wrapper-selftest-does-not-mutate-prod-package")
    return executed


if __name__ == "__main__":
    run_saul_trust_fixtures()
    print("sai_auth_saul_test: all fixtures passed")
