import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from gateway_adapter import GatewayAdapter


class Response:
    def __init__(self, payload, status=200, headers=None): self.payload, self.status, self.headers = payload, status, headers or {}
    def __enter__(self): return self
    def __exit__(self, *_): pass
    def read(self): return json.dumps(self.payload).encode()


class AdapterTest(unittest.TestCase):
    def registry(self):
        return {"models": [
            {"key": "qwen3.8-27b-ridge-installed", "id": "hf.co/ridge", "aliases": ["qwen3.8-ridge-gguf"], "availability": "installed", "roles": ["coding"]},
            {"key": "ornith-1.5-9b-ad-q4-k-iq4-xs-vision", "id": "hf.co/ornith", "aliases": ["ornith-1.5-9b-vision"], "availability": "not-installed", "roles": ["vision"]},
            {"key": "qwen3.5-2b-4bit-mlx-compactor", "id": "mlx/qwen35", "aliases": ["qwen3.5-2b-4bit-mlx-compactor"], "availability": "not-installed", "roles": ["compact"]},
        ]}

    def test_hook_and_image_selection(self):
        adapter = GatewayAdapter("http://gateway", lambda request, timeout=10: Response({}))
        self.assertEqual(adapter.role({"messages": []}, "compact"), "compact")
        self.assertEqual(adapter.role({"messages": [{"content": [{"type": "image_url"}]}]}), "vision")
        self.assertEqual(adapter.role({"messages": []}), "coding")

    def test_unknown_task_fails_closed(self):
        adapter = GatewayAdapter("http://gateway", lambda request, timeout=10: Response({}))
        with self.assertRaisesRegex(RuntimeError, "unknown PiS AI task"):
            adapter.role({"task": "summarize", "messages": []})

    def test_complete_delegates_to_existing_gateway_with_correlation(self):
        captured = {}
        def opener(request, timeout=600):
            if request.full_url.endswith("/model-registry"):
                registry = self.registry(); registry["routes"] = {"vision": "ornith-1.5-9b-ad-q4-k-iq4-xs-vision"}; return Response(registry)
            captured.update({"url": request.full_url, "headers": dict(request.header_items()), "body": json.loads(request.data)})
            return Response({"choices": []}, headers={"x-request-id": "upstream"})
        adapter = GatewayAdapter("http://gateway", opener)
        status, headers, _ = adapter.complete({"request_id": "req-12345678", "messages": []}, session_id="session-12345678")
        self.assertEqual(status, 200); self.assertEqual(captured["url"], "http://gateway/v1/chat/completions")
        self.assertNotIn("model", captured["body"]); self.assertEqual(captured["headers"]["X-pisai-task"], "coding")
        self.assertEqual(captured["headers"]["X-pisai-request-id"], "req-12345678"); self.assertEqual(captured["headers"]["X-pisai-route-id"], "coding:req-12345678"); self.assertEqual(headers["x-request-id"], "upstream")
        self.assertEqual(captured["headers"]["X-pisai-session-id"], "session-12345678")
        self.assertEqual(captured["body"]["source"], "pi-api")
        self.assertEqual(captured["body"]["telemetry"]["session_id"], "session-12345678")

    def test_status_is_read_only_runtime_proof(self):
        adapter = GatewayAdapter("http://gateway", lambda request, timeout=10: Response({"activeModel": "ridge", "context": {"window": 32768}}))
        self.assertEqual(adapter.status()["context"]["window"], 32768)

    def test_unavailable_role_fails_before_forwarding(self):
        calls = []
        def opener(request, timeout=600):
            if request.full_url.endswith("/model-registry"):
                registry = self.registry(); registry["routes"] = {"vision": "ornith-1.5-9b-ad-q4-k-iq4-xs-vision"}; return Response(registry)
            calls.append(request.full_url); return Response({})
        adapter = GatewayAdapter("http://gateway", opener)
        with self.assertRaisesRegex(RuntimeError, "unavailable"): adapter.complete({"messages": []}, "vision")
        self.assertEqual(calls, [])

    def test_live_registry_route_overrides_environment_alias(self):
        captured = {}
        def opener(request, timeout=600):
            if request.full_url.endswith("/model-registry"):
                registry = self.registry(); registry["routes"] = {"coding": "qwen3.8-ridge-gguf"}; return Response(registry)
            captured["body"] = json.loads(request.data); return Response({"choices": []})
        adapter = GatewayAdapter("http://gateway", opener)
        adapter.complete({"messages": []})
        self.assertEqual(captured["body"]["model"], "qwen3.8-ridge-gguf")


if __name__ == "__main__": unittest.main()
