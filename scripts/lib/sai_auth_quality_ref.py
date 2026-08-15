#!/usr/bin/env python3
"""Decision-0005 domain-aware quality-reference mapping verifier.

Fails if the mapping is missing, rust is treated as universal, or a parallel
rust/go/swift/openssf quality subsystem appears. Does not copy frameworks.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sai_auth as a  # noqa: E402

MAP_REL = ".ai/contracts/20260813-pr62-saul-smoke/quality-reference-mapping.yaml"
ALLOWED = {"IMPLEMENTED", "NOT_APPLICABLE", "BLOCKER", "DEFERRED_NONBLOCKING"}
SUBSYS = re.compile(r"(^|/)((rust|go|golang|swift|openssf)-quality)(/|$)", re.I)
CHECKOUT_PIN = re.compile(r"actions/checkout@([0-9a-f]{40})\b")
CHECKOUT_FLOAT = re.compile(r"actions/checkout@v\d")
RUST_UNIVERSAL = re.compile(
    r"rust-lang/rust.*(universal|product template|all domains)|universal product template",
    re.I,
)


def load_mapping(root) -> dict:
    return a.read_yaml(Path(root) / MAP_REL) or {}


def mapping_problems(root, data=None) -> list:
    data = data if data is not None else load_mapping(root)
    fails = []
    path = Path(root) / MAP_REL
    if not path.is_file() or not data:
        return ["mapping_missing"]
    if data.get("one_system") not in ("Decision-0005", "0005"):
        fails.append("one_system_not_0005")
    if data.get("do_not_copy_frameworks") is not True:
        fails.append("do_not_copy_frameworks")
    rust_ok = False
    for ref in data.get("references") or []:
        rid = str(ref.get("id") or "")
        domain = str(ref.get("domain") or "")
        if rid == "rust-lang/rust":
            rust_ok = "control-plane" in domain and "universal" not in domain
            if ref.get("role") == "universal" or "universal" in domain:
                fails.append("rust_universal")
        st = str(ref.get("status") or "")
        if st and st not in ALLOWED:
            fails.append(f"ref_status:{rid}:{st}")
    if not rust_ok:
        fails.append("rust_not_control_plane")
    blob = path.read_text(encoding="utf-8")
    if RUST_UNIVERSAL.search(blob) and "not a universal" not in blob.lower():
        fails.append("rust_universal_text")
    for prop in data.get("properties") or []:
        st = str(prop.get("status") or "")
        if st not in ALLOWED:
            fails.append(f"prop_status:{prop.get('id')}:{st}")
        if st == "DEFERRED_NONBLOCKING" and not prop.get("reason"):
            fails.append(f"deferred_no_reason:{prop.get('id')}")
        if st == "NOT_APPLICABLE" and not prop.get("reason"):
            fails.append(f"na_no_reason:{prop.get('id')}")
        det = str(prop.get("detector") or "")
        if det in ("pending-contractor", "", "None"):
            fails.append(f"detector_pending:{prop.get('id')}")
    sel = data.get("select_by_domain") or {}
    go = sel.get("go-core-backend") or []
    swift = sel.get("swift-swiftui") or []
    if "rust-lang/rust" in go or "rust-lang/rust" in swift:
        fails.append("rust_applied_as_product_template")
    return fails


def subsystem_hits(root) -> list:
    hits = []
    try:
        files = a.git(root, "ls-files").stdout.splitlines()
    except Exception:
        files = []
    for rel in files:
        if SUBSYS.search(rel):
            hits.append(rel)
        base = Path(rel).name
        if re.match(r"verify-(rust|go|golang|swift|openssf)-quality$", base):
            hits.append(rel)
    return hits


def checkout_unpinned(root) -> list:
    hits = []
    for rel in (
        ".github/workflows/saul-cto-review.default-branch.yml",
        ".github/workflows/agent-audit.yml",
    ):
        p = Path(root) / rel
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8")
        if CHECKOUT_FLOAT.search(text) and not CHECKOUT_PIN.search(text):
            hits.append(rel)
        for m in re.finditer(r"uses:\s*actions/checkout@(\S+)", text):
            token = m.group(1)
            if not re.fullmatch(r"[0-9a-f]{40}", token):
                hits.append(f"{rel}:{token}")
    return hits


def evaluate(root) -> list:
    return mapping_problems(root) + subsystem_hits(root) + checkout_unpinned(root)


def cmd(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        from sai_auth_quality_ref_test import run_quality_ref_fixtures
        n = run_quality_ref_fixtures()
        print(f"verify-saul-quality-reference self-test: {len(n)} fixtures executed")
        return 0
    root = a.toplevel() or os.getcwd()
    fails = evaluate(root)
    if fails:
        print("FAIL", " ".join(fails))
        return 1
    print("PASS quality-reference-mapping")
    return 0


if __name__ == "__main__":
    raise SystemExit(cmd())
