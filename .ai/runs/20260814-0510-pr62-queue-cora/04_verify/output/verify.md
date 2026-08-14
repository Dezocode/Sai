# Verify — Cora A-012 / v12 (administration only)

Commands run before commit (HEAD still 4503f55):

- `python3 -m json.tool` on contract.json, lease, metadata.json: OK
- YAML parse of A-012.yaml, v12.yaml, consumed-08c26942e30d3e7c.yaml,
  requirements/ledger.yaml: OK
- Line counts ≤300: A-012 45, v12 127, consumed 51, ledger 146
- Path identity: v12 allowed_paths == v11; denied_paths == v11;
  lease-c3a003pr62q1 active on v12; task_id 20260813-2017 kept;
  contract.json current_revision v12; cora_admin_complete true
- `git diff` blockers/items, scripts, workflows, _config,
  authorizations, decisions, .cursor: empty
- `scripts/verify-semantic-hierarchy`: OK
- Did not PASS any blocker. Did not merge. Did not push.
  Did not mark ready. Did not implement scripts/workflows.

Saul consume facts checked against comment 5289717183:
run 31771910025, head 4503f55, REQUEST_CHANGES, codex_invoked true,
synthetic false, hostinger-saul-codex, contract_revision 11,
idempotency_key 08c26942e30d3e7c.
