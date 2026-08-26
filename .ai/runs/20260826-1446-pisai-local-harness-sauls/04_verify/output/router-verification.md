# Router verification

- Contract and router suites: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v prototypes/plugins/pisai-local/tests/test_contract.py prototypes/plugins/pisai-local/tests/test_router.py` — 7 tests passed.
- `git diff --check` — passed.
- Mocked proof covers Pi hook role selection, image-to-vision selection, delegation to the existing Mac gateway, correlated request headers, read-only runtime proof, and structured gateway boundaries.
- No model weights, secrets, Hostinger inference service, or Sai production dependency are included.
- Real Mac gateway proof remains a deployment-time acceptance test because this validation intentionally did not start services or change model residency; the adapter does not own lifecycle or bind a port.
