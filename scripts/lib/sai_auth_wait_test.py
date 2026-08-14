#!/usr/bin/env python3
"""sai-wait wakes early on digest change and does not invoke a model."""
from __future__ import annotations

import threading
import time
from pathlib import Path
import tempfile

from sai_auth_wait import wait_loop


def run_wait_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "README").write_text("x\n")
        executed.add("wait-early-wake")
        (root / ".ai/runs/20260813-2015-pr62-queue-ceo").mkdir(parents=True)
        state = root / ".ai/runs/20260813-2015-pr62-queue-ceo/coordinator-state.json"
        state.write_text("{\"v\":1}\n")
        t = threading.Thread(target=lambda: (
            time.sleep(0.2),
            state.write_text("{\"v\":2}\n"),
        ))
        t.start()
        result = wait_loop(root, 2, chunk=0.1, include_remote=False)
        t.join()
        if result["model_invoked"] is not False:
            raise RuntimeError(result)
        if result["waited_seconds"] >= 2:
            raise RuntimeError("should wake early: %s" % result)
        if not result["woke_early"]:
            raise RuntimeError(result)
        print("SELFTEST PASS  wait-early-wake")
        executed.add("wait-no-model")
        print("SELFTEST PASS  wait-no-model")
        executed.add("wait-last-resort-other-work")
        result = wait_loop(
            root, 900, chunk=0.1, include_remote=False,
            work_exists_digest="local-work-exists",
        )
        if result.get("reason") != "other_work":
            raise RuntimeError(result)
        if not result.get("woke_early") or result.get("waited_seconds", 1) != 0:
            raise RuntimeError(result)
        if result.get("wait_is_last_resort") is not True:
            raise RuntimeError(result)
        if result.get("model_invoked") is not False:
            raise RuntimeError(result)
        print("SELFTEST PASS  wait-last-resort-other-work")
    return executed


if __name__ == "__main__":
    run_wait_fixtures()
    print("sai_auth_wait_test: OK")
