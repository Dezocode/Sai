#!/usr/bin/env python3
"""Lifecycle e2e for decision 0006. Prints a matrix A–Y with evidence paths."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/lib"))
import sai_auth as a  # noqa: E402
from sai_auth_review import consume, invoke  # noqa: E402
from sai_auth_verify import human_gate, verify_pre_commit, verify_range  # noqa: E402

TASK = "20260813-9999-e2e-auth-ctr-code-auth1"
CID = "20260813-e2e-auth"
MATRIX = {}


def rec(letter, status, evidence):
    MATRIX[letter] = (status, evidence)
    print(f"E2E {letter} {status}: {evidence}")


def sh(cwd, *cmd, check=True, env=None):
    e = os.environ.copy()
    if env:
        e.update(env)
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=e)
    if check and p.returncode != 0:
        raise RuntimeError(f"{cmd}\n{p.stdout}\n{p.stderr}")
    return p


def setup(tmp: Path):
    # copy control plane into an isolated git repo
    for rel in [
        ".ai/_config/authorization.yaml",
        ".ai/agents/registry.json",
        ".ai/requests/README.md",
        "scripts/lib/sai_auth.py",
        "scripts/lib/sai_auth_flow.py",
        "scripts/lib/sai_auth_verify.py",
        "scripts/lib/sai_auth_review.py",
        "scripts/lib/sai_auth_package.py",
        "scripts/lib/sai_auth_test.py",
        "scripts/sai-authorize-task",
        "scripts/sai-assume-agent",
        "scripts/sai-release-agent",
        "scripts/verify-agent-authorization",
        "scripts/verify-contract-authorization",
        "scripts/invoke-saul-review",
        "scripts/consume-saul-contract-review",
        "scripts/record-sai-verification",
        ".ai/agents/saul/runtimes/codex/prompts/cto-review.md",
        ".ai/agents/saul/AGENT.md",
        ".ai/agents/saul/runtimes/codex/automation/profile.md",
        "CODEX.md",
    ]:
        src, dst = ROOT / rel, tmp / rel
        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    sh(tmp, "git", "init", "-b", "feat/e2e-auth")
    sh(tmp, "git", "config", "user.email", "e2e@example.com")
    sh(tmp, "git", "config", "user.name", "E2E")
    (tmp / "scripts").mkdir(exist_ok=True)
    for n in os.listdir(tmp / "scripts"):
        p = tmp / "scripts" / n
        if p.is_file():
            p.chmod(0o755)
    sh(tmp, "git", "add", "-A")
    sh(tmp, "git", "commit", "-m", "seed\n\nTask-ID: 20260813-1517-auth-loop-cursor-cloud\nAgent: cursor-cloud\n")
    return tmp


def main():
    tmp = Path(tempfile.mkdtemp(prefix="sai-auth-e2e-"))
    setup(tmp)
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("CODEX_API_KEY", None)

    # A/B authorize with no impl agent
    p = sh(tmp, "scripts/sai-authorize-task", "--task-id", TASK,
           "--purpose", "e2e", "--required-role", "contractor-coding")
    out = p.stdout
    rec("A", "PASS" if "CONTRACT_REQUIRED" in out else "FAIL", out.strip().splitlines()[0])
    rec("B", "PASS" if "CONTRACT_REQUIRED" in out else "FAIL", str(tmp / ".ai/requests" / TASK / "request.yaml"))

    # C assume Cora
    p = sh(tmp, "scripts/sai-assume-agent", "ctr-admin", "--task-id", TASK)
    rec("C", "PASS" if "ASSUMED ctr-admin" in p.stdout else "FAIL", p.stdout.strip())

    # D create contract v1
    p = sh(tmp, "scripts/sai-authorize-task", "--task-id", TASK, "--create-contract",
           "--contract-id", CID, "--contractor-id", "ctr-code-auth1",
           "--branch", "feat/e2e-auth",
           "--allowed-path", "scripts/**", "--allowed-path", "tests/**")
    rec("D", "PASS" if "revision=v1" in p.stdout else "FAIL", p.stdout.strip())

    sh(tmp, "scripts/sai-release-agent")
    p = sh(tmp, "scripts/sai-assume-agent", "ctr-code-auth1", "--task-id", TASK,
           "--contract-id", CID)
    rec("E", "PASS" if "ASSUMED ctr-code-auth1" in p.stdout else "FAIL", p.stdout.strip())

    # F provisional change inside scope
    (tmp / "scripts/e2e_ok.sh").write_text("#!/bin/sh\necho ok\n")
    sh(tmp, "git", "add", "scripts/e2e_ok.sh")
    rc = verify_pre_commit(tmp)
    rec("F", "PASS" if rc == 0 else "FAIL", f"pre-commit rc={rc}")

    # G–J / O–P: filled by GitHub evidence after push; local event simulation
    rec("G", "PENDING", "requires GitHub pull_request event on Dezocode/Sai")
    rec("H", "PENDING", "requires Actions invoke of Codex")
    rec("I", "PENDING", "requires Saul Codex profile loaded in runner")
    rec("J", "PENDING", "requires real Saul REQUEST_CHANGES from Codex")

    # Local consume of a REQUEST_CHANGES fixture (K/L) — machinery, not a real Saul approve
    a.save_session(tmp, {"agent_id": "ctr-admin", "task_id": TASK, "runtime": "cursor-cloud-vm"})
    review = {
        "reviewer": "saul", "runtime": "codex", "contract_id": CID,
        "contract_revision": 1, "disposition": "REQUEST_CHANGES",
        "implementation_head": a.head_sha(tmp),
        "idempotency_key": "e2e-rc1", "findings": [
            {"id": "CTO-001", "severity": "P1",
             "contract_field": "verification_requirements", "action": "add",
             "requested_change": "scripts/verify-agent-authorization --self-test"},
        ],
    }
    consume(tmp, CID, review)
    rec("K", "PASS", "Cora consumed REQUEST_CHANGES as ctr-admin")
    ptr = a.load_pointer(tmp, CID)
    rec("L", "PASS" if ptr.get("current_revision") == "v2" else "FAIL",
        f"revision={ptr.get('current_revision')} amendment A-002")

    # M v1 lease stale; contractor blocked
    sh(tmp, "scripts/sai-release-agent")
    p = sh(tmp, "scripts/sai-assume-agent", "ctr-code-auth1", "--task-id", TASK,
           "--contract-id", CID, check=False)
    rec("M", "PASS" if p.returncode != 0 else "FAIL", p.stderr.strip() or p.stdout.strip())

    # N re-issue lease at v2 then assume
    a.save_session(tmp, {"agent_id": "ctr-admin", "task_id": TASK, "runtime": "cursor-cloud-vm"})
    from sai_auth_flow import _issue_lease
    rev = a.load_revision(tmp, CID, 2)
    _issue_lease(tmp, CID, 2, "ctr-code-auth1", TASK, "feat/e2e-auth",
                 rev["allowed_paths"], rev.get("denied_paths") or [], rev.get("capabilities") or [])
    sh(tmp, "scripts/sai-release-agent")
    p = sh(tmp, "scripts/sai-assume-agent", "ctr-code-auth1", "--task-id", TASK,
           "--contract-id", CID)
    rec("N", "PASS" if p.returncode == 0 else "FAIL", p.stdout.strip())

    rec("O", "PENDING", "second GitHub event / Actions run")
    rec("P", "PENDING", "real Saul APPROVE exact revision+SHA")
    rec("Q", "PENDING", "real Sai APPROVE exact revision+SHA (ceo identity)")
    rec("R", "PENDING", "CI green on exact SHA after push")

    fails, state = human_gate(tmp, CID, ci_green=True)
    rec("S", "PASS" if state == "BLOCKED" else "FAIL",
        f"expected BLOCKED before dual exact-head; got {state} {fails[:3]}")

    rec("T", "PENDING", "extra commit then prove Saul/Sai implementation STALE")
    rec("U", "PENDING", "fresh exact-head reviews restore READY")

    # V authority expansion
    a.save_session(tmp, {"agent_id": "ctr-admin", "task_id": TASK})
    consume(tmp, CID, {
        "reviewer": "saul", "runtime": "codex", "contract_id": CID,
        "contract_revision": 2, "disposition": "REQUEST_CHANGES",
        "idempotency_key": "e2e-exp", "findings": [
            {"id": "CTO-099", "action": "expand", "contract_field": "allowed_paths",
             "requested_change": [".ai/**"], "authority_expanding": True},
        ],
    })
    hap = a.read_yaml(a.contract_dir(tmp, CID) / "human-approval-required.yaml")
    rec("V", "PASS" if hap and not hap.get("resolved") and a.load_pointer(tmp, CID).get("current_revision") == "v2" else "FAIL",
        "human-approval-required.yaml; revision not auto-bumped")

    # W negative local cases (contractor identity)
    sh(tmp, "scripts/sai-release-agent")
    p = sh(tmp, "scripts/sai-assume-agent", "ctr-code-auth1", "--task-id", TASK,
           "--contract-id", CID, check=False)
    w_ok = p.returncode == 0
    notes = []
    if not w_ok:
        notes.append("could not re-assume contractor for W")
    # wrong path via verify_paths
    (tmp / ".ai/agents/saul").mkdir(parents=True, exist_ok=True)
    (tmp / ".ai/agents/saul/pwn.md").write_text("no\n")
    sh(tmp, "git", "add", ".ai/agents/saul/pwn.md")
    if verify_pre_commit(tmp) == 0:
        w_ok = False
        notes.append("wrong-path did not block")
    sh(tmp, "git", "reset", "HEAD", "--", ".ai/agents/saul/pwn.md")
    rec("W", "PASS" if w_ok else "FAIL", "; ".join(notes) or "wrong-path blocked under contractor session")

    # X idempotency
    os.environ.pop("OPENAI_API_KEY", None)
    rc1, d1 = invoke(tmp, CID, "v2", "abc", "implementation")
    rc2, d2 = invoke(tmp, CID, "v2", "abc", "implementation")
    rec("X", "PASS" if d1 and d2 and d1.get("idempotency_key") == d2.get("idempotency_key") else "FAIL",
        f"key={d1.get('idempotency_key') if d1 else None}")

    # Y Codex unavailable => BLOCKED not APPROVE
    rec("Y", "PASS" if d1 and d1.get("disposition") == "BLOCKED" and d1.get("reason") == "CODEX_UNAVAILABLE" else "FAIL",
        f"{(d1 or {}).get('disposition')} {(d1 or {}).get('reason')}")

    print("E2E_DIR", tmp)
    print("MATRIX")
    for k in [chr(x) for x in range(ord("A"), ord("Y") + 1)]:
        st, ev = MATRIX.get(k, ("MISSING", ""))
        print(f"  {k} {st} | {ev}")
    failed = [k for k, v in MATRIX.items() if v[0] == "FAIL"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
