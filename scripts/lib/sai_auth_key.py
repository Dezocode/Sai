#!/usr/bin/env python3
"""Saul review key + completed-disposition cache. Deterministic; no model."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

sys_path = str(Path(__file__).resolve().parent)
if sys_path not in __import__("sys").path:
    __import__("sys").path.insert(0, sys_path)
import sai_auth as a  # noqa: E402


def requirement_digest(root, cid, sha=None, revision=None) -> str:
    """Hash ledger + revision bounds. Missing inputs => empty digest."""
    parts = []
    rel = f".ai/contracts/{cid}/requirements/ledger.yaml" if cid else ""
    text = ""
    if cid and sha:
        text = a.git_show(root, sha, rel) or ""
    elif cid:
        p = Path(root) / rel
        if p.is_file():
            text = p.read_text(encoding="utf-8")
    if text:
        parts.append(text)
    if cid:
        try:
            ptr = a.load_pointer(root, cid, sha=sha) or {}
            rev_l = revision or ptr.get("current_revision")
            rev = a.load_revision(root, cid, rev_l, sha=sha) if rev_l else None
        except Exception:
            rev = None
        if rev:
            payload = {
                "verification_requirements": rev.get("verification_requirements") or [],
                "allowed_paths": rev.get("allowed_paths") or [],
                "denied_paths": rev.get("denied_paths") or [],
                "capabilities": rev.get("capabilities") or [],
            }
            parts.append(json.dumps(payload, sort_keys=True, default=str))
    if not parts:
        return ""
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()[:16]


def saul_review_key(
    *,
    repository="",
    pr="",
    review_type="",
    contract_id="",
    contract_revision="",
    implementation_head="",
    blocking_requirement_digest="",
    review_scope="final",
) -> str:
    raw = "|".join([
        str(repository or ""),
        str(pr or ""),
        str(review_type or ""),
        str(contract_id or ""),
        str(a.revision_int(contract_revision) if contract_revision not in (None, "") else ""),
        str(implementation_head or ""),
        str(blocking_requirement_digest or ""),
        str(review_scope or "final"),
    ])
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def compute_saul_review_key(root, cid, revision, sha, review_type):
    return saul_review_key(
        repository=os.environ.get("GITHUB_REPOSITORY") or "",
        pr=os.environ.get("GITHUB_PR_NUMBER") or os.environ.get("PR_NUMBER") or "",
        review_type=review_type,
        contract_id=cid or "",
        contract_revision=revision,
        implementation_head=sha,
        blocking_requirement_digest=requirement_digest(root, cid, revision=revision),
        review_scope=os.environ.get("SAI_SAUL_REVIEW_SCOPE") or "final",
    )


def cache_dir() -> Path:
    p = Path(os.environ.get("SAI_SAUL_KEY_CACHE") or "/tmp/sai-saul-keys")
    p.mkdir(parents=True, exist_ok=True)
    return p


def lookup_completed(key: str):
    p = cache_dir() / f"{key}.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def remember_review(key: str, doc: dict) -> None:
    if not key:
        return
    slim = {
        "saul_review_key": key,
        "disposition": doc.get("disposition"),
        "reason": doc.get("reason"),
        "codex_invoked": doc.get("codex_invoked"),
        "synthetic": doc.get("synthetic"),
        "implementation_head": doc.get("implementation_head"),
        "contract_id": doc.get("contract_id"),
        "contract_revision": doc.get("contract_revision"),
        "review_type": doc.get("review_type"),
    }
    dest = cache_dir() / f"{key}.json"
    dest.write_text(json.dumps(slim, indent=2) + "\n", encoding="utf-8")
