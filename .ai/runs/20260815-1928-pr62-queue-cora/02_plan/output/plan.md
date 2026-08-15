# Plan — Cora quality-ref amendment, reuse v12

HEAD `abae75d42e675d781be8b4041ea62fc8773defdc`.
**reuse=true. v13=false. A-013=false.** No new Decision 0009.
No new blockers. Prefer not to commit/push.

1. Amend REQ-5303750100/3512/5356 in place (digests + source
   URLs for 5303804678/5303809236). Keep ledger ≤300. Do not
   append two new full REQ blocks.
2. Update B-FRONTIER-QUALITY-ARCH-001 description + compact
   domain-aware mapping YAML under the contract tree.
   Preserve blocker_id. Statuses IMPLEMENTED | NOT_APPLICABLE
   | BLOCKER | DEFERRED_NONBLOCKING.
3. Update B-QUALITY-ANTI-BALLOON-001 notes: domain-specific
   refs, not rust-as-universal. Preserve ID.
4. Update reviews/cora-decision-0009-v12-reuse.yaml
   frontier-quality-arch deliverable to domain-aware mapping.
   Confirm officer_writer ceo/grant-pr62-queue-ceo;
   contractor ctr-code-pr62smoke / lease-c3a003pr62q1.
5. Wave run 20260815-1928-pr62-queue-cora + standing handoff
   note. Cora does not write decisions, architecture.md,
   authorizations, scripts, workflows, _config, schemas, or
   .cursor. implements false. technical_pass false.
