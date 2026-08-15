# Saul architecture review

Architecture review is part of **every Saul inner-loop invocation**, not an end-only audit.

## Per-contractor-completion review

For every new exact HEAD Saul must perform both:

1. **LOCAL_ARCH** — changed components and their direct architectural neighborhood: owners, callers/callees, interfaces, schemas, tests, persistence and state.
2. **IMPACT_ARCH** — architectural domains invalidated by the change even when affected files have no changed lines.

Applicable domains include authorization, identity, trust boundaries, operational context, state ownership, multi-primary isolation, Ralph control flow, Cora routing, contractor isolation, blocker lifecycle, Saul review, Sai governance, event routing, recovery/resume, CI/quality, workflow security, persistence, interfaces/schemas, observability, bounded resources, dependency direction, failure recovery, portability, simplicity and reviewability.

Each applicable domain is `PASS_CURRENT`, `FAIL`, `STALE`, or `NOT_APPLICABLE`. Old architecture proof cannot survive an invalidating dependency/context change merely because a file was untouched.

Material architecture failures create canonical `ARCH-*` technical blockers immediately and require real Saul architectural clearance after remediation.

## Current-head system synthesis

Before real-Saul technical convergence, Saul must perform **SYSTEM_ARCH** over the assembled exact current state and current domain proofs. It must establish coherent sources of truth, ownership, dependency direction, trust, state isolation, lifecycle, concurrency, failure recovery, portability, bounded resources, observability, simplicity, reviewability, requirement completeness and absence of unnecessary duplicate machinery.

100% passing implementation shards without current architecture PASS is not technical convergence.

A foundational change may escalate incremental review to `SYSTEM_ARCH_REQUIRED_NOW`; the architecture engine need not wait for nominal convergence when the impact is broad.
