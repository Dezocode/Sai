#!/usr/bin/env python3
"""Triage + OpenClaw policy + deny-authority intended-function tests."""
from __future__ import annotations
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class TriagePolicyTests(unittest.TestCase):
    def test_openclaw_policy_denies_merge(self):
        text = (ROOT / "runtime-intelligence/openclaw/policy.yaml").read_text()
        self.assertIn("merge_main", text)
        self.assertIn("denied:", text)
        self.assertIn("self_declare_initialized", text)

    def test_deny_merge_main_exit_13(self):
        p = subprocess.run(
            ["bash", str(ROOT / "scripts/runtime-intelligence/deny-authority"), "merge-main"],
            capture_output=True, text=True,
        )
        self.assertEqual(p.returncode, 13)
        self.assertIn("DENIED", p.stderr)

    def test_deny_force_push(self):
        p = subprocess.run(
            ["bash", str(ROOT / "scripts/runtime-intelligence/deny-authority"), "force-push"],
            capture_output=True, text=True,
        )
        self.assertEqual(p.returncode, 13)

    def test_deny_mark_ready(self):
        p = subprocess.run(
            ["bash", str(ROOT / "scripts/runtime-intelligence/deny-authority"), "mark-ready"],
            capture_output=True, text=True,
        )
        self.assertEqual(p.returncode, 13)

    def test_t4_without_evidence_denied(self):
        p = subprocess.run(
            ["bash", str(ROOT / "scripts/runtime-intelligence/deny-authority"), "t4-activate", "none"],
            capture_output=True, text=True,
        )
        self.assertEqual(p.returncode, 13)

    def test_docker_compose_high_effort_default(self):
        text = (ROOT / "runtime-intelligence/docker/docker-compose.yml").read_text()
        self.assertIn("RI_GROK_EFFORT: ${RI_GROK_EFFORT:-high}", text)
        self.assertIn("sai.never_merge_main", text)

    def test_status_not_active(self):
        text = (ROOT / ".ai/shared/skills/runtime-intelligence/init/STATUS.md").read_text()
        self.assertIn("PROVISIONAL", text)
        self.assertIn("NOT INITIALIZED", text)




class AuthPathGlobTests(unittest.TestCase):
    def test_dot_ai_paths_match_class_globs(self):
        # Regression: lstrip("./") broke ".ai/..." class paths.
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts/lib"))
        import sai_auth as a
        self.assertTrue(a.glob_match(".ai/contracts/x/y.json", ".ai/contracts/**"))
        self.assertTrue(a.glob_match(".ai/runs/t/handoff.md", ".ai/runs/**"))
        self.assertFalse(a.glob_match("scripts/foo.py", ".ai/contracts/**"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
