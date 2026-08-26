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
    def test_hook_and_image_selection(self):
        adapter = GatewayAdapter("http://gateway", lambda request, timeout=10: Response({}))
        self.assertEqual(adapter.role({"messages": []}, "compact"), "compact")
        self.assertEqual(adapter.role({"messages": [{"content": [{"type": "image_url"}]}]}), "vision")
        self.assertEqual(adapter.role({"messages": []}), "coding")

    def test_complete_delegates_to_existing_gateway_with_correlation(self):
        captured = {}
        def opener(request, timeout=600):
            captured.update({"url": request.full_url, "headers": dict(request.header_items()), "body": json.loads(request.data)})
            return Response({"choices": []}, headers={"x-request-id": "upstream"})
        adapter = GatewayAdapter("http://gateway", opener)
        status, headers, _ = adapter.complete({"request_id": "req-12345678", "messages": []})
        self.assertEqual(status, 200); self.assertEqual(captured["url"], "http://gateway/v1/chat/completions")
        self.assertEqual(captured["body"]["model"], "qwen3.8-ridge-gguf"); self.assertEqual(captured["headers"]["X-pisai-task"], "coding")
        self.assertEqual(captured["headers"]["X-pisai-request-id"], "req-12345678"); self.assertEqual(headers["x-request-id"], "upstream")

    def test_status_is_read_only_runtime_proof(self):
        adapter = GatewayAdapter("http://gateway", lambda request, timeout=10: Response({"activeModel": "ridge", "context": {"window": 32768}}))
        self.assertEqual(adapter.status()["context"]["window"], 32768)


if __name__ == "__main__": unittest.main()
