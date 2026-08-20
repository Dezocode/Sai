# 0005 — Lauren mode as a project Custom Mode for Cloud Agents

- Date: 2026-08-19
- Task-ID: 20260819-2341-lauren-mode-cloud-cursor-cloud
- Status: accepted
- Approver: dezocode (requested Lauren mode in cloud skills, 08-19-26 changelog live, Browser pane, and cloud agent config)

## Decision

Add a project skill at `.cursor/skills/lauren-mode/` with Custom Mode frontmatter (`mode: true`) as SAI's Cloud Agent pin for Lauren Tan's pstack. Commit `.cursor/rules/pstack-models.mdc` with Task slugs confirmed on a Cloud Agent VM. Keep the live Cloud Agent environment dashboard-managed. Do not commit `.cursor/environment.json`.

## Context

The 2026-08-19 Cursor changelog made any skill pin-able as a Custom Mode. dezocode asked to get "Lauren mode" live in cloud skills, along with subscriptions, `/goal`, VM-isolated subagents, steering, the internal Browser pane, and the existing cloud agent config. pstack was already project-enabled (decision 0004). `/setup-pstack` still writes `~/.cursor/rules/pstack-models.mdc`, which Cloud Agents never see.

## Alternatives considered

- **Pin `/poteto-mode` only** — rejected as the sole answer. The marketplace skill does not encode SAI ICM, the 08-19-26 harness, Browser pane, or SDK launch against this environment.
- **Copy the pstack skill tree into `.cursor/skills/`** — already rejected in 0004 (duplicate `/` names).
- **Always-apply rule that inlines poteto-mode** — rejected. Mode skills are heavy. Custom Mode pinning is the product mechanism.
- **Commit `.cursor/environment.json`** — rejected. It would override the personal dashboard environment. Plugins and skills are not environment.json fields.

## Rationale

Project skills under `.cursor/skills/` load in Cloud Agents and Desktop. A thin wrapper named `lauren-mode` is a new `/` identity, so it does not collide with `/poteto-mode`. Committed `pstack-models.mdc` is the cloud-safe leftover from 0004. Environment facts belong in a skill reference, not a competing env file.

## Consequences

- Operators pin `/lauren-mode` with Option+Enter / Use as Mode on a **new** session that includes this commit.
- Two Custom Modes can appear (`/lauren-mode` and `/poteto-mode`). SAI Cloud Agents should pin `/lauren-mode`.
- Model lines in `pstack-models.mdc` must stay inside the caller's available Task slugs. Re-run `/setup-pstack` and update the committed file when slugs change.
- Personal environment `6f2ece39-800a-11f1-ba66-0e7d0216e441` remains the dashboard source of truth until a co-founder chooses a repo-managed environment.
- Fresh-agent discovery (slash alias, model invocation, always-apply pointer, snapshot reuse) is decision 0006.

## Supersedes

Nothing. Complements 0004. Does not reopen vendoring pstack. Discovery follow-up is 0006.
