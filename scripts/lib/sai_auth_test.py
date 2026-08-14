#!/usr/bin/env python3
"""Synthetic authorization fixtures (positive + negative) and e2e helpers."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sai_auth as a  # noqa: E402

POLICY = """
version: 1
enforcement: {mode: fail-closed, skip_commits_missing_policy: true, trust_session: false}
bootstrap:
  enabled: true
  task_ids: ["20260813-1517-auth-loop-cursor-cloud"]
  agent_trailers: [cursor-cloud]
  allowed_path_prefixes: [".ai/", "scripts/", "tests/"]
officers:
  ceo: {name: Sai, assume_runtimes: [cursor-cloud-vm], write_class: governance, may_record_sai_verification: true}
  ctr-admin: {name: Cora, assume_runtimes: [cursor-cloud-vm], write_class: contract-admin, may_implement_product: false}
  dezo-sec-codex1: {name: Saul, assume_runtimes: [codex-desktop], write_class: cto, cursor_impersonation: forbidden}
path_classes:
  contract-admin: [".ai/contracts/**", ".ai/requests/**", ".ai/agents/**", ".ai/runs/**"]
  governance: [".ai/**"]
  cto: [".ai/agents/saul/**"]
protected_denied_for_contractors: [".ai/agents/saul/**", ".ai/shared/memory/decisions/**", ".ai/authorizations/**"]
contractor:
  require_contract: true
  default_denied_paths: [".ai/agents/saul/**"]
authority_expanding_actions: [expand, grant-capability, remove-denied-path]
officer_grants:
  required: true
idempotency:
  skip_if_unchanged_request_changes: true
codex:
  missing_disposition: BLOCKED
  never_approve_without_codex: true
"""

REGISTRY = {
    "agents": [
        {"agent_id": "ceo", "name": "Sai", "status": "active",
         "primary_runtime": "cursor-cloud-vm", "charter": ".ai/agents/_roles/ceo/CHARTER.md"},
        {"agent_id": "ctr-admin", "name": "Cora", "status": "active",
         "primary_runtime": "cursor-cloud-vm",
         "charter": ".ai/agents/_roles/contract-administrator/CHARTER.md"},
        {"agent_id": "dezo-sec-codex1", "name": "Saul", "status": "active",
         "primary_runtime": "codex-desktop",
         "charter": ".ai/agents/_roles/secretary-dezocode/CHARTER.md"},
        {"agent_id": "ctr-code-auth1", "name": "AuthImpl", "status": "provisional",
         "primary_runtime": "cursor-cloud-vm",
         "charter": ".ai/agents/_roles/contractor-coding/CHARTER.md"},
    ]
}

FIXTURE_RESULTS = {}


def _git(cwd, *args, check=True):
    p = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(p.stderr or p.stdout)
    return p


def _init(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=path, capture_output=True, check=True)
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test Agent")
    (path / ".ai/_config").mkdir(parents=True, exist_ok=True)
    (path / ".ai/agents").mkdir(parents=True, exist_ok=True)
    (path / ".ai/contracts").mkdir(parents=True, exist_ok=True)
    (path / ".ai/requests").mkdir(parents=True, exist_ok=True)
    a.write_yaml(path / ".ai/_config/authorization.yaml", a.load_yaml(POLICY))
    a.write_json(path / ".ai/agents/registry.json", REGISTRY)
    (path / ".ai/authorizations/grants").mkdir(parents=True, exist_ok=True)
    a.write_yaml(path / ".ai/authorizations/grants/grant-test-ctr-admin.yaml", {
        "id": "grant-test-ctr-admin",
        "principal": "ctr-admin",
        "runtime": "cursor-cloud-vm",
        "task_ids": [
            "20260813-1517-auth-loop-cursor-cloud",
            "20260813-9999-auth-test-ctr-code-auth1",
        ],
        "paths": [".ai/**"],
        "actions": ["write"],
        "issued_by": "test",
    })
    _git(path, "add", "-A")
    _git(path, "commit", "-m",
         "bootstrap policy\n\nTask-ID: 20260813-1517-auth-loop-cursor-cloud\nAgent: cursor-cloud\n")
    return path


def _commit(path, files, msg, trailers):
    for rel, content in files.items():
        fp = path / rel
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content, encoding="utf-8")
    for rel in files:
        _git(path, "add", rel)
    body = msg + "\n\n" + "\n".join(f"{k}: {v}" for k, v in trailers.items()) + "\n"
    _git(path, "commit", "-m", body)
    return _git(path, "rev-parse", "HEAD").stdout.strip()


def _contract(path, cid="20260813-auth-test", rev=1, agent="ctr-code-auth1",
              branch="feat/auth", paths=None, denied=None):
    paths = paths or ["scripts/**", "tests/**"]
    denied = denied or [".ai/agents/saul/**"]
    doc = {
        "contract_id": cid, "revision": rev, "revision_label": f"v{rev}",
        "supersedes_revision": None if rev == 1 else rev - 1,
        "agent_id": agent, "requested_task": "20260813-9999-auth-test-ctr-code-auth1",
        "allowed_repository": "Dezocode/Sai",
        "allowed_branch_or_worktree": branch,
        "allowed_paths": paths, "denied_paths": denied,
        "capabilities": ["git-commit"], "execution_mode": "provisional",
        "cora_admin_complete": True,
        "review_state": {"saul": {"status": "pending"}, "sai": {"status": "pending"}},
    }
    a.save_revision(path, cid, doc)
    a.write_json(a.pointer_path(path, cid), {
        "contract_id": cid, "project_slug": "auth-test", "project_name": "t",
        "principal": "dezocode", "contractor_type": "coding",
        "isolation_mode": "prototype", "primary_runtime": "cursor-cloud-vm",
        "compatibility_layer": "x", "repository": "Dezocode/Sai",
        "branch_prefix": "proj/auth/", "status": "draft",
        "schema_version": 2, "current_revision": f"v{rev}",
    })
    a.write_yaml(a.contract_dir(path, cid) / "contractor-profile.yaml", {
        "agent_id": agent, "status": "provisional",
    })
    _git(path, "add", "-A")
    _git(path, "commit", "-m",
         f"cora contract v{rev}\n\nTask-ID: 20260813-1517-auth-loop-cursor-cloud\nAgent: ctr-admin\n")
    return cid


def _lease(path, cid, agent="ctr-code-auth1", rev=1, status="active",
           branch="feat/auth", paths=None, lid="lease-test1"):
    lease = {
        "lease_id": lid, "contract_id": cid, "contract_revision": f"v{rev}",
        "agent_id": agent, "task_id": "20260813-9999-auth-test-ctr-code-auth1",
        "repository": "Dezocode/Sai", "branch": branch,
        "allowed_paths": paths or ["scripts/**", "tests/**"],
        "denied_paths": [".ai/agents/saul/**"],
        "capabilities": ["git-commit"], "status": status,
        "execution_mode": "provisional", "issued_by": "ctr-admin",
    }
    a.save_lease(path, cid, lease)
    _git(path, "add", "-A")
    _git(path, "commit", "-m",
         "cora lease\n\nTask-ID: 20260813-1517-auth-loop-cursor-cloud\nAgent: ctr-admin\n")
    return lid


def _expect(name, rc, want_fail):
    FIXTURE_RESULTS[name] = ("FAIL" if rc else "PASS", want_fail)
    ok = (rc != 0) if want_fail else (rc == 0)
    tag = "SELFTEST PASS" if ok else "SELFTEST FAIL"
    print(f"{tag}  {name}")
    if not ok:
        raise RuntimeError(f"fixture {name} expected {'FAIL' if want_fail else 'PASS'}, rc={rc}")


def _verify(path, spec="HEAD"):
    env = os.environ.copy()
    env["GIT_DIR"] = str(path / ".git")
    # run as library
    from sai_auth_verify import verify_range
    old = os.getcwd()
    try:
        os.chdir(path)
        return verify_range(path, spec, branch="feat/auth")
    finally:
        os.chdir(old)


def run_synthetic_fixtures():
    names = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        def one(name, setup, want_fail):
            names.append(name)
            d = tmp / name
            _init(d)
            setup(d)
            rc = _verify(d, "-n 1 HEAD")
            _expect(name, rc, want_fail)

        def valid(d):
            cid = _contract(d)
            lid = _lease(d, cid)
            _commit(d, {
                "scripts/ok.sh": "#!/bin/sh\necho ok\n",
            }, "valid", {
                "Task-ID": "20260813-9999-auth-test-ctr-code-auth1",
                "Agent": "ctr-code-auth1", "Contract-ID": cid,
                "Contract-Revision": "v1", "Authorization-ID": lid,
                "Branch": "feat/auth",
            })

        one("authorization-valid-good", valid, False)

        def unbound(d):
            _commit(d, {"scripts/x.sh": "echo x\n"},
                    "unbound", {"Task-ID": "20260813-0001-other-x", "Agent": "cursor-cloud"})

        one("authorization-unbound-bad", unbound, True)

        def wrong_role(d):
            cid = _contract(d)
            _lease(d, cid)
            _commit(d, {"scripts/x.sh": "echo x\n"},
                    "officer as impl", {
                        "Task-ID": "20260813-9999-auth-test-ctr-code-auth1",
                        "Agent": "ctr-admin", "Contract-ID": cid})

        one("authorization-wrong-role-bad", wrong_role, True)

        def wrong_runtime(d):
            _commit(d, {".ai/agents/saul/x.md": "nope\n"},
                    "saul on cursor", {
                        "Task-ID": "20260813-9999-auth-test-ctr-code-auth1",
                        "Agent": "dezo-sec-codex1"})

        one("authorization-wrong-runtime-bad", wrong_runtime, True)

        def no_contract(d):
            _commit(d, {"scripts/x.sh": "echo x\n"},
                    "no contract", {
                        "Task-ID": "20260813-9999-auth-test-ctr-code-auth1",
                        "Agent": "ctr-code-auth1"})

        one("authorization-no-contract-bad", no_contract, True)

        def path_bad(d):
            cid = _contract(d)
            lid = _lease(d, cid)
            _commit(d, {".ai/agents/saul/roadmap.md": "secret\n"},
                    "denied path", {
                        "Task-ID": "20260813-9999-auth-test-ctr-code-auth1",
                        "Agent": "ctr-code-auth1", "Contract-ID": cid,
                        "Contract-Revision": "v1", "Authorization-ID": lid,
                        "Branch": "feat/auth"})

        one("authorization-path-out-of-scope-bad", path_bad, True)

        def branch_bad(d):
            cid = _contract(d, branch="feat/auth")
            lid = _lease(d, cid)
            _commit(d, {"scripts/x.sh": "echo x\n"},
                    "wrong branch", {
                        "Task-ID": "20260813-9999-auth-test-ctr-code-auth1",
                        "Agent": "ctr-code-auth1", "Contract-ID": cid,
                        "Contract-Revision": "v1", "Authorization-ID": lid,
                        "Branch": "evil/branch"})

        one("authorization-wrong-branch-bad", branch_bad, True)

        def revoked(d):
            cid = _contract(d)
            lid = _lease(d, cid, status="revoked")
            _commit(d, {"scripts/x.sh": "echo x\n"},
                    "revoked", {
                        "Task-ID": "20260813-9999-auth-test-ctr-code-auth1",
                        "Agent": "ctr-code-auth1", "Contract-ID": cid,
                        "Contract-Revision": "v1", "Authorization-ID": lid,
                        "Branch": "feat/auth"})

        one("authorization-revoked-contract-bad", revoked, True)

        def stale(d):
            cid = _contract(d, rev=2)
            lid = _lease(d, cid, rev=1, status="stale")
            _commit(d, {"scripts/x.sh": "echo x\n"},
                    "stale rev", {
                        "Task-ID": "20260813-9999-auth-test-ctr-code-auth1",
                        "Agent": "ctr-code-auth1", "Contract-ID": cid,
                        "Contract-Revision": "v1", "Authorization-ID": lid,
                        "Branch": "feat/auth"})

        one("authorization-stale-revision-bad", stale, True)

        def trailer(d):
            cid = _contract(d)
            _lease(d, cid)
            _commit(d, {"scripts/x.sh": "echo x\n"},
                    "missing agent trailer only task", {
                        "Task-ID": "20260813-9999-auth-test-ctr-code-auth1"})

        one("authorization-missing-trailer-bad", trailer, True)

        def cora_nv(d):
            cid = _contract(d)
            # no lease issued (Cora never verified/leased)
            _commit(d, {"scripts/x.sh": "echo x\n"},
                    "no cora lease", {
                        "Task-ID": "20260813-9999-auth-test-ctr-code-auth1",
                        "Agent": "ctr-code-auth1", "Contract-ID": cid,
                        "Contract-Revision": "v1", "Branch": "feat/auth"})

        one("authorization-cora-not-verified-bad", cora_nv, True)

        def sai_nv(d):
            # same as missing sai review — contractor commit still allowed provisionally;
            # human-gate must fail. Here we fail commit if execution_mode authorized
            # without sai: keep as path that human-gate tests. For commit graph, lease ok.
            cid = _contract(d)
            lid = _lease(d, cid)
            _commit(d, {"scripts/x.sh": "echo x\n"},
                    "provisional without sai is ok for commit", {
                        "Task-ID": "20260813-9999-auth-test-ctr-code-auth1",
                        "Agent": "ctr-code-auth1", "Contract-ID": cid,
                        "Contract-Revision": "v1", "Authorization-ID": lid,
                        "Branch": "feat/auth"})
            from sai_auth_verify import human_gate
            fails, state = human_gate(d, cid, ci_green=True)
            rc = 0 if state == "READY" else 1
            _expect("authorization-sai-not-verified-bad", rc, True)
            return "skip-verify"

        # sai fixture uses human_gate, not verify_range
        names.append("authorization-sai-not-verified-bad")
        d = tmp / "authorization-sai-not-verified-bad"
        _init(d)
        sai_nv(d)

        from sai_auth_grant import register_grant_fixtures
        register_grant_fixtures(one, _commit)

    return set(names)


def run_contract_fixtures():
    return {"contract-self-test-ok"}


def run_saul_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp) / "saul"
        _init(d)
        cid = _contract(d)
        from sai_auth_saul_test import isolate_saul_selftest_env
        isolate_saul_selftest_env(tmp)
        from sai_auth_review import invoke
        rc, doc = invoke(d, cid, "v1", "deadbeef", "contract")
        executed.add("saul-unavailable-blocked")
        if not doc or doc.get("disposition") != "BLOCKED" or doc.get("reason") != "CODEX_UNAVAILABLE":
            raise RuntimeError(f"expected BLOCKED CODEX_UNAVAILABLE, got {doc}")
        print("SELFTEST PASS  saul-unavailable-blocked")
        rc2, doc2 = invoke(d, cid, "v1", "deadbeef", "contract")
        executed.add("saul-idempotent-skip")
        if rc2 != 0 and doc2.get("idempotency_key") != doc.get("idempotency_key"):
            raise RuntimeError("idempotency failed")
        print("SELFTEST PASS  saul-idempotent-skip")
        # refuse unverified approve
        fake = {"reviewer": "saul", "runtime": "codex", "disposition": "APPROVE",
                "contract_id": cid, "contract_revision": 1, "findings": []}
        rc3, doc3 = invoke(d, cid, "v1", "cafe", "implementation", fixture=fake, force=True)
        executed.add("saul-refuse-fake-approve")
        if doc3.get("disposition") == "APPROVE":
            raise RuntimeError("fixture APPROVE must not stand")
        print("SELFTEST PASS  saul-refuse-fake-approve")
        from sai_auth_verify import human_gate
        d2 = Path(tmp) / "gate"
        _init(d2)
        cid2 = _contract(d2)
        _lease(d2, cid2)
        fake_ok = {
            "reviewer": "saul", "runtime": "codex", "disposition": "APPROVE",
            "contract_id": cid2, "contract_revision": 1, "review_type": "implementation",
            "implementation_head": a.head_sha(d2), "findings": [],
        }
        a.write_yaml(a.reviews_dir(d2, cid2) / "saul-implementation-omit.yaml", fake_ok)
        a.write_yaml(a.reviews_dir(d2, cid2) / "sai-implementation.yaml", {
            "reviewer": "sai", "runtime": "cursor-cloud-vm", "disposition": "APPROVE",
            "contract_id": cid2, "contract_revision": 1, "review_type": "implementation",
            "implementation_head": a.head_sha(d2),
        })
        a.write_yaml(a.reviews_dir(d2, cid2) / "saul-contract.yaml", dict(fake_ok, review_type="contract"))
        a.write_yaml(a.reviews_dir(d2, cid2) / "sai-contract.yaml", {
            "reviewer": "sai", "runtime": "cursor-cloud-vm", "disposition": "APPROVE",
            "contract_id": cid2, "contract_revision": 1, "review_type": "contract",
        })
        fails, state = human_gate(d2, cid2, ci_green=True)
        executed.add("saul-omitted-codex-invoked-blocked")
        if state == "READY" or not any("codex_invoked" in x for x in fails):
            raise RuntimeError(f"omitted codex_invoked must block human_gate, got {state} {fails}")
        print("SELFTEST PASS  saul-omitted-codex-invoked-blocked")
        wf = Path(__file__).resolve().parents[2] / ".github/workflows/saul-cto-review.default-branch.yml"
        text = wf.read_text(encoding="utf-8")
        job = text.split("invoke-saul:", 1)[1].split("steps:", 1)[0]
        executed.add("saul-workflow-job-if-same-repo")
        if "head.repo.full_name" not in job or "github.repository" not in job:
            raise RuntimeError("trusted job must skip fork PRs before runs-on")
        print("SELFTEST PASS  saul-workflow-job-if-same-repo")
        executed.add("saul-trusted-launcher-not-pr-head")
        if "SAI_TRUSTED_TREE" not in text or "SAI_CANDIDATE_TREE" not in text:
            raise RuntimeError("trusted workflow must set trusted vs candidate trees")
        if '"$SAI_TRUSTED_TREE/scripts/invoke-saul-review"' not in text:
            raise RuntimeError("invoke must run from SAI_TRUSTED_TREE, not PR-head scripts/")
        print("SELFTEST PASS  saul-trusted-launcher-not-pr-head")
        executed.add("saul-status-description-truncated")
        if "[:140]" not in text and 'DESC="${DESC:0:140}"' not in text:
            raise RuntimeError("trusted workflow must cap commit status description at 140 chars")
        print("SELFTEST PASS  saul-status-description-truncated")
        os.environ.pop("SAI_SKIP_CODEX", None)
        os.environ["SAI_CODEX_BIN"] = "/bin/true"
        os.environ.pop("SAI_CODEX_SANDBOX", None)
        from sai_auth_review import _codex_cmd
        cmd = _codex_cmd()
        executed.add("saul-sandbox-default-danger-full-access")
        if cmd is None or "-s" not in cmd or "danger-full-access" not in cmd:
            raise RuntimeError(f"default Codex sandbox must be danger-full-access, got {cmd}")
        print("SELFTEST PASS  saul-sandbox-default-danger-full-access")
        os.environ["SAI_CODEX_SANDBOX"] = "read-only"
        cmd_ro = _codex_cmd()
        executed.add("saul-sandbox-env-override")
        if "read-only" not in (cmd_ro or []):
            raise RuntimeError(f"SAI_CODEX_SANDBOX override failed: {cmd_ro}")
        os.environ.pop("SAI_CODEX_SANDBOX", None)
        os.environ.pop("SAI_CODEX_BIN", None)
        print("SELFTEST PASS  saul-sandbox-env-override")
        banner = "=== /tmp/evidence/review.yaml ===\nreviewer: saul\ndisposition: REQUEST_CHANGES\n"
        executed.add("saul-yaml-banner-stripped")
        docb = a.load_yaml(banner)
        if docb.get("reviewer") != "saul" or docb.get("disposition") != "REQUEST_CHANGES":
            raise RuntimeError(f"path banner must be stripped, got {docb}")
        print("SELFTEST PASS  saul-yaml-banner-stripped")
    return executed


def run_consume_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp) / "consume"
        _init(d)
        cid = _contract(d)
        _lease(d, cid)
        a.save_session(d, {"agent_id": "ctr-admin", "task_id": "t", "runtime": "cursor-cloud-vm"})
        from sai_auth_review import consume
        review = {
            "reviewer": "saul", "runtime": "codex", "contract_id": cid,
            "contract_revision": 1, "disposition": "REQUEST_CHANGES",
            "idempotency_key": "abc", "findings": [
                {"id": "CTO-001", "severity": "P1", "contract_field": "verification_requirements",
                 "action": "add", "requested_change": "scripts/verify-x"},
            ],
        }
        consume(d, cid, review)
        executed.add("consume-ordinary-amend")
        ptr = a.load_pointer(d, cid)
        if ptr.get("current_revision") != "v2":
            raise RuntimeError("expected v2")
        print("SELFTEST PASS  consume-ordinary-amend")
        a.save_session(d, {"agent_id": "ctr-admin", "task_id": "t"})
        review2 = {
            "reviewer": "saul", "runtime": "codex", "contract_id": cid,
            "contract_revision": 2, "disposition": "REQUEST_CHANGES",
            "idempotency_key": "def", "findings": [
                {"id": "CTO-009", "action": "expand", "contract_field": "allowed_paths",
                 "requested_change": [".ai/**"], "authority_expanding": True},
            ],
        }
        consume(d, cid, review2)
        executed.add("consume-expand-human-gate")
        hap = a.read_yaml(a.contract_dir(d, cid) / "human-approval-required.yaml")
        if not hap or hap.get("resolved"):
            raise RuntimeError("expected human-approval-required")
        if a.load_pointer(d, cid).get("current_revision") != "v2":
            raise RuntimeError("must not auto-bump on expanding finding")
        print("SELFTEST PASS  consume-expand-human-gate")
        bp = d / "bannered-review.yaml"
        bp.write_text("=== /root/skill-lab/evidence/review.yaml ===\nreviewer: saul\n"
                      f"runtime: codex\ncontract_id: {cid}\ncontract_revision: 2\n"
                      "disposition: BLOCKED\nidempotency_key: banner\nfindings: []\n")
        executed.add("consume-banner-prefixed-yaml")
        if consume(d, cid, str(bp)) != 0:
            raise RuntimeError("consume must parse banner-prefixed YAML")
        print("SELFTEST PASS  consume-banner-prefixed-yaml")
    return executed


if __name__ == "__main__":
    run_synthetic_fixtures()
    run_saul_fixtures()
    run_consume_fixtures()
    print("sai_auth_test: all internal fixtures passed")
