"""Tests for Foundry slice 80 spin-off planner and materializer."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
PLUGINS = REPO_ROOT / "prototypes" / "plugins"
SPINOFF_ROOT = PLUGINS / "foundry" / "spinoff-planner-exporter"
for entry in (str(SPINOFF_ROOT),):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from spinoff.audit import scan_forbidden_refs
from spinoff.materializer import materialize_candidate
from spinoff.planner import build_plan_from_path

DEMO_GRAPH = PLUGINS / "demo-widget" / "foundry.graph.json"
DEMO_OUTPUT = PLUGINS / "demo-widget" / "foundry.graph.output.json"


def _tree_digest(root: Path) -> str:
    entries = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            entries.append(f"{rel}:{digest}")
    return hashlib.sha256("\n".join(entries).encode("utf-8")).hexdigest()


class SpinoffTests(unittest.TestCase):
    repo_root = str(REPO_ROOT)

    def test_plan_exportable(self) -> None:
        plan = build_plan_from_path(str(DEMO_GRAPH), self.repo_root)
        self.assertTrue(plan.exportable)
        self.assertEqual([], plan.blockers)
        self.assertIn("widget-py", plan.closure)
        self.assertIn("remote-api", plan.closure)
        self.assertEqual("EXPORT_COPY", plan.nodes["widget-py"].strategy)
        self.assertEqual("REMOTE", plan.nodes["remote-api"].strategy)
        self.assertTrue(plan.plan_hash)
        self.assertTrue(plan.graph_hash)

    def test_plan_from_slice78_output_fixture(self) -> None:
        plan = build_plan_from_path(str(DEMO_OUTPUT), self.repo_root)
        self.assertTrue(plan.exportable)
        self.assertEqual([], plan.blockers)
        self.assertIn("widget-py", plan.closure)
        self.assertIn("remote-api", plan.closure)
        self.assertEqual("EXPORT_COPY", plan.nodes["widget-py"].strategy)
        self.assertEqual("REMOTE", plan.nodes["remote-api"].strategy)
        self.assertEqual("pinned-demo-fixture-hash", plan.graph_hash)
        self.assertTrue(plan.plan_hash)

    def test_materialize(self) -> None:
        plan = build_plan_from_path(str(DEMO_GRAPH), self.repo_root)
        with tempfile.TemporaryDirectory() as tmp:
            manifest = materialize_candidate(plan, self.repo_root, tmp)
            out = Path(tmp)
            self.assertTrue((out / "src" / "widget.py").is_file())
            self.assertTrue((out / "PROVENANCE.json").is_file())
            contract_files = list(out.glob("contracts/*.json"))
            self.assertEqual(1, len(contract_files))
            self.assertIn("src/widget.py", manifest)
            self.assertFalse((out / "src" / "legacy.py").exists())

    def test_no_forbidden_refs(self) -> None:
        plan = build_plan_from_path(str(DEMO_GRAPH), self.repo_root)
        with tempfile.TemporaryDirectory() as tmp:
            materialize_candidate(plan, self.repo_root, tmp)
            hits = scan_forbidden_refs(tmp)
            self.assertEqual([], hits)

    def test_unknown_blocks(self) -> None:
        blocked_graph = {
            "schema_version": 1,
            "plugin_id": "blocked",
            "prototype_root": "prototypes/plugins/demo-widget",
            "entry_nodes": ["widget-py"],
            "nodes": [
                {
                    "id": "widget-py",
                    "kind": "file",
                    "classification": "UNKNOWN",
                    "path": "src/widget.py",
                }
            ],
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(blocked_graph, fh)
            graph_path = fh.name
        try:
            plan = build_plan_from_path(graph_path, self.repo_root)
            self.assertFalse(plan.exportable)
            self.assertTrue(plan.blockers)
            with self.assertRaises(ValueError):
                materialize_candidate(plan, self.repo_root, tempfile.mkdtemp())
        finally:
            Path(graph_path).unlink(missing_ok=True)

    def test_idempotent_materialization(self) -> None:
        plan = build_plan_from_path(str(DEMO_GRAPH), self.repo_root)
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            materialize_candidate(plan, self.repo_root, first)
            materialize_candidate(plan, self.repo_root, second)
            self.assertEqual(_tree_digest(Path(first)), _tree_digest(Path(second)))


if __name__ == "__main__":
    unittest.main()
