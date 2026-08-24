# Handoff 20260824-0038-pr77-stalereset-hermes — PR 77 Round-19

Closed Saul P1 F037: ghJson re-stored expired X-RateLimit-Reset each response, looping ghWindowRoll consume-once so GH_WINDOW_BUDGET=60 never blocked (pre-fix sim: 200 reqs, USED=1, gate open). Now only strictly-future resets are stored; local window authoritative headerless/stale; genuine future resets still consumed once (positive control). Gates: --selftest 124 PASS/0 FAIL (3 new Round-19 cases
