import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from router import Config, Router, select_role


class FakeBackend:
    def __init__(self): self.loaded = []; self.chat_calls = []
    def call(self, method, path, payload=None, timeout=60):
        if path == "/api/ps": return 200, {}, json.dumps({"models": self.loaded}).encode()
        if path == "/api/generate":
            if payload.get("keep_alive") == 0: self.loaded = [m for m in self.loaded if m["name"] != payload["model"]]
            else: self.loaded = [{"name": payload["model"], "context_length": payload["options"]["num_ctx"]}]
            return 200, {}, b"{}"
        if path == "/v1/chat/completions": self.chat_calls.append(payload); return 200, {}, b'{"choices":[]}'
        raise AssertionError(path)


class RouterTest(unittest.TestCase):
    def make_router(self, resources=None):
        directory = tempfile.TemporaryDirectory(); self.addCleanup(directory.cleanup)
        config = Config("http://fake", {"coding": "ridge", "vision": "ornith", "compact": "qwen35"}, 32768, .85, .97, Path(directory.name))
        return Router(config, FakeBackend(), resources or (lambda: {"available": True, "swap_used_ratio": .1}))

    def test_hook_and_image_select_roles(self):
        self.assertEqual(select_role({"messages": []}, "vision"), "vision")
        self.assertEqual(select_role({"messages": [{"content": [{"type": "image_url"}]}]}), "vision")
        self.assertEqual(select_role({"messages": []}), "coding")

    def test_route_switch_records_proof_and_headers(self):
        router = self.make_router(); status, headers, _ = router.chat({"request_id": "req-12345678", "messages": []})
        self.assertEqual(status, 200); self.assertEqual(headers["x-pisai-route"], "coding"); self.assertEqual(headers["x-pisai-model"], "ridge")
        status, headers, _ = router.chat({"request_id": "req-vision1", "messages": [{"content": [{"type": "image"}]}]})
        self.assertEqual(headers["x-pisai-route"], "vision"); self.assertEqual(router.memory.read("events.jsonl")[-1]["resident_model"], "ornith")

    def test_unsafe_transition_fails_closed(self):
        router = self.make_router(lambda: {"available": True, "swap_used_ratio": .90})
        with self.assertRaisesRegex(RuntimeError, "safety gate"): router.chat({"messages": []})

    def test_issue_ledger_is_structured(self):
        router = self.make_router(); router.memory.append("issues.jsonl", {"issue_id": "ISSUE-1", "summary": "missing hook", "status": "open"})
        self.assertEqual(router.memory.read("issues.jsonl")[0]["status"], "open")


if __name__ == "__main__": unittest.main()
