#!/usr/bin/env python3
"""Material-event adapter fixtures: duplicate NOOP, new SHA materializes."""
from __future__ import annotations

import tempfile
from pathlib import Path

from sai_auth_event import ingest


def run_event_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        payload = {
            "event_type": "SAUL_REQUEST_CHANGES",
            "task_id": "20260813-2017-pr62-queue-ctr-code",
            "head": "a" * 40,
            "contract_revision": 3,
            "findings_digest": "cto012",
            "source": "github",
            "recommended_next_transition": "CONTRACTOR_WORK",
        }
        a1, e1 = ingest(d, payload)
        executed.add("event-first-material")
        if a1 != "material" or e1.get("status") != "MATERIAL":
            raise RuntimeError((a1, e1))
        print("SELFTEST PASS  event-first-material")
        a2, e2 = ingest(d, payload)
        executed.add("event-duplicate-noop")
        if a2 != "noop" or e2.get("status") != "NOOP":
            raise RuntimeError((a2, e2))
        print("SELFTEST PASS  event-duplicate-noop")
        payload2 = dict(payload, head="b" * 40)
        a3, e3 = ingest(d, payload2)
        executed.add("event-new-sha-material")
        if a3 != "material" or e3.get("old_state_digest") != e1.get("new_state_digest"):
            raise RuntimeError((a3, e3, e1))
        print("SELFTEST PASS  event-new-sha-material")
        a4, e4 = ingest(d, {"event_type": "NOT_A_TYPE"})
        executed.add("event-unknown-reject")
        if a4 != "reject":
            raise RuntimeError((a4, e4))
        print("SELFTEST PASS  event-unknown-reject")
    return executed


if __name__ == "__main__":
    run_event_fixtures()
    print("sai_auth_event_test: all fixtures passed")
