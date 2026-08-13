#!/usr/bin/env python3
"""Codebase health: CI coverage, bloat, duplicates, orphans, runtime self-test."""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    print("code-health: PyYAML is required", file=sys.stderr)
    sys.exit(2)

AGENT_RUNTIME_README = re.compile(r"^\.ai/agents/[^/]+/runtimes/[^/]+/README\.md$")
AUTOMATION_PROFILE = re.compile(
    r"^\.ai/agents/([^/]+)/(?:runtimes/[^/]+/)?automation/profile\.md$"
)


class Result:
    def __init__(self):
        self.fails = []
        self.passes = 0

    def fail(self, msg):
        self.fails.append(msg)
        print(f"FAIL  {msg}", file=sys.stderr)

    def ok(self, msg):
        self.passes += 1
        print(f"PASS  {msg}")

    def exit_code(self):
        return 1 if self.fails else 0


def load_config(root: str) -> dict:
    path = Path(root) / ".ai/_config/code-health.yaml"
    with open(path, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    if not isinstance(cfg, dict) or "checks" not in cfg:
        raise SystemExit("code-health: invalid registry (missing checks)")
    return cfg


def git_files(root: str, exclude_prefixes) -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], cwd=root, text=True)
    files = []
    for line in out.splitlines():
        if any(line.startswith(p) for p in exclude_prefixes):
            continue
        files.append(line)
    return files


def read_text(root: str, rel: str) -> str:
    return (Path(root) / rel).read_bytes().decode("utf-8", errors="replace")


def is_binary(root: str, rel: str) -> bool:
    data = (Path(root) / rel).read_bytes()[:1024]
    return b"\0" in data


def ext_of(rel: str) -> str:
    return os.path.splitext(rel)[1]


def same_family(a: str, b: str) -> bool:
    if AGENT_RUNTIME_README.match(a) and AGENT_RUNTIME_README.match(b):
        return True
    ma, mb = AUTOMATION_PROFILE.match(a), AUTOMATION_PROFILE.match(b)
    return bool(ma and mb and ma.group(1) == mb.group(1))


def check_ci_coverage(root: str, cfg: dict, res: Result) -> None:
    wf_rel = cfg.get("ci", {}).get("workflow", ".github/workflows/agent-audit.yml")
    wf_path = Path(root) / wf_rel
    if not wf_path.is_file():
        res.fail(f"CI workflow missing: {wf_rel}")
        return
    wf = wf_path.read_text(encoding="utf-8")
    for check in cfg["checks"]:
        cid = check.get("id", "?")
        status = check.get("status")
        if status == "active":
            marker = check.get("ci_marker")
            if not marker:
                res.fail(f"active check {cid} has empty ci_marker")
            elif marker not in wf:
                res.fail(f"active check {cid}: ci_marker {marker!r} not in {wf_rel}")
            else:
                res.ok(f"ci-coverage {cid}")
            if check.get("self_test") in (None, "none"):
                res.fail(f"active check {cid} has no self_test")
        elif status == "deferred":
            if check.get("ci_marker"):
                res.fail(f"deferred check {cid} must not set ci_marker until activated")
            else:
                res.ok(f"ci-coverage deferred {cid}")
        else:
            res.fail(f"check {cid} has invalid status {status!r}")

    registered = set()
    for check in cfg["checks"]:
        cmd = check.get("command") or ""
        token = cmd.split()[0] if cmd else ""
        if token:
            registered.add(token)
    exclude = cfg.get("scan", {}).get("exclude_prefixes", [])
    for rel in git_files(root, exclude):
        if not rel.startswith("scripts/verify-"):
            continue
        if "/" in rel[len("scripts/"):]:
            continue
        if rel not in registered:
            res.fail(f"unregistered root verifier: {rel}")
        else:
            res.ok(f"registered {rel}")


def check_bloat(root: str, cfg: dict, files: list[str], res: Result) -> None:
    bloat = cfg["bloat"]
    default_lines = int(bloat.get("default_max_lines", 600))
    default_bytes = int(bloat.get("default_max_bytes", 65536))
    by_ext = bloat.get("by_extension") or {}
    allow = set(bloat.get("allowlist") or [])
    for rel in files:
        if rel in allow or is_binary(root, rel):
            continue
        data = (Path(root) / rel).read_bytes()
        lines = data.count(b"\n") + (0 if data.endswith(b"\n") or not data else 1)
        spec = by_ext.get(ext_of(rel), {})
        max_lines = int(spec.get("max_lines", default_lines))
        max_bytes = int(spec.get("max_bytes", default_bytes))
        if lines > max_lines:
            res.fail(f"bloat {rel}: {lines} lines > {max_lines}")
        elif len(data) > max_bytes:
            res.fail(f"bloat {rel}: {len(data)} bytes > {max_bytes}")
    scanned = len([f for f in files if f not in allow])
    if not any(x.startswith("bloat ") for x in res.fails):
        res.ok(f"bloat ({scanned} files under limit)")


def check_duplicates(root: str, cfg: dict, files: list[str], res: Result) -> None:
    dup = cfg["duplicates"]
    skip_empty = cfg.get("scan", {}).get("skip_empty_for_duplicates", True)
    hashes = defaultdict(list)
    texts = {}
    for rel in files:
        if is_binary(root, rel):
            continue
        data = (Path(root) / rel).read_bytes()
        if skip_empty and not data:
            continue
        hashes[hashlib.sha256(data).hexdigest()].append(rel)
        texts[rel] = data.decode("utf-8", errors="replace")

    if dup.get("exact", True):
        for _h, paths in hashes.items():
            if len(paths) < 2:
                continue
            for i, a in enumerate(paths):
                for b in paths[i + 1 :]:
                    if not same_family(a, b):
                        res.fail(f"exact duplicate: {a} == {b}")

    near = dup.get("near") or {}
    if near.get("enabled"):
        min_lines = int(near.get("min_lines", 60))
        k = int(near.get("shingle_lines", 5))
        thresh = float(near.get("jaccard_threshold", 0.95))
        exclude_base = set(near.get("exclude_basenames") or [])
        candidates = []
        for rel, text in texts.items():
            if os.path.basename(rel) in exclude_base:
                continue
            nlines = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
            if nlines < min_lines:
                continue
            lines = text.splitlines()
            sh = {"\n".join(lines[i : i + k]) for i in range(len(lines) - k + 1)}
            candidates.append((rel, ext_of(rel), sh, nlines))
        for i, (a, ea, sa, _na) in enumerate(candidates):
            for b, eb, sb, _nb in candidates[i + 1 :]:
                if ea != eb or same_family(a, b) or not sa or not sb:
                    continue
                j = len(sa & sb) / len(sa | sb)
                if j >= thresh:
                    res.fail(f"near duplicate ({j:.3f}): {a} ~ {b}")
        res.ok(f"duplicates (exact + near; {len(candidates)} near candidates)")


def check_orphans(root: str, cfg: dict, files: list[str], res: Result) -> None:
    ocfg = cfg["orphans"]
    roots = ocfg.get("roots") or []
    allow = set(ocfg.get("allowlist") or [])
    scripts = []
    for rel in files:
        for r in roots:
            if rel == r or rel.startswith(r.rstrip("/") + "/"):
                scripts.append(rel)
                break
    contents = {}
    for rel in files:
        try:
            contents[rel] = read_text(root, rel)
        except OSError:
            contents[rel] = ""
    for s in scripts:
        if s in allow:
            continue
        base = os.path.basename(s)
        mentioned = False
        for rel, text in contents.items():
            if rel == s:
                continue
            if base in text or s in text:
                mentioned = True
                break
        if not mentioned:
            res.fail(f"orphan script (unreferenced): {s}")
    if not any(x.startswith("orphan ") for x in res.fails):
        res.ok(f"orphans ({len(scripts)} scripts referenced or allowlisted)")


def run_live(root: str, cfg: dict, res: Result) -> None:
    exclude = cfg.get("scan", {}).get("exclude_prefixes", [])
    files = git_files(root, exclude)
    check_ci_coverage(root, cfg, res)
    check_bloat(root, cfg, files, res)
    check_duplicates(root, cfg, files, res)
    check_orphans(root, cfg, files, res)


def _git_init(path: Path, files: dict[str, str]) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "health@test"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "health"], cwd=path, check=True)
    for rel, content in files.items():
        p = path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "fixture"], cwd=path, check=True, capture_output=True
    )


MINI_CFG = {
    "ci": {"workflow": ".github/workflows/agent-audit.yml"},
    "scan": {"exclude_prefixes": [], "skip_empty_for_duplicates": True},
    "bloat": {
        "default_max_lines": 20,
        "default_max_bytes": 4096,
        "by_extension": {".md": {"max_lines": 20}},
        "allowlist": [],
    },
    "duplicates": {
        "exact": True,
        "near": {
            "enabled": True,
            "min_lines": 8,
            "shingle_lines": 3,
            "jaccard_threshold": 0.8,
            "exclude_basenames": [],
        },
    },
    "orphans": {"roots": ["scripts"], "allowlist": []},
    "checks": [
        {
            "id": "demo",
            "status": "active",
            "command": "scripts/verify-demo",
            "ci_marker": "verify-demo",
            "self_test": "synthetic",
        }
    ],
}


def self_test() -> int:
    """Runtime evaluation: known-good trees pass; known-bad trees fail."""
    errors = []

    def expect_fail(name, fn):
        res = Result()
        fn(res)
        if not res.fails:
            errors.append(f"{name}: expected FAIL, got pass")
            print(f"SELFTEST FAIL  {name} (should have failed)", file=sys.stderr)
        else:
            print(f"SELFTEST PASS  {name} rejected bad input")

    def expect_pass(name, fn):
        res = Result()
        fn(res)
        if res.fails:
            errors.append(f"{name}: expected PASS, got {res.fails}")
            print(f"SELFTEST FAIL  {name}: {res.fails}", file=sys.stderr)
        else:
            print(f"SELFTEST PASS  {name}")

    with tempfile.TemporaryDirectory() as tmp:
        bad_bloat = Path(tmp) / "bloat-bad"
        good_bloat = Path(tmp) / "bloat-good"
        _git_init(bad_bloat, {"doc.md": "x\n" * 40})
        _git_init(good_bloat, {"doc.md": "ok\n"})
        expect_fail(
            "bloat-bad",
            lambda r: check_bloat(str(bad_bloat), MINI_CFG, ["doc.md"], r),
        )
        expect_pass(
            "bloat-good",
            lambda r: check_bloat(str(good_bloat), MINI_CFG, ["doc.md"], r),
        )

        bad_dup = Path(tmp) / "dup-bad"
        good_dup = Path(tmp) / "dup-good"
        body = "line\n" * 12
        _git_init(bad_dup, {"a.md": body, "b.md": body})
        _git_init(good_dup, {"a.md": body, "b.md": "other\n" * 12})
        expect_fail(
            "dup-bad",
            lambda r: check_duplicates(str(bad_dup), MINI_CFG, ["a.md", "b.md"], r),
        )
        expect_pass(
            "dup-good",
            lambda r: check_duplicates(str(good_dup), MINI_CFG, ["a.md", "b.md"], r),
        )

        bad_or = Path(tmp) / "or-bad"
        good_or = Path(tmp) / "or-good"
        _git_init(bad_or, {"scripts/lonely": "#!/bin/sh\necho hi\n"})
        _git_init(
            good_or,
            {
                "scripts/used": "#!/bin/sh\necho hi\n",
                "README.md": "run scripts/used\n",
            },
        )
        expect_fail(
            "orphan-bad",
            lambda r: check_orphans(str(bad_or), MINI_CFG, ["scripts/lonely"], r),
        )
        expect_pass(
            "orphan-good",
            lambda r: check_orphans(
                str(good_or), MINI_CFG, ["scripts/used", "README.md"], r
            ),
        )

        bad_ci = Path(tmp) / "ci-bad"
        good_ci = Path(tmp) / "ci-good"
        wf_bad = "name: x\nrun: echo none\n"
        wf_good = "name: x\nrun: verify-demo\n"
        _git_init(
            bad_ci,
            {
                ".github/workflows/agent-audit.yml": wf_bad,
                "scripts/verify-demo": "#!/bin/sh\n",
            },
        )
        _git_init(
            good_ci,
            {
                ".github/workflows/agent-audit.yml": wf_good,
                "scripts/verify-demo": "#!/bin/sh\n",
            },
        )
        expect_fail("ci-coverage-bad", lambda r: check_ci_coverage(str(bad_ci), MINI_CFG, r))
        expect_pass(
            "ci-coverage-good", lambda r: check_ci_coverage(str(good_ci), MINI_CFG, r)
        )

    if errors:
        print(f"code-health self-test: {len(errors)} failure(s)", file=sys.stderr)
        return 1
    print("code-health self-test: all fixture evaluations passed")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="SAI codebase health checks")
    parser.add_argument(
        "command",
        nargs="?",
        default="all",
        choices=["all", "ci-coverage", "bloat", "duplicates", "orphans", "list"],
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", default=None)
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    root = args.root or subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()
    cfg = load_config(root)
    res = Result()
    exclude = cfg.get("scan", {}).get("exclude_prefixes", [])
    files = git_files(root, exclude)

    if args.command == "list":
        for check in cfg["checks"]:
            print(f"{check.get('status','?'):9} {check.get('id')}  {check.get('command')}")
        return 0
    if args.command == "all":
        run_live(root, cfg, res)
    elif args.command == "ci-coverage":
        check_ci_coverage(root, cfg, res)
    elif args.command == "bloat":
        check_bloat(root, cfg, files, res)
    elif args.command == "duplicates":
        check_duplicates(root, cfg, files, res)
    elif args.command == "orphans":
        check_orphans(root, cfg, files, res)

    if res.fails:
        print(f"code-health: {len(res.fails)} FAIL(s), {res.passes} PASS", file=sys.stderr)
    else:
        print(f"code-health: {res.passes} PASS")
    return res.exit_code()


if __name__ == "__main__":
    sys.exit(main())
