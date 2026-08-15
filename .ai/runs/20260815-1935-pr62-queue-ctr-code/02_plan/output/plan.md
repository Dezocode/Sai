# Plan — Decision 0009 repo executables

Parent `pr62-primary`. Lease `lease-c3a003pr62q1`. Contract v12.
Build on live HEAD `c13bef88ad0bd6ee65380fa62171214dee9bc725`.
Do not PASS, push, merge, mint keys, provision Hostinger, or write
`.ai/shared/memory/decisions/**` / `.ai/authorizations/**`.

## Current vs desired

Decision 0009 is persisted; four P0s are DISCOVERED. Executables missing:
exact-state Check projection, quality-reference mapping fill, anti-balloon
detector, Ralph rejects A–G, saul-gated-ci consumer. `sai-resume` still
reports stale v4 from coordinator-state.json. `actions/checkout@v4` floats.

Desired: one publisher emits `Saul / Product Quality` plus generated
`Saul / Blocker / <ID>` Checks. Ordinary CI consumes public v2 evidence
and cannot mint PASS. Mapping points at Decision-0005 + quality-profile.
Anti-balloon is a 0005 detector, not a second framework. Resume reconstructs
live v12 and rejects false terminals. Meta blocker stays IMPLEMENTING.

## File changes

- NEW schema `saul-exact-state-review.schema.json`
- EXTEND `sai_auth_saul_check.py` + `saul-publish-check` (no new trusted job)
- NEW `verify-saul-gated-ci` consumer
- FILL `quality-reference-mapping.yaml`; NEW `verify-saul-quality-reference`
- PIN checkout SHA in trusted workflow + agent-audit (same uses: count)
- NEW `sai_auth_antiballoon.py` + `verify-saul-anti-balloon`
- EXTEND `sai_auth_resume.py` + tests A–G; refresh coordinator-state to v12
- Wire code-health-saul.yaml + agent-audit unconditional run:
- Ledger: three P0s IMPLEMENTED_AWAITING_SAUL; Ralph meta IMPLEMENTING

## Caps

Do not grow `code-health.py` (500), `sai_auth_review.py` (500),
`sai_auth_test.py` (~497). Trusted workflow ≤300. YAML ≤300. Discover
new `--self-test` verifiers from the Saul include file.

## Verification

`verify-code-health --self-test` and live; all listed `verify-saul-*`,
`sai-resume`, `sai-blockers` self-tests; `verify-agent-authorization` and
`verify-merge-handoff` on `origin/main..HEAD`; `python3 -m json.tool` on
new schemas; `wc -l` on edited yaml/py/yml/md.
