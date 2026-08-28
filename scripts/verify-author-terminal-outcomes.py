#!/usr/bin/env python3
"""Mechanical proof: Author supports Foundry terminal outcomes without architectural surgery (slice 77).

Delete: production stays green when the Author tree is removed.
Integrate: Author depends only on public SaiDesignLanguage; no production app coupling.
Spin-off: Author tree is self-contained; no checkout-root or ../../Sai refs in code.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ALLOWED_SWIFT_IMPORTS = {"SaiDesignLanguage", "SwiftUI", "Foundation", "SaiAuthor"}
FORBIDDEN_IMPORTS = {"SaiMac", "SaiIOS", "SaiFeatures", "SaiKit"}
SPM_MANIFEST_IMPORTS = {"PackageDescription"}
SPINOFF_FORBIDDEN = (
    "../../Sai",
    "Dezocode/Sai",
    "monaecode/Sai",
    ".git/",
)
SPINOFF_SCAN_SUFFIXES = {".swift", ".sh"}


def repo_root() -> Path:
    out = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()
    return Path(out)


def spinoff_scan_paths(author: Path) -> list[Path]:
    paths: list[Path] = []
    pkg = author / "Package.swift"
    if pkg.is_file():
        paths.append(pkg)
    for path in author.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix in SPINOFF_SCAN_SUFFIXES:
            paths.append(path)
    return paths


def check_delete(root: Path) -> None:
    script = root / "scripts" / "verify-author-delete-isolation.py"
    if not script.is_file():
        raise SystemExit("FAIL delete: missing scripts/verify-author-delete-isolation.py")
    subprocess.check_call([sys.executable, str(script)])


def check_integrate(author: Path) -> None:
    pkg = (author / "Package.swift").read_text()
    if 'product(name: "SaiDesignLanguage"' not in pkg:
        raise SystemExit("FAIL integrate: Package.swift must depend on SaiDesignLanguage only")
    if re.search(r'product\(name:\s*"(SaiMac|SaiIOS|SaiFeatures)"', pkg):
        raise SystemExit("FAIL integrate: production app products must not be dependencies")
    if "prototypes/plugins" in pkg:
        raise SystemExit("FAIL integrate: Package.swift must not reference prototype lane paths")

    for swift in author.rglob("*.swift"):
        if swift.name == "Package.swift" or "tests" in swift.parts:
            continue
        rel = swift.relative_to(author)
        text = swift.read_text()
        for line in text.splitlines():
            m = re.match(r"^\s*import\s+(\w+)", line)
            if not m:
                continue
            name = m.group(1)
            if name in FORBIDDEN_IMPORTS:
                raise SystemExit(f"FAIL integrate: forbidden import {name} in {rel}")
            if name == "SaiAuthor" and rel.parts[0] not in ("SaiAuthorMac", "SaiAuthorIOS"):
                raise SystemExit(f"FAIL integrate: SaiAuthor import only allowed in platform apps, not {rel}")
            if name not in ALLOWED_SWIFT_IMPORTS:
                raise SystemExit(f"FAIL integrate: unexpected import {name} in {rel}")

    print("PASS integrate-readiness")


def check_spinoff(author: Path) -> None:
    pkg = (author / "Package.swift").read_text()
    if not re.search(r'path:\s*"\.\./', pkg):
        raise SystemExit("FAIL spin-off: Package.swift must use relative SaiKit path")
    if "github.com" in pkg:
        raise SystemExit("FAIL spin-off: Package.swift must not pin remote URLs")

    for path in author.rglob("*"):
        if path.is_symlink():
            raise SystemExit(f"FAIL spin-off: symlink not allowed: {path.relative_to(author)}")

    for path in spinoff_scan_paths(author):
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(author)
        for needle in SPINOFF_FORBIDDEN:
            if needle in text:
                raise SystemExit(f"FAIL spin-off: {needle!r} in {rel}")

    rel_sources = [p for p in author.rglob("*.swift") if p.is_file()]
    if len(rel_sources) < 5:
        raise SystemExit("FAIL spin-off: expected full Author shell sources in-tree")

    print("PASS spin-off-readiness")


def main() -> int:
    root = repo_root()
    author = root / "prototypes" / "plugins" / "author"
    if not (author / "Package.swift").is_file():
        sys.stderr.write("FAIL: author package missing\n")
        return 1

    check_delete(root)
    check_integrate(author)
    check_spinoff(author)
    print("PASS terminal-outcomes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
