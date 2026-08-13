#!/usr/bin/env python3
"""Build a retrievable exact-head Saul review package. Git is durable truth."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import sai_auth as a

MARKER_B, MARKER_E = "---SAUL_REVIEW_YAML---", "---END_SAUL_REVIEW_YAML---"

PROFILE_PATHS = [
    "CODEX.md",
    ".ai/agents/saul/AGENT.md",
    ".ai/agents/saul/runtimes/codex/automation/profile.md",
    ".ai/agents/saul/runtimes/codex/prompts/cto-review.md",
]
DOC_PATHS = [
    ".ai/shared/memory/decisions/0006-agent-authorization-loop.md",
    ".ai/_config/authorization.yaml",
    ".ai/_config/security-policy.md",
    ".ai/shared/schemas/contract-review.schema.json",
]
INLINE_LIMIT = 400000


def _git(root, *args):
    return a.git(root, *args).stdout


def _base_ref(root):
    env = os.environ.get("GITHUB_BASE_REF")
    if env:
        return f"origin/{env}" if not env.startswith("origin/") else env
    for cand in ("origin/main", "main"):
        p = a.git(root, "rev-parse", "--verify", cand)
        if p.returncode == 0:
            return cand
    p = a.git(root, "rev-parse", "--verify", "HEAD^")
    if p.returncode == 0:
        return "HEAD^"
    return "HEAD"


def _changed_files(root, sha, base):
    p = a.git(root, "diff", "--name-only", f"{base}...{sha}")
    names = [x for x in p.stdout.splitlines() if x]
    if names:
        return names
    return a.commit_paths(root, sha)


def _complete_diff(root, sha, base):
    p = a.git(root, "diff", f"{base}...{sha}")
    if p.returncode == 0 and p.stdout.strip():
        return p.stdout
    return _git(root, "show", sha)


def _prior_findings(root, cid):
    if not cid:
        return []
    d = a.reviews_dir(root, cid)
    if not d.is_dir():
        return []
    out = []
    for p in sorted(d.glob("saul-*.yaml")):
        doc = a.read_yaml(p) or {}
        out.append({
            "file": str(p.relative_to(root)) if str(p).startswith(str(root)) else p.name,
            "disposition": doc.get("disposition"),
            "contract_revision": doc.get("contract_revision"),
            "implementation_head": doc.get("implementation_head"),
            "reason": doc.get("reason"),
            "findings": doc.get("findings") or [],
            "github_run_id": doc.get("github_run_id"),
        })
    return out


def _ci_status(sha):
    repo = os.environ.get("GITHUB_REPOSITORY")
    token_ok = bool(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
    if not repo or not token_ok:
        return "CI status not queried (missing GITHUB_REPOSITORY or token).\n"
    try:
        p = subprocess.run(
            ["gh", "api", f"repos/{repo}/commits/{sha}/status"],
            capture_output=True, text=True, timeout=30,
        )
        if p.returncode != 0:
            return f"CI status query failed (exit {p.returncode}).\n"
        data = json.loads(p.stdout or "{}")
        lines = [f"combined_state={data.get('state')}"]
        for st in (data.get("statuses") or [])[:30]:
            lines.append(
                f"{st.get('context')}: {st.get('state')} {st.get('description') or ''}"
            )
        return "\n".join(lines) + "\n"
    except Exception as e:
        return f"CI status query error: {type(e).__name__}\n"


def _pr_meta():
    return {
        "repository": os.environ.get("GITHUB_REPOSITORY") or "Dezocode/Sai",
        "pr_number": os.environ.get("GITHUB_PR_NUMBER")
        or os.environ.get("PR_NUMBER")
        or (os.environ.get("GITHUB_REF_NAME") or "").replace("/merge", ""),
        "base_ref": os.environ.get("GITHUB_BASE_REF") or "main",
        "head_ref": os.environ.get("GITHUB_HEAD_REF") or "",
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_event": os.environ.get("GITHUB_EVENT_NAME"),
        "runner_name": os.environ.get("RUNNER_NAME"),
        "runner_os": os.environ.get("RUNNER_OS"),
        "runner_arch": os.environ.get("RUNNER_ARCH"),
    }


def _scope(revdoc):
    if not revdoc:
        return {}
    return {
        "allowed_paths": revdoc.get("allowed_paths"),
        "denied_paths": revdoc.get("denied_paths"),
        "capabilities": revdoc.get("capabilities"),
        "allowed_repository": revdoc.get("allowed_repository"),
        "allowed_branch_or_worktree": revdoc.get("allowed_branch_or_worktree"),
        "verification_requirements": revdoc.get("verification_requirements"),
        "agent_id": revdoc.get("agent_id"),
        "cora_admin_complete": revdoc.get("cora_admin_complete"),
    }


def write_package(root, cid, revision, sha, review_type, dest_dir):
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    base = _base_ref(root)
    files = _changed_files(root, sha, base)
    diff = _complete_diff(root, sha, base)
    revdoc = a.load_revision(root, cid, revision) if cid and revision else None
    prior = _prior_findings(root, cid)
    meta = {
        "review_type": review_type,
        "review_scope": os.environ.get("SAI_SAUL_REVIEW_SCOPE") or "final",
        "contract_id": cid,
        "contract_revision": revision,
        "implementation_head": sha,
        "base_ref": base,
        "changed_file_count": len(files),
        "diff_bytes": len(diff.encode("utf-8")),
        "scope": _scope(revdoc),
        **_pr_meta(),
    }
    (dest / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (dest / "changed-files.txt").write_text("\n".join(files) + ("\n" if files else ""), encoding="utf-8")
    (dest / "diff.patch").write_text(diff, encoding="utf-8")
    (dest / "prior-findings.yaml").write_text(a.dump_yaml(prior), encoding="utf-8")
    (dest / "ci-status.txt").write_text(_ci_status(sha), encoding="utf-8")
    if revdoc:
        (dest / "contract-revision.yaml").write_text(a.dump_yaml(revdoc), encoding="utf-8")
    return dest, meta, files, diff, revdoc, prior


def build_prompt(root, cid, revision, sha, review_type, package_dir=None):
    pkg = package_dir or os.environ.get("SAI_SAUL_PACKAGE_DIR")
    if not pkg:
        root_p = Path(root)
        git_pkg = root_p / ".saul-review-package"
        pkg = str(git_pkg if (root_p / ".git").is_dir() else Path("/tmp/saul/package"))
    dest, meta, files, diff, revdoc, prior = write_package(
        root, cid, revision, sha, review_type, pkg,
    )
    parts = [
        "You are Saul (dezo-sec-codex1), Codex-native CTO. Do not impersonate Cora or Sai.",
        "Load the tracked Saul profile from the checkout paths listed below, then review.",
        f"Package directory (read these files): {dest}",
        a.dump_yaml({"review_metadata": meta}),
        "# changed files (complete exact-head set vs base)\n" + "\n".join(files),
        "# prior Saul findings / resolution state\n" + a.dump_yaml(prior),
    ]
    if revdoc:
        parts.append("# current contract revision (immutable)\n" + a.dump_yaml(revdoc))
    for rel in PROFILE_PATHS + DOC_PATHS:
        p = Path(root) / rel
        if p.is_file():
            parts.append(f"Tracked context (read from checkout if truncated): {rel}")
            parts.append(p.read_text(encoding="utf-8")[:8000])
    if sha:
        parts.append(f"# implementation HEAD {sha}\n" + a.commit_message(root, sha))
        parts.append(_git(root, "show", "--stat", sha)[:4000])
    if len(diff) <= INLINE_LIMIT:
        parts.append("# complete exact-head diff vs base\n" + diff)
    else:
        parts.append(
            f"# complete diff is {len(diff)} bytes at {dest / 'diff.patch'} — "
            "you MUST read that file before FINAL APPROVE. Stat/summary is not sufficient."
        )
        parts.append("# diff preview (truncated)\n" + diff[:INLINE_LIMIT])
    scope = meta.get("review_scope") or "final"
    parts.append(
        f"Review type: {review_type}. Review scope: {scope}. "
        "FINAL CTO review MUST cover the complete changed-file set and complete diff. "
        "Do not APPROVE if you only inspected a commit message or git show --stat. "
        "Intermediate delta reviews may emphasize files changed since the last Saul "
        "finding, but FINAL still requires the complete exact-head set. "
        f"Emit YAML between {MARKER_B} and {MARKER_E}. "
        "disposition must be APPROVE, REQUEST_CHANGES, or BLOCKED. "
        "Each finding needs id (CTO-N), severity, contract_field, action, "
        "requested_change, authority_expanding. Schema: "
        ".ai/shared/schemas/contract-review.schema.json."
    )
    return "\n\n".join(parts)
