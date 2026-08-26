# Router verification

- Contract, adapter, and memory suites: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v prototypes/plugins/pisai-local/tests/test_contract.py prototypes/plugins/pisai-local/tests/test_gateway_adapter.py prototypes/plugins/pisai-local/tests/test_memory.py` — 11 tests passed.
- `git diff --check` — passed.
- Mocked proof covers Pi hook role selection, image-to-vision selection, delegation to the existing Mac gateway, correlated request headers, read-only runtime proof, and structured gateway boundaries.
- No model weights, secrets, Hostinger inference service, or Sai production dependency are included.
- Real Mac gateway proof remains a deployment-time acceptance test because this validation intentionally did not start services or change model residency; the adapter does not own lifecycle or bind a port.
- Live read-only probes: canonical `127.0.0.1:11437` `/proxy/health`, `/proxy/runtime`, and `/v1/models` returned successfully. The registry reports Ridge as installed, Ornith and Qwen3.5 compactor as not-installed, and an empty `routes` table; no route-switch request was issued under swap pressure.
- Reproducible probe: `python3 prototypes/plugins/pisai-local/tests/live_readonly_probe.py` performs only GET requests and requires 200 responses plus a 32,768-token active context. `--require-routes` intentionally remains failing until the shared registry publishes all three verified roles.
- Adapter catalog preflight rejects `not-installed`, `planned`, `disabled`, and other unavailable role records before forwarding; the test confirms an unavailable vision request produces no gateway completion call.
- Pi memory proof covers bounded chunking, 3K active-spec rejection, compactor delegation through the gateway, structured ledger writes, and absence of raw-history persistence.
- Live registry route precedence is tested: when the Mac publishes a role route, it overrides the environment fallback alias; unavailability is still rejected before forwarding.
