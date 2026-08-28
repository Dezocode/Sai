"""Freeze source repository state for deterministic spin-off plans."""

from __future__ import annotations

import subprocess
from pathlib import Path

from spinoff.graph_input import DependencyGraph
from spinoff.model import FrozenSource


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def freeze_source(repo_root: str, graph: DependencyGraph) -> FrozenSource:
    root = Path(repo_root).resolve()
    repo = _git(root, "config", "--get", "remote.origin.url")
    if not repo:
        repo = str(root)
    head_sha = _git(root, "rev-parse", "HEAD")
    base_ref = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
    prototype_root = graph.prototype_root
    try:
        prototype_head_sha = _git(root, "rev-parse", f"HEAD:{prototype_root}")
    except subprocess.CalledProcessError:
        prototype_head_sha = head_sha
    return FrozenSource(
        repo=repo,
        base_ref=base_ref,
        head_sha=head_sha,
        prototype_root=prototype_root,
        prototype_head_sha=prototype_head_sha,
    )
