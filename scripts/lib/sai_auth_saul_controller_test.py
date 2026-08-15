#!/usr/bin/env python3
"""Controller wake fixtures U/V. Prints SELFTEST PASS  <fixture>."""
from __future__ import annotations

from sai_auth_saul_controller import (
    default_convergence_predicate, process_events,
)


def _convergence_pred(event: dict) -> bool:
    return bool(event.get("technical_convergence"))


def run_controller_fixtures():
    executed = set()

    executed.add("sai-wake-convergence-once-good")
    wakes = []
    events = [{"type": "SHARD_PROGRESS", "i": i, "technical_convergence": True}
              for i in range(50)]
    events.append({
        "type": "TECHNICAL_CONVERGENCE",
        "technical_convergence": True,
    })
    n = process_events(
        events, wake_sai=wakes.append, convergence_predicate=_convergence_pred,
    )
    if n != 1 or len(wakes) != 1:
        raise RuntimeError(("sai-wake-convergence-once-good", n, len(wakes)))
    if wakes[0].get("type") != "TECHNICAL_CONVERGENCE":
        raise RuntimeError(wakes[0])
    print("SELFTEST PASS  sai-wake-convergence-once-good")

    executed.add("sai-wake-request-changes-zero-good")
    wakes = []
    n = process_events(
        [{"type": "SAUL_REQUEST_CHANGES", "disposition": "REQUEST_CHANGES"}],
        wake_sai=wakes.append,
        convergence_predicate=_convergence_pred,
    )
    if n != 0 or wakes:
        raise RuntimeError(("sai-wake-request-changes-zero-good", n, wakes))
    n_closed = process_events(
        [{"type": "TECHNICAL_CONVERGENCE", "technical_convergence": True}],
        wake_sai=wakes.append,
        convergence_predicate=default_convergence_predicate,
    )
    if n_closed != 0:
        raise RuntimeError("default predicate must be fail-closed")
    print("SELFTEST PASS  sai-wake-request-changes-zero-good")
    return executed


if __name__ == "__main__":
    run_controller_fixtures()
    print("sai_auth_saul_controller_test: OK")
