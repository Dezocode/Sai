# Handoff — Cora TPR-001/002 reuse of v12

reuse=true. v13=false. lease-c3a003pr62q1. contractor
ctr-code-pr62smoke. contract 20260813-pr62-saul-smoke v12
unchanged. HEAD 01fe60609d6d61d71cb401a06619b71601ed94f6.

allowed_paths cover TPR-001 (delete
trusted-reviewer-provision.yml; stop sai_auth_wait poll;
optional provision python/fixture) and TPR-002 (in-place
sai_auth_review.py no net lines; retarget sai_auth_test.py;
new small TPR test module; strip Invoke Codex env).
denied_paths unchanged. Appended REQ-TPR-001 / REQ-TPR-002.
Did not write blockers/items. Did not PASS. implements false.
do_not_merge true. do_not_push true. technical_pass false.

Contractor next work-item: write TPR-001 / TPR-002 blocker
items without PASS, then implement under v12. Do not restore
saul-review.yml. Do not grow sai_auth_review.py. Do not merge.
Do not mark ready. Saul still clears.
