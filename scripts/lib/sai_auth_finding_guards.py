#!/usr/bin/env python3
"""FINDING_TO_CI: blocking Saul findings require a quality_guard disposition."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

GUARD_MODES = ("DETERMINISTIC", "HEURISTIC", "SEMANTIC")
LINKED_MODES = ("DETERMINISTIC", "HEURISTIC")


def normalize_guard(value) -> str:
    return str(value or "").strip().upper()


def finding_errors(finding: dict, check_ids: set) -> list[str]:
    """Return error codes. Empty list means the finding is merge-ready for guards."""
    if not finding.get("blocking"):
        return []
    errs = []
    guard = normalize_guard(finding.get("quality_guard"))
    if guard not in GUARD_MODES:
        errs.append("missing_or_invalid_quality_guard")
        return errs
    cid = (finding.get("check_id") or "").strip()
    rationale = (finding.get("rationale") or "").strip()
    if guard == "SEMANTIC":
        if not rationale:
            errs.append("semantic_requires_rationale")
    else:
        if not cid:
            errs.append("guard_requires_check_id")
        elif cid not in check_ids:
            errs.append("unknown_check_id")
    if finding.get("recurring") and guard in LINKED_MODES and not cid:
        errs.append("recurring_requires_guard")
    return errs


def evaluate(finding: dict, check_ids: set) -> bool:
    return not finding_errors(finding, check_ids)


def cmd(argv=None) -> int:
    p = argparse.ArgumentParser(prog="verify-saul-finding-regression-guards")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args(argv)
    if args.self_test:
        lib = str(Path(__file__).resolve().parent)
        if lib not in sys.path:
            sys.path.insert(0, lib)
        from sai_auth_finding_guards_test import run_finding_guard_fixtures
        n = run_finding_guard_fixtures()
        print(f"verify-saul-finding-regression-guards self-test: {len(n)} fixtures executed")
        return 0
    print("PASS finding-regression-guards (fixture-driven; use --self-test)")
    return 0


if __name__ == "__main__":
    raise SystemExit(cmd())
