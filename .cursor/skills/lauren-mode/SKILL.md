---
name: lauren-mode
description: >-
  SAI Cloud Custom Mode for Lauren Tan's pstack. Use for /lauren-mode, Lauren
  mode, pinning poteto-mode in Cloud Agents, or 08-19-26 always-on cloud
  harness work.
disable-model-invocation: true
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

1. Type `/lauren-mode`
2. Press Option+Enter / Alt+Enter, or choose Use as Mode
3. Pair with `/goal` when the objective should survive the first PR
