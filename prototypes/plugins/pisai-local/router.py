#!/usr/bin/env python3
"""Reference Mac-side PiS AI router; prototype-only and stdlib-only."""
from __future__ import annotations

import argparse, json, os, re, subprocess, threading, time, uuid
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROLES = ("coding", "vision", "compact")


def has_image(value: Any) -> bool:
    if isinstance(value, dict):
        return value.get("type") in {"image", "image_url", "input_image"} or any(has_image(v) for v in value.values())
    return isinstance(value, list) and any(has_image(v) for v in value)


def select_role(body: dict[str, Any], hook_task: str | None = None) -> str:
    role = (hook_task or body.get("task") or "").lower()
    if role in ROLES:
        return role
    return "vision" if has_image(body.get("messages", [])) else "coding"


def estimate_tokens(value: Any) -> int:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return len(text) // 4


@dataclass(frozen=True)
class Config:
    gateway: str
    models: dict[str, str]
    context_tokens: int
    block_swap_ratio: float
    block_ram_ratio: float
    memory_dir: Path

    @classmethod
    def from_env(cls) -> "Config":
        memory = os.environ.get("PISAI_MEMORY_DIR", os.path.join(os.environ.get("PI_CODING_AGENT_DIR", "~/.pi/agent"), "memory", "pisai"))
        return cls(
            os.environ.get("PISAI_GATEWAY_BASE_URL", "http://127.0.0.1:11437").rstrip("/"),
            {"coding": os.environ.get("PISAI_CODING_MODEL", "qwen38-ridge"), "vision": os.environ.get("PISAI_VISION_MODEL", "ornith-vision"), "compact": os.environ.get("PISAI_COMPACTOR_MODEL", "qwen35-2b-compactor")},
            int(os.environ.get("PISAI_CONTEXT_TOKENS", "32768")),
            float(os.environ.get("PISAI_BLOCK_SWAP_RATIO", "0.85")),
            float(os.environ.get("PISAI_BLOCK_RAM_RATIO", "0.97")),
            Path(memory).expanduser(),
        )


class JsonBackend:
    def __init__(self, base_url: str): self.base_url = base_url.rstrip("/")

    def call(self, method: str, path: str, payload: Any = None, timeout: int = 60) -> tuple[int, dict[str, str], bytes]:
        data = None if payload is None else json.dumps(payload).encode()
        try:
            with urlopen(Request(self.base_url + path, data=data, method=method, headers={"Content-Type": "application/json"} if data else {}), timeout=timeout) as response:
                return response.status, dict(response.headers), response.read()
        except HTTPError as error: return error.code, dict(error.headers), error.read()
        except URLError as error: raise RuntimeError(f"gateway unavailable: {error.reason}") from error


class Memory:
    def __init__(self, path: Path): self.path, self.lock = path, threading.RLock()

    def append(self, name: str, record: dict[str, Any]) -> None:
        self.path.mkdir(parents=True, exist_ok=True, mode=0o700); os.chmod(self.path, 0o700)
        with self.lock, (self.path / name).open("a", encoding="utf-8") as file: file.write(json.dumps(record, sort_keys=True) + "\n")
        os.chmod(self.path / name, 0o600)

    def read(self, name: str) -> list[dict[str, Any]]:
        file = self.path / name
        if not file.exists(): return []
        with self.lock, file.open(encoding="utf-8") as handle: return [json.loads(line) for line in handle if line.strip()]


class Router:
    def __init__(self, config: Config | None = None, backend: Any | None = None, resource_probe: Callable[[], dict[str, Any]] | None = None):
        self.config = config or Config.from_env(); self.backend = backend or JsonBackend(self.config.gateway); self.memory = Memory(self.config.memory_dir)
        self.resource_probe = resource_probe or self.resources; self.residency_lock = threading.RLock()

    @staticmethod
    def resources() -> dict[str, Any]:
        try:
            raw = subprocess.check_output(["sysctl", "-n", "vm.swapusage"], text=True, timeout=2)
            values = {key: float(value[:-1]) for key, value in re.findall(r"(total|used|free) = ([0-9.]+M)", raw)}
            total = values.get("total", 0)
            return {"available": bool(total), "swap_used_ratio": values.get("used", 0) / total if total else None, "swap_total_mb": total, "swap_used_mb": values.get("used", 0)}
        except (OSError, ValueError, subprocess.SubprocessError): return {"available": False}

    def safe(self) -> None:
        snapshot = self.resource_probe(); swap = snapshot.get("swap_used_ratio"); ram = snapshot.get("ram_used_ratio")
        if swap is not None and swap >= self.config.block_swap_ratio: raise RuntimeError("swap safety gate blocked route transition")
        if ram is not None and ram >= self.config.block_ram_ratio: raise RuntimeError("RAM safety gate blocked route transition")

    def resident(self, role: str) -> dict[str, Any]:
        model = self.config.models[role]
        with self.residency_lock:
            self.safe(); status, _, raw = self.backend.call("GET", "/api/ps")
            if status != 200: raise RuntimeError("resident-state API verification failed")
            loaded = json.loads(raw or b"{}").get("models", [])
            for item in loaded:
                if item.get("name") != model: self.backend.call("POST", "/api/generate", {"model": item.get("name"), "keep_alive": 0})
            status, _, _ = self.backend.call("POST", "/api/generate", {"model": model, "prompt": " ", "stream": False, "keep_alive": "15m", "options": {"num_ctx": self.config.context_tokens, "num_predict": 1}})
            if status >= 300: raise RuntimeError(f"model warm-up failed: {status}")
            status, _, raw = self.backend.call("GET", "/api/ps")
            observed = next((item for item in json.loads(raw or b"{}").get("models", []) if item.get("name") == model), None)
            if status != 200 or observed is None: raise RuntimeError("selected/resident model verification failed")
            context = observed.get("context_length", observed.get("context"))
            if context is not None and int(context) != self.config.context_tokens: raise RuntimeError("resident context verification failed")
            return {"selected_model": model, "resident_model": observed.get("name"), "context_tokens": self.config.context_tokens, "resources": self.resource_probe()}

    def chat(self, body: dict[str, Any], hook_task: str | None = None) -> tuple[int, dict[str, str], bytes]:
        request_id = str(body.get("request_id") or uuid.uuid4()); role = select_role(body, hook_task); proof = self.resident(role)
        outgoing = dict(body); outgoing["model"] = proof["selected_model"]
        status, headers, data = self.backend.call("POST", "/v1/chat/completions", outgoing, timeout=600)
        event = {"schema": "ollama-pisai-hooks.v1", "noos_schema": "noos-compatible.v1", "noos_revision": 2, "event": "route_response", "request_id": request_id, "role": role, "status": status, **proof}
        self.memory.append("events.jsonl", event)
        headers.update({"x-pisai-request-id": request_id, "x-pisai-route": role, "x-pisai-model": proof["selected_model"], "x-pisai-telemetry-id": request_id})
        return status, headers, data


class Handler(BaseHTTPRequestHandler):
    router = Router()
    protocol_version = "HTTP/1.1"
    def log_message(self, *_: Any) -> None: pass
    def body(self) -> dict[str, Any]: return json.loads(self.rfile.read(int(self.headers.get("content-length", "0"))) or b"{}")
    def send_json(self, status: int, value: Any, headers: dict[str, str] | None = None) -> None:
        data = value if isinstance(value, bytes) else json.dumps(value).encode(); self.send_response(status); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(data)))
        for key, val in (headers or {}).items():
            if key.lower() not in {"content-length", "connection", "transfer-encoding"}: self.send_header(key, val)
        self.end_headers(); self.wfile.write(data)
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/healthz": self.send_json(200, {"ok": True, "service": "pisai-local-router"}); return
            if path == "/v1/pisai/status": self.send_json(200, {"ok": True, "models": self.router.config.models, "context_tokens": self.router.config.context_tokens, "resources": self.router.resource_probe(), "single_resident": True}); return
            if path == "/v1/pisai/memory/issues": self.send_json(200, {"issues": self.router.memory.read("issues.jsonl")}); return
            self.send_json(404, {"error": "not found"})
        except Exception as error: self.send_json(503, {"error": str(error)})
    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = self.body()
            if path == "/v1/chat/completions":
                status, headers, data = self.router.chat(body, self.headers.get("x-pisai-task")); self.send_json(status, data, headers); return
            if path == "/v1/pisai/memory/issue":
                body.setdefault("issue_id", "ISSUE-" + uuid.uuid4().hex[:12]); body.setdefault("status", "open"); body.setdefault("ts", time.time())
                if not body.get("summary"): raise ValueError("summary is required")
                self.router.memory.append("issues.jsonl", body); self.send_json(201, body); return
            self.send_json(404, {"error": "not found"})
        except Exception as error: self.send_json(503, {"error": str(error)})


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--host", default=os.environ.get("PISAI_ROUTER_HOST", "127.0.0.1")); parser.add_argument("--port", type=int, default=int(os.environ.get("PISAI_ROUTER_PORT", "11437"))); args = parser.parse_args()
    print(f"PiS AI local router listening on http://{args.host}:{args.port}", flush=True); ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__": main()
