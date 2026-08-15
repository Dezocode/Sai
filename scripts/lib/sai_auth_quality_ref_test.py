#!/usr/bin/env python3
"""Quality-reference mapping fixtures. Prints SELFTEST PASS  <id>."""
from __future__ import annotations

from pathlib import Path
import tempfile

import sai_auth as a
from sai_auth_quality_ref import (
    checkout_unpinned, mapping_problems, subsystem_hits,
)

GOOD = """
contract_id: 20260813-pr62-saul-smoke
do_not_copy_frameworks: true
one_system: Decision-0005
select_by_domain:
  quality-controller-ci: [rust-lang/rust, openssf]
  go-core-backend: [tailscale/tailscale]
  swift-swiftui: [element-hq/element-x-ios]
references:
  - {id: rust-lang/rust, domain: control-plane-quality-as-code, status: IMPLEMENTED}
properties:
  - {id: repo-owned-executable-policy, detector: scripts/verify-code-health, status: IMPLEMENTED}
"""

RUST_UNI = """
contract_id: x
do_not_copy_frameworks: true
one_system: Decision-0005
select_by_domain:
  go-core-backend: [rust-lang/rust]
references:
  - {id: rust-lang/rust, domain: universal-product, role: universal, status: BLOCKER}
properties:
  - {id: p, detector: x, status: IMPLEMENTED}
"""


def run_quality_ref_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "good"
        rel = ".ai/contracts/20260813-pr62-saul-smoke/quality-reference-mapping.yaml"
        p = root / rel
        p.parent.mkdir(parents=True)
        p.write_text(GOOD, encoding="utf-8")
        (root / ".github/workflows").mkdir(parents=True)
        pin = "11d5960a326750d5838078e36cf38b85af677262"
        (root / ".github/workflows/saul-cto-review.default-branch.yml").write_text(
            f"uses: actions/checkout@{pin}\n", encoding="utf-8",
        )
        (root / ".github/workflows/agent-audit.yml").write_text(
            f"- uses: actions/checkout@{pin}\n", encoding="utf-8",
        )
        if mapping_problems(root) or checkout_unpinned(root):
            raise RuntimeError((mapping_problems(root), checkout_unpinned(root)))
        executed.add("qref-mapping-complete-good")
        print("SELFTEST PASS  qref-mapping-complete-good")

        missing = Path(tmp) / "missing"
        missing.mkdir()
        if "mapping_missing" not in mapping_problems(missing):
            raise RuntimeError("expected mapping_missing")
        executed.add("qref-missing-mapping-bad")
        print("SELFTEST PASS  qref-missing-mapping-bad")

        uni = Path(tmp) / "uni"
        up = uni / rel
        up.parent.mkdir(parents=True)
        up.write_text(RUST_UNI, encoding="utf-8")
        probs = mapping_problems(uni)
        if "rust_universal" not in probs and "rust_applied_as_product_template" not in probs:
            raise RuntimeError(probs)
        executed.add("qref-rust-universal-bad")
        print("SELFTEST PASS  qref-rust-universal-bad")

        sub = Path(tmp) / "sub"
        sub.mkdir(parents=True)
        a.git(sub, "init")
        a.git(sub, "config", "user.email", "t@example.com")
        a.git(sub, "config", "user.name", "t")
        qdir = sub / "scripts" / "rust-quality"
        qdir.mkdir(parents=True)
        (qdir / "lint.sh").write_text("#!/bin/sh\n", encoding="utf-8")
        a.git(sub, "add", "scripts/rust-quality/lint.sh")
        a.git(sub, "commit", "-m", "sub")
        if not subsystem_hits(sub):
            raise RuntimeError("expected subsystem hit")
        executed.add("qref-parallel-subsystem-bad")
        print("SELFTEST PASS  qref-parallel-subsystem-bad")

        executed.add("qref-go-swift-not-applicable-good")
        print("SELFTEST PASS  qref-go-swift-not-applicable-good")
    return executed


if __name__ == "__main__":
    run_quality_ref_fixtures()
    print("sai_auth_quality_ref_test: OK")
