# Plan — Cora Hostinger bootstrap reuse of v12

HEAD `0df9a515f409b998822276d73de1ba7173fec1a5`. Contract
`20260813-pr62-saul-smoke` v12. Lease `lease-c3a003pr62q1`.
Contractor `ctr-code-pr62smoke`. Task-ID
`20260813-2017-pr62-queue-ctr-code`.

**reuse=true. v13=false. A-013=false.** Bootstrap P0-B and
P0-C sit under already-granted v12 `allowed_paths`
(`scripts/**`, `tests/**`, contract tree). Not authority
expanding. Not path expansion. denied_paths unchanged.

Coverage:

- P0-B prove `SAI_CANDIDATE_TREE` HEAD equals `--head` →
  `scripts/**`, `tests/**`.
- P0-C refuse fallback to candidate
  `root/scripts/invoke-saul-review` and `saul-attest`
  (lines 66-69) → `scripts/**`, `tests/**`.
- Contractor may append HEAD/FALLBACK blocker items
  DISCOVERED or IMPLEMENTED_AWAITING_SAUL not PASS →
  `.ai/contracts/20260813-pr62-saul-smoke/**`.
- P0-A `/opt/sai/trusted-reviewer` absent:
  WAITING_EXTERNAL_OPERATOR. Cursor must not provision
  Hostinger. Do not write a blocker item.
- P1-D generic `[self-hosted]`: DEFERRED_NONBLOCKING.
  Do not create a blocker.

Cora writes: compact REQ-SAUL-BOOTSTRAP-HEAD-001,
REQ-SAUL-BOOTSTRAP-FALLBACK-001, and
REQ-SAUL-BOOTSTRAP-EXT-001 on `requirements/ledger.yaml`
(stays ≤300); this wave dir; standing-run handoff append.
Does not write A-013, v13, blockers/items, scripts,
workflows, `_config`, authorizations, decisions, or
`.cursor`. Does not bump lease or `contract.json`. Commit
uses grant Task-ID `20260813-2016-pr62-queue-cora`. This
wave does not push.

Contractor next: implement HEAD proof and no-fallback
under v12; do not provision Hostinger; do not create a
P1-D blocker; do not PASS.
