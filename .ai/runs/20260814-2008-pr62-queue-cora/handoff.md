# Handoff — Cora Hostinger bootstrap reuse of v12

reuse=true. v13=false. lease-c3a003pr62q1. contractor
ctr-code-pr62smoke. contract 20260813-pr62-saul-smoke v12
unchanged. HEAD 0df9a515f409b998822276d73de1ba7173fec1a5.

allowed_paths cover bootstrap HEAD proof and no-fallback
to candidate invoke-saul-review / saul-attest under
scripts/** and tests/**. denied_paths unchanged. Appended
REQ-SAUL-BOOTSTRAP-HEAD-001, REQ-SAUL-BOOTSTRAP-FALLBACK-001,
and REQ-SAUL-BOOTSTRAP-EXT-001. Did not write
blockers/items. Did not PASS. implements false.
do_not_merge true. do_not_push true. technical_pass false.

P0-A `/opt/sai/trusted-reviewer` absent is
WAITING_EXTERNAL_OPERATOR. Cursor must not provision
Hostinger. P1-D generic `[self-hosted]` is
DEFERRED_NONBLOCKING; do not create a blocker.

Contractor next work-item: prove SAI_CANDIDATE_TREE HEAD
equals `--head`; refuse fallback to candidate
root/scripts/invoke-saul-review and saul-attest; append
HEAD/FALLBACK blocker DISCOVERED or
IMPLEMENTED_AWAITING_SAUL not PASS. Do not provision
Hostinger. Do not create a P1-D blocker. Do not merge.
Do not mark ready. Do not PASS.
