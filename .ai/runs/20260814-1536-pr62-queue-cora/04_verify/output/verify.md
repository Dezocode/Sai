# Verify — Cora TPR-001/002 reuse (administration only)

Commands run before commit (HEAD still 01fe606):

- `python3 -m json.tool` on metadata.json, contract.json, lease: OK
- YAML parse of requirements/ledger.yaml: OK
- Line counts ≤300: ledger 162, v12 127
- Wave handoff.md 881 bytes (>20)
- contract.json current_revision v12; lease-c3a003pr62q1
  active on v12; agent_id ctr-code-pr62smoke
- No A-013.yaml; no v13.yaml; no TPR blocker items
- `git diff` scripts/, .github/workflows/, _config,
  authorizations, decisions, .cursor, blockers/,
  amendments/, revisions/: empty
- `scripts/verify-semantic-hierarchy`: OK
- Did not PASS. Did not merge. Did not push. Did not
  mark ready. Did not implement scripts/workflows.

reuse=true. v13=false. allowed_paths cover TPR-001/002.
