"""Materialize spin-off candidate trees from export plans."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Dict

from spinoff.model import SpinoffPlan


def _relative_output_path(node) -> Path:
    if node.rewrite_to:
        return Path(node.rewrite_to)
    if node.path:
        return Path(node.path)
    if node.kind == "service":
        return Path("contracts") / f"{node.id}.contract.txt"
    return Path(node.id)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    canonical = json.dumps(payload, sort_keys=True, indent=2) + "\n"
    path.write_text(canonical, encoding="utf-8")


def materialize_candidate(plan: SpinoffPlan, repo_root: str, out_dir: str) -> Dict[str, str]:
    if not plan.exportable:
        raise ValueError("plan is not exportable: " + "; ".join(plan.blockers))

    root = Path(repo_root).resolve()
    output = Path(out_dir).resolve()
    if output.exists():
        for child in sorted(output.iterdir(), reverse=True):
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    output.mkdir(parents=True, exist_ok=True)

    manifest: Dict[str, str] = {}
    prototype_root = root / plan.frozen.prototype_root

    for node_id in plan.closure:
        node = plan.nodes[node_id]
        rel_out = _relative_output_path(node)
        dest = output / rel_out

        if node.strategy == "EXPORT_COPY":
            src = prototype_root / node.path
            if not src.is_file():
                raise FileNotFoundError(f"missing export source: {src}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            manifest[str(rel_out)] = hashlib.sha256(dest.read_bytes()).hexdigest()
        elif node.strategy == "REMOTE":
            stub = {
                "node_id": node.id,
                "name": node.name,
                "contract": node.contract,
                "strategy": node.strategy,
            }
            contract_path = dest if dest.suffix == ".json" else dest.with_suffix(".json")
            _write_json(contract_path, stub)
            manifest[str(contract_path.relative_to(output))] = node.contract
        elif node.strategy == "DROP":
            continue

    provenance = {
        "tool_version": plan.tool_version,
        "plan_hash": plan.plan_hash,
        "graph_hash": plan.graph_hash,
        "frozen": {
            "repo": plan.frozen.repo,
            "base_ref": plan.frozen.base_ref,
            "head_sha": plan.frozen.head_sha,
            "prototype_root": plan.frozen.prototype_root,
            "prototype_head_sha": plan.frozen.prototype_head_sha,
        },
        "manifest": dict(sorted(manifest.items())),
    }
    _write_json(output / "PROVENANCE.json", provenance)
    return manifest
