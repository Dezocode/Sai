# Router verification

- Contract and router suites: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v prototypes/plugins/pisai-local/tests/test_contract.py prototypes/plugins/pisai-local/tests/test_router.py` — 7 tests passed.
- `git diff --check` — passed.
- Mocked proof covers Pi hook role selection, image-to-vision selection, coding→vision residency switching, selected/resident model and context evidence, correlated response headers, structured issue ledger, and fail-closed swap safety.
- No model weights, secrets, Hostinger inference service, or Sai production dependency are included.
- Real Mac gateway proof remains a deployment-time acceptance test because this validation intentionally did not start services or change model residency.
