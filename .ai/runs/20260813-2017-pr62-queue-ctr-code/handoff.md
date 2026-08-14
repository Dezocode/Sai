# Handoff — ctr-code-pr62smoke (CTO-028 officer pins only)

Lease `lease-c3a003pr62q1`, contract v8 (Cora A-008), Task-ID
`20260813-2017-pr62-queue-ctr-code`.

Saul run 31761796169 / comment 5288500483 rejected contractor-authored
`sha_bound_authorization` in `.ai/_config/authorization.yaml`. Replay now
loads pins only from
`git show HEAD:.ai/authorizations/sha-bound-authorization.yaml` and
requires `issuer` in officers (`ceo` or `ctr-admin`) plus `issuer_grant`
on a tracked grant. `_config` pins and dirty working-tree officer files
do not authorize. `.ai/authorizations/**` is contractor-denied.

Did not write the officer pin YAML (Sai recorded it at `2a57842`).
Did not disable `saul-review.yml` `pull_request`. Did not PASS.
CTO-028 is `IMPLEMENTED_AWAITING_SAUL`. CTO-025 stays
`BLOCKED_EXTERNAL`. CTO-021 stays `IMPLEMENTED_AWAITING_SAUL` (not
PASSED).

`self_pass: false`. `do_not_merge: true`. Next: fresh Saul review.
