#!/usr/bin/env python3
"""Validate one agent event dict against agent-event.schema.json (stdlib only).

Loads .ai/shared/schemas/agent-event.schema.json at startup and validates
events by walking the schema — required fields, enums, patterns, formats,
and additionalProperties are all derived from the loaded schema.

Usage:
  validate-agent-event.py [--self-test]
  echo '{"event_id":...}' | validate-agent-event.py
  validate-agent-event.py event.json

Exit 0 when valid; prints errors to stderr and exits 1 when invalid.
With --self-test, runs positive + negative regression cases and exits non-zero
if any case misbehaves.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA_REL = ".ai/shared/schemas/agent-event.schema.json"


def _repo_root() -> Path:
    here = Path(__file__).resolve().parent
    for parent in [here, *here.parents]:
        candidate = parent / SCHEMA_REL
        if candidate.is_file():
            return parent
    return Path.cwd()


def _load_schema() -> dict[str, Any]:
    path = _repo_root() / SCHEMA_REL
    if not path.is_file():
        raise FileNotFoundError(f"schema not found: {path}")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


SCHEMA = _load_schema()


def _fail(errors: list[str], path: str, msg: str) -> None:
    errors.append(f"{path}: {msg}")


def _parse_rfc3339(value: str) -> bool:
    """Return True when value is a parseable RFC3339 / ISO8601 date-time."""
    candidate = value
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        datetime.fromisoformat(candidate)
    except ValueError:
        return False
    return True


def _validate_schema(value: Any, schema: dict[str, Any], path: str, errors: list[str]) -> None:
    schema_type = schema.get("type")

    if schema_type == "object":
        if not isinstance(value, dict):
            _fail(errors, path, "must be a JSON object")
            return
        props = schema.get("properties", {})
        allowed = set(props)
        if schema.get("additionalProperties") is False:
            extra = set(value) - allowed
            if extra:
                _fail(errors, path, f"additional properties not allowed: {sorted(extra)}")
        for key in schema.get("required", []):
            if key not in value:
                _fail(errors, path, f"missing required field '{key}'")
        for key, subschema in props.items():
            if key in value:
                _validate_schema(value[key], subschema, f"{path}.{key}", errors)
        return

    if schema_type == "array":
        if not isinstance(value, list):
            _fail(errors, path, "must be an array")
            return
        item_schema = schema.get("items", {})
        for i, item in enumerate(value):
            _validate_schema(item, item_schema, f"{path}[{i}]", errors)
        return

    if schema_type == "string":
        if not isinstance(value, str):
            _fail(errors, path, "must be a string")
            return
        min_len = schema.get("minLength")
        if min_len is not None and len(value) < min_len:
            _fail(errors, path, f"must be at least {min_len} characters")
        pattern = schema.get("pattern")
        if pattern and not re.fullmatch(pattern, value):
            _fail(errors, path, "does not match required pattern")
        fmt = schema.get("format")
        if fmt == "date-time" and not _parse_rfc3339(value):
            _fail(errors, path, "must be a valid RFC3339 date-time")
        enum = schema.get("enum")
        if enum is not None and value not in enum:
            _fail(errors, path, f"must be one of {sorted(enum)}")
        return

    if schema_type is not None:
        _fail(errors, path, f"unsupported schema type '{schema_type}'")


def validate_event(doc: Any, *, path: str = "$") -> list[str]:
    errors: list[str] = []
    _validate_schema(doc, SCHEMA, path, errors)
    return errors


def _schema_pattern(field: str) -> str | None:
    props = SCHEMA.get("properties", {})
    field_schema = props.get(field, {})
    return field_schema.get("pattern")


def _valid_sample() -> dict[str, Any]:
    return {
        "event_id": "20260730-0313-ceo-protocol-verify-ceo:1785380000000000000",
        "event_type": "VERIFY",
        "task_id": "20260730-0313-ceo-protocol-verify-ceo",
        "actor": "ceo",
        "repository": "Dezocode/Sai",
        "timestamp": "2026-07-30T03:13:00Z",
        "purpose": "schema validator self-test positive case",
        "result": "pass",
    }


def self_test() -> int:
    failures = 0

    if not (_repo_root() / SCHEMA_REL).is_file():
        print(f"SELF-TEST FAIL: schema missing at {SCHEMA_REL}", file=sys.stderr)
        return 1

    if validate_event(_valid_sample()):
        print("SELF-TEST FAIL: valid sample rejected", file=sys.stderr)
        failures += 1

    offset_sample = dict(_valid_sample(), timestamp="2026-07-30T03:13:00+00:00")
    if validate_event(offset_sample):
        print("SELF-TEST FAIL: RFC3339 offset timestamp rejected", file=sys.stderr)
        failures += 1

    base_sha_pattern = _schema_pattern("base_sha")
    commit_sha_pattern = _schema_pattern("commit_sha")
    if not base_sha_pattern or base_sha_pattern != commit_sha_pattern:
        print("SELF-TEST FAIL: schema drift — base_sha/commit_sha patterns differ or missing", file=sys.stderr)
        failures += 1

    negative_cases = [
        ({}, "empty object"),
        ({"event_id": "short", "event_type": "VERIFY", "task_id": "20260730-0313-x-ceo",
          "actor": "ceo", "repository": "Dezocode/Sai", "timestamp": "2026-07-30T03:13:00Z",
          "purpose": "p", "result": "r"}, "event_id too short"),
        (dict(_valid_sample(), event_type="NOT_A_TYPE"), "invalid event_type enum"),
        (dict(_valid_sample(), repository="not-a-repo"), "invalid repository pattern"),
        (dict(_valid_sample(), task_id="bad-task-id"), "invalid task_id pattern"),
        (dict(_valid_sample(), agent_id="slack-mcp-shape"), "additional property agent_id"),
        (dict(_valid_sample(), purpose=None), "null purpose"),
        ({k: v for k, v in _valid_sample().items() if k != "result"}, "missing result"),
        (dict(_valid_sample(), timestamp="not-a-date"), "invalid timestamp"),
    ]

    for doc, label in negative_cases:
        if not validate_event(doc):
            print(f"SELF-TEST FAIL: negative case accepted ({label})", file=sys.stderr)
            failures += 1

    if failures:
        print(f"validate-agent-event: SELF-TEST FAILED ({failures} problem(s))", file=sys.stderr)
        return 1
    print(f"validate-agent-event: SELF-TEST OK (schema loaded from {SCHEMA_REL})")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()

    docs: list[Any] = []
    if len(argv) > 1 and argv[1] != "-":
        with open(argv[1], encoding="utf-8") as fh:
            docs.append(json.load(fh))
    else:
        raw = sys.stdin.read()
        if not raw.strip():
            print("validate-agent-event: no input", file=sys.stderr)
            return 2
        docs.append(json.loads(raw))

    failed = 0
    for i, doc in enumerate(docs, 1):
        path = f"event[{i}]" if len(docs) > 1 else "$"
        for err in validate_event(doc, path=path):
            print(f"FAIL {err}", file=sys.stderr)
            failed += 1
    if failed:
        print(f"validate-agent-event: FAILED ({failed} problem(s))", file=sys.stderr)
        return 1
    print("validate-agent-event: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
