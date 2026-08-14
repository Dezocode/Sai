#!/usr/bin/env python3
"""Hermetic proofs that bootstrap binds HEAD and never runs candidate executables."""
from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

from sai_auth_bootstrap import (
    CANDIDATE_HEAD_MISMATCH,
    CANDIDATE_NOT_GIT,
    CANDIDATE_SHA_UNRESOLVED,
    MUTABLE_REF,
    TRUSTED_REVIEWER_UNAVAILABLE,
    BootstrapError,
    assert_candidate_head,
    require_immutable_sha,
    require_trusted_executables,
)

ROOT = Path(__file__).resolve().parents[2]
OPERATOR = ROOT / "scripts" / "saul-hostinger-bootstrap-review"
FAKE_SHA = "c" * 40
MAL_INVOKE = "#!/bin/sh\necho cand-invoke >> \"$MARKER_DIR/marker-cand\"\n"
MAL_ATTEST = "#!/bin/sh\necho cand-attest >> \"$MARKER_DIR/marker-cand\"\n"
TRU_INVOKE = "#!/bin/sh\necho trusted-invoke >> \"$MARKER_DIR/marker-trusted\"\n"
TRU_ATTEST = "#!/bin/sh\necho trusted-attest >> \"$MARKER_DIR/marker-trusted\"\nexit 0\n"


def _git_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_AUTHOR_NAME"] = "t"
    env["GIT_AUTHOR_EMAIL"] = "t@example.com"
    env["GIT_COMMITTER_NAME"] = "t"
    env["GIT_COMMITTER_EMAIL"] = "t@example.com"
    return env


def _git(cwd: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(cwd), "-c", "commit.gpgsign=false",
         "-c", "core.hooksPath=/dev/null", *args],
        capture_output=True, text=True, check=True, env=_git_env(),
    )
    return p.stdout.strip()


def _repo(parent: Path, name: str = "cand") -> tuple[Path, str]:
    root = parent / name
    root.mkdir()
    (root / "README").write_text("one\n")
    _git(root, "init")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "init")
    return root, _git(root, "rev-parse", "HEAD")


def _exec(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


def _catch(fn, code):
    try:
        fn()
    except BootstrapError as e:
        if e.code != code:
            raise RuntimeError((code, e.code, e.machine))
        return e
    raise RuntimeError(f"expected {code}")


def _host_env(tmp: Path, cand: Path, trusted: Path | None, extra=None):
    key = tmp / "attest.pem"
    key.write_text("not-a-real-key\n")
    env = dict(os.environ)
    env["SAI_SAUL_BOOTSTRAP"] = "1"
    env["SAI_SAUL_ATTEST_KEY"] = str(key)
    env["SAI_CANDIDATE_TREE"] = str(cand)
    if trusted is not None:
        env["SAI_TRUSTED_TREE"] = str(trusted)
    else:
        env.pop("SAI_TRUSTED_TREE", None)
    env["MARKER_DIR"] = str(tmp)
    if extra:
        env.update(extra)
    return env


def _run_op(env, args):
    return subprocess.run(
        [sys.executable, str(OPERATOR), *args],
        capture_output=True, text=True, env=env,
    )


def run_bootstrap_fixtures():
    executed = set()
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        cand, sha1 = _repo(tmp)
        (cand / "README").write_text("two\n")
        _git(cand, "add", "-A")
        _git(cand, "commit", "-m", "second")
        sha = _git(cand, "rev-parse", "HEAD")

        executed.add("head-match-accepted")
        got = assert_candidate_head(cand, sha)
        if got != sha.lower():
            raise RuntimeError((got, sha))
        mixed = sha.upper()
        if assert_candidate_head(cand, mixed) != sha.lower():
            raise RuntimeError("mixed-case sha not normalized")
        print("SELFTEST PASS  head-match-accepted")

        executed.add("head-mismatch-both-shas")
        err = _catch(lambda: assert_candidate_head(cand, sha1), CANDIDATE_HEAD_MISMATCH)
        if sha.lower() not in err.machine or sha1.lower() not in err.machine:
            raise RuntimeError(err.machine)
        if f"expected={sha1.lower()}" not in err.machine:
            raise RuntimeError(err.machine)
        if f"actual={sha.lower()}" not in err.machine:
            raise RuntimeError(err.machine)
        print("SELFTEST PASS  head-mismatch-both-shas")

        executed.add("candidate-not-git")
        nogit = tmp / "nogit"
        nogit.mkdir()
        _catch(lambda: assert_candidate_head(nogit, sha), CANDIDATE_NOT_GIT)
        _catch(lambda: assert_candidate_head(tmp / "missing", sha), CANDIDATE_NOT_GIT)
        print("SELFTEST PASS  candidate-not-git")

        executed.add("sha-unresolved")
        _catch(lambda: assert_candidate_head(cand, FAKE_SHA), CANDIDATE_SHA_UNRESOLVED)
        print("SELFTEST PASS  sha-unresolved")

        executed.add("head-drift-after-capture")
        prior = sha
        (cand / "README").write_text("three\n")
        _git(cand, "add", "-A")
        _git(cand, "commit", "-m", "advance")
        new_sha = _git(cand, "rev-parse", "HEAD")
        err = _catch(lambda: assert_candidate_head(cand, prior), CANDIDATE_HEAD_MISMATCH)
        if prior.lower() not in err.machine or new_sha.lower() not in err.machine:
            raise RuntimeError(err.machine)
        assert_candidate_head(cand, new_sha)
        print("SELFTEST PASS  head-drift-after-capture")

        executed.add("mutable-ref-rejected")
        for ref in ("HEAD", "head", "@", "main", "refs/heads/x", "refs/heads/main",
                    "origin/main", "master", "", None, sha[:12], "HEAD^{commit}"):
            try:
                require_immutable_sha(ref)
            except BootstrapError as e:
                if e.code != MUTABLE_REF:
                    raise RuntimeError((ref, e.code))
            else:
                raise RuntimeError(f"accepted mutable {ref!r}")
        print("SELFTEST PASS  mutable-ref-rejected")

        markers = tmp
        cand_scripts = cand / "scripts"
        _exec(cand_scripts / "invoke-saul-review", MAL_INVOKE)
        _exec(cand_scripts / "saul-attest", MAL_ATTEST)

        executed.add("trusted-tree-missing-candidate-not-run")
        missing = tmp / "no-trusted"
        _catch(lambda: require_trusted_executables(missing), TRUSTED_REVIEWER_UNAVAILABLE)
        if (markers / "marker-cand").exists():
            raise RuntimeError("candidate invoke ran when trusted missing")
        print("SELFTEST PASS  trusted-tree-missing-candidate-not-run")

        trusted = tmp / "trusted"
        (trusted / "scripts").mkdir(parents=True)
        executed.add("trusted-invoke-missing-blocked")
        _exec(trusted / "scripts" / "saul-attest", TRU_ATTEST)
        _catch(lambda: require_trusted_executables(trusted), TRUSTED_REVIEWER_UNAVAILABLE)
        if (markers / "marker-cand").exists() or (markers / "marker-trusted").exists():
            raise RuntimeError("scripts ran when trusted invoke missing")
        print("SELFTEST PASS  trusted-invoke-missing-blocked")

        executed.add("trusted-attest-missing-blocked")
        (trusted / "scripts" / "saul-attest").unlink()
        _exec(trusted / "scripts" / "invoke-saul-review", TRU_INVOKE)
        _catch(lambda: require_trusted_executables(trusted), TRUSTED_REVIEWER_UNAVAILABLE)
        if (markers / "marker-cand").exists():
            raise RuntimeError("candidate ran when trusted attest missing")
        print("SELFTEST PASS  trusted-attest-missing-blocked")

        executed.add("trusted-pair-only-executes")
        _exec(trusted / "scripts" / "invoke-saul-review", TRU_INVOKE)
        _exec(trusted / "scripts" / "saul-attest", TRU_ATTEST)
        invoke, attest = require_trusted_executables(trusted)
        if not str(invoke).startswith(str(trusted.resolve())):
            raise RuntimeError(invoke)
        env = dict(os.environ)
        env["MARKER_DIR"] = str(markers)
        subprocess.run([str(invoke)], check=True, env=env)
        subprocess.run([str(attest)], check=True, env=env)
        trusted_mark = (markers / "marker-trusted").read_text()
        if "trusted-invoke" not in trusted_mark or "trusted-attest" not in trusted_mark:
            raise RuntimeError(trusted_mark)
        if (markers / "marker-cand").exists():
            raise RuntimeError("candidate markers appeared")
        print("SELFTEST PASS  trusted-pair-only-executes")

        executed.add("symlink-escape-blocked")
        escaped = tmp / "escaped-trusted"
        (escaped / "scripts").mkdir(parents=True)
        os.symlink(cand_scripts / "invoke-saul-review", escaped / "scripts" / "invoke-saul-review")
        _exec(escaped / "scripts" / "saul-attest", TRU_ATTEST)
        _catch(lambda: require_trusted_executables(escaped), TRUSTED_REVIEWER_UNAVAILABLE)
        if (markers / "marker-cand").exists():
            raise RuntimeError("symlink escape executed candidate")
        print("SELFTEST PASS  symlink-escape-blocked")

        executed.add("operator-self-test-not-hostinger")
        r = _run_op(dict(os.environ), ["--self-test"])
        if r.returncode != 2 or "NOT_HOSTINGER_SAUL" not in (r.stderr or ""):
            raise RuntimeError((r.returncode, r.stderr, r.stdout))
        print("SELFTEST PASS  operator-self-test-not-hostinger")

        executed.add("operator-no-candidate-fallback")
        env = _host_env(tmp, cand, None)
        r = _run_op(env, ["--head", new_sha])
        if r.returncode != 1 or TRUSTED_REVIEWER_UNAVAILABLE not in (r.stderr or ""):
            raise RuntimeError((r.returncode, r.stderr))
        if r.returncode == 2:
            raise RuntimeError("trusted-missing must not be NOT_HOSTINGER_SAUL")
        if (markers / "marker-cand").exists():
            raise RuntimeError("operator ran candidate fallback")
        print("SELFTEST PASS  operator-no-candidate-fallback")

        executed.add("operator-mismatch-fail-closed")
        env = _host_env(tmp, cand, trusted)
        r = _run_op(env, ["--head", prior])
        if r.returncode != 1 or CANDIDATE_HEAD_MISMATCH not in (r.stderr or ""):
            raise RuntimeError((r.returncode, r.stderr))
        if prior.lower() not in r.stderr or new_sha.lower() not in r.stderr:
            raise RuntimeError(r.stderr)
        if (markers / "marker-cand").exists():
            raise RuntimeError("mismatch invoked candidate")
        print("SELFTEST PASS  operator-mismatch-fail-closed")

        executed.add("operator-requires-candidate-env")
        env = _host_env(tmp, cand, trusted)
        del env["SAI_CANDIDATE_TREE"]
        r = _run_op(env, ["--head", new_sha])
        if r.returncode != 1 or CANDIDATE_NOT_GIT not in (r.stderr or ""):
            raise RuntimeError((r.returncode, r.stderr))
        print("SELFTEST PASS  operator-requires-candidate-env")

        executed.add("operator-mutable-head-rejected")
        env = _host_env(tmp, cand, trusted)
        r = _run_op(env, ["--head", "HEAD"])
        if r.returncode != 1 or MUTABLE_REF not in (r.stderr or ""):
            raise RuntimeError((r.returncode, r.stderr))
        print("SELFTEST PASS  operator-mutable-head-rejected")

        executed.add("operator-trusted-invoke-only")
        (markers / "marker-trusted").unlink(missing_ok=True)
        env = _host_env(tmp, cand, trusted)
        r = _run_op(env, ["--head", new_sha, "--out", str(tmp / "review.yaml")])
        if (markers / "marker-cand").exists():
            raise RuntimeError("operator executed candidate scripts")
        trusted_mark = (markers / "marker-trusted").read_text() if (markers / "marker-trusted").is_file() else ""
        if "trusted-invoke" not in trusted_mark:
            raise RuntimeError((r.returncode, r.stderr, r.stdout, trusted_mark))
        print("SELFTEST PASS  operator-trusted-invoke-only")

        executed.add("operator-source-has-no-fallback")
        src = OPERATOR.read_text(encoding="utf-8")
        if "invoke = root" in src or "attest = root" in src:
            raise RuntimeError("fallback assignment still present")
        if 'root / "scripts" / "invoke-saul-review"' in src:
            raise RuntimeError("candidate invoke fallback path present")
        if 'root / "scripts" / "saul-attest"' in src:
            raise RuntimeError("candidate attest fallback path present")
        print("SELFTEST PASS  operator-source-has-no-fallback")

    return executed


if __name__ == "__main__":
    n = run_bootstrap_fixtures()
    print(f"sai_auth_bootstrap_test: {len(n)} fixtures executed")
