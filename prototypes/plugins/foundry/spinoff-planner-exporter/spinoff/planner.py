"""Build deterministic spin-off plans from Foundry graphs."""

from __future__ import annotations

import hashlib
import json
from typing import Dict, List, Optional

from spinoff import __version__
from spinoff.freeze import freeze_source
from spinoff.graph_input import (
    DependencyGraph,
    canonical_graph_hash,
    load_graph,
    parse_graph,
    transitive_closure,
    validate_node,
)
from spinoff.model import PlannedNode, SpinoffPlan
from spinoff.strategy import map_classification


def _plan_payload(plan: SpinoffPlan) -> dict:
    return {
        "tool_version": plan.tool_version,
        "graph_hash": plan.graph_hash,
        "frozen": {
            "repo": plan.frozen.repo,
            "base_ref": plan.frozen.base_ref,
            "head_sha": plan.frozen.head_sha,
            "prototype_root": plan.frozen.prototype_root,
            "prototype_head_sha": plan.frozen.prototype_head_sha,
        },
        "closure": plan.closure,
        "nodes": {
            node_id: {
                "id": node.id,
                "kind": node.kind,
                "classification": node.classification,
                "strategy": node.strategy,
                "path": node.path,
                "import_path": node.import_path,
                "name": node.name,
                "contract": node.contract,
                "requires": list(node.requires),
                "rewrite_to": node.rewrite_to,
            }
            for node_id, node in sorted(plan.nodes.items())
        },
        "blockers": list(plan.blockers),
    }


def compute_plan_hash(plan: SpinoffPlan) -> str:
    canonical = json.dumps(_plan_payload(plan), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_plan(
    graph: DependencyGraph,
    repo_root: str,
    raw_graph: Optional[dict] = None,
) -> SpinoffPlan:
    frozen = freeze_source(repo_root, graph)
    if graph.graph_hash:
        graph_hash = graph.graph_hash
    elif raw_graph:
        graph_hash = canonical_graph_hash(raw_graph)
    else:
        graph_hash = ""
    blockers: List[str] = []
    planned: Dict[str, PlannedNode] = {}

    for node in graph.nodes.values():
        blockers.extend(validate_node(node))
        try:
            strategy = map_classification(node.classification)
        except ValueError as exc:
            blockers.append(f"{node.id}: {exc}")
            strategy = "UNKNOWN"
        planned[node.id] = PlannedNode(
            id=node.id,
            kind=node.kind,
            classification=node.classification,
            strategy=strategy,
            path=node.path,
            import_path=node.import_path,
            name=node.name,
            contract=node.contract,
            requires=list(node.requires),
            rewrite_to=node.rewrite_to,
        )

    closure = transitive_closure(graph, graph.entry_nodes)
    plan = SpinoffPlan(
        frozen=frozen,
        graph_hash=graph_hash,
        plan_hash="",
        tool_version=__version__,
        closure=closure,
        nodes=planned,
        blockers=sorted(set(blockers)),
    )
    plan.plan_hash = compute_plan_hash(plan)
    return plan


def build_plan_from_path(graph_path: str, repo_root: str) -> SpinoffPlan:
    raw = load_graph(graph_path)
    graph = parse_graph(raw)
    return build_plan(graph, repo_root, raw_graph=raw)
