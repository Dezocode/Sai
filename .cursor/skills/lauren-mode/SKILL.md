---
name: lauren-mode
description: >-
  SAI Cloud Custom Mode for Lauren Tan's pstack. Use for /lauren-mode, /lauren,
  Lauren mode, /lauren mode (space), pinning poteto-mode in Cloud Agents,
  PR 70 cloud skills, or 08-19-26 always-on cloud harness work.
mode: true
icon: crown
color: yellow
---

# Lauren mode

Project Custom Mode for SAI Cloud Agents. Pin it from `/` with Option+Enter (Mac) or Alt+Enter (Windows), or choose Use as Mode. The skill stays in context until you exit the mode.

This file does **not** vendor pstack. The marketplace plugin stays enabled in `.cursor/settings.json`. When `/poteto-mode` is available, follow that skill in full (principles, playbooks, `poteto-agent`). This mode adds Cloud Agent harness rules pstack does not encode.

## Start of every task

1. Keep SAI coordination. Read `.ai/CONTEXT.md` when identity or repo facts are in doubt. Do not skip ICM reporting, commit trailers, or merge-handoff.
2. Match a pstack playbook if the work is non-trivial. Copy its steps into the todolist. Skip a step only with `skip: <reason>`.
3. Load only the reference this turn needs:
   - Long-lived objective, subscriptions, VM subagents, steering → `references/harness.md`
   - Built-in Browser pane, `@Browser`, desktop GUI → `references/browser-pane.md`
   - Launching this repo via `@cursor/sdk` → `references/sdk-cloud.md`
   - Personal Cloud Agent environment facts → `references/environment.md`

## Non-negotiables

- Do not copy pstack skills into `.cursor/skills/` (decision 0004). This wrapper is the allowed project skill.
- Do not commit `.cursor/environment.json`. The live environment is personal and dashboard-managed (decision 0005).
- Spawn pstack playbook delegates as `subagent_type: "poteto-agent"` unless a routed skill names another type.
- For isolated verification or swarm work, give each subagent its own cloud VM (`Task` `environment: "cloud"`). See `references/harness.md`.
- For a goal the agent must hold until done, call `CreateGoal` and `UpdateGoal`. Do not invent a calendar estimate.
- Write replies per pstack unslop. No em dashes. No mid-sentence colons.

## Pinning

In a **new** Cloud Agent or a reloaded Desktop window on a commit that includes this file:

1. Type `/lauren-mode` or `/lauren` (mobile often sends `/lauren mode` with a space)
2. Press Option+Enter / Alt+Enter, or choose Use as Mode. Mobile has no Option+Enter; Use as Mode or type the slash so the skill attaches.
3. Pair with `/goal` when the objective should survive the first PR

If `.cursor/skills/lauren-mode/SKILL.md` is missing, this checkout is older than Dezocode/Sai#70 (`8a30202`). Fetch `origin/main` and check out that commit before claiming the skill was never added. Personal Cloud Agents on env `6f2ece39-800a-11f1-ba66-0e7d0216e441` reuse snapshot `bld-20260819-500928d1-8214-4bc0-9bb9-e36884ef51f0`, which predates the merge.
