#!/usr/bin/env python3
"""Trusted SHA-bound review-unit coverage. Candidate manifests are not authority.

A shard is a bounded chunk derived from exact base/head/diff digests, not a
file bucket. Wrappers: scripts/saul-review-shards, scripts/verify-saul-shard-quality.
"""
from __future__ import annotations

import argparse, hashlib, json, os, re, shutil, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path

SCHEMA_MANIFEST = "saul-review-manifest"
POLICY_V1 = b"saul-quality-shards-v1"
MAX_UNITS_PER_SHARD = 4
SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
IMP_RE = re.compile(
    r"^\s*(?:import|from|require(?:\(|\s)|include\s|[Uu]ses:\s+|\"\$ref\"\s*:)\s*(\S+)", re.M)


class CoverageError(Exception):
    def __init__(self, verdict: str, reason: str):
        self.verdict, self.reason = verdict, reason
        super().__init__(f"{verdict}: {reason}")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()


def default_policy_digest() -> str:
    return (os.environ.get("SAI_SAUL_POLICY_DIGEST") or "").strip().lower() or sha256_hex(POLICY_V1)


def _git_env() -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    return env


def git_run(repo: Path, *args: str, binary: bool = False) -> subprocess.CompletedProcess:
    kw = {"capture_output": True, "env": _git_env()}
    kw.update({"text": False} if binary else {"text": True, "encoding": "utf-8", "errors": "replace"})
    return subprocess.run(
        ["git", "-C", str(repo), "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", *args], **kw)


def git_out(repo: Path, *args: str) -> str:
    p = git_run(repo, *args)
    if p.returncode != 0:
        raise CoverageError("BLOCKED", f"git {' '.join(args)}: {(p.stderr or p.stdout or '').strip()[:200]}")
    return (p.stdout or "").strip()


def require_sha(value: str, label: str) -> str:
    raw = (value or "").strip().lower()
    if not SHA40.fullmatch(raw):
        raise CoverageError("BLOCKED", f"{label} must be a 40-char commit SHA")
    return raw


def repository_id(repo: Path, explicit: str | None = None) -> str:
    if explicit:
        return explicit
    p = git_run(repo, "remote", "get-url", "origin")
    if p.returncode != 0:
        return "local"
    url = (p.stdout or "").strip().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    if "github.com" in url:
        return url.split("github.com")[-1].lstrip("/:").replace(":", "/")
    return url or "local"


def classify_kind(path: str) -> str:
    p = path.replace("\\", "/")
    if p.startswith(".github/workflows/") and p.endswith((".yml", ".yaml")):
        return "workflow"
    if p.endswith(".schema.json") or "/schemas/" in p:
        return "schema"
    if p.endswith((".yml", ".yaml", ".json", ".toml", ".ini")):
        return "config"
    return "text"


def architecture_domains(path: str, kind: str) -> list[str]:
    p = path.replace("\\", "/")
    d = []
    if kind == "workflow" or p.startswith(".github/"):
        d += ["workflow-security", "ci-quality"]
    if kind in ("schema", "config") or "/schemas/" in p:
        d += ["interfaces-schemas"]
    if p.startswith("scripts/"):
        d += ["saul-review", "bounded-resources"]
    if p.startswith(".ai/"):
        d += ["sai-governance"]
    return sorted(set(d or ["reviewability"]))


def dependency_digest(blob: bytes) -> str:
    try:
        refs = sorted(set(IMP_RE.findall(blob.decode("utf-8"))))
    except UnicodeDecodeError:
        return sha256_hex(b"binary-deps")
    return sha256_hex("\n".join(refs).encode())


def blob_at(repo: Path, sha: str, path: str) -> bytes:
    p = git_run(repo, "cat-file", "-p", f"{sha}:{path}", binary=True)
    return p.stdout or b"" if p.returncode == 0 else b""


def parse_raw(text: str) -> list[dict]:
    rows = []
    for line in text.splitlines():
        if not line.startswith(":"):
            continue
        meta, paths = line[1:].split("\t", 1)
        parts = meta.split()
        if len(parts) < 5:
            continue
        oldmode, newmode, oldsha, newsha, status = parts[:5]
        left, *rest = paths.split("\t")
        right = rest[0] if rest else left
        rec = {"oldmode": oldmode, "newmode": newmode, "oldsha": oldsha, "newsha": newsha,
               "status": status, "path": right if status[:1] in "RC" else left,
               "old_path": left if status[:1] in "RCD" else None}
        if status.startswith("D"):
            rec["path"] = left
        if status.startswith("A"):
            rec["old_path"] = None
        rows.append(rec)
    return rows


def parse_numstat_binary(text: str) -> set[str]:
    out = set()
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < 3 or parts[0] != "-" or parts[1] != "-":
            continue
        path = parts[2].split(" => ")[-1].strip("{} ") if " => " in parts[2] else parts[2]
        out.add(path)
    return out


def parse_hunks(diff_text: str) -> list[dict]:
    hunks, path, old_path, cur = [], None, None, None
    for line in diff_text.splitlines(True):
        if line.startswith("diff --git "):
            path = old_path = cur = None
        elif line.startswith("rename from "):
            old_path = line[12:].rstrip("\n")
        elif line.startswith("rename to "):
            path = line[10:].rstrip("\n")
        elif line.startswith("--- a/"):
            old_path = line[6:].rstrip("\n")
            if old_path == "/dev/null":
                old_path = None
        elif line.startswith("+++ b/"):
            path = line[6:].rstrip("\n")
            if path == "/dev/null":
                path = old_path
        else:
            m = HUNK_RE.match(line)
            if m:
                cur = {"path": path, "old_path": old_path,
                       "old_range": {"start": int(m.group(1)), "count": int(m.group(2) or 1)},
                       "new_range": {"start": int(m.group(3)), "count": int(m.group(4) or 1)},
                       "body": line}
                hunks.append(cur)
            elif cur is not None and line[:1] in (" ", "+", "-", "\\"):
                cur["body"] += line
    return hunks


def _finish_unit(repo, base, head, path, change_type, kind, *, old_path=None,
                 old_range=None, new_range=None, content=b"") -> dict:
    domains = architecture_domains(path, kind)
    ctx_sha = head if change_type != "delete" else base
    ctx = blob_at(repo, ctx_sha, path if change_type != "delete" else (old_path or path))
    ident = {"path": path, "old_path": old_path, "change_type": change_type,
             "kind": kind, "old_range": old_range, "new_range": new_range}
    return {
        "unit_id": sha256_hex(canonical(ident)), "path": path, "old_path": old_path,
        "change_type": change_type, "kind": kind, "old_range": old_range, "new_range": new_range,
        "content_digest": sha256_hex(content), "context_digest": sha256_hex(ctx),
        "dependency_digest": dependency_digest(ctx), "architecture_domains": domains,
        "architecture_digest": sha256_hex("|".join(domains).encode()),
    }


def build_units(repo: Path, base: str, head: str, raw_rows, binary_paths, hunks) -> list[dict]:
    by_path = defaultdict(list)
    for h in hunks:
        if h.get("path"):
            by_path[h["path"]].append(h)
    units, handled = [], set()

    def add(u):
        units.append(u)
        handled.update({u["path"], u["old_path"]} - {None})

    def fu(path, ctype, kind, **kw):
        return _finish_unit(repo, base, head, path, ctype, kind, **kw)

    for r in raw_rows:
        path, status, kind = r["path"], r["status"], classify_kind(r["path"])
        mode_ch = r["oldmode"] != r["newmode"] and not status.startswith(("A", "D"))
        sample = blob_at(repo, base if status.startswith("D") else head, path)
        is_bin = path in binary_paths or r.get("old_path") in binary_paths or b"\x00" in sample
        if is_bin:
            blob = blob_at(repo, base, r["old_path"] or path) + b"\0" + blob_at(repo, head, path)
            add(fu(path, "binary", "binary", old_path=r.get("old_path"), content=blob))
            continue
        if status.startswith("D"):
            add(fu(path, "delete", kind, old_path=path, content=blob_at(repo, base, path)))
            continue
        if status.startswith(("R", "C")):
            blob = (r["old_path"] or "").encode() + b"\0" + blob_at(repo, head, path)
            add(fu(path, "rename", kind, old_path=r.get("old_path"), content=blob))
            for h in by_path.get(path, []):
                add(fu(path, "hunk", kind, old_path=r.get("old_path"),
                       old_range=h["old_range"], new_range=h["new_range"], content=h["body"].encode()))
            if mode_ch:
                add(fu(path, "mode", kind, old_path=r.get("old_path"),
                       content=f"{r['oldmode']}:{r['newmode']}".encode()))
            continue
        if status.startswith("A"):
            add(fu(path, "add", kind, content=blob_at(repo, head, path)))
            continue
        if mode_ch and r["oldsha"] == r["newsha"]:
            add(fu(path, "mode", kind, content=f"{r['oldmode']}:{r['newmode']}".encode()))
            continue
        file_hunks = by_path.get(path, [])
        if file_hunks:
            for h in file_hunks:
                add(fu(path, "hunk", kind, old_range=h["old_range"], new_range=h["new_range"],
                       content=h["body"].encode()))
        else:
            add(fu(path, "hunk", kind, content=blob_at(repo, head, path)))
        if mode_ch:
            add(fu(path, "mode", kind, content=f"{r['oldmode']}:{r['newmode']}".encode()))
    missing = set()
    for r in raw_rows:
        missing.add(r["path"])
        if r.get("old_path"):
            missing.add(r["old_path"])
    missing -= handled
    if missing:
        raise CoverageError("FAIL", f"changed paths disappeared: {sorted(missing)}")
    units.sort(key=lambda u: (u["path"], u["change_type"], u["unit_id"]))
    return units


def group_shards(units, base, head, diff_digest, policy_digest) -> list[dict]:
    ordered = sorted(units, key=lambda u: u["unit_id"])
    shards = []
    for i in range(0, len(ordered), MAX_UNITS_PER_SHARD):
        ids = [u["unit_id"] for u in ordered[i:i + MAX_UNITS_PER_SHARD]]
        sid = sha256_hex("|".join([base, head, diff_digest, policy_digest, *ids]).encode())
        shards.append({"shard_id": sid, "unit_ids": ids})
    assigned = [i for s in shards for i in s["unit_ids"]]
    expect = [u["unit_id"] for u in ordered]
    if assigned != expect or len(set(assigned)) != len(assigned):
        raise CoverageError("FAIL", "shard partition is not exact")
    return shards


def derive_manifest(repo: Path, base_sha: str, head_sha: str, *,
                    repository: str | None = None, policy_digest: str | None = None) -> dict:
    repo = Path(repo)
    base = require_sha(git_out(repo, "rev-parse", "--verify", f"{base_sha}^{{commit}}"), "base_sha")
    head = require_sha(git_out(repo, "rev-parse", "--verify", f"{head_sha}^{{commit}}"), "head_sha")
    flags = ("--full-index", "--find-renames", "-M")
    raw = git_out(repo, "diff", *flags, "--raw", base, head)
    numstat = git_out(repo, "diff", *flags, "--numstat", base, head)
    patch = git_out(repo, "diff", *flags, "-U3", "--no-color", "--no-ext-diff", base, head)
    units = build_units(repo, base, head, parse_raw(raw), parse_numstat_binary(numstat), parse_hunks(patch))
    policy = policy_digest or default_policy_digest()
    keys = ("unit_id", "path", "change_type", "content_digest",
            "context_digest", "dependency_digest", "architecture_digest")
    unit_root = sha256_hex(canonical([{k: u[k] for k in keys} for u in units]))
    diff_digest = sha256_hex(canonical({"base": base, "head": head, "unit_root": unit_root}))
    return {
        "schema": SCHEMA_MANIFEST, "derived_by": "trusted-git",
        "repository": repository_id(repo, repository), "base_sha": base, "head_sha": head,
        "diff_digest": diff_digest, "unit_root": unit_root, "policy_digest": policy,
        "units": units, "shards": group_shards(units, base, head, diff_digest, policy),
    }


def _empty(verdict, reason):
    return {"verdict": verdict, "reason": reason, "unit_verdicts": {}, "shard_verdicts": {},
            "missing_unit_ids": [], "duplicate_unit_ids": [], "convergence": False}


def _flatten_evidence(docs) -> list[tuple[dict, dict]]:
    if isinstance(docs, dict):
        docs = [docs]
    return [(doc, u) for doc in docs or [] for u in doc.get("units") or []]


def _slot(u: dict) -> tuple:
    return (u.get("path"), u.get("change_type"), u.get("kind") or "",
            (u.get("new_range") or {}).get("start"))


def _stale_or_fail(exp: dict, ev: dict, same_head: bool) -> str:
    pairs = (("content_digest", "STALE_CODE"), ("context_digest", "STALE_CONTEXT"),
             ("dependency_digest", "STALE_CONTEXT"), ("architecture_digest", "STALE_ARCHITECTURE"))
    for key, stale in pairs:
        if ev.get(key) != exp[key]:
            return "FAIL" if same_head else stale
    return "PASS_CURRENT"


def _adjudicate(exp, doc, ev, expected, cur_head, cur_base) -> tuple[str, str | None]:
    same_head = (doc.get("head_sha") or "").lower() == cur_head
    if doc.get("synthetic") is True:
        return "FAIL", "synthetic"
    if doc.get("codex_invoked") is not True:
        return "FAIL", "codex_not_invoked"
    if (doc.get("base_sha") or "").lower() != cur_base:
        return "FAIL", "wrong_base"
    if same_head and doc.get("diff_digest") != expected["diff_digest"]:
        return "FAIL", "wrong_diff_digest"
    if same_head and ev.get("content_digest") != exp["content_digest"]:
        return "FAIL", "wrong_content_digest"
    pol = doc.get("policy_digest") or expected["policy_digest"]
    if pol != expected["policy_digest"]:
        return ("FAIL" if same_head else "STALE_CONTEXT"), "policy"
    v = _stale_or_fail(exp, ev, same_head)
    return v, None if v == "PASS_CURRENT" else v.lower()


def evaluate_coverage(expected: dict, evidence_docs, *,
                      current_head: str | None = None, current_base: str | None = None) -> dict:
    if not expected or expected.get("derived_by") != "trusted-git":
        return _empty("BLOCKED", "expected manifest is not trusted-git")
    units = expected["units"]
    by_id = {u["unit_id"]: u for u in units}
    expected_ids = [u["unit_id"] for u in units]
    if len(expected_ids) != len(set(expected_ids)):
        return _empty("FAIL", "trusted manifest has duplicate units")
    pairs = _flatten_evidence(evidence_docs)
    id_counts = Counter(u.get("unit_id") for _, u in pairs)
    duplicates = sorted(i for i, c in id_counts.items() if i and c > 1)
    cur_head = (current_head or expected["head_sha"]).lower()
    cur_base = (current_base or expected["base_sha"]).lower()
    claimed, used = {}, set()
    for idx, (doc, ev) in enumerate(pairs):
        eid = ev.get("unit_id")
        if eid in by_id and eid not in claimed:
            claimed[eid] = (doc, ev)
            used.add(idx)
    groups_e, groups_p = defaultdict(list), defaultdict(list)
    for u in units:
        if u["unit_id"] not in claimed:
            groups_e[_slot(u)].append(u)
    for i, (d, e) in enumerate(pairs):
        if i not in used:
            groups_p[_slot(e)].append((i, d, e))
    for key, elist in groups_e.items():
        for u, triple in zip(elist, groups_p.get(key) or []):
            claimed[u["unit_id"]] = (triple[1], triple[2])
    missing = [i for i in expected_ids if i not in claimed]
    unit_verdicts, reasons = {}, []
    for uid in expected_ids:
        if uid not in claimed:
            unit_verdicts[uid] = "UNREVIEWED"
            continue
        doc, ev = claimed[uid]
        v, why = _adjudicate(by_id[uid], doc, ev, expected, cur_head, cur_base)
        unit_verdicts[uid] = v
        if why:
            reasons.append(why)
    shard_verdicts = {}
    for shard in expected["shards"]:
        vs = [unit_verdicts.get(i, "UNREVIEWED") for i in shard["unit_ids"]]
        shard_verdicts[shard["shard_id"]] = "PASS" if vs and all(x == "PASS_CURRENT" for x in vs) else "FAIL"
    extra = [i for i in id_counts if i and i not in by_id]
    fail = bool(missing or duplicates or extra or reasons
                or any(v != "PASS_CURRENT" for v in unit_verdicts.values()))
    verdict = "FAIL" if fail else "PASS"
    conv = (verdict == "PASS" and all(v == "PASS_CURRENT" for v in unit_verdicts.values())
            and len(unit_verdicts) == len(expected_ids) and not duplicates)
    reason = "ok" if conv else ("missing_unit" if missing else "duplicate_unit" if duplicates
                                else (reasons[0] if reasons else "coverage_fail"))
    return {"verdict": verdict, "reason": reason, "unit_verdicts": unit_verdicts,
            "shard_verdicts": shard_verdicts, "missing_unit_ids": missing,
            "duplicate_unit_ids": duplicates, "convergence": conv}


def shard_scratch_path(scratch_root: Path, shard_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{32,64}", shard_id or ""):
        raise CoverageError("BLOCKED", "invalid shard_id for scratch")
    return Path(scratch_root) / shard_id


def delete_completed_shard_scratch(scratch_root: Path, shard_id: str) -> Path:
    """Delete Hostinger scratch for a completed shard. Returns the path (must be gone)."""
    p = shard_scratch_path(scratch_root, shard_id)
    if p.is_dir():
        shutil.rmtree(p)
    elif p.exists():
        p.unlink()
    return p


def prior_scratch_absent(scratch_root: Path, shard_id: str) -> bool:
    return not shard_scratch_path(scratch_root, shard_id).exists()


def cmd(argv=None) -> int:
    p = argparse.ArgumentParser(prog="sai_auth_review_coverage")
    p.add_argument("action", nargs="?", choices=("shards", "verify", "self-test"))
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--repo", default=".")
    p.add_argument("--base")
    p.add_argument("--head")
    p.add_argument("--repository")
    p.add_argument("--out")
    p.add_argument("--evidence")
    p.add_argument("--scratch-root")
    p.add_argument("--delete-scratch")
    args = p.parse_args(argv)
    if args.self_test or args.action == "self-test":
        from sai_auth_review_coverage_test import run_fixtures
        n = run_fixtures()
        print(f"sai_auth_review_coverage self-test: {len(n)} fixtures executed")
        return 0
    if args.delete_scratch:
        root = Path(args.scratch_root or os.environ.get("SAI_SHARD_SCRATCH_ROOT") or "/tmp/sai-shard-scratch")
        pth = delete_completed_shard_scratch(root, args.delete_scratch)
        print("SCRATCH_ABSENT" if not pth.exists() else "SCRATCH_PRESENT")
        return 0 if not pth.exists() else 1
    if not args.base or not args.head:
        print("FAIL need --base and --head", file=sys.stderr)
        return 2
    try:
        man = derive_manifest(Path(args.repo), args.base, args.head, repository=args.repository)
    except CoverageError as e:
        print(f"{e.verdict} {e.reason}")
        return 2 if e.verdict == "BLOCKED" else 1
    if args.action != "verify":
        text = json.dumps(man, indent=2)
        Path(args.out).write_text(text + "\n", encoding="utf-8") if args.out else print(text)
        return 0
    docs = json.loads(Path(args.evidence).read_text(encoding="utf-8")) if args.evidence else []
    result = evaluate_coverage(man, docs)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["verdict"] == "PASS" and result["convergence"]:
        return 0
    return 2 if result["verdict"] == "BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(cmd())
