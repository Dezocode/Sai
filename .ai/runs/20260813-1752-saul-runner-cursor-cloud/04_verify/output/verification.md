# Verification — Saul self-hosted runner continuation

Task: `20260813-1752-saul-runner-cursor-cloud`  
Head at this write: uncommitted P1 remediations after production REQUEST_CHANGES.

## Runner (GitHub Jobs API + logs)

| Field | Evidence |
|---|---|
| name | `hostinger-saul-codex` |
| labels used | `[self-hosted]` (Jobs API; no extra custom labels returned) |
| group | Default |
| OS/arch | Linux / X64 |
| container | `/.dockerenv` present; hostname `c775b2b0df55`; docker CLI absent |
| Codex | `/usr/bin/codex` `codex-cli 0.147.0`; `~/.codex` present |
| first assignment | run **31728732258** on `0f5fc2d` (failed PyYAML, before Codex) |

`gh api repos/Dezocode/Sai/actions/runners` remains HTTP 403 for this token.
Labels were proven by job assignment, not guessed.

## Production Codex runs

| Run | SHA | Runner | Result |
|---|---|---|---|
| 31728732258 | 0f5fc2d | hostinger-saul-codex | BLOCKED NO_ARTIFACT (PyYAML missing) |
| 31728917780 | 7f532b0 | hostinger-saul-codex | pip missing |
| 31729026639 | 4cedada | hostinger-saul-codex | PEP 668; yaml still missing |
| 31729323810 | a742cbc | hostinger-saul-codex | **codex_invoked: true**; BLOCKED (sandbox /tmp package) comment 5284597443 |
| 31729666256 | 34b26f5 | hostinger-saul-codex | **codex_invoked: true synthetic: false REQUEST_CHANGES** comment 5284640842 |

## Cora / contractor (local production-path scripts, real Saul YAML)

Contract `20260813-pr62-saul-smoke`:

- v1 drafted by Cora (`ctr-admin`)
- consume of run 31729666256 REQUEST_CHANGES → **v2** amendment **A-002**
- TRACE: `CTO-001 -> A-002 -> v2`, `CTO-002 -> A-002 -> v2`, `CTO-003 -> A-002 -> v2`
- lease `lease-2415d447bf88` **stale** (`contract moved to v2`)
- assume `ctr-code-pr62smoke` → `STALE_OR_MISSING_LEASE`
- Cora issued `lease-5d635bef02b9` for v2; assume succeeded; released

## Matrix A–Y

| Item | Result | Evidence |
|---|---|---|
| A–F local identity | PASS | e2e + self-tests |
| G GitHub event | PASS | PR events fire `saul-cto-review` |
| H Actions invokes Codex | PASS | run 31729666256 `codex_invoked: true` on hostinger-saul-codex |
| I Saul profile loaded | PASS | prompt includes tracked Saul paths; Codex returned structured CTO findings |
| J real REQUEST_CHANGES | PASS | comment 5284640842; artifact YAML in this run |
| K Cora consume | PASS | consume of that YAML as ctr-admin |
| L v2 + TRACE | PASS | A-002 traces |
| M v1 lease stale | PASS | lease-2415d447bf88 stale |
| N reload v2 | PASS | lease-5d635bef02b9 assume |
| O second GH event | PENDING | next push after this remediation |
| P Saul APPROVE exact | FAIL | latest production disposition is REQUEST_CHANGES not APPROVE |
| Q Sai APPROVE exact | FAIL | unbound cursor-cloud must not impersonate ceo |
| R CI green exact SHA | PASS* | agent-audit green on prior heads; saul-cto-review red until APPROVE |
| S human gate BLOCKED until dual | PASS | no READY without Saul+Sai exact-head |
| T extra commit stale | FAIL | no APPROVE yet to stale |
| U fresh READY | FAIL | never READY |
| V expanding not auto-granted | PASS | consume fixtures + no auto-grant here |
| W wrong-path / unbound | PASS | fixtures |
| X idempotent skip | PASS | local + workflow concurrency group |
| Y Codex missing BLOCKED | PASS | earlier ubuntu-latest runs; also omitted-codex_invoked fixture |

\* agent-audit is independent of the CTO check.

## P1 remediations from REQUEST_CHANGES 31729666256

- CTO-001: `human_gate` requires `codex_invoked is True` and `synthetic is False`; schema requires those fields for Saul; fixture `saul-omitted-codex-invoked-blocked`
- CTO-002: `bootstrap.standing: false`; `bootstrap_ok` rejects `standing: true`; bound_pr 62; disable_after_human_review
- CTO-003: job-level same-repo `if` before `runs-on`; fixture `saul-workflow-job-if-same-repo`

## Not READY FOR HUMAN REVIEW

Missing: second Codex review APPROVE of exact revision+SHA, Sai independent same-state APPROVE, READY gate, stale-after-new-commit, restored READY. CTO-1 P0 from run 31729323810 (untrusted PR code on a persistent Codex runner) is mitigated for forks at job level but `pull_request_target`/trusted-scripts-from-main is not landed (would freeze the old ubuntu-latest workflow until merge).
