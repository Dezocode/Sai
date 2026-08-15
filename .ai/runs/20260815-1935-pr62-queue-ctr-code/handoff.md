# Handoff — ctr-code-pr62smoke (Decision 0009 executables)

Lease `lease-c3a003pr62q1`, contract v12. Task-ID
`20260813-2017-pr62-queue-ctr-code`. Wave `20260815-1935-pr62-queue-ctr-code`.
Parent `pr62-primary`. Built on `c13bef88`. Cursor is never Saul.

Comptroller: exact-state schema; publisher emits `Saul / Product Quality`
and generated `Saul / Blocker / <ID>` Checks. `verify-saul-gated-ci`
consumes public v2 evidence and cannot mint PASS. Absent proof reports
non-success and exits 0 unless false-terminal / missing ledger / substitute.

Frontier: filled `quality-reference-mapping.yaml` pointing at Decision-0005
and quality-profile. Go/Swift product tests NOT_APPLICABLE. rust is
control-plane only. Privileged checkout pinned to
`11d5960a326750d5838078e36cf38b85af677262`.

Anti-balloon: `verify-saul-anti-balloon` (not a second framework).

Ralph: sai-resume reconstructs live v12; coordinator-state refreshed;
fixtures A–G execute. Meta blocker IMPLEMENTING. Never PASSED.

`do_not_pass: true`. `do_not_merge: true`. `do_not_push: true`.
Next: parent pushes; Hostinger Saul reviews this exact head.
