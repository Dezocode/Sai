# Intake — Cora Decision 0009 principal blockers, v12 reuse

Requester: parent logical Primary `pr62-primary`. Named child
Cora (`ctr-admin`), physical runtime
`bc-c5aa6ff2-91e9-56eb-8c3e-7b343ddf2a36`. Grant
`grant-pr62-queue-cora`. Standing commit Task-ID
`20260813-2016-pr62-queue-cora`. Agent: ctr-admin.

Exact requested outcome: ingest Dezocode principal comments
on PR #62 (blocking):

1. `5303750100` — FINAL architecture → Decision 0009
   (0009 free; 0001-0008 exist). Trusted Saul Comptroller +
   nested SHA-bound product-quality loop. Does not supersede
   0005/0006/0007/0008.
2. `5303751556` — `B-SAUL-COMPTROLLER-READINESS-001`
3. `5303753512` — `B-FRONTIER-QUALITY-ARCH-001`
4. `5303755356` — `B-QUALITY-ANTI-BALLOON-001`
5. `5303757105` — `B-RALPH-BLOCKER-CI-CONVERGENCE-001`
   (meta; Saul PASSes last)

Preserve those IDs. Do not invent duplicates. Do not PASS.
YAML ≤300 lines. Compact REQs. Administration only.

## Repository facts (command-backed)

- HEAD `abae75d42e675d781be8b4041ea62fc8773defdc` on
  `cursor/codebase-health-90ba` (matches parent snapshot).
- origin/main `40efe0a0724764fc1cf3c45ed8498b5606a0f453`.
- origin `github.com/Dezocode/Sai` canonical, not a fork.
- Working tree clean at intake.
- `gh api` comments 5303750100/1556/3512/5356/7105: user
  Dezocode, created 2026-08-15T18:58:31Z .. 19:00:18Z.
- Decisions 0001-0008 exist; no `0009-*.md`.
- IDs above absent from tree (rg no matches).
- `contract.json` `current_revision` v12. No A-013.yaml /
  v13.yaml.
- Lease `lease-c3a003pr62q1` active, revision v12, agent
  `ctr-code-pr62smoke`.
- v12 `allowed_paths`: `.ai/runs/**`,
  `.ai/contracts/20260813-pr62-saul-smoke/**`, `tests/**`,
  `scripts/**`, `.github/workflows/**`, `.ai/_config/**`,
  `.ai/shared/schemas/**`.
- `denied_paths`: `.ai/agents/saul/**`,
  `.ai/shared/memory/decisions/**`, `.ai/authorizations/**`.
- Grant `grant-pr62-queue-cora` covers `.ai/contracts/**`,
  `.ai/runs/**` (and requests/agents). Officer grant
  `grant-pr62-queue-ceo` covers `.ai/**` including
  decisions/architecture.
- requirements/ledger.yaml 259 lines; blockers/ledger.yaml
  76 lines.

## Authorization evaluation (not PASS)

- Comment `5303750100` is the human authority source for
  Decision 0009. Officer writes
  `.ai/shared/memory/decisions/0009-trusted-saul-comptroller-product-quality-loop.md`
  and `.ai/shared/memory/architecture.md` under
  `grant-pr62-queue-ceo`, agent `ceo`, Task-ID
  `20260813-2015-pr62-queue-ceo`. Cora does not write them.
  Tracked officer grant already covers `.ai/**`. Not a new
  human-expansion gate. Not A-013 for officer paths.
- Contractor implementation (scripts, schemas, `_config`,
  workflows, contract evidence, tests) is already in v12
  `allowed_paths`. reuse=true. v13=false. A-013=false.
  path_expansion=false.
- Contractor MUST NOT write `decisions/**` or
  `authorizations/**`.

## Findings (not PASS)

- Four new P0 blockers DISCOVERED; clearance_authority
  saul; Cora/contractor/Sai cannot PASS.
- REQ-5303750100 tracks Decision 0009 officer persist.
- Compact ledger append required (259→≤300).
- B-SAUL-QUALITY-LOOP-001 remains separate; 0009 appends
  it, does not supersede.
