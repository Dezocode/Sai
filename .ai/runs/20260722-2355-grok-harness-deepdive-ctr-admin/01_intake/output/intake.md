# Intake — 20260722-2355-grok-harness-deepdive-ctr-admin

## Requester

- **Human:** dezocode (Slack `U0BHYH0NMCY`)
- **Attached agent:** `@cora` → Cora (`ctr-admin`), Contract Administrator
- **Source:** Direct Cursor Cloud instruction with operator `~/.grok` harness inventory
- **Related:** Prior research task `20260722-2341-grok-build-runtime-research-ctr-admin` (PR #47)

## Exact requested outcome

1. Review Grok Build harness files / layout (operator ranking + public docs).
2. Research whether SAI needs a **new runtime** for Grok Build.
3. Critique Dezocode/Sai agent files for each runtime against documentation on
   advanced agents / tools / configs, aiming at more comprehensive and
   tailored scaffolding per runtime.
4. Maintain ICM and `.ai` protocols.
5. Stay in **research phase — pre contract building**.

## Repository facts (verified)

| Fact | Evidence |
|---|---|
| Canonical repo | `Dezocode/Sai` (`gh repo view` → `nameWithOwner: Dezocode/Sai`, `isFork: false`) |
| Remote | `origin` → `github.com/dezocode/sai` |
| Default branch | `main` @ `8da8530183736a6c7daf11b406fddfa08684a95d` |
| Working branch | `cursor/grok-build-runtime-research-bd87` @ `d8a3dfe109615f519ad195af6ed38a37c21050be` |
| Worktree | `/workspace` (clean after pull; research-only edits below) |
| Prior research | Completed under `20260722-2341-…`; draft decision not filed |
| Local Grok | No `grok` binary / no `~/.grok` on this VM |

## Constraints

- No contractor contract, no `GROK.md`, no schema/enum/scaffold code changes
  in this task.
- Hard architectural gate: filing a durable decision under
  `.ai/shared/memory/decisions/` requires co-founder accept (security /
  architecture policy) — keep draft in run artifacts.
- Stale `in_progress` run `20260715-1620-contractor-charters-ctr-admin`
  claims `.ai/contracts/` / `.ai/ONBOARDING.md` — do not touch those paths.
- Cloud branch prefix `cursor/…-bd87` differs from charter `ctr-admin/` —
  continue existing PR branch rather than rename mid-flight.

## Acceptance criteria

See `metadata.json` `acceptance_criteria`.

## Risks

- Operator tool ID spellings may differ from docs.x.ai permission names /
  enterprise always-safe IDs — live `grok inspect` required later.
- Deepening research must not contradict prior PR #47 verdict without
  explicit supersession notes (it should refine, not reverse).
