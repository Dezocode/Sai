# Intake — Grok Build runtime research (pre-contract)

## Requester

- **Human:** dezocode (Slack `U0BHYH0NMCY`), via Cursor Cloud run attaching `@cora`
- **Source:** Direct instruction in cloud agent run
  `https://cursor.com/agents/bc-936d30a3-1a98-4255-acc0-a3687588bd87`
- **Actor agent:** Cora (`ctr-admin`), Contract Administrator — active in
  `.ai/agents/registry.json`

## Exact requested outcome

1. Review Grok Build harness files / operator notes and research whether SAI
   needs a **new runtime** for Grok Build.
2. Critique Dezocode/Sai agent files for each existing runtime against
   documentation of advanced agent tools, capabilities, and configs — so
   scaffolding can become more comprehensive and tailored per runtime.
3. Stay in **research phase**; maintain ICM and `.ai` protocols; **do not**
   build a contractor contract yet.

## Repository verification (command-backed)

| Fact | Evidence |
|---|---|
| Canonical repo | `gh repo view` → `Dezocode/Sai`, `isFork=false`, default `main` |
| Remote | `origin` → `github.com/dezocode/sai` (fetch/push) |
| Start branch/SHA | `main` @ `8da8530` clean |
| Research branch | `cursor/grok-build-runtime-research-bd87` (Cursor Cloud branch template; charter prefix `ctr-admin/` deferred — noted under risks) |
| Worktree | `/workspace` — sole agent in this tree |
| Local Grok home | **Absent** on this VM (`NO_LOCAL_GROK_HOME`); harness analysis uses requester notes + public xAI docs |

## Constraints

- Decision 0002: one registry row / runtime-neutral identity; runtime-specific
  caps live under `runtimes/<suite>/`.
- Contract schema enum today:
  `cursor-cloud-vm | cursor-desktop | claude-code-cli | codex-desktop` only
  (`.ai/shared/schemas/contract.schema.json`).
- Scaffold scripts accept `--primary-runtime cursor|claude|codex` only.
- Stale run `20260715-1620-contractor-charters-ctr-admin` still
  `in_progress` and claims `.ai/contracts/`, `.ai/agents/cora/`, etc. —
  **this research must not edit those paths**.
- Hard architectural change (new runtime suite) → PLAN/human review gate
  before implementation (security-policy / decision-record territory).

## Acceptance criteria

- Written research report with verdict + scaffolding critique.
- Slack INTAKE/PLAN before edits; HANDOFF at end.
- No contract artifacts under `.ai/contracts/` in this task.
- Next safe action clear for co-founders / Sai.

## Dependencies

- Public Grok Build docs (`docs.x.ai/build/*`)
- Requester harness ranking notes (operator evidence; not secrets)
- Existing Layer 3 runtime index + Claude Agent SDK reference

## Risks

- Branch naming: Cloud mandate `cursor/…-bd87` vs charter `ctr-admin/…` —
  documented; co-founders may rename on merge policy.
- Operator `~/.grok` tree not inspectable here — public docs + notes only.
- Stale overlapping claims on contract/agent paths if someone resumes that run.
