"""Scan spin-off output for forbidden references to the source Sai checkout."""

from __future__ import annotations

from pathlib import Path
from typing import List

FORBIDDEN_PATTERNS = (
    "../../Sai",
    "Dezocode/Sai",
    "monaecode/Sai",
    "prototypes/plugins/",
)


def scan_forbidden_refs(out_dir: str) -> List[str]:
    root = Path(out_dir).resolve()
    hits: List[str] = []
    if not root.exists():
        return hits

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name == "PROVENANCE.json":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(root)
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in text:
                hits.append(f"{rel}: contains forbidden reference {pattern!r}")
    return hits
