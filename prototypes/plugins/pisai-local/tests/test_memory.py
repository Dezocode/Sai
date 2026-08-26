import json, tempfile, unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from gateway_adapter import GatewayAdapter
from memory import Compactor, PiMemory, chunks, estimate_tokens


class Response:
    def __init__(self, payload, status=200): self.payload, self.status, self.headers = payload, status, {}
    def __enter__(self): return self
    def __exit__(self, *_): pass
    def read(self): return json.dumps(self.payload).encode()


class MemoryTest(unittest.TestCase):
    def test_chunking_is_bounded(self): self.assertEqual([len(x) for x in chunks("x" * 100, 40)], [40, 40, 20])
    def test_oversized_spec_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "3000"): PiMemory(directory).write_spec({"objective": "x" * 13000})
    def test_compactor_writes_structured_ledgers_only(self):
        calls = []
        def opener(request, timeout=600):
            if request.full_url.endswith("/model-registry"):
                return Response({"models": [{"key": "qwen3.5-2b-4bit-mlx-compactor", "id": "mlx/qwen35", "aliases": ["qwen3.5-2b-4bit-mlx-compactor"], "availability": "installed"}]})
            calls.append(json.loads(request.data)); return Response({"choices": [{"message": {"content": json.dumps({"facts": [], "decisions": ["bounded"], "todos": ["verify"], "issues": [], "evidence": [], "objective": "ship", "current_state": "test", "next_action": "run"})}}]})
        with tempfile.TemporaryDirectory() as directory:
            result = Compactor(GatewayAdapter("http://gateway", opener), PiMemory(directory)).compact("history")
            self.assertLessEqual(result["estimated_tokens"], 3000); self.assertTrue((Path(directory) / "active-spec.md").exists()); self.assertTrue((Path(directory) / "todos.jsonl").exists()); self.assertTrue(calls)


if __name__ == "__main__": unittest.main()
