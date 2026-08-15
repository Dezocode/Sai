# Verify — Cora Decision 0009 ingest (administration only)

Commands run before commit (HEAD still abae75d):

- `python3 -m json.tool` on metadata.json and stage
  manifests: OK
- YAML parse of requirements/ledger.yaml,
  blockers/ledger.yaml, four blocker items, admin review:
  OK
- REQ-5303750100/1556/3512/5356/7105 present, blocking
  true, in-progress
- Four blockers DISCOVERED, clearance_authority saul,
  clearance_review_id null
- Line counts ≤300: requirements/ledger 299, blockers
  ledger 84, admin review 116, v12 127, items 35-38
- Wave handoff.md written (>20 bytes)
- contract.json current_revision v12; lease-c3a003pr62q1
  active on v12; agent_id ctr-code-pr62smoke
- No A-013.yaml; no v13.yaml; Cora did not write
  decisions/0009 or architecture.md
- `git diff` scripts/, .github/workflows/, _config,
  schemas, authorizations, decisions, .cursor,
  amendments/, revisions/: empty for Cora
- `scripts/verify-semantic-hierarchy`: OK
- Did not PASS. Did not merge. Did not push. Did not
  mark ready. Did not implement scripts/workflows.

reuse=true. v13=false. A-013=false. Officer writes
Decision 0009. Contractor four disjoint slices under v12.
