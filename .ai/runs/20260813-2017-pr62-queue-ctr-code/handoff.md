# Handoff — ctr-code-pr62smoke (CTO-029 introducer provenance)

Lease `lease-c3a003pr62q1`, contract v9 (Cora A-009), Task-ID
`20260813-2017-pr62-queue-ctr-code`.

Saul run 31763018964 / comment 5288630796 rejected HEAD officer
issuer+grant as pin provenance. Replay now requires `source` and
`introduced_by_sha`, extracts the pin from that officer commit, and
checks commit-time `matching_grant` (not HEAD grants). Forged intro
metadata and rewritten HEAD grants do not authorize historical SHAs.

Did not write the officer pin YAML (Sai recorded `introduced_by_sha`
at `e84e5d7` pointing at `2a57842`). Did not disable
`saul-review.yml` `pull_request`. Did not PASS. CTO-029 is
`IMPLEMENTED_AWAITING_SAUL`. CTO-025 stays `BLOCKED_EXTERNAL`.

`self_pass: false`. `do_not_merge: true`. Next: fresh Saul review.
