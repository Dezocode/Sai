---
description: Cross-fleet and cross-runtime intercom hooking between subagents, runtimes, and all agents on Sai workstreams. Use this skill whenever joining or creating intercom groups, announcing a fleet, answering collision/region-claim checks, relaying contract changes between repos, bridging two groups as a bridge agent, coordinating with pr141-fix / PR136 fleets / Hermes workers, or wiring hooks that connect local agent sessions to repo-side state — even if nobody explicitly says "intercom".
---

# Crosscomm — intercom hooking between subagents, runtimes, and all agents


## 2b. Atomic intercom mechanics (as used by her + pr141-grunt-lead)

- **Send**: `intercom({action:"send", to:"<exact-session-id>", message})` — target by exact session id (`subagent-chat-<uuid>`), never by guessable names. `action:"reply"` only answers a PENDING ask; for anything else use send. A failed reply ("no pending ask") means switch to send.
- **Groups**: join with `intercom({action:"join", group:"<name>"})`. Fleet groups isolate by default; bridge agents deliberately hold membership in TWO groups (e.g., default + a fleet group) to relay. Announce your group when introducing your fleet so bridges can find you.
- **Non-interactive agents**: an auto-acknowledgement ("cannot respond while working") means the message is QUEUED for when the task exits — do not resend; do not treat silence as rejection.
- **Re-intro pattern**: if a counterpart says your earlier message "failed with a provider error", resend the ESSENTIALS compressed (verdicts + asks), not the full transcript.
- **Status pings from coordinators**: answer in one line — PRs touched, phase (investigating/fixing/verifying), overlap warnings. Then follow up with the substantive gap-verdict separately.
- **Cross-fleet asks** (region clearance, contract pinning, owner-gated pings) go through the bridge or lead; route semantic decisions to the OWNER via the consuming PR instead of deciding unilaterally.
Patterns proven during the 2026-08-24 Sai convergence (PRs #77/#136/#141/#145/#146, three fleets, zero collisions).

## 1. Group topology

- Every fleet gets one group; bridge agents deliberately sit in TWO groups (e.g., `default` + `saul-support`) to relay between fleets.
- Reach a specific session by exact session id (`subagent-chat-<uuid>`), not by guessable names. Non-interactive agents auto-acknowledge; your message is queued, not lost.
- Announce your fleet once: who you are, what repo/regions you own, how to reach you. Re-announce when scope changes.

## 2. Collision handshake (region-claim protocol)

When another fleet works the same repo:

1. They announce regions at risk (file paths or door names).
2. You reply with an explicit region-level claim: "No overlap" or exact claimed paths.
3. Relay verdicts through bridges; never assume silence means clearance.

## 3. Contract pinning across fleets

If Fleet A's consumer depends on Fleet B's producer:

- Ask B to pin the dependency with a **regression test** (e.g., `test_local_fleet_preserves_task_id_passthrough`), not just a verbal promise.
- Route semantic questions (auth direction, schema shape) to the OWNER via the consuming PR, tagged `@dezocode`, with contrastive options — not open-ended questions.

## 4. Bridge etiquette

- Bridges relay facts, not decisions: decisions stay with the owning fleet + owner.
- Auto-responder ("cannot respond while working") = message queued; do NOT resend.
- When your work supersedes a staged delta, publish a gap-verdict so the other fleet stands down instead of duplicating.

## 5. Hooking local sessions to repo state

- Local side: Atomic/Hermes intercom groups, hook scripts (`.sai/hooks/*`). Repo side: sessions-API planes (`/api/hermes-sessions/{sessions,prs,health}`), PR check-runs.
- Convergence key: **Task-ID** — one identity per task across both sides. Producers must pass it through (pin with tests); consumers reconcile on it.
- Auth: local `gh` credential (`gh auth token`) as the enrollment proof; server-side acceptance class (verifier vs writer) is an owner decision.

## 6. Anti-patterns

- Launching against artifacts you didn't author without checking ownership first (verify `/tmp/<checkout>` and research-doc provenance).
- Editing a shared file while another fleet has an in-flight integration tree — stage patches, integrate sequentially, gate after each merge.
- Treating "checks green" as convergence: convergence = exact-head CI green + reviewer SUCCESS + acceptance ticked + owner verification.
