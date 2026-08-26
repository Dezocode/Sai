#!/usr/bin/env python3
"""Read-only proof for the existing Mac gateway; never loads or unloads models."""
import argparse, json, sys
from pathlib import Path
from urllib.request import Request, urlopen


def get(base, path):
    with urlopen(Request(base.rstrip("/") + path, headers={"Accept": "application/json"}), timeout=5) as response:
        return response.status, json.loads(response.read() or b"{}")


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--base", default="http://127.0.0.1:11437"); parser.add_argument("--require-routes", action="store_true"); args = parser.parse_args()
    health_status, health = get(args.base, "/proxy/health")
    runtime_status, runtime = get(args.base, "/proxy/runtime")
    models_status, models = get(args.base, "/v1/models")
    registry = runtime.get("registry", {}); routes = registry.get("routes") or {}
    result = {"base": args.base, "health_status": health_status, "runtime_status": runtime_status, "models_status": models_status, "active_model": runtime.get("activeModel"), "active_backend": runtime.get("activeBackend"), "context_window": runtime.get("activeProfile", {}).get("contextWindow"), "route_keys": sorted(routes), "model_count": len(models.get("data", [])), "read_only": True}
    print(json.dumps(result, indent=2, sort_keys=True))
    required = health_status == runtime_status == models_status == 200 and result["context_window"] == 32768
    if args.require_routes: required = required and set(routes) == {"coding", "vision", "compact"}
    return 0 if required else 2


if __name__ == "__main__": sys.exit(main())
