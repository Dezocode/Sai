"""Consumer for slice-78-shaped Foundry dependency graph JSON.

Slice 78 owns the authoritative schema and graph engine; this module only
reads fixture-shaped graphs for slice 80 spin-off planning.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Set

CLASSIFICATIONS = frozenset(
    {"REUSE", "PROMOTE", "EXPORT", "REMOTE", "PROMOTE_SHARED", "DROP", "UNKNOWN"}
)
BLOCKING_CLASSIFICATIONS = frozenset({"UNKNOWN", "PROMOTE"})


@dataclass
class GraphNode:
    id: str
    kind: str
    classification: str
    path: str = ""
    import_path: str = ""
    name: str = ""
    contract: str = ""
    requires: List[str] = field(default_factory=list)
    rewrite_to: str = ""


@dataclass
class DependencyGraph:
    schema_version: int
    plugin_id: str
    prototype_root: str
    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    entry_nodes: List[str] = field(default_factory=list)
    graph_hash: str = ""


def is_go_internal(import_path: str) -> bool:
    return "/internal/" in import_path or import_path.endswith("/internal")


def validate_node(node: GraphNode) -> List[str]:
    issues: List[str] = []
    if node.classification not in CLASSIFICATIONS:
        issues.append(f"{node.id}: invalid classification {node.classification}")
    if node.classification in BLOCKING_CLASSIFICATIONS:
        issues.append(f"{node.id}: {node.classification} classification blocks export")
    if node.kind == "file" and node.classification == "EXPORT" and not node.path:
        issues.append(f"{node.id}: EXPORT file requires path")
    if node.kind == "go_import" and not node.import_path:
        issues.append(f"{node.id}: go_import requires import_path")
    if node.kind == "go_import" and is_go_internal(node.import_path):
        if node.classification == "REUSE":
            issues.append(
                f"{node.id}: Go internal import {node.import_path} cannot REUSE cross-repo"
            )
        if node.classification not in {"EXPORT", "REMOTE", "PROMOTE_SHARED", "DROP"}:
            issues.append(
                f"{node.id}: Go internal import requires EXPORT, REMOTE, PROMOTE_SHARED, or DROP"
            )
    if node.kind == "service" and node.classification == "REMOTE" and not node.contract:
        issues.append(f"{node.id}: REMOTE service requires contract")
    return issues


def is_slice78_output(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    provenance = data.get("provenance")
    return (
        isinstance(provenance, dict)
        and "graph_hash" in data
        and isinstance(data.get("manifest_id"), str)
        and isinstance(data.get("nodes"), list)
        and isinstance(data.get("edges"), list)
    )


def _path_has_extension(path: str) -> bool:
    _, ext = os.path.splitext(path)
    return bool(ext)


def _infer_node_kind(classification: str, path: str) -> str:
    if classification == "REMOTE":
        return "service"
    if path and _path_has_extension(path):
        return "file"
    return "package"


def _default_prototype_root(manifest_id: str, data: dict) -> str:
    root = data.get("prototype_root", "")
    if root:
        return root
    if manifest_id and "/" not in manifest_id:
        return f"prototypes/plugins/{manifest_id}"
    raise ValueError("prototype_root required when manifest_id is not a plugin id")


def _remote_contract(manifest_id: str) -> str:
    return f"openapi://{manifest_id}/v1"


def _remote_name(node_id: str, manifest_id: str) -> str:
    if node_id.endswith("-api"):
        prefix = manifest_id.split("-")[0]
        return node_id.replace("remote-", f"{prefix}-", 1)
    return node_id


def parse_slice78_output(data: dict) -> DependencyGraph:
    manifest_id = data.get("manifest_id", "")
    if not manifest_id:
        raise ValueError("manifest_id required")
    provenance = data.get("provenance") or {}
    schema_version = provenance.get("schema_version", 1)
    prototype_root = _default_prototype_root(manifest_id, data)
    if not prototype_root.startswith("prototypes/plugins/"):
        raise ValueError("prototype_root must be under prototypes/plugins/")

    requires: Dict[str, List[str]] = {
        n["id"]: [] for n in data.get("nodes", []) if n.get("id")
    }
    for edge in data.get("edges", []):
        from_id = edge.get("from", "")
        to_id = edge.get("to", "")
        if from_id not in requires:
            raise ValueError(f"edge references unknown node: {from_id}")
        if to_id not in requires:
            raise ValueError(f"edge references unknown node: {to_id}")
        requires[from_id].append(to_id)

    nodes: Dict[str, GraphNode] = {}
    for raw in data.get("nodes", []):
        node_id = raw["id"]
        if node_id in nodes:
            raise ValueError(f"duplicate node id: {node_id}")
        classification = raw.get("classification", "UNKNOWN")
        path = raw.get("path", "")
        kind = _infer_node_kind(classification, path)
        contract = ""
        name = ""
        node_path = ""
        if kind == "service":
            contract = _remote_contract(manifest_id)
            name = _remote_name(node_id, manifest_id)
        elif kind == "file":
            node_path = path
        nodes[node_id] = GraphNode(
            id=node_id,
            kind=kind,
            classification=classification,
            path=node_path,
            name=name,
            contract=contract,
            requires=sorted(set(requires.get(node_id, []))),
        )

    entry_nodes = list(data.get("entry_nodes") or [])
    if not entry_nodes:
        entry_nodes = [
            n.id
            for n in nodes.values()
            if n.kind == "file" and n.classification == "EXPORT"
        ]
    return DependencyGraph(
        schema_version=schema_version,
        plugin_id=manifest_id,
        prototype_root=prototype_root,
        nodes=nodes,
        entry_nodes=entry_nodes,
        graph_hash=data.get("graph_hash", ""),
    )


def load_graph(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if is_slice78_output(data):
        return data
    if data.get("schema_version") != 1:
        raise ValueError("unsupported schema_version")
    if not data.get("plugin_id"):
        raise ValueError("plugin_id required")
    root = data.get("prototype_root", "")
    if not root.startswith("prototypes/plugins/"):
        raise ValueError("prototype_root must be under prototypes/plugins/")
    return data


def parse_nodes(data: dict) -> DependencyGraph:
    nodes: Dict[str, GraphNode] = {}
    for raw in data.get("nodes", []):
        node_id = raw["id"]
        if node_id in nodes:
            raise ValueError(f"duplicate node id: {node_id}")
        nodes[node_id] = GraphNode(
            id=node_id,
            kind=raw["kind"],
            classification=raw.get("classification", "UNKNOWN"),
            path=raw.get("path", ""),
            import_path=raw.get("import_path", ""),
            name=raw.get("name", ""),
            contract=raw.get("contract", ""),
            requires=list(raw.get("requires", [])),
            rewrite_to=raw.get("rewrite_to", ""),
        )
    entry_nodes = list(data.get("entry_nodes") or [])
    if not entry_nodes:
        entry_nodes = [
            n.id
            for n in nodes.values()
            if n.kind == "file" and n.classification == "EXPORT"
        ]
    return DependencyGraph(
        schema_version=data["schema_version"],
        plugin_id=data["plugin_id"],
        prototype_root=data["prototype_root"],
        nodes=nodes,
        entry_nodes=entry_nodes,
    )


def parse_graph(data: dict) -> DependencyGraph:
    if is_slice78_output(data):
        return parse_slice78_output(data)
    return parse_nodes(data)


def canonical_graph_hash(data: dict) -> str:
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def transitive_closure(
    graph: DependencyGraph,
    entry_ids: Iterable[str],
) -> List[str]:
    nodes = graph.nodes
    seen: Set[str] = set()
    order: List[str] = []

    def visit(node_id: str) -> None:
        if node_id in seen:
            return
        if node_id not in nodes:
            raise ValueError(f"unknown node id: {node_id}")
        seen.add(node_id)
        node = nodes[node_id]
        for dep in node.requires:
            visit(dep)
        order.append(node_id)

    for entry_id in entry_ids:
        visit(entry_id)
    return order
