#!/usr/bin/env python3
"""Hermetic SHA-shard coverage fixtures. Names contain good/bad per registry."""
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sai_auth_review_coverage import (  # noqa: E402
    SCHEMA_MANIFEST, classify_kind, delete_completed_shard_scratch,
    derive_manifest, evaluate_coverage, prior_scratch_absent, shard_scratch_path,
)

REQUIRED = (
    "shard-manifest-complete-good",
    "shard-missing-unit-bad",
    "shard-duplicate-covering-omission-bad",
    "shard-wrong-content-digest-bad",
    "shard-stale-head-bad",
    "shard-wrong-base-digest-bad",
    "shard-synthetic-bad",
    "shard-codex-not-invoked-bad",
    "shard-binary-omitted-bad",
    "shard-rename-delete-omitted-bad",
    "shard-scratch-removed-good",
)
PROD = Path(__file__).with_name("sai_auth_review_coverage.py")


def _env():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
    })
    return env


def _git(cwd: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(cwd), "-c", "commit.gpgsign=false",
         "-c", "core.hooksPath=/dev/null", *args],
        capture_output=True, text=True, check=True, env=_env(),
        encoding="utf-8", errors="replace",
    )
    return (p.stdout or "").strip()


def _repo(parent: Path) -> tuple[Path, str, str]:
    repo = parent / "r"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    app = "\n".join(f"L{i:02d}" for i in range(50)) + "\n"
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text(app)
    (repo / "gone.txt").write_text("delete-me\n")
    (repo / "oldname.txt").write_text("rename-me\n")
    sh = repo / "mode.sh"
    sh.write_text("#!/bin/sh\necho x\n")
    (repo / "blob.bin").write_bytes(b"\x00BIN\x00AAAA")
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "ci.yml").write_text("name: ci\non: push\njobs: {}\n")
    (repo / "schema.json").write_text('{"$schema":"x","type":"object"}\n')
    (repo / "keep.txt").write_text("keep\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD")
    lines = app.splitlines()
    lines[4] = "L04-CHANGED"
    lines[40] = "L40-CHANGED"
    (repo / "src" / "app.py").write_text("\n".join(lines) + "\n")
    (repo / "gone.txt").unlink()
    _git(repo, "mv", "oldname.txt", "newname.txt")
    sh.chmod(sh.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    _git(repo, "update-index", "--chmod=+x", "mode.sh")
    (repo / "blob.bin").write_bytes(b"\x00BIN\x00BBBB")
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "name: ci\non: pull_request\njobs: {}\n"
    )
    (repo / "schema.json").write_text('{"$schema":"x","type":"object","title":"t"}\n')
    (repo / "added.txt").write_text("new-file\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "head")
    head = _git(repo, "rev-parse", "HEAD")
    return repo, base, head


def _evidence(man: dict, *, omit=(), dup=None, mutate=None, **over) -> list[dict]:
    omit = set(omit)
    docs = []
    for shard in man["shards"]:
        units = [u for u in man["units"]
                 if u["unit_id"] in shard["unit_ids"] and u["unit_id"] not in omit]
        ev_units = []
        for u in units:
            row = {
                "unit_id": u["unit_id"], "verdict": "PASS_CURRENT",
                "content_digest": u["content_digest"],
                "context_digest": u["context_digest"],
                "dependency_digest": u["dependency_digest"],
                "architecture_digest": u["architecture_digest"],
            }
            if mutate:
                mutate(row, u)
            ev_units.append(row)
            if dup and u["unit_id"] == dup:
                ev_units.append(dict(row))
        docs.append({
            "schema": "saul-shard-evidence",
            "shard_id": shard["shard_id"],
            "base_sha": man["base_sha"], "head_sha": man["head_sha"],
            "diff_digest": man["diff_digest"], "unit_root": man["unit_root"],
            "policy_digest": man["policy_digest"],
            "codex_invoked": True, "synthetic": False, "shard_verdict": "PASS",
            "units": ev_units, **over,
        })
    return docs


def _ok(name, cond, detail=""):
    if not cond:
        raise RuntimeError(f"{name} failed {detail}")
    print(f"SELFTEST PASS  {name}")
    return name


def _types(man):
    return {u["change_type"] for u in man["units"]}


def _find(man, **pred):
    out = []
    for u in man["units"]:
        if all(u.get(k) == v for k, v in pred.items()):
            out.append(u)
    return out


def run_fixtures():
    executed = set()
    src = PROD.read_text(encoding="utf-8")
    for tok in ("20260813-pr62-saul-smoke", "cursor/codebase-health-90ba",
                "lease-c3a003pr62q1", "PR #62", "pull/62"):
        if tok in src:
            raise RuntimeError(f"production hardcodes {tok}")
    with tempfile.TemporaryDirectory() as td:
        parent = Path(td)
        repo, base, head = _repo(parent)
        man = derive_manifest(repo, base, head, repository="example/fixture")
        if man.get("schema") != SCHEMA_MANIFEST or man.get("derived_by") != "trusted-git":
            raise RuntimeError("manifest not trusted-git")
        types = _types(man)
        need = {"hunk", "binary", "rename", "delete", "mode", "add"}
        if not need.issubset(types):
            raise RuntimeError(f"missing change types {need - types} have={types}")
        hunks = _find(man, path="src/app.py", change_type="hunk")
        if len(hunks) < 2:
            raise RuntimeError(f"need multi-hunk, got {len(hunks)}")
        if not _find(man, change_type="binary"):
            raise RuntimeError("binary unit missing")
        if not _find(man, change_type="rename"):
            raise RuntimeError("rename unit missing")
        if not _find(man, change_type="delete"):
            raise RuntimeError("delete unit missing")
        if not any(u.get("kind") == "workflow" for u in man["units"]):
            raise RuntimeError("workflow unit missing")
        if not any(u.get("kind") in ("schema", "config") for u in man["units"]):
            raise RuntimeError("schema/config unit missing")
        assigned = [i for s in man["shards"] for i in s["unit_ids"]]
        ids = [u["unit_id"] for u in man["units"]]
        if sorted(assigned) != sorted(ids) or len(set(assigned)) != len(assigned):
            raise RuntimeError("units not partitioned into shards")
        good = _evidence(man)
        ev = evaluate_coverage(man, good)
        executed.add(_ok(
            "shard-manifest-complete-good",
            ev["verdict"] == "PASS" and ev["convergence"] is True
            and all(v == "PASS_CURRENT" for v in ev["unit_verdicts"].values()),
            ev,
        ))

        drop = ids[0]
        miss = evaluate_coverage(man, _evidence(man, omit={drop}))
        executed.add(_ok(
            "shard-missing-unit-bad",
            miss["verdict"] == "FAIL" and drop in miss["missing_unit_ids"]
            and miss["unit_verdicts"].get(drop) == "UNREVIEWED"
            and miss["convergence"] is False,
            miss,
        ))

        other = ids[1]
        dup = evaluate_coverage(man, _evidence(man, omit={other}, dup=drop))
        executed.add(_ok(
            "shard-duplicate-covering-omission-bad",
            dup["verdict"] == "FAIL" and other in dup["missing_unit_ids"]
            and drop in dup["duplicate_unit_ids"] and dup["convergence"] is False,
            dup,
        ))

        def tamp(row, u):
            if u["unit_id"] == drop:
                row["content_digest"] = "0" * 64
        wrong = evaluate_coverage(man, _evidence(man, mutate=tamp))
        executed.add(_ok(
            "shard-wrong-content-digest-bad",
            wrong["verdict"] == "FAIL"
            and wrong["unit_verdicts"].get(drop) == "FAIL"
            and wrong["convergence"] is False,
            wrong,
        ))

        (repo / "src" / "app.py").write_text(
            (repo / "src" / "app.py").read_text().replace("L04-CHANGED", "L04-AGAIN")
        )
        _git(repo, "add", "src/app.py")
        _git(repo, "commit", "-m", "stale")
        new_head = _git(repo, "rev-parse", "HEAD")
        new_man = derive_manifest(repo, base, new_head, repository="example/fixture")
        stale = evaluate_coverage(new_man, good)
        stale_vs = set(stale["unit_verdicts"].values())
        executed.add(_ok(
            "shard-stale-head-bad",
            stale["verdict"] == "FAIL" and "STALE_CODE" in stale_vs
            and stale["convergence"] is False
            and new_head != head,
            stale,
        ))

        based = evaluate_coverage(man, _evidence(man, diff_digest="f" * 64))
        executed.add(_ok(
            "shard-wrong-base-digest-bad",
            based["verdict"] == "FAIL" and based["convergence"] is False
            and (based["reason"] == "wrong_diff_digest"
                 or any(v == "FAIL" for v in based["unit_verdicts"].values())),
            based,
        ))

        syn = evaluate_coverage(man, _evidence(man, synthetic=True))
        executed.add(_ok(
            "shard-synthetic-bad",
            syn["verdict"] == "FAIL" and syn["convergence"] is False
            and all(v == "FAIL" for v in syn["unit_verdicts"].values()),
            syn,
        ))

        noc = evaluate_coverage(man, _evidence(man, codex_invoked=False))
        executed.add(_ok(
            "shard-codex-not-invoked-bad",
            noc["verdict"] == "FAIL" and noc["convergence"] is False
            and all(v == "FAIL" for v in noc["unit_verdicts"].values()),
            noc,
        ))

        bin_ids = [u["unit_id"] for u in _find(man, change_type="binary")]
        if not bin_ids:
            raise RuntimeError("no binary unit for omit fixture")
        bomit = evaluate_coverage(man, _evidence(man, omit=set(bin_ids)))
        executed.add(_ok(
            "shard-binary-omitted-bad",
            bomit["verdict"] == "FAIL"
            and set(bin_ids) <= set(bomit["missing_unit_ids"])
            and bomit["convergence"] is False,
            bomit,
        ))

        rd = [u["unit_id"] for u in man["units"] if u["change_type"] in ("rename", "delete")]
        if len(rd) < 2:
            raise RuntimeError(f"need rename+delete units, got {rd}")
        rdomit = evaluate_coverage(man, _evidence(man, omit=set(rd)))
        executed.add(_ok(
            "shard-rename-delete-omitted-bad",
            rdomit["verdict"] == "FAIL" and set(rd) <= set(rdomit["missing_unit_ids"])
            and rdomit["convergence"] is False,
            rdomit,
        ))

        scratch = parent / "scratch"
        sids = [s["shard_id"] for s in man["shards"]]
        if len(sids) < 1:
            raise RuntimeError("need a shard for scratch")
        first, nxt = sids[0], (sids[1] if len(sids) > 1 else sids[0])
        sp = shard_scratch_path(scratch, first)
        sp.mkdir(parents=True)
        (sp / "detail.json").write_text(json.dumps({"shard_id": first}))
        gone = delete_completed_shard_scratch(scratch, first)
        ready = prior_scratch_absent(scratch, first)
        if nxt != first:
            shard_scratch_path(scratch, nxt).mkdir(parents=True)
        executed.add(_ok(
            "shard-scratch-removed-good",
            (not gone.exists()) and ready is True
            and classify_kind(".github/workflows/ci.yml") == "workflow",
            {"gone": str(gone), "ready": ready},
        ))

    missing = [n for n in REQUIRED if n not in executed]
    if missing:
        raise RuntimeError(f"fixtures not executed: {missing}")
    return executed


if __name__ == "__main__":
    n = run_fixtures()
    print(f"sai_auth_review_coverage_test: {len(n)} fixtures OK")
