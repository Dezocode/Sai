#!/usr/bin/env python3
"""Anti-balloon fixtures. Prints SELFTEST PASS  <id>."""
from __future__ import annotations

from pathlib import Path
import tempfile

import sai_auth as a
from sai_auth_antiballoon import (
    duplicate_guard_ids, independent_ready, orphan_quality_paths,
    per_blocker_workflows, raised_thresholds, unexecuted_guards,
)


def run_antiballoon_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as tmp:
        good = Path(tmp) / "good"
        good.mkdir(parents=True)
        a.git(good, "init")
        a.git(good, "config", "user.email", "t@example.com")
        a.git(good, "config", "user.name", "t")
        cfg = good / ".ai/_config"
        cfg.mkdir(parents=True)
        (cfg / "code-health.yaml").write_text(
            "bloat:\n  by_extension:\n    \".yaml\": {max_lines: 300}\n"
            "    \".py\": {max_lines: 500}\nchecks:\n  - {id: a, status: active}\n",
            encoding="utf-8",
        )
        (cfg / "code-health-saul.yaml").write_text(
            "checks:\n  - {id: saul-gated-ci, status: active, command: scripts/verify-saul-gated-ci --self-test}\n",
            encoding="utf-8",
        )
        (cfg / "pr-ballooning.yaml").write_text(
            "warning_thresholds: {yaml_lines: 300, py_lines: 500, md_lines: 600}\n",
            encoding="utf-8",
        )
        wf = good / ".github/workflows"
        wf.mkdir(parents=True)
        (wf / "agent-audit.yml").write_text(
            "run: scripts/verify-saul-gated-ci --self-test\n", encoding="utf-8",
        )
        (good / "scripts").mkdir()
        (good / "scripts/verify-saul-gated-ci").write_text("#!/bin/sh\n", encoding="utf-8")
        schema = good / ".ai/shared/schemas"
        schema.mkdir(parents=True)
        (schema / "saul-exact-state-review.schema.json").write_text("{}\n", encoding="utf-8")
        chk = good / "scripts/lib"
        chk.mkdir(parents=True)
        (chk / "sai_auth_saul_check.py").write_text(
            "EXACT_STATE_SCHEMA = 'saul-exact-state-review.schema.json'\n", encoding="utf-8",
        )
        a.git(good, "add", ".")
        a.git(good, "commit", "-m", "g")
        if duplicate_guard_ids(good) or per_blocker_workflows(good) or unexecuted_guards(good):
            raise RuntimeError("good tree should be clean")
        if orphan_quality_paths(good):
            raise RuntimeError(orphan_quality_paths(good))
        if raised_thresholds(good):
            raise RuntimeError(raised_thresholds(good))
        executed.add("antiballoon-clean-good")
        print("SELFTEST PASS  antiballoon-clean-good")

        dup = Path(tmp) / "dup"
        dcfg = dup / ".ai/_config"
        dcfg.mkdir(parents=True)
        (dcfg / "code-health.yaml").write_text(
            "checks:\n  - {id: x}\ninclude: [code-health-saul.yaml]\n", encoding="utf-8",
        )
        (dcfg / "code-health-saul.yaml").write_text("checks:\n  - {id: x}\n", encoding="utf-8")
        if "x" not in duplicate_guard_ids(dup):
            raise RuntimeError(duplicate_guard_ids(dup))
        executed.add("antiballoon-dup-guard-bad")
        print("SELFTEST PASS  antiballoon-dup-guard-bad")

        wfbad = Path(tmp) / "wfb"
        wdir = wfbad / ".github/workflows"
        wdir.mkdir(parents=True)
        (wdir / "saul-blocker-cto-026.yml").write_text(
            "name: Saul / Blocker / CTO-026\n", encoding="utf-8",
        )
        if not per_blocker_workflows(wfbad):
            raise RuntimeError("expected per-blocker workflow")
        executed.add("antiballoon-per-blocker-workflow-bad")
        print("SELFTEST PASS  antiballoon-per-blocker-workflow-bad")

        unex = Path(tmp) / "unex"
        ucfg = unex / ".ai/_config"
        ucfg.mkdir(parents=True)
        (ucfg / "code-health-saul.yaml").write_text(
            "checks:\n  - {id: ghost, status: active, command: scripts/verify-saul-ghost --self-test}\n",
            encoding="utf-8",
        )
        (unex / ".github/workflows").mkdir(parents=True)
        (unex / ".github/workflows/agent-audit.yml").write_text("run: echo none\n", encoding="utf-8")
        if "ghost" not in unexecuted_guards(unex):
            raise RuntimeError(unexecuted_guards(unex))
        executed.add("antiballoon-unexecuted-guard-bad")
        print("SELFTEST PASS  antiballoon-unexecuted-guard-bad")

        thr = Path(tmp) / "thr"
        tcfg = thr / ".ai/_config"
        tcfg.mkdir(parents=True)
        (tcfg / "code-health.yaml").write_text(
            "bloat:\n  by_extension:\n    \".yaml\": {max_lines: 999}\n", encoding="utf-8",
        )
        if not raised_thresholds(thr):
            raise RuntimeError("expected raised threshold")
        executed.add("antiballoon-threshold-raised-bad")
        print("SELFTEST PASS  antiballoon-threshold-raised-bad")

        rdy = Path(tmp) / "rdy"
        (rdy / ".ai/contracts/20260813-pr62-saul-smoke").mkdir(parents=True)
        (rdy / ".ai/contracts/20260813-pr62-saul-smoke/merge-readiness.yaml").write_text(
            "status: READY\nlogical: COMPLETE\n", encoding="utf-8",
        )
        if not independent_ready(rdy):
            raise RuntimeError("expected independent READY")
        executed.add("antiballoon-ready-truth-bad")
        print("SELFTEST PASS  antiballoon-ready-truth-bad")

        orph = Path(tmp) / "orph"
        orph.mkdir(parents=True)
        a.git(orph, "init")
        a.git(orph, "config", "user.email", "t@example.com")
        a.git(orph, "config", "user.name", "t")
        (orph / "scripts").mkdir()
        (orph / "scripts/verify-saul-orphan").write_text("#!/bin/sh\n", encoding="utf-8")
        a.git(orph, "add", "scripts/verify-saul-orphan")
        a.git(orph, "commit", "-m", "o")
        if not orphan_quality_paths(orph):
            raise RuntimeError("expected orphan verifier")
        executed.add("antiballoon-orphan-schema-bad")
        print("SELFTEST PASS  antiballoon-orphan-schema-bad")
    return executed


if __name__ == "__main__":
    run_antiballoon_fixtures()
    print("sai_auth_antiballoon_test: OK")
