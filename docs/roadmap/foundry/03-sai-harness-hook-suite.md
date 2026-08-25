# PR contract — normalized Sai Harness hook/event suite

PRD: [`docs/prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md`](../../prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md)
Roadmap: [`00-sai-harness-foundry-sequence.md`](00-sai-harness-foundry-sequence.md)

## Mission

Build a prototype-local normalized hook/event bus for Sai Harness that can consume the hook surfaces actually supported by Cursor, Atomic and Grokbot, route them through Crosscom, and provide deterministic aspect/task context without weakening production root `.cursor` verification authority.

## Acceptance

- [ ] Define a versioned internal hook event vocabulary separate from runtime-specific raw payloads.
- [ ] Runtime adapters declare supported/unsupported mappings; unsupported events are not fabricated.
- [ ] Cover useful lifecycle surfaces where supported: workspace/session start/end, prompt receipt, pre/post tool, tool failure, shell before/after, MCP before/after, file read/edit, subagent start/stop, compact, stop/wake, response/thought, Harness tick/heartbeat.
- [ ] Preserve raw source event + normalized form + provenance sufficient for debugging.
- [ ] Hook execution has explicit order, timeout, cancellation and fail-open/fail-closed semantics by event class.
- [ ] Production root `.cursor/hooks.json` remains `sai-verify` authority; the prototype hook suite cannot replace, suppress or bypass it.
- [ ] Prototype activation is explicit through the Harness/runtime/workspace path; do not assume nested `.cursor/hooks.json` files auto-load.
- [ ] Aspect decomposition produces typed aspects suitable for routing (for example name/kind-or-intent/target lane/text) and is attached only through hook surfaces that actually support context injection.
- [ ] Prompt text is never silently rewritten unless the runtime contract explicitly supports and records that transformation.
- [ ] Sensitive tool/shell payloads are redacted/filtered before Crosscom fan-out according to a small explicit policy.
- [ ] Hook-generated Crosscom events retain Task-ID, agent/runtime, repo/PR/full-HEAD provenance when applicable.
- [ ] Hook event storms are bounded/coalesced; no unbounded per-token/per-thought cross-network chatter.
- [ ] Stop/wake loops have hard loop limits and cannot self-amplify indefinitely.
- [ ] Every effectful hook action goes through the Harness audit gateway and is idempotency-safe where retryable.
- [ ] Tests replay fixtures from each runtime adapter and prove deterministic normalization, unsupported-event honesty, timeout behavior, redaction and production-hook non-interference.
- [ ] Core normalized hook tests do not require #141/network availability.
- [ ] Exact-head verification/review converges before owner-ready.

## Non-goals

- No GitHub/session API repo bridge yet.
- No production `.cursor` hook redesign.
- No Foundry manifest/planner/executor behavior.
