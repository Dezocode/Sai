# Plan — CTO-028 officer-only SHA-bound pins

Qualifying Saul run 31761796169 / comment 5288500483 / head
`f4443fa0b00ec950768ba7aff14020732e338e9d` (CTO-028 P0).

## Current vs desired

Current: replay loads `audit.sha_bound_authorization` from
`git show HEAD:.ai/_config/authorization.yaml`. Contract v8 allows this
contractor to write `.ai/_config/**`, so a contractor HEAD pin can
retrospectively authorize historical SHAs.

Desired: load pins only from
`git show HEAD:.ai/authorizations/sha-bound-authorization.yaml` (never
the dirty working tree). Require `issuer` in officers (`ceo` or
`ctr-admin`) and `issuer_grant` present on a tracked grant whose
principal is that issuer. Ignore `_config` and any contractor-allowed
path. Deny `.ai/authorizations/**` for contractors.

Sai already recorded the officer pin file at `2a57842`. This contractor
does not write that YAML.

## Changes

- Delete `sha_bound_authorization` from `.ai/_config/authorization.yaml`.
- Add `.ai/authorizations/**` to `protected_denied_for_contractors`.
- `sai_auth_grant.py` / `sai_auth_verify.py`: officer-file loader +
  provenance; strip `_config` pins from live cfg.
- `sai_auth_rebind_test.py`: contractor `_config` pin does not authorize;
  officer file with issuer+grant does; wrong sha does not; dirty WT does
  not. Keep ≤500 lines.
- Append CTO-028 `IMPLEMENTED_AWAITING_SAUL`. Do not PASS. Keep
  CTO-021/025 non-PASSED (CTO-025 stays BLOCKED_EXTERNAL). Do not
  disable `saul-review.yml` pull_request.

## Verification

`verify-agent-authorization --self-test`, `origin/main..HEAD` (needs Sai
pins on HEAD), `verify-code-health`, `sai-blockers --self-test`,
`--clear CTO-028 --actor cursor` must REJECT.

`self_pass: false`. `do_not_merge: true`.
