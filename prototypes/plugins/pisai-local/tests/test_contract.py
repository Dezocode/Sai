import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).parents[1]


class ContractTest(unittest.TestCase):
    def test_routing_schema_is_strict_and_has_three_roles(self):
        schema = json.loads((ROOT / "config/model-routing.schema.json").read_text())
        self.assertTrue(schema["additionalProperties"] is False)
        self.assertEqual(schema["properties"]["task"]["enum"], ["coding", "vision", "compact"])

    def test_route_overlay_uses_exact_catalog_keys(self):
        routes = json.loads((ROOT / "config/model-registry.routes.example.json").read_text())
        self.assertEqual(set(routes["routes"]), {"coding", "vision", "compact"})
        self.assertFalse(routes["routePolicy"]["silentFallback"])

    def test_environment_is_secret_free_and_32k_bounded(self):
        env = (ROOT / "config/pisai-router.env.example").read_text()
        self.assertIn("PISAI_CONTEXT_TOKENS=32768", env)
        self.assertIn("PISAI_ACTIVE_SPEC_MAX_TOKENS=3000", env)
        self.assertIn("PISAI_GATEWAY_HEALTH_PATH=/proxy/health", env)
        self.assertIn("PISAI_GATEWAY_STATUS_PATH=/proxy/runtime", env)
        self.assertIn("PISAI_CODING_MODEL=qwen3.8-ridge-gguf", env)
        self.assertNotRegex(env, r"(?i)(token|secret|password|api[_-]?key)\s*=")

    def test_architecture_keeps_hostinger_out_of_inference(self):
        doc = (ROOT / "docs/ARCHITECTURE.md").read_text()
        self.assertIn("Hostinger control/API plane", doc)
        self.assertIn("no Mac inference duplicate", doc)
        self.assertIn("POST /v1/chat/completions", doc)

    def test_architecture_requires_full_request_residency_gate(self):
        doc = (ROOT / "docs/ARCHITECTURE.md").read_text()
        self.assertIn("FIFO async gate", doc)
        self.assertIn("single_resident_queue_acquired", doc)
        self.assertIn("does not start a backend", doc)


if __name__ == "__main__":
    unittest.main()
