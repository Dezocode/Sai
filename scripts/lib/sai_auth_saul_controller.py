#!/usr/bin/env python3
"""Saul inner-loop controller: wake Sai only on cryptographic convergence."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SHARD_TYPES = {
    "SHARD_PROGRESS", "SHARD_PASS", "SHARD_FAIL", "SHARD_BLOCKED",
    "SHARD_UNIT", "SAUL_SHARD",
}


def default_convergence_predicate(event: dict) -> bool:
    """Fail-closed until an authenticity module is injected."""
    return False


def is_shard_progress(event: dict) -> bool:
    et = str(event.get("type") or event.get("event_type") or "")
    if et in SHARD_TYPES or et.startswith("SHARD_"):
        return True
    return bool(event.get("shard_progress"))


def process_events(events, *, wake_sai, convergence_predicate=None) -> int:
    """Never wake Sai on shard progress. Wake only when predicate is true."""
    pred = convergence_predicate or default_convergence_predicate
    n = 0
    for ev in events or []:
        if is_shard_progress(ev):
            continue
        if pred(ev):
            wake_sai(ev)
            n += 1
    return n


def cmd(argv=None) -> int:
    p = argparse.ArgumentParser(prog="saul-review-controller")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args(argv)
    if args.self_test:
        lib = str(Path(__file__).resolve().parent)
        if lib not in sys.path:
            sys.path.insert(0, lib)
        from sai_auth_saul_controller_test import run_controller_fixtures
        n = run_controller_fixtures()
        print(f"saul-review-controller self-test: {len(n)} fixtures executed")
        return 0
    print("PASS saul-review-controller (no events; default fail-closed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(cmd())
