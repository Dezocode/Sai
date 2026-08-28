#!/usr/bin/env python3
"""Drive slice 80 spin-off planner unit tests for sai-verify proof."""
from __future__ import annotations

import os
import subprocess
import sys


def main() -> int:
    root = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "-v",
            "prototypes/plugins/foundry/spinoff-planner-exporter/tests/test_spinoff.py",
        ],
        cwd=root,
        env=env,
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
