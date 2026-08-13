# pstack-Informed Execution Contract

Source snapshot: `no-session/pstack`, observed 2026-08-12, `SKILL.md` version 1.1.0, MIT licensed.

This bundle does **not** copy pstack wholesale. It adapts the workflow concepts appropriate to a Cursor-managed, safety-sensitive codebase.

## Imported principles

- plan before build;
- engineering review locks architecture/data flow/edge cases before code;
- review, security audit, QA, shipping, monitoring, and reflection are separate concerns;
- guarded/frozen edits for risky scopes;
- completion claims require evidence;
- three unsuccessful attempts require escalation/change of strategy;
- uncertainty on security-sensitive changes is a blocker, not permission to guess;
- independent review is preferred to agent self-grading.

## SAI-specific modification

pstack optimizes a solo founder loop around shipping. Phase 0 intentionally inserts a stronger precondition:

```text
PLAN -> ENG REVIEW -> QUALITY-OS BUILD -> ADVERSARIAL SELF-TEST -> UNLOCK
                                                           |
                                                           v
                                        only then normal product BUILD
```

During Phase 0, `/ship` semantics are interpreted as "ship the Quality OS control plane", not ship SAI product functionality.

## Completion protocol

Every gate and final handoff uses exactly one status:

- `DONE` — required work and evidence complete;
- `DONE_WITH_CONCERNS` — complete with explicit non-blocking concerns;
- `BLOCKED` — cannot safely proceed; evidence says why;
- `NEEDS_CONTEXT` — a material required input truly cannot be inferred from repository/environment.

## Guard semantics for Cursor

Before a material change, define an edit scope. Architecture/security/migration changes force a narrow scope and deep verification. A tool may not edit outside its claimed scope merely because a repair attempt failed.

## pstack provenance

See `.sai-quality/provenance/pstack-reference.json` and `SOURCES.md`.
