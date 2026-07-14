# Verification — 20260714-0514-automation-fallback-cursor-cloud-30d8

Change under test: Phase 6 of `.ai/INITIALIZE.md` now has exactly two
allowed outcomes (automation exists, or complete spec delivered to the
principal); `scripts/agent-automation-spec` generates the full spec;
`scripts/verify-semantic-hierarchy` enforces the policy in the registry.

## Commands and results

| # | Check | Result |
|---|---|---|
| 1 | `bash -n` on `agent-automation-spec`, `verify-semantic-hierarchy` | PASS |
| 2 | Generator produces complete spec for this agent (settings table, verbatim prompt, post-creation steps) | PASS — `.ai/agents/automation-specs/cursor-cloud-30d8.md` reviewed line by line; duplicate schedule wording found and fixed, regenerated |
| 3 | `verify-semantic-hierarchy` on live tree (registry now `delegated:` with existing spec) | PASS (`OK`) |
| 4 | Negative: registry `automation: "unavailable: ..."` | PASS — rejected with instruction to use Path B |
| 5 | Negative: registry `delegated:` pointing at nonexistent spec | PASS — rejected (`spec does not exist`) |
| 6 | Registry restored byte-identical after negative tests; JSON parses | PASS |
| 7 | Phase 6 text re-read after edit collision repair — Paths A and B complete, no dangling references | PASS |
| 8 | Spec prompt + settings delivered to dezocode in #agentupdates | delivery evidence in handoff.md |
| 9 | CI on pushed range | recorded in handoff.md |

## Skipped checks (with reasons)

- Actual creation of the automation and its first run: requires dezocode
  (or a Desktop session under dezocode) — that is the designed Path B
  handover, tracked by the registry's `delegated:` state.
