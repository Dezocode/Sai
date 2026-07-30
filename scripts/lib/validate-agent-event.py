#!/usr/bin/env python3
"""Validate one agent event dict against agent-event.schema.json (stdlib only).

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
from typing import Any

SCHEMA_PATH = ".ai/shared/schemas/agent-event.schema.json"

EVENT_TYPES = {
    "INTAKE", "PLAN", "WORKTREE", "CHANGE", "COMMIT", "PUSH", "PR",
    "VERIFY", "SYNC", "CONFLICT", "BLOCKED", "HANDOFF", "BYPASS",
    "CONTRACT", "CONTRACT_REVIEW", "PERSONA_GATE",
}
DRIVE_STATUSES = {"pending", "synced", "failed", "diverged", "not-applicable"}
TASK_ID = re.compile(r"^[0-9]{8}-[0-9]{4}-[a-z0-9][a-z0-9-]*$")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA = re.compile(r"^[0-9a-f]{7,40}$")
ISO8601_Z = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$"
)

ALLOWED_TOP = {
    "event_id", "event_type", "task_id", "actor", "repository", "branch",
    "worktree", "base_sha", "commit_sha", "timestamp", "purpose",
    "justification", "scope", "result", "verification", "git_refs",
    "drive_status", "drive_checksum", "risks", "review_gate",
    "parent_event_id", "contract_id", "project_slug",
}
ALLOWED_GIT_REFS = {"commit_url", "push_range", "pr_url"}


def _fail(errors: list[str], path: str, msg: str) -> None:
    errors.append(f"{path}: {msg}")


def _check_str(errors: list[str], path: str, value: Any, *, min_len: int = 0) -> None:
    if not isinstance(value, str):
        _fail(errors, path, "must be a string")
        return
    if len(value) < min_len:
        _fail(errors, path, f"must be at least {min_len} characters")


def validate_event(doc: Any, *, path: str = "$") -> list[str]:
    errors: list[str] = []
    if not isinstance(doc, dict):
        return [f"{path}: must be a JSON object"]

    extra = set(doc) - ALLOWED_TOP
    if extra:
        _fail(errors, path, f"additional properties not allowed: {sorted(extra)}")

    required = (
        "event_id", "event_type", "task_id", "actor", "repository",
        "timestamp", "purpose", "result",
    )
    for key in required:
        if key not in doc:
            _fail(errors, path, f"missing required field '{key}'")

    if "event_id" in doc:
        _check_str(errors, f"{path}.event_id", doc["event_id"], min_len=8)

    if "event_type" in doc:
        _check_str(errors, f"{path}.event_type", doc["event_type"])
        if isinstance(doc["event_type"], str) and doc["event_type"] not in EVENT_TYPES:
            _fail(errors, f"{path}.event_type", f"must be one of {sorted(EVENT_TYPES)}")

    if "task_id" in doc:
        _check_str(errors, f"{path}.task_id", doc["task_id"])
        if isinstance(doc["task_id"], str) and not TASK_ID.match(doc["task_id"]):
            _fail(errors, f"{path}.task_id", "does not match task-id grammar")

    if "actor" in doc:
        _check_str(errors, f"{path}.actor", doc["actor"])

    if "repository" in doc:
        _check_str(errors, f"{path}.repository", doc["repository"])
        if isinstance(doc["repository"], str) and not REPOSITORY.match(doc["repository"]):
            _fail(errors, f"{path}.repository", "must match owner/repo pattern")

    for key in ("branch", "worktree", "purpose", "justification", "result",
                "verification", "drive_checksum", "risks", "review_gate",
                "parent_event_id", "contract_id", "project_slug"):
        if key in doc:
            _check_str(errors, f"{path}.{key}", doc[key])

    for key in ("base_sha", "commit_sha"):
        if key in doc:
            _check_str(errors, f"{path}.{key}", doc[key])
            if isinstance(doc[key], str) and not SHA.match(doc[key]):
                _fail(errors, f"{path}.{key}", "must be a git sha (7-40 hex chars)")

    if "timestamp" in doc:
        _check_str(errors, f"{path}.timestamp", doc["timestamp"])
        if isinstance(doc["timestamp"], str):
            if not ISO8601_Z.match(doc["timestamp"]):
                _fail(errors, f"{path}.timestamp", "must be ISO8601 UTC (…Z)")
            else:
                ts = doc["timestamp"].rstrip("Z")
                if "." in ts:
                    ts = ts.split(".")[0]
                try:
                    datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    _fail(errors, f"{path}.timestamp", "invalid date-time")

    if "scope" in doc:
        scope = doc["scope"]
        if not isinstance(scope, list):
            _fail(errors, f"{path}.scope", "must be an array")
        else:
            for i, item in enumerate(scope):
                if not isinstance(item, str):
                    _fail(errors, f"{path}.scope[{i}]", "must be a string")

    if "drive_status" in doc:
        _check_str(errors, f"{path}.drive_status", doc["drive_status"])
        if isinstance(doc["drive_status"], str) and doc["drive_status"] not in DRIVE_STATUSES:
            _fail(errors, f"{path}.drive_status", f"must be one of {sorted(DRIVE_STATUSES)}")

    if "git_refs" in doc:
        refs = doc["git_refs"]
        if not isinstance(refs, dict):
            _fail(errors, f"{path}.git_refs", "must be an object")
        else:
            ref_extra = set(refs) - ALLOWED_GIT_REFS
            if ref_extra:
                _fail(errors, f"{path}.git_refs", f"additional properties not allowed: {sorted(ref_extra)}")
            for key in refs:
                _check_str(errors, f"{path}.git_refs.{key}", refs[key])

    return errors


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

    if validate_event(_valid_sample()):
        print("SELF-TEST FAIL: valid sample rejected", file=sys.stderr)
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
    ]

    for doc, label in negative_cases:
        if not validate_event(doc):
            print(f"SELF-TEST FAIL: negative case accepted ({label})", file=sys.stderr)
            failures += 1

    if failures:
        print(f"validate-agent-event: SELF-TEST FAILED ({failures} problem(s))", file=sys.stderr)
        return 1
    print("validate-agent-event: SELF-TEST OK")
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
