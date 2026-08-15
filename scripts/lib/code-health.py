#!/usr/bin/env python3
"""Codebase health: CI coverage, bloat, duplicates, orphans, runtime self-test."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
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

_CI_PATH = Path(__file__).resolve().parent / "code-health-ci.py"
_spec = importlib.util.spec_from_file_location("code_health_ci", _CI_PATH)
ci = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ci)

KNOWN_FIXTURES = {
    "bloat-bad", "bloat-good",
    "dup-bad", "dup-good",
    "orphan-bad", "orphan-good",
    "ci-coverage-bad", "ci-coverage-good", "ci-coverage-mention-only",
    "ci-coverage-conditional-job", "ci-coverage-step-if",
    "registry-mode-invalid", "registry-health-detector-livepass", "registry-valid",
    "authorization-valid-good", "authorization-unbound-bad",
    "authorization-wrong-role-bad", "authorization-wrong-runtime-bad",
    "authorization-no-contract-bad", "authorization-cora-not-verified-bad",
    "authorization-sai-not-verified-bad", "authorization-path-out-of-scope-bad",
    "authorization-wrong-branch-bad", "authorization-revoked-contract-bad",
    "authorization-stale-revision-bad", "authorization-missing-trailer-bad",
    "authorization-forged-officer-trailer-bad", "authorization-officer-grant-good",
    "authorization-bootstrap-expired-bad",
}


def _yaml_fixtures(rel: str) -> set:
    p = Path(__file__).resolve().parents[2] / rel
    if not p.is_file() or yaml is None:
        return set()
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return {f for c in data.get("checks") or [] for f in (c.get("fixtures") or [])}


KNOWN_FIXTURES |= _yaml_fixtures(".ai/_config/code-health-saul.yaml")


class Result:
    def __init__(self, quiet=False):
        self.fails = []
        self.passes = 0
        self.quiet = quiet

    def fail(self, msg):
        self.fails.append(msg)
        if not self.quiet:
            print(f"FAIL  {msg}", file=sys.stderr)

    def ok(self, msg):
        self.passes += 1
        if not self.quiet:
            print(f"PASS  {msg}")

    def exit_code(self):
        return 1 if self.fails else 0


def load_config(root: str) -> dict:
    path = Path(root) / ".ai/_config/code-health.yaml"
    with open(path, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    if not isinstance(cfg, dict) or "checks" not in cfg:
        raise SystemExit("code-health: invalid registry (missing checks)")
    for rel in cfg.get("include") or []:
        ip = path.parent / rel
        if not ip.is_file():
            raise SystemExit(f"code-health: missing include {rel}")
        inc = yaml.safe_load(ip.read_text(encoding="utf-8")) or {}
        cfg.setdefault("checks", []).extend(inc.get("checks") or [])
        extra = inc.get("saul_quality_learning")
        if isinstance(extra, dict):
            cfg.setdefault("saul_quality_learning", {}).update(extra)
    return cfg


def git_files(root: str, exclude_prefixes) -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], cwd=root, text=True)
    return [ln for ln in out.splitlines() if not any(ln.startswith(p) for p in exclude_prefixes)]


def read_text(root: str, rel: str) -> str:
    return (Path(root) / rel).read_bytes().decode("utf-8", errors="replace")


def is_binary(root: str, rel: str) -> bool:
    return b"\0" in (Path(root) / rel).read_bytes()[:1024]


def ext_of(rel: str) -> str:
    return os.path.splitext(rel)[1]


def check_bloat(root: str, cfg: dict, files: list[str], res: Result) -> None:
    bloat = cfg["bloat"]
    default_lines = int(bloat.get("default_max_lines", 600))
    default_bytes = int(bloat.get("default_max_bytes", 65536))
    by_ext = bloat.get("by_extension") or {}
    allow = set(bloat.get("allowlist") or [])
    n0 = len(res.fails)
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
    if len(res.fails) == n0:
        res.ok(f"bloat ({len([f for f in files if f not in allow])} files under limit)")


def check_duplicates(root: str, cfg: dict, files: list[str], res: Result) -> None:
    dup = cfg["duplicates"]
    families = dup.get("families") or []
    skip_empty = cfg.get("scan", {}).get("skip_empty_for_duplicates", True)
    hashes = defaultdict(list)
    texts = {}
    n0 = len(res.fails)
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
                    if not ci.same_family(a, b, families):
                        res.fail(f"exact duplicate: {a} == {b}")

    near = dup.get("near") or {}
    candidates = []
    if near.get("enabled"):
        min_lines = int(near.get("min_lines", 60))
        k = int(near.get("shingle_lines", 5))
        thresh = float(near.get("jaccard_threshold", 0.95))
        exclude_base = set(near.get("exclude_basenames") or [])
        for rel, text in texts.items():
            if os.path.basename(rel) in exclude_base:
                continue
            nlines = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
            if nlines < min_lines:
                continue
            lines = text.splitlines()
            sh = {"\n".join(lines[i : i + k]) for i in range(len(lines) - k + 1)}
            candidates.append((rel, ext_of(rel), sh))
        for i, (a, ea, sa) in enumerate(candidates):
            for b, eb, sb in candidates[i + 1 :]:
                if ea != eb or ci.same_family(a, b, families) or not sa or not sb:
                    continue
                j = len(sa & sb) / len(sa | sb)
                if j >= thresh:
                    res.fail(f"near duplicate ({j:.3f}): {a} ~ {b}")
    if len(res.fails) == n0:
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
    n0 = len(res.fails)
    for s in scripts:
        if s in allow:
            continue
        base = os.path.basename(s)
        if any(rel != s and (base in text or s in text) for rel, text in contents.items()):
            continue
        res.fail(f"orphan script (unreferenced): {s}")
    if len(res.fails) == n0:
        res.ok(f"orphans ({len(scripts)} scripts referenced or allowlisted)")


def run_live(root: str, cfg: dict, res: Result) -> None:
    exclude = cfg.get("scan", {}).get("exclude_prefixes", [])
    files = git_files(root, exclude)
    ci.check_ci_coverage(root, cfg, res, git_files, KNOWN_FIXTURES)
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
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=path, check=True, capture_output=True)


MINI_RTE = {
    "modes": ["synthetic", "live-pass", "none"],
    "require_negative_fixtures_for_classes": ["health-detector"],
}
MINI_CFG = {
    "ci": {
        "workflow": ".github/workflows/agent-audit.yml",
        "coverage_jobs": ["icm-enforcement"],
    },
    "runtime_evaluation": MINI_RTE,
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
        "families": [],
    },
    "orphans": {"roots": ["scripts"], "allowlist": []},
    "checks": [
        {
            "id": "demo",
            "class": "structure",
            "status": "active",
            "command": "scripts/verify-demo",
            "self_test": "synthetic",
            "fixtures": ["ci-coverage-bad", "ci-coverage-good"],
        }
    ],
}

WF_GOOD = """
name: x
jobs:
  icm-enforcement:
    steps:
      - run: scripts/verify-demo
"""
WF_MENTION = """
name: x
jobs:
  icm-enforcement:
    steps:
      - run: |
          grep -q scripts/verify-demo .github/workflows/agent-audit.yml
          test -f scripts/verify-demo
          echo scripts/verify-demo
          chmod +x scripts/verify-demo
          # scripts/verify-demo
"""
WF_NONE = """
name: x
jobs:
  icm-enforcement:
    steps:
      - run: echo none
"""
WF_CONDITIONAL_JOB = """
name: x
jobs:
  icm-enforcement:
    steps:
      - run: echo none
  merge-handoff-slack:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - run: scripts/verify-demo
"""
WF_STEP_IF = """
name: x
jobs:
  icm-enforcement:
    steps:
      - if: github.ref == 'refs/heads/main'
        run: scripts/verify-demo
"""


def self_test() -> int:
    errors = []
    executed = set()

    def expect_fail(name, fn):
        executed.add(name)
        res = Result(quiet=True)
        fn(res)
        if not res.fails:
            errors.append(f"{name}: expected FAIL, got pass")
            print(f"SELFTEST FAIL  {name} (should have failed)", file=sys.stderr)
        else:
            print(f"SELFTEST PASS  {name} rejected bad input")

    def expect_pass(name, fn):
        executed.add(name)
        res = Result(quiet=True)
        fn(res)
        if res.fails:
            errors.append(f"{name}: expected PASS, got {res.fails}")
            print(f"SELFTEST FAIL  {name}: {res.fails}", file=sys.stderr)
        else:
            print(f"SELFTEST PASS  {name}")

    with tempfile.TemporaryDirectory() as tmp:
        bad_bloat, good_bloat = Path(tmp) / "bloat-bad", Path(tmp) / "bloat-good"
        _git_init(bad_bloat, {"doc.md": "x\n" * 40})
        _git_init(good_bloat, {"doc.md": "ok\n"})
        expect_fail("bloat-bad", lambda r: check_bloat(str(bad_bloat), MINI_CFG, ["doc.md"], r))
        expect_pass("bloat-good", lambda r: check_bloat(str(good_bloat), MINI_CFG, ["doc.md"], r))

        body = "line\n" * 12
        bad_dup, good_dup = Path(tmp) / "dup-bad", Path(tmp) / "dup-good"
        _git_init(bad_dup, {"a.md": body, "b.md": body})
        _git_init(good_dup, {"a.md": body, "b.md": "other\n" * 12})
        expect_fail("dup-bad", lambda r: check_duplicates(str(bad_dup), MINI_CFG, ["a.md", "b.md"], r))
        expect_pass("dup-good", lambda r: check_duplicates(str(good_dup), MINI_CFG, ["a.md", "b.md"], r))

        bad_or, good_or = Path(tmp) / "or-bad", Path(tmp) / "or-good"
        _git_init(bad_or, {"scripts/lonely": "#!/bin/sh\necho hi\n"})
        _git_init(good_or, {"scripts/used": "#!/bin/sh\necho hi\n", "README.md": "run scripts/used\n"})
        expect_fail("orphan-bad", lambda r: check_orphans(str(bad_or), MINI_CFG, ["scripts/lonely"], r))
        expect_pass(
            "orphan-good",
            lambda r: check_orphans(str(good_or), MINI_CFG, ["scripts/used", "README.md"], r),
        )

        def cov(path, wf):
            _git_init(
                path,
                {".github/workflows/agent-audit.yml": wf, "scripts/verify-demo": "#!/bin/sh\n"},
            )
            return lambda r: ci.check_ci_coverage(str(path), MINI_CFG, r, git_files, KNOWN_FIXTURES)

        expect_fail("ci-coverage-bad", cov(Path(tmp) / "ci-bad", WF_NONE))
        expect_pass("ci-coverage-good", cov(Path(tmp) / "ci-good", WF_GOOD))
        expect_fail("ci-coverage-mention-only", cov(Path(tmp) / "ci-mention", WF_MENTION))
        expect_fail(
            "ci-coverage-conditional-job",
            cov(Path(tmp) / "ci-cond-job", WF_CONDITIONAL_JOB),
        )
        expect_fail("ci-coverage-step-if", cov(Path(tmp) / "ci-step-if", WF_STEP_IF))

    def check_reg(name, mutate, should_fail):
        cfg = yaml.safe_load(yaml.dump(MINI_CFG))
        mutate(cfg)
        if should_fail:
            expect_fail(name, lambda r: ci.validate_registry(cfg, KNOWN_FIXTURES, r))
        else:
            expect_pass(name, lambda r: ci.validate_registry(cfg, KNOWN_FIXTURES, r))

    check_reg(
        "registry-mode-invalid",
        lambda c: c["checks"][0].__setitem__("self_test", "totally-made-up"),
        True,
    )
    check_reg(
        "registry-health-detector-livepass",
        lambda c: (c["checks"][0].__setitem__("class", "health-detector"),
                   c["checks"][0].__setitem__("self_test", "live-pass")),
        True,
    )
    check_reg("registry-valid", lambda c: None, False)

    auth = Path(__file__).resolve().parent / "sai_auth_test.py"
    if auth.is_file():
        spec = importlib.util.spec_from_file_location("sai_auth_test", auth)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        executed.update(mod.run_synthetic_fixtures())

    root = ""
    try:
        root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    except subprocess.CalledProcessError:
        pass
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent) + os.pathsep + env.get("PYTHONPATH", "")
    if root:
        live = load_config(root)
        ci.collect_selftest_fixtures(root, live, executed, env)
        for check in live.get("checks") or []:
            if check.get("self_test") != "synthetic":
                continue
            for fix in check.get("fixtures") or []:
                if fix not in executed:
                    errors.append(f"declared fixture {fix!r} on {check.get('id')} was not executed")

    if errors:
        print(f"code-health self-test: {len(errors)} failure(s)", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
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
        ci.check_ci_coverage(root, cfg, res, git_files, KNOWN_FIXTURES)
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
