"""Pi-side adapter for the existing Mac gateway; never starts a second server."""
from __future__ import annotations

import json, os, uuid
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class GatewayAdapter:
    """Selects a registered role and delegates lifecycle ownership to Mac."""

    def __init__(self, base_url: str | None = None, opener=urlopen):
        self.base_url = (base_url or os.environ.get("PISAI_GATEWAY_BASE_URL", "http://127.0.0.1:11437")).rstrip("/")
        self.models = {"coding": os.environ.get("PISAI_CODING_MODEL", "qwen3.8-ridge-gguf"), "vision": os.environ.get("PISAI_VISION_MODEL", "ornith-1.5-9b-vision"), "compact": os.environ.get("PISAI_COMPACTOR_MODEL", "qwen3.5-2b-4bit-mlx-compactor")}
        self.opener = opener

    @staticmethod
    def has_image(value: Any) -> bool:
        if isinstance(value, dict): return value.get("type") in {"image", "image_url", "input_image"} or any(GatewayAdapter.has_image(v) for v in value.values())
        return isinstance(value, list) and any(GatewayAdapter.has_image(v) for v in value)

    def role(self, body: dict[str, Any], hook_task: str | None = None) -> str:
        task = (hook_task or body.get("task") or "").lower()
        if task in self.models: return task
        return "vision" if self.has_image(body.get("messages", [])) else "coding"

    def get_json(self, path: str) -> dict[str, Any]:
        try:
            with self.opener(Request(self.base_url + path, headers={"Accept": "application/json"}), timeout=10) as response:
                return json.loads(response.read() or b"{}")
        except (HTTPError, URLError) as error: raise RuntimeError(f"gateway verification failed: {error}") from error

    def status(self) -> dict[str, Any]:
        """Read the existing proxy's public runtime proof; no mutation."""
        return self.get_json("/proxy/runtime")

    def model_for(self, role: str) -> tuple[str, dict[str, Any]]:
        registry = self.get_json("/model-registry")
        wanted = self.models[role]
        profiles = registry.get("models", [])
        profile = next((item for item in profiles if item.get("key") == wanted or item.get("id") == wanted or wanted in item.get("aliases", [])), None)
        if profile is None:
            raise RuntimeError(f"role {role} is not registered in the Mac catalog")
        availability = str(profile.get("availability", "configured")).lower()
        if availability in {"not-installed", "planned", "unavailable", "disabled", "missing"}:
            raise RuntimeError(f"role {role} is unavailable: {availability}")
        return wanted, profile

    def complete(self, body: dict[str, Any], hook_task: str | None = None, session_id: str | None = None) -> tuple[int, dict[str, str], bytes]:
        request_id = str(body.get("request_id") or uuid.uuid4()); role = self.role(body, hook_task); selected_model, profile = self.model_for(role); outgoing = dict(body); outgoing["model"] = selected_model
        headers = {"Content-Type": "application/json", "x-pisai-task": role, "x-pisai-route-id": f"{role}:{request_id}", "x-pisai-request-id": request_id, "x-pisai-telemetry-id": request_id, "x-pisai-selected-model": outgoing["model"], "x-ollama-hook-contract": "ollama-pisai-hooks.v1", "x-pi-noos-schema": "noos-compatible.v1"}
        try:
            with self.opener(Request(self.base_url + "/v1/chat/completions", data=json.dumps(outgoing).encode(), headers=headers, method="POST"), timeout=600) as response:
                return response.status, dict(response.headers), response.read()
        except HTTPError as error: return error.code, dict(error.headers), error.read()
        except URLError as error: raise RuntimeError(f"gateway request failed: {error}") from error


def main() -> None:
    print(json.dumps(GatewayAdapter().status(), indent=2))


if __name__ == "__main__": main()
