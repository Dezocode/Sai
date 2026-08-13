#!/usr/bin/env python3
"""Negative authority tests for Runtime Intelligence subprocess (Decision 0007).

These tests document and enforce *intent* of forbidden operations. They do not
perform live merge/force-push against GitHub.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRIAGE = ROOT / ".ai/shared/skills/runtime-intelligence/TRIAGE.yaml"
STATUS = ROOT / ".ai/shared/skills/runtime-intelligence/init/STATUS.md"
SKILL = ROOT / ".ai/shared/skills/runtime-intelligence/SKILL.md"


class NegativeAuthorityTests(unittest.TestCase):
    def test_triage_invariants_never_merge_main(self):
        text = TRIAGE.read_text(encoding="utf-8")
        self.assertIn("never_merge_main: true", text)
        self.assertIn("never_force_push: true", text)
        self.assertIn("never_mark_pr_ready: true", text)
        self.assertIn("never_self_approve_initialization: true", text)
        self.assertIn("support_pr_base_is_parent_branch_by_default: true", text)

    def test_status_is_provisional(self):
        text = STATUS.read_text(encoding="utf-8")
        self.assertIn("PROVISIONAL", text)
        self.assertNotIn("Status: ACTIVE", text)
        self.assertIn("PENDING", text)

    def test_skill_forbids_main_merge(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("MUST NOT merge to `main`", text)
        self.assertIn("stacked/sub-PR", text)

    def test_t4_requires_explicit_capacity_evidence(self):
        text = TRIAGE.read_text(encoding="utf-8")
        self.assertIn("requires_explicit_capacity_evidence: true", text)

    def test_refuse_claim_initialized_without_approvals(self):
        # Simulated gate: subprocess may not claim complete
        saul = os.environ.get("RI_SAUL_STATUS", "PENDING")
        sai = os.environ.get("RI_SAI_STATUS", "PENDING")
        human = os.environ.get("RI_HUMAN_STATUS", "PENDING")
        may_claim = saul == "APPROVE" and sai == "APPROVE" and human == "APPROVE"
        self.assertFalse(may_claim, "default env must not allow initialized claim")

    def test_stacked_base_not_main(self):
        meta = (ROOT / ".ai/runs/20260813-1945-ri-subprocess-init/metadata.json").read_text(
            encoding="utf-8"
        )
        self.assertIn("cursor/codebase-health-90ba", meta)
        self.assertNotIn('"parent_branch": "main"', meta)


if __name__ == "__main__":
    # ensure we run from repo root semantics
    os.chdir(ROOT)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(NegativeAuthorityTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
