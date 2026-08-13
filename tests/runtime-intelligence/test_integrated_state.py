#!/usr/bin/env python3
"""Integrated-state harness intended-function tests."""
from __future__ import annotations
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/runtime-intelligence/integrated-state-checkout"


class IntegratedStateTests(unittest.TestCase):
    def test_refuse_zero_sha(self):
        with tempfile.TemporaryDirectory() as td:
            p = subprocess.run(
                ["bash", str(SCRIPT), "--repo", str(ROOT), "--pr", "62",
                 "--head", "0000000000000000000000000000000000000000",
                 "--worktree", str(Path(td) / "wt")],
                capture_output=True, text=True,
            )
            self.assertNotEqual(p.returncode, 0)

    def test_accept_current_head(self):
        head = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
        with tempfile.TemporaryDirectory() as td:
            wt = Path(td) / "wt"
            p = subprocess.run(
                ["bash", str(SCRIPT), "--repo", str(ROOT), "--pr", "64",
                 "--head", head, "--worktree", str(wt)],
                capture_output=True, text=True,
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("integrated\":true", p.stdout.replace(" ", ""))
            got = subprocess.check_output(["git", "-C", str(wt), "rev-parse", "HEAD"], text=True).strip()
            self.assertEqual(got, head)


if __name__ == "__main__":
    unittest.main(verbosity=2)
