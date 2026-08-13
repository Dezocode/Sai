#!/usr/bin/env python3
"""SAI authorization primitives. Session cache is convenience only; CI uses Git."""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

TRAILER = re.compile(r"^([A-Za-z0-9-]+):\s*(.*)$")
POLICY = ".ai/_config/authorization.yaml"
SESSION_REL = ".git/sai-session.json"
# Evidence packs sometimes prefix YAML with `=== /path/file.yaml ===`.
YAML_PATH_BANNER = re.compile(r"^=+[ \t]+\S.*[ \t]+=+\s*$")
TASK_ID_GRAMMAR = re.compile(r"^[0-9]{8}-[0-9]{4}-[a-z0-9][a-z0-9-]*$")


def fail(msg):
    print(f"FAIL {msg}", file=sys.stderr)
    return False


def ok(msg):
    print(f"PASS {msg}")
    return True


def strip_yaml_path_banners(text):
    """Drop leading `=== path ===` banners so consume/read_yaml stay machine-readable."""
    if not text:
        return text
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines) and YAML_PATH_BANNER.match(lines[i].rstrip("\n\r")):
        i += 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    return "".join(lines[i:])


def load_yaml(text):
    if yaml is None:
        raise RuntimeError("PyYAML is required")
    return yaml.safe_load(strip_yaml_path_banners(text)) or {}


def task_id_grammar_ok(task):
    return bool(task) and bool(TASK_ID_GRAMMAR.match(task))


def malformed_task_id_preserved(root, sha, task_id):
    """Grammar-only exception. Does not skip authorization replay."""
    try:
        cfg = load_config(root)
    except Exception:
        return False
    for row in (cfg.get("audit") or {}).get("preserve_malformed_task_id") or []:
        if (row.get("sha") or "") == sha and (row.get("original_task_id") or "") == task_id:
            return True
    return False


def dump_yaml(obj):
    if yaml is None:
        raise RuntimeError("PyYAML is required")
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)


def read_yaml(path: Path):
    return load_yaml(path.read_text(encoding="utf-8")) if path.is_file() else None


def write_yaml(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_yaml(obj), encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def git(root, *args, check=False, input_text=None):
    p = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        input=input_text,
    )
    if check and p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip() or f"git {args}")
    return p


def toplevel(start=None):
    p = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, cwd=start,
    )
    return Path(p.stdout.strip()) if p.returncode == 0 else Path(start or ".")


def load_config(root):
    path = Path(root) / POLICY
    cfg = read_yaml(path)
    if not cfg:
        raise RuntimeError(f"missing {POLICY}")
    return cfg


def load_registry(root, sha=None):
    if sha:
        text = git_show(root, sha, ".ai/agents/registry.json")
        return json.loads(text) if text else {"agents": []}
    path = Path(root) / ".ai/agents/registry.json"
    return read_json(path) or {"agents": []}


def find_agent(reg, ident):
    ident = (ident or "").strip()
    for a in reg.get("agents") or []:
        if a.get("agent_id") == ident or a.get("name") == ident:
            return a
    return None


def git_show(root, sha, rel):
    p = git(root, "show", f"{sha}:{rel}")
    return None if p.returncode != 0 else p.stdout


def head_sha(root):
    p = git(root, "rev-parse", "HEAD")
    return p.stdout.strip() if p.returncode == 0 else None


def current_branch(root):
    p = git(root, "rev-parse", "--abbrev-ref", "HEAD")
    return p.stdout.strip() if p.returncode == 0 else "HEAD"


def commit_message(root, sha):
    return git(root, "log", "-1", "--format=%B", sha).stdout


def commit_paths(root, sha):
    p = git(root, "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", sha)
    return [x for x in p.stdout.splitlines() if x]


def staged_paths(root):
    p = git(root, "diff", "--cached", "--name-only")
    return [x for x in p.stdout.splitlines() if x]


def rev_list(root, spec):
    args = spec.split() if isinstance(spec, str) else list(spec)
    p = git(root, "rev-list", "--no-merges", *args)
    return [x for x in p.stdout.splitlines() if x]


def commit_has_policy(root, sha):
    return git(root, "cat-file", "-e", f"{sha}:{POLICY}").returncode == 0


def parse_trailers(msg):
    out = {}
    for line in (msg or "").splitlines():
        m = TRAILER.match(line.strip())
        if m:
            out.setdefault(m.group(1), m.group(2).strip())
    return out


def glob_match(path, pattern):
    path = path.replace("\\", "/")
    if path.startswith("./"):
        path = path[2:]
    pattern = pattern.replace("\\", "/")
    if pattern.endswith("/**"):
        root = pattern[:-3].rstrip("/")
        return path == root or path.startswith(root + "/")
    if pattern.endswith("/") and path.startswith(pattern):
        return True
    if "**" in pattern:
        rx = re.escape(pattern).replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
        return re.fullmatch(rx, path) is not None
    if path == pattern or path.startswith(pattern.rstrip("*")):
        if "*" not in pattern and (path == pattern or path.startswith(pattern + "/")):
            return True
    return fnmatch.fnmatch(path, pattern)


def path_allowed(path, allowed, denied):
    if any(glob_match(path, d) for d in denied or []):
        return False
    if not allowed:
        return False
    return any(glob_match(path, a) for a in allowed)


def session_path(root):
    return Path(root) / SESSION_REL


def load_session(root):
    return read_json(session_path(root))


def save_session(root, obj):
    p = session_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    write_json(p, obj)


def clear_session(root):
    p = session_path(root)
    if p.is_file():
        p.unlink()


def request_path(root, task_id):
    return Path(root) / ".ai/requests" / task_id / "request.yaml"


def load_request(root, task_id):
    return read_yaml(request_path(root, task_id))


def save_request(root, task_id, obj):
    write_yaml(request_path(root, task_id), obj)


def contract_dir(root, cid):
    return Path(root) / ".ai/contracts" / cid


def pointer_path(root, cid):
    return contract_dir(root, cid) / "contract.json"


def revision_path(root, cid, rev):
    n = revision_int(rev)
    return contract_dir(root, cid) / "revisions" / f"v{n}.yaml"


def revision_int(rev):
    if isinstance(rev, int):
        return rev
    s = str(rev).strip().lstrip("v")
    return int(s)


def revision_label(rev):
    return f"v{revision_int(rev)}"


def load_pointer(root, cid, sha=None):
    if sha:
        text = git_show(root, sha, f".ai/contracts/{cid}/contract.json")
        return json.loads(text) if text else None
    return read_json(pointer_path(root, cid))


def load_revision(root, cid, rev, sha=None):
    rel = f".ai/contracts/{cid}/revisions/v{revision_int(rev)}.yaml"
    if sha:
        text = git_show(root, sha, rel)
        return load_yaml(text) if text else None
    return read_yaml(Path(root) / rel)


def save_revision(root, cid, doc):
    n = revision_int(doc.get("revision") or doc.get("revision_label") or 1)
    doc["revision"] = n
    doc["revision_label"] = f"v{n}"
    write_yaml(revision_path(root, cid, n), doc)
    return n


def current_revision(root, cid, sha=None):
    ptr = load_pointer(root, cid, sha=sha)
    if not ptr:
        return None
    return ptr.get("current_revision")


def lease_dir(root, cid):
    return contract_dir(root, cid) / "leases"


def load_lease(root, cid, lease_id, sha=None):
    rel = f".ai/contracts/{cid}/leases/{lease_id}.json"
    if sha:
        text = git_show(root, sha, rel)
        return json.loads(text) if text else None
    return read_json(Path(root) / rel)


def save_lease(root, cid, lease):
    lid = lease["lease_id"]
    write_json(lease_dir(root, cid) / f"{lid}.json", lease)


def list_leases(root, cid, sha=None):
    if sha:
        p = git(root, "ls-tree", "--name-only", sha, f".ai/contracts/{cid}/leases/")
        names = [Path(x).name for x in p.stdout.splitlines() if x.endswith(".json")]
        out = []
        for n in names:
            lid = n[:-5]
            doc = load_lease(root, cid, lid, sha=sha)
            if doc:
                out.append(doc)
        return out
    d = lease_dir(root, cid)
    if not d.is_dir():
        return []
    return [read_json(p) for p in sorted(d.glob("*.json")) if read_json(p)]


def reviews_dir(root, cid):
    return contract_dir(root, cid) / "reviews"


def amendments_dir(root, cid):
    return contract_dir(root, cid) / "amendments"


def review_key(contract_id, revision, head, reviewer, review_type):
    raw = "|".join([
        str(contract_id or ""),
        str(revision_int(revision) if revision is not None else ""),
        str(head or ""),
        str(reviewer or ""),
        str(review_type or ""),
    ])
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def officer_cfg(cfg, agent_id):
    return (cfg.get("officers") or {}).get(agent_id)


def is_officer(cfg, agent_id):
    return officer_cfg(cfg, agent_id) is not None


def assume_allowed(cfg, agent, runtime):
    aid = agent.get("agent_id")
    oc = officer_cfg(cfg, aid)
    allowed = list((oc or {}).get("assume_runtimes") or [])
    if not allowed:
        pr = agent.get("primary_runtime")
        if pr:
            allowed = [pr]
        suite = {
            "cursor-cloud-vm": ["cursor-cloud-vm", "cursor-desktop"],
            "cursor-desktop": ["cursor-cloud-vm", "cursor-desktop"],
        }
        allowed = list(set(allowed + suite.get(pr, [])))
    if oc and oc.get("cursor_impersonation") == "forbidden":
        if runtime in (cfg.get("runtimes") or {}).get("cursor_implementation", []):
            return False
    return runtime in allowed or runtime == agent.get("primary_runtime")


def class_paths(cfg, write_class):
    return list((cfg.get("path_classes") or {}).get(write_class) or [])


def bootstrap_ok(cfg, trailers, paths, *, root=None, sha=None):
    boot = cfg.get("bootstrap") or {}
    if boot.get("standing") is True:
        return False
    task = trailers.get("Task-ID") or trailers.get("Task-Id")
    agent = trailers.get("Agent")
    if task not in (boot.get("task_ids") or []):
        return False
    if agent not in (boot.get("agent_trailers") or []):
        return False
    prefixes = boot.get("allowed_path_prefixes") or []
    for p in paths:
        if not any(p == pref or p.startswith(pref.rstrip("/") + "/") or glob_match(p, pref)
                   for pref in prefixes):
            return False
    from sai_auth_grant import bootstrap_until_ok
    return bootstrap_until_ok(cfg, task, root, sha)


def utcnow():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def detect_runtime():
    if os.environ.get("SAI_RUNTIME"):
        return os.environ["SAI_RUNTIME"]
    if os.environ.get("CURSOR_CLOUD") or os.environ.get("CURSOR_AGENT"):
        return "cursor-cloud-vm"
    return "cursor-cloud-vm"


def ensure_primary_runtime(root):
    """Register compact primary-runtime identity at first write-gate only."""
    git_dir = Path(root) / ".git"
    if not git_dir.is_dir():
        return None
    path = git_dir / "sai-primary-runtime.json"
    if path.is_file():
        return read_json(path)
    doc = {
        "runtime": detect_runtime(),
        "registered_at": utcnow(),
        "activation": "lazy-first-write",
        "session_start_init": False,
        "note": "compact orchestrator; Git is durable truth",
    }
    write_json(path, doc)
    return doc
