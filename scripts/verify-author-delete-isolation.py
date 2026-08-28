#!/usr/bin/env python3
"""Adversarial proof: deleting Author cannot break production design-check or sai-verify."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile


def main() -> int:
    root = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()
    os.chdir(root)

    for rel in ("apps/apple", "cmd/sai", "internal"):
        path = os.path.join(root, rel)
        if not os.path.isdir(path):
            continue
        proc = subprocess.run(
            ["grep", "-R", "-n", "prototypes/plugins", path],
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            sys.stderr.write("FAIL: production references prototypes/plugins\n")
            sys.stderr.write(proc.stdout)
            return 1

    author = os.path.join(root, "prototypes/plugins/author")
    if not os.path.isfile(os.path.join(author, "Package.swift")):
        sys.stderr.write("FAIL: author package missing\n")
        return 1

    tmpdir = tempfile.mkdtemp(prefix="author-del-")
    backup = os.path.join(tmpdir, "author-backup")
    try:
        shutil.move(author, backup)
        subprocess.check_call(["go", "run", "./cmd/sai-design-check"])
        subprocess.check_call(["go", "test", "./cmd/sai-verify/..."])
    finally:
        if os.path.isdir(backup):
            shutil.move(backup, author)
        shutil.rmtree(tmpdir, ignore_errors=True)

    print("PASS delete-isolation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
