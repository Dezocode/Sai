# Registry / CI-coverage helpers for scripts/lib/code-health.py.
from __future__ import annotations

import re
import shlex
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

SELF_TEST_MODES = ("synthetic", "live-pass", "none")
STATUSES = ("active", "deferred")
SKIP_FIRST = {
    "grep", "test", "echo", ":", "true", "false", "chmod", "printf",
}

NEGATIVE_FIX = re.compile(r"(?:^|-)(bad|mention-only)(?:-|$)")
POSITIVE_FIX = re.compile(r"(?:^|-)good(?:-|$)")


def collect_run_blocks(obj, acc):
    if isinstance(obj, dict):
        run = obj.get("run")
        if isinstance(run, str):
            acc.append(run)
        for v in obj.values():
            collect_run_blocks(v, acc)
    elif isinstance(obj, list):
        for item in obj:
            collect_run_blocks(item, acc)


def join_continuations(block: str) -> list[str]:
    joined, buf = [], ""
    for line in block.splitlines():
        s = line.rstrip()
        if s.endswith("\\"):
            buf += s[:-1] + " "
        else:
            joined.append(buf + s)
            buf = ""
    if buf:
        joined.append(buf)
    return joined


def strip_comment(line: str) -> str:
    in_q = None
    out = []
    for i, c in enumerate(line):
        if in_q:
            out.append(c)
            if c == in_q and (i == 0 or line[i - 1] != "\\"):
                in_q = None
            continue
        if c in "'\"":
            in_q = c
            out.append(c)
        elif c == "#":
            break
        else:
            out.append(c)
    return "".join(out).strip()


def tokenize(line: str) -> list[str]:
    s = strip_comment(line)
    if not s:
        return []
    try:
        return shlex.split(s, posix=True)
    except ValueError:
        return s.split()


def executable_invocations(run_blocks: list[str]) -> list[list[str]]:
    lines = []
    for block in run_blocks:
        for raw in join_continuations(block):
            tok = tokenize(raw)
            if not tok or tok[0] in SKIP_FIRST:
                continue
            lines.append(tok)
    return lines


def command_tokens(command: str) -> list[str]:
    return tokenize(command)


def is_prefix_invocation(line_toks: list[str], cmd_toks: list[str]) -> bool:
    if not cmd_toks or len(line_toks) < len(cmd_toks):
        return False
    return line_toks[: len(cmd_toks)] == cmd_toks


def covered_check_ids(invocations: list[list[str]], commands: dict) -> set:
    """Longest matching registered command wins per executable line."""
    covered = set()
    items = [(cid, toks) for cid, toks in commands.items() if toks]
    for line in invocations:
        best_ids, best_len = [], -1
        for cid, toks in items:
            if is_prefix_invocation(line, toks) and len(toks) >= best_len:
                if len(toks) > best_len:
                    best_ids, best_len = [cid], len(toks)
                else:
                    best_ids.append(cid)
        covered.update(best_ids)
    return covered


def workflow_invocations(wf_text: str) -> list[list[str]]:
    if yaml is None:
        raise RuntimeError("PyYAML is required")
    doc = yaml.safe_load(wf_text) or {}
    blocks = []
    collect_run_blocks(doc, blocks)
    return executable_invocations(blocks)


def same_family(a: str, b: str, families) -> bool:
    for fam in families or []:
        pat = fam.get("pattern")
        if not pat:
            continue
        rx = re.compile(pat)
        ma, mb = rx.match(a), rx.match(b)
        if not ma or not mb:
            continue
        group = fam.get("same_group")
        if group:
            if ma.group(int(group)) == mb.group(int(group)):
                return True
        else:
            return True
    return False


def validate_registry(cfg: dict, known_fixtures: set, res) -> None:
    rte = cfg.get("runtime_evaluation") or {}
    modes = tuple(rte.get("modes") or SELF_TEST_MODES)
    req_classes = set(rte.get("require_negative_fixtures_for_classes") or [])
    for check in cfg.get("checks") or []:
        cid = check.get("id", "?")
        status = check.get("status")
        st = check.get("self_test")
        klass = check.get("class")
        if status not in STATUSES:
            res.fail(f"check {cid} has invalid status {status!r}")
            continue
        if st not in modes:
            res.fail(f"check {cid} has invalid self_test {st!r} (allowed: {modes})")
            continue
        fixtures = list(check.get("fixtures") or [])
        if status == "deferred":
            if check.get("ci_marker"):
                res.fail(f"deferred check {cid} must not set ci_marker until activated")
            if st != "none":
                res.fail(f"deferred check {cid} self_test must be none")
            continue
        if st == "none":
            res.fail(f"active check {cid} has no self_test")
        if not check.get("command"):
            res.fail(f"active check {cid} missing command")
        if st == "synthetic" or klass in req_classes:
            if klass in req_classes and st != "synthetic":
                res.fail(
                    f"check {cid} class {klass} requires self_test synthetic, got {st!r}"
                )
            if st == "synthetic":
                if not fixtures:
                    res.fail(f"synthetic check {cid} missing fixtures")
                unknown = [f for f in fixtures if f not in known_fixtures]
                if unknown:
                    res.fail(f"synthetic check {cid} unknown fixtures: {unknown}")
                if klass in req_classes:
                    if not any(NEGATIVE_FIX.search(f) for f in fixtures):
                        res.fail(f"check {cid} needs a negative fixture")
                    if not any(POSITIVE_FIX.search(f) for f in fixtures):
                        res.fail(f"check {cid} needs a positive fixture")


def check_ci_coverage(root: str, cfg: dict, res, git_files, known_fixtures: set) -> None:
    validate_registry(cfg, known_fixtures, res)
    wf_rel = cfg.get("ci", {}).get("workflow", ".github/workflows/agent-audit.yml")
    wf_path = Path(root) / wf_rel
    if not wf_path.is_file():
        res.fail(f"CI workflow missing: {wf_rel}")
        return
    invocations = workflow_invocations(wf_path.read_text(encoding="utf-8"))
    commands = {}
    for check in cfg["checks"]:
        if check.get("status") != "active":
            continue
        cmd = check.get("command")
        if cmd:
            commands[check["id"]] = command_tokens(cmd)
    covered = covered_check_ids(invocations, commands)
    for check in cfg["checks"]:
        cid = check.get("id", "?")
        if check.get("status") != "active":
            if check.get("status") == "deferred":
                res.ok(f"ci-coverage deferred {cid}")
            continue
        if cid in covered:
            res.ok(f"ci-coverage {cid} executed")
        else:
            res.fail(
                f"active check {cid}: command {check.get('command')!r} "
                f"is not an executable run: step in {wf_rel}"
            )

    registered = set()
    for check in cfg["checks"]:
        cmd = check.get("command") or ""
        token = cmd.split()[0] if cmd else ""
        if token:
            registered.add(token)
    exclude = cfg.get("scan", {}).get("exclude_prefixes", [])
    for rel in git_files(root, exclude):
        if not rel.startswith("scripts/verify-"):
            continue
        if "/" in rel[len("scripts/") :]:
            continue
        if rel not in registered:
            res.fail(f"unregistered root verifier: {rel}")
        else:
            res.ok(f"registered {rel}")
