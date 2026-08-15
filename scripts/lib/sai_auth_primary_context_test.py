#!/usr/bin/env python3
"""Primary context fixtures: unique / none / ambiguous / no cross-contamination."""
from __future__ import annotations

import tempfile
from pathlib import Path

import sai_auth as a
from sai_auth_primary_context import (
    AMBIGUOUS_PRIMARY_CONTEXT, NO_PRIMARY_CONTEXT, load_primary_context,
)


def _git(root: Path, remote: str):
    a.git(root, "init", "-b", "main")
    a.git(root, "config", "user.email", "t@example.com")
    a.git(root, "config", "user.name", "t")
    (root / "README").write_text("x\n", encoding="utf-8")
    a.git(root, "add", "README")
    a.git(root, "commit", "-m", "init")
    a.git(root, "remote", "add", "origin", remote)


def _programs(root: Path, rows: list, contracts: dict):
    cfg = root / ".ai" / "_config"
    cfg.mkdir(parents=True)
    a.write_yaml(cfg / "primary-programs.yaml", {"programs": rows})
    for cid, meta in contracts.items():
        d = root / ".ai" / "contracts" / cid
        d.mkdir(parents=True)
        a.write_json(d / "contract.json", meta)


def run_primary_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)

        unique = td / "unique"
        unique.mkdir()
        _git(unique, "https://github.com/example/unique.git")
        _programs(unique, [
            {
                "logical_id": "alpha-primary", "kind": "primary_implementation",
                "status": "active", "pr": 7, "contract_id": "c-alpha",
            },
            {
                "logical_id": "ri-side", "kind": "runtime_intelligence",
                "status": "active", "pr": 8, "contract_id": "c-ri",
            },
        ], {
            "c-alpha": {
                "contract_id": "c-alpha", "current_revision": "v3",
                "principal": "principal-alpha",
            },
        })
        ctx, err = load_primary_context(unique)
        if err or ctx is None or ctx.get("logical_id") != "alpha-primary":
            raise RuntimeError((ctx, err))
        if ctx.get("pr") != 7 or ctx.get("contract_id") != "c-alpha":
            raise RuntimeError(ctx)
        if ctx.get("repository") != "example/unique":
            raise RuntimeError(ctx)
        if not ctx.get("head_sha") or not ctx.get("base_sha"):
            raise RuntimeError(ctx)
        executed.add("primary-unique-good")
        print("SELFTEST PASS  primary-unique-good")

        none = td / "none"
        none.mkdir()
        _git(none, "https://github.com/example/none.git")
        _programs(none, [
            {
                "logical_id": "ri-only", "kind": "runtime_intelligence",
                "status": "active", "pr": 9, "contract_id": "c-ri",
            },
        ], {})
        ctx, err = load_primary_context(none)
        if ctx is not None or err != NO_PRIMARY_CONTEXT:
            raise RuntimeError((ctx, err))
        executed.add("primary-none-bad")
        print("SELFTEST PASS  primary-none-bad")

        amb = td / "amb"
        amb.mkdir()
        _git(amb, "https://github.com/example/amb.git")
        _programs(amb, [
            {
                "logical_id": "p-one", "kind": "primary_implementation",
                "status": "active", "pr": 11, "contract_id": "c-one",
            },
            {
                "logical_id": "p-two", "kind": "primary_implementation",
                "status": "active", "pr": 12, "contract_id": "c-two",
            },
        ], {
            "c-one": {"contract_id": "c-one", "current_revision": "v1",
                      "principal": "principal-one"},
            "c-two": {"contract_id": "c-two", "current_revision": "v2",
                      "principal": "principal-two"},
        })
        ctx, err = load_primary_context(amb)
        if ctx is not None or err != AMBIGUOUS_PRIMARY_CONTEXT:
            raise RuntimeError((ctx, err))
        if ctx is not None and ctx.get("logical_id") in ("p-one", "p-two"):
            raise RuntimeError("must not silently select first active program")
        executed.add("primary-ambiguous-bad")
        print("SELFTEST PASS  primary-ambiguous-bad")

        a_ctx, a_err = load_primary_context(amb, logical_id="p-one")
        b_ctx, b_err = load_primary_context(amb, logical_id="p-two")
        if a_err or b_err:
            raise RuntimeError((a_err, b_err))
        if a_ctx is b_ctx:
            raise RuntimeError("contexts must be isolated objects")
        if a_ctx["contract_id"] == b_ctx["contract_id"]:
            raise RuntimeError("contract cross-contamination")
        if a_ctx["pr"] == b_ctx["pr"]:
            raise RuntimeError("pr cross-contamination")
        if a_ctx["event_namespace"] == b_ctx["event_namespace"]:
            raise RuntimeError("namespace cross-contamination")
        if a_ctx["principal"] == b_ctx["principal"]:
            raise RuntimeError("principal cross-contamination")
        a_ctx["pr"] = 999
        if b_ctx["pr"] == 999:
            raise RuntimeError("mutating one context leaked into the other")
        if b_ctx["logical_id"] != "p-two" or a_ctx["logical_id"] != "p-one":
            raise RuntimeError((a_ctx, b_ctx))
        executed.add("primary-no-cross-contam-good")
        print("SELFTEST PASS  primary-no-cross-contam-good")

    return executed


if __name__ == "__main__":
    run_primary_fixtures()
    print("sai_auth_primary_context_test: OK")
