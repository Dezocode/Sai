---
name: icm-portfolio-audit
description: >-
  Audit monaecode/Sai portfolio state for ICM compliance: fork sync vs
  Dezocode/Sai, run-folder hygiene, registry integrity, CI parity. Use when
  asked to audit the fork, check ICM/protocol adherence, or before opening
  any PR to canonical main.
---

# ICM portfolio audit

Run these checks in order; report each with actual command output as
evidence. Never mark a check OK without output.

1. **Fork sync by SHA** — `git fetch origin upstream`; compare
   `git rev-parse origin/main upstream/main`. If behind and
   fast-forwardable, fast-forward by SHA (never recreate upstream commits).
   Diverged → `[SAI][CONFLICT]`, stop.
2. **Semantic hierarchy** — `scripts/verify-semantic-hierarchy`. FAILs in
   *new* work must be fixed; FAILs baked into upstream-merged history are
   reported, not silently bypassed (bypass only with
   `SAI_AUDIT_BYPASS="<reason>"` and a queued BYPASS event).
3. **Audit trail** — `scripts/verify-agent-audit <base>..<head>` for the
   branch range under review.
4. **Registry integrity** — `.ai/agents/registry.json`: unique `agent_id`,
   one active CEO, every active agent has folder + charter. Flag drift;
   do not silently correct another agent's entry.
5. **CI parity** — `.github/workflows/agent-audit.yml` on fork matches
   canonical (`git diff upstream/main -- .github/workflows/agent-audit.yml`).
6. **Run hygiene** — every `.ai/runs/<task-id>/` has valid `metadata.json`
   (`task_id`, `agent`, `repository`, `status`) and closed runs have
   `handoff.md`.

Output: `[SAI][VERIFY]` (all pass) or `[SAI][BLOCKED]` (any fail) queued
via `scripts/agent-report`, plus a summary table in chat.
