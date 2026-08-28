"""CLI entry point for Foundry spin-off tooling."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from spinoff.audit import scan_forbidden_refs
from spinoff.materializer import materialize_candidate
from spinoff.planner import build_plan_from_path


def _repo_root(value: str) -> str:
    return str(Path(value).resolve())


def cmd_plan(args: argparse.Namespace) -> int:
    plan = build_plan_from_path(args.graph, args.repo_root)
    payload = {
        "exportable": plan.exportable,
        "plan_hash": plan.plan_hash,
        "graph_hash": plan.graph_hash,
        "blockers": plan.blockers,
        "closure": plan.closure,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if plan.exportable else 2


def cmd_materialize(args: argparse.Namespace) -> int:
    plan = build_plan_from_path(args.graph, args.repo_root)
    materialize_candidate(plan, args.repo_root, args.out_dir)
    hits = scan_forbidden_refs(args.out_dir)
    if hits:
        for hit in hits:
            print(hit, file=sys.stderr)
        return 3
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="foundry-spinoff")
    parser.add_argument("--repo-root", default=".", type=_repo_root)
    sub = parser.add_subparsers(dest="command", required=True)

    plan_cmd = sub.add_parser("plan", help="build and summarize a spin-off plan")
    plan_cmd.add_argument("graph", help="path to foundry.graph.json")
    plan_cmd.set_defaults(func=cmd_plan)

    mat_cmd = sub.add_parser("materialize", help="materialize an exportable plan")
    mat_cmd.add_argument("graph", help="path to foundry.graph.json")
    mat_cmd.add_argument("out_dir", help="output directory for candidate tree")
    mat_cmd.set_defaults(func=cmd_materialize)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
