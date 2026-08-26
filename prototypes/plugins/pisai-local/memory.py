"""Bounded Pi memory and gateway-mediated compaction for the prototype."""
from __future__ import annotations

import json, time, uuid
from pathlib import Path
from typing import Any
from gateway_adapter import GatewayAdapter


MAX_SPEC_TOKENS = 3000
CHUNK_CHARS = 48000


def estimate_tokens(value: Any) -> int:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return len(text) // 4


def chunks(history: str, size: int = CHUNK_CHARS) -> list[str]:
    history = history.strip()
    return [history[i:i + size] for i in range(0, len(history), size)] or [""]


def normalize_spec(value: dict[str, Any]) -> dict[str, Any]:
    fields = ("objective", "current_state", "decisions", "todos", "issues", "evidence", "next_action")
    spec = {field: value.get(field, [] if field in {"decisions", "todos", "issues", "evidence"} else "") for field in fields}
    for field in ("decisions", "todos", "issues", "evidence"):
        if not isinstance(spec[field], list): spec[field] = [spec[field]] if spec[field] else []
    return spec


class PiMemory:
    def __init__(self, root: str | Path): self.root = Path(root).expanduser()
    def append(self, ledger: str, item: Any, request_id: str | None = None) -> None:
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        path = self.root / f"{ledger}.jsonl"
        with path.open("a", encoding="utf-8") as handle: handle.write(json.dumps({"ts": time.time(), "request_id": request_id, "item": item}, ensure_ascii=False) + "\n")
        path.chmod(0o600)
    def write_spec(self, spec: dict[str, Any]) -> None:
        spec = normalize_spec(spec)
        rendered = json.dumps(spec, ensure_ascii=False)
        if estimate_tokens(rendered) > MAX_SPEC_TOKENS: raise ValueError("active spec exceeds 3000 estimated tokens")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700); temporary = self.root / "active-spec.md.tmp"; target = self.root / "active-spec.md"
        temporary.write_text("# PiS AI Active Spec\n\n" + rendered + "\n", encoding="utf-8"); temporary.chmod(0o600); temporary.replace(target)


def response_json(data: bytes) -> dict[str, Any]:
    payload = json.loads(data); content = payload["choices"][0]["message"]["content"]
    if isinstance(content, list): content = "".join(str(item.get("text", item)) for item in content if isinstance(item, dict))
    start, end = str(content).find("{"), str(content).rfind("}")
    if start < 0 or end <= start: raise ValueError("compactor response was not JSON")
    return json.loads(str(content)[start:end + 1])


class Compactor:
    def __init__(self, adapter: GatewayAdapter, memory: PiMemory): self.adapter, self.memory = adapter, memory
    def compact(self, history: str, current_spec: dict[str, Any] | None = None) -> dict[str, Any]:
        request_id = "compact-" + uuid.uuid4().hex[:16]; summaries = []
        for chunk in chunks(history):
            status, _, data = self.adapter.complete({"task": "compact", "request_id": request_id, "messages": [{"role": "user", "content": "Return JSON only with keys facts, decisions, todos, issues, evidence. Do not invent facts.\n" + chunk}]})
            if status >= 300: raise RuntimeError(f"compactor gateway returned {status}")
            summaries.append(response_json(data))
        status, _, data = self.adapter.complete({"task": "compact", "request_id": request_id, "messages": [{"role": "user", "content": "Return JSON only with keys objective, current_state, decisions, todos, issues, evidence, next_action. Keep the active spec under 3000 estimated tokens.\n" + json.dumps({"current_spec": current_spec or {}, "summaries": summaries})}]})
        if status >= 300: raise RuntimeError(f"compactor gateway returned {status}")
        spec = normalize_spec(response_json(data)); self.memory.write_spec(spec)
        for ledger in ("decisions", "todos", "issues", "evidence"):
            for item in spec[ledger]: self.memory.append(ledger, item, request_id)
        self.memory.append("compaction-events", {"chunks": len(summaries), "estimated_tokens": estimate_tokens(spec)}, request_id)
        return {"request_id": request_id, "spec": spec, "chunks": len(summaries), "estimated_tokens": estimate_tokens(spec)}
