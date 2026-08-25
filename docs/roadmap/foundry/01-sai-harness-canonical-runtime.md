# PR contract — canonical Sai Harness runtime prototype

PRD: [`docs/prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md`](../../prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md)
Roadmap: [`00-sai-harness-foundry-sequence.md`](00-sai-harness-foundry-sequence.md)

## Mission

Converge the validated persistent Atomic/Grokbot/Sai CLI experiments from current #141/#146 into one canonical, removable **Sai Harness prototype** under `prototypes/plugins/sai-harness/`. This PR establishes persistent runtime identity, channel supervision, local state/audit and restart/resume semantics. It does not yet implement the generic Crosscom transport schema, normalized hook bus or repo bridge.

## Acceptance

- [ ] Re-resolve parent/prerequisite heads; never overwrite newer #136/#141/#146 work.
- [ ] Canonical implementation root is `prototypes/plugins/sai-harness/`; no shipping target depends on it.
- [ ] Validated #146 behavior is migrated/consolidated rather than duplicated across `cross-intercom` and `sai-harness` indefinitely.
- [ ] One registered agent identity maps to one persistent Atomic-backed live channel with deterministic naming.
- [ ] Grokbot is the bounded supervisor/wake layer, not a second policy authority.
- [ ] Channel creation/attach/restart requires registered identity; unknown identities fail closed or remain explicitly provisional with zero authority.
- [ ] Persistent state records Task-ID, runtime/agent identity, channel/session lineage, last successful turn and recovery metadata.
- [ ] Restart/resume preserves conversation/task continuity where the underlying runtime supports it; unsupported continuity is surfaced honestly.
- [ ] Local audit trail is append-only/idempotent enough to explain decide -> act -> retry/dead-letter transitions.
- [ ] Stuck/errored workers have bounded timeout, retry/backoff and dead-letter behavior; no unbounded respawn or busy polling.
- [ ] Headless fallback is limited to explicit cases (for example isolated CI/debug work), not the default invisible execution path.
- [ ] Owner can observe/attach to every persistent channel without changing agent state merely by observing.
- [ ] Host install/wrapper material is derived from the prototype source; `/usr/local/bin`, shell aliases or tmux state are deployment/runtime outputs, not canonical source authority.
- [ ] Atomic/OpenBot/other external code reuse carries required license/provenance and is represented as an external dependency, not copied casually.
- [ ] Deleting `prototypes/plugins/sai-harness/` leaves production build/test behavior unchanged.
- [ ] `sai-verify` maps/proves the Harness surface without creating a parallel verifier.
- [ ] Existing production `.cursor/hooks.json`, Go/OpenAPI and Sai Design Language authority remain unchanged except through separately authorized production PRs.
- [ ] Adversarial tests cover unregistered identity, duplicate channel, stale channel, restart, bounded recovery, prototype deletion and production-backdependency rejection.
- [ ] Exact-head lane/design/verification evidence and genuine independent review converge before owner-ready.

## Non-goals

- No generic Crosscom envelope/router yet.
- No repo->agent or agent->repo bridge yet.
- No Foundry manifest/dependency graph yet.
- No Integrate/Spin Off execution.
- No production dependence on the Harness.
