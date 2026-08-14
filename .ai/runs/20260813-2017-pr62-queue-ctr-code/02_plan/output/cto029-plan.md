# Plan — CTO-029 pin introducer provenance

Qualifying Saul run 31763018964 / comment 5288630796 / head
`9382d1fdbf3f878983db8b8beb4ce4bfb83f98b2` (CTO-029 P0).
Officer pin YAML already has `introduced_by_sha` at `e84e5d7` (points at
`2a57842`). Cora A-009/v9 is in-flight locally; do not take those files.

## Current vs desired

Current: `sha_bound_rows()` accepts a HEAD pin when `issuer` is an officer
and `issuer_grant` names a **HEAD** grant. It ignores `source`,
`introduced_by_sha`, and the commit that first added the pin.

Desired: for each pin used to authorize historical SHA S:

1. Require non-empty `source` and 40-hex `introduced_by_sha`.
2. `git cat-file -e` that SHA; the commit must contain the pin file.
3. Extract the pin file from **introduced_by_sha** (git show, not HEAD
   working tree). Pin for S must exist there (same sha, agent_id,
   task_id, authorization_id).
4. Introducing commit Agent trailer is `ceo` or `ctr-admin`.
5. `matching_grant` at **introduced_by_sha** (commit-time grants, not
   HEAD; no pin recursion) covers that officer+task_id.
6. Pin `issuer_grant` matches the introducing commit Authorization-ID.
7. Bind `source` and `issuer_grant` from the introducing blob; HEAD
   rewrite of those fields does not authorize.
8. Negatives: missing/wrong `introduced_by_sha`; rewritten HEAD grant.
9. Ignore contractor `_config` pins. Load via git show only.

Do not write `.ai/authorizations/**`. Rebase if Sai/Cora land; never force.

## Changes

- `sai_auth_grant.py`: provenance loader; `matching_grant(..., use_pins=)`.
- `sai_auth_rebind_test.py`: stamp `introduced_by_sha` on good pins;
  forged missing/wrong intro; HEAD grant rewrite. Keep ≤500 lines.
- `sai_auth_verify.py`: comment only.
- Append CTO-029 `IMPLEMENTED_AWAITING_SAUL`. Keep CTO-025
  `BLOCKED_EXTERNAL`. Do not disable `saul-review.yml` `pull_request`.

## Verification

`--self-test`, `verify-code-health`, `sai-blockers --clear CTO-029
--actor cursor` → REJECT. Range replay after rebase. `self_pass: false`.
`do_not_merge: true`.
