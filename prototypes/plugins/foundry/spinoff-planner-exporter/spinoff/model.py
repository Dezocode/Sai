"""Shared types for spin-off planning."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class FrozenSource:
    repo: str
    base_ref: str
    head_sha: str
    prototype_root: str
    prototype_head_sha: str


@dataclass
class PlannedNode:
    id: str
    kind: str
    classification: str
    strategy: str
    path: str = ""
    import_path: str = ""
    name: str = ""
    contract: str = ""
    requires: List[str] = field(default_factory=list)
    rewrite_to: str = ""


@dataclass
class SpinoffPlan:
    frozen: FrozenSource
    graph_hash: str
    plan_hash: str
    tool_version: str
    closure: List[str] = field(default_factory=list)
    nodes: Dict[str, PlannedNode] = field(default_factory=dict)
    blockers: List[str] = field(default_factory=list)

    @property
    def exportable(self) -> bool:
        return not self.blockers
