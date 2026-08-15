#!/usr/bin/env python3
"""Decision-0005 anti-balloon detector. Not a second framework.

Fails on duplicate guard IDs, per-blocker Saul workflows, registered-but
unexecuted guards, orphan schemas/scripts, independent READY claims, and
raised bloat thresholds that hide a fail.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sai_auth as a  # noqa: E402

try:
    import yaml
except ImportError:
    yaml = None

CAPS = {".yml": 300, ".yaml": 300, ".py": 500, ".md": 600}
BLOCKER_WF = re.compile(r"saul[-_]blocker[-_]", re.I)
READY_WORDS = re.compile(r"\b(READY_FOR_HUMAN_REVIEW|liveness:\s*READY)\b")


def _load(path: Path):
    if yaml is None or not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def duplicate_guard_ids(root) -> list:
    ids = []
    data = _load(Path(root) / ".ai/_config/code-health.yaml")
    for c in data.get("checks") or []:
        if c.get("id"):
            ids.append(c["id"])
    for inc in data.get("include") or []:
        extra = _load(Path(root) / ".ai/_config" / inc)
        for c in extra.get("checks") or []:
            if c.get("id"):
                ids.append(c["id"])
    counts = Counter(ids)
    return [i for i, n in counts.items() if n > 1]


def per_blocker_workflows(root) -> list:
    wf = Path(root) / ".github" / "workflows"
    if not wf.is_dir():
        return []
    hits = []
    for p in wf.glob("*.yml"):
        if BLOCKER_WF.search(p.name):
            hits.append(str(p.relative_to(root)))
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if re.search(r"^name:\s*Saul / Blocker /", text, re.M):
            hits.append(str(p.relative_to(root)))
    return hits


def unexecuted_guards(root, executed=None) -> list:
    data = _load(Path(root) / ".ai/_config/code-health-saul.yaml")
    wf = Path(root) / ".github/workflows/agent-audit.yml"
    text = wf.read_text(encoding="utf-8") if wf.is_file() else ""
    missing = []
    for c in data.get("checks") or []:
        if c.get("status") != "active":
            continue
        cmd = (c.get("command") or "").split()
        token = cmd[0] if cmd else ""
        if token and token not in text:
            missing.append(c.get("id") or token)
    return missing


def orphan_quality_paths(root) -> list:
    hits = []
    try:
        tracked = a.git(root, "ls-files").stdout.splitlines()
    except Exception:
        return hits
    refs = ""
    for rel in (
        ".github/workflows/agent-audit.yml",
        ".ai/_config/code-health-saul.yaml",
        "scripts/lib/sai_auth_saul_check.py",
        "scripts/lib/sai_auth_saul_gated.py",
    ):
        p = Path(root) / rel
        if p.is_file():
            refs += p.read_text(encoding="utf-8", errors="replace")
    for rel in tracked:
        base = Path(rel).name
        if rel.startswith("scripts/verify-saul-") and rel.count("/") == 1:
            if base not in refs and rel not in refs:
                hits.append(rel)
    schema = "saul-exact-state-review.schema.json"
    if any(t.endswith(schema) for t in tracked) and schema not in refs:
        hits.append(".ai/shared/schemas/" + schema)
    return hits


def independent_ready(root) -> list:
    hits = []
    resume_ok = False
    compact = {}
    try:
        from sai_auth_resume import reconstruct
        compact = reconstruct(root)
        resume_ok = bool(compact.get("exit_predicate_satisfied"))
    except Exception:
        pass
    live = str(compact.get("liveness") or "")
    if live in ("READY", "COMPLETE", "TERMINAL", "DONE") and not resume_ok:
        hits.append("reconstructed_false_terminal")
    p = Path(root) / ".ai/contracts/20260813-pr62-saul-smoke/merge-readiness.yaml"
    if p.is_file():
        text = p.read_text(encoding="utf-8")
        if re.search(r"^(status|logical):\s*(READY|COMPLETE|TERMINAL)\s*$", text, re.M):
            if not resume_ok:
                hits.append("merge-readiness.yaml")
    return hits


def raised_thresholds(root) -> list:
    cfg = _load(Path(root) / ".ai/_config/code-health.yaml")
    bloat = (cfg.get("bloat") or {}).get("by_extension") or {}
    hits = []
    for ext, cap in CAPS.items():
        got = (bloat.get(ext) or {}).get("max_lines")
        if got is not None and int(got) > cap:
            hits.append(f"{ext}:{got}>{cap}")
    warn = _load(Path(root) / ".ai/_config/pr-ballooning.yaml")
    wt = warn.get("warning_thresholds") or {}
    for key, cap in (("yaml_lines", 300), ("py_lines", 500), ("md_lines", 600)):
        if key in wt and int(wt[key]) > cap:
            hits.append(f"pr-ballooning:{key}")
    return hits


def evaluate(root) -> list:
    return (
        [f"dup:{x}" for x in duplicate_guard_ids(root)]
        + [f"blocker_wf:{x}" for x in per_blocker_workflows(root)]
        + [f"unexecuted:{x}" for x in unexecuted_guards(root)]
        + [f"orphan:{x}" for x in orphan_quality_paths(root)]
        + [f"ready:{x}" for x in independent_ready(root)]
        + [f"threshold:{x}" for x in raised_thresholds(root)]
    )


def cmd(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        from sai_auth_antiballoon_test import run_antiballoon_fixtures
        n = run_antiballoon_fixtures()
        print(f"verify-saul-anti-balloon self-test: {len(n)} fixtures executed")
        return 0
    root = a.toplevel() or os.getcwd()
    fails = evaluate(root)
    if fails:
        print("FAIL", " ".join(fails[:20]))
        return 1
    print("PASS anti-balloon")
    return 0


if __name__ == "__main__":
    raise SystemExit(cmd())
