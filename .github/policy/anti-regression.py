#!/usr/bin/env python3
"""Trusted anti-regression policy for repository-controlled behavior.

The policy is executed from the trusted base revision and evaluates the exact
candidate revision. Candidate source may be exercised only as an unprivileged,
credential-free system under test. Verdicts come from this trusted file.

Protected repository-controlled outcomes:
- all JSON remains parseable;
- no new obvious credential material appears;
- OpenClaw remains loopback-only by default;
- connection state cannot claim connected without valid evidence;
- the line-budget and anti-regression constitutions remain enforceable;
- scaffold/path controls and contract review remain fail-closed;
- contract shell authorization remains least-privilege;
- registered agents remain operationally configured.

External service availability (for example Slack or Cursor MCP uptime) is outside
GitHub CI and must be verified by the runtime that owns that service.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass


PRIVATE_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bghp_[A-Za-z0-9]{36}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
)
TELEGRAM_RE = re.compile(
    r"^https://(?:t\.me|telegram\.me)/[A-Za-z0-9_+-]+(?:\?start=[A-Za-z0-9_+-]+)?/?$",
    re.I,
)
SLACK_RE = re.compile(
    r"^https://[a-z0-9-]+\.slack\.com/archives/[A-Z0-9]+/p[0-9]+"
    r"(?:\?thread_ts=[0-9.]+)?(?:&cid=[A-Z0-9]+)?$",
    re.I,
)
INVALID = {"", "—", "-", "pending", "n/a", "na", "none", "null", "tbd", "todo"}


@dataclass
class Result:
    name: str
    ok: bool
    detail: str = ""


class Policy:
    def __init__(self, trusted: pathlib.Path, candidate: pathlib.Path) -> None:
        self.trusted = trusted.resolve()
        self.candidate = candidate.resolve()
        self.results: list[Result] = []

    def record(self, name: str, ok: bool, detail: str = "") -> bool:
        self.results.append(Result(name, ok, detail.strip()))
        return ok

    @staticmethod
    def clean_env() -> dict[str, str]:
        keep = {"PATH", "HOME", "LANG", "LC_ALL", "TMPDIR"}
        env = {k: v for k, v in os.environ.items() if k in keep}
        env.update(
            {
                "SAI_CI_STRICT_CONTRACTS": "1",
                "SAI_CI_REQUIRE_SDK_SMOKE": "0",
                "CI": "true",
            }
        )
        return env

    def command(
        self,
        name: str,
        argv: list[str],
        *,
        cwd: pathlib.Path | None = None,
        timeout: int = 45,
    ) -> bool:
        try:
            cp = subprocess.run(
                argv,
                cwd=str(cwd or self.candidate),
                env=self.clean_env(),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return self.record(name, False, str(exc))
        output = cp.stdout[-5000:] if cp.stdout else ""
        return self.record(name, cp.returncode == 0, output)

    def json_validity(self, root: pathlib.Path | None = None) -> bool:
        root = (root or self.candidate).resolve()
        failures: list[str] = []
        for path in root.rglob("*.json"):
            if ".git" in path.parts:
                continue
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                failures.append(f"{path.relative_to(root)}: {exc}")
        return self.record("JSON remains machine-readable", not failures, "\n".join(failures))

    @staticmethod
    def secret_hits(root: pathlib.Path) -> set[tuple[str, str]]:
        hits: set[tuple[str, str]] = set()
        for path in root.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for line in text.splitlines():
                if "re.compile(" in line:
                    continue
                if any(pattern.search(line) for pattern in PRIVATE_PATTERNS):
                    hits.add((str(path.relative_to(root)), line.strip()))
        return hits

    def no_new_secrets(self, candidate: pathlib.Path | None = None) -> bool:
        candidate = (candidate or self.candidate).resolve()
        new_hits = self.secret_hits(candidate) - self.secret_hits(self.trusted)
        detail = "\n".join(sorted(path for path, _ in new_hits))
        return self.record("No new credential material", not new_hits, detail)

    @staticmethod
    def json_documents(root: pathlib.Path):
        for path in root.rglob("*.json"):
            if ".git" in path.parts:
                continue
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                continue
            yield path, value

    def gateway_loopback(self, root: pathlib.Path | None = None) -> bool:
        root = (root or self.candidate).resolve()
        found = False
        for path, doc in self.json_documents(root):
            if not isinstance(doc, dict):
                continue
            gateway = doc.get("gateway")
            ingest = doc.get("dashboard_ingest")
            if not isinstance(gateway, dict) or not isinstance(ingest, dict):
                continue
            if "host" not in gateway and "bind_policy" not in gateway:
                continue
            found = True
            remote = gateway.get("remote_access") or {}
            forbidden = remote.get("forbidden_without_documentation") or []
            if (
                gateway.get("host") == "127.0.0.1"
                and gateway.get("bind_policy") == "loopback_default"
                and ingest.get("bind") == "127.0.0.1"
                and "0.0.0.0" in forbidden
            ):
                return self.record(
                    "OpenClaw remains loopback-only",
                    True,
                    str(path.relative_to(root)),
                )
        return self.record(
            "OpenClaw remains loopback-only",
            False,
            "gateway contract missing" if not found else "no safe gateway contract found",
        )

    @staticmethod
    def parse_markdown_tables(root: pathlib.Path):
        for path in root.rglob("*.md"):
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            headers: list[str] = []
            for line in lines:
                if not line.startswith("|"):
                    continue
                cols = [c.strip() for c in line.split("|")[1:-1]]
                if not cols:
                    continue
                if "agent_id" in cols and "connected" in cols:
                    headers = cols
                    continue
                if not headers or all(set(c) <= {"-", ":"} for c in cols if c):
                    continue
                if len(cols) < len(headers):
                    cols += [""] * (len(headers) - len(cols))
                yield path, dict(zip(headers, cols))

    def connection_truth(self, root: pathlib.Path | None = None) -> bool:
        root = (root or self.candidate).resolve()
        failures: list[str] = []
        rows = 0
        for path, row in self.parse_markdown_tables(root):
            if "telegram_dm_link" not in row or "slack_intro_permalink" not in row:
                continue
            rows += 1
            connected = row.get("connected", "").strip().lower()
            if connected != "yes":
                continue
            tg = row.get("telegram_dm_link", "").strip()
            slack = row.get("slack_intro_permalink", "").strip()
            habbo = row.get("habbo_presence", "").strip().lower()
            if not TELEGRAM_RE.fullmatch(tg):
                failures.append(f"{path}: connected=yes with invalid Telegram link")
            if not SLACK_RE.fullmatch(slack):
                failures.append(f"{path}: connected=yes with invalid Slack permalink")
            if habbo != "connected":
                failures.append(f"{path}: connected=yes without connected Habbo presence")
        return self.record(
            "Connection state remains fail-closed",
            rows > 0 and not failures,
            "\n".join(failures) if failures else f"rows inspected: {rows}",
        )

    @staticmethod
    def workflow_texts(root: pathlib.Path):
        wf = root / ".github" / "workflows"
        if not wf.is_dir():
            return []
        texts = []
        for path in sorted([*wf.glob("*.yml"), *wf.glob("*.yaml")]):
            try:
                texts.append((path, path.read_text(encoding="utf-8")))
            except (OSError, UnicodeDecodeError):
                pass
        return texts

    @staticmethod
    def named_workflow(root: pathlib.Path, name: str) -> tuple[pathlib.Path, str] | None:
        for path, text in Policy.workflow_texts(root):
            if re.search(rf"(?m)^name:\s*['\"]?{re.escape(name)}['\"]?\s*$", text):
                return path, text
        return None

    def constitution(self, root: pathlib.Path | None = None) -> bool:
        root = (root or self.candidate).resolve()
        failures: list[str] = []
        budget = self.named_workflow(root, "PR line budget")
        anti = self.named_workflow(root, "Anti-regression")
        if not budget:
            failures.append("PR line budget workflow missing")
        else:
            _, text = budget
            checks = {
                "uses pull_request_target": "pull_request_target:" in text,
                "budget is 1200 additions": bool(re.search(r'MAX_ADDITIONS:\s*["\']?1200["\']?', text)),
                "threshold is additions only": "additions > MAX_ADDITIONS" in text,
                "deletions are not thresholded": "changed_lines" not in text and "additions + deletions" not in text,
                "no candidate checkout": "actions/checkout" not in text,
            }
            failures.extend(f"budget: {k}" for k, ok in checks.items() if not ok)
        if not anti:
            failures.append("Anti-regression workflow missing")
        else:
            _, text = anti
            checks = {
                "uses pull_request_target": "pull_request_target:" in text,
                "binds exact base SHA": "github.event.pull_request.base.sha" in text,
                "binds exact head SHA": "github.event.pull_request.head.sha" in text,
                "does not persist checkout credentials": text.count("persist-credentials: false") >= 2,
                "uses trusted policy": "trusted/.github/policy/anti-regression.py" in text,
                "does not expose write permission": not bool(re.search(r"(?m)^\s*(contents|checks|pull-requests|actions|statuses):\s*write\s*$", text)),
            }
            failures.extend(f"anti-regression: {k}" for k, ok in checks.items() if not ok)
        return self.record("CI constitution remains enforceable", not failures, "\n".join(failures))

    def scaffold_behavior(self, candidate: pathlib.Path | None = None) -> bool:
        candidate = (candidate or self.candidate).resolve()
        verifier = self.trusted / "scripts" / "verify-scaffold-safety"
        return self.command(
            "Scaffolding remains fail-closed and contract review remains truthful",
            ["bash", str(verifier)],
            cwd=candidate,
        )

    def shell_authorization(self, candidate: pathlib.Path | None = None) -> bool:
        candidate = (candidate or self.candidate).resolve()
        verifier = self.trusted / "scripts" / "verify-contract-shell-allowlist"
        return self.command(
            "Contract shell authorization remains least-privilege",
            ["bash", str(verifier)],
            cwd=candidate,
        )

    def agent_operability(self, candidate: pathlib.Path | None = None) -> bool:
        candidate = (candidate or self.candidate).resolve()
        verifier = self.trusted / "scripts" / "verify-agent-setup"
        return self.command(
            "Registered agents remain operationally configured",
            ["bash", str(verifier), str(candidate)],
            cwd=candidate,
        )

    def feature_contract(self) -> bool:
        kernel = self.trusted / "cmd" / "sai-verify"; ok = True
        if not kernel.is_dir():
            self.record("Feature map preservation", True, "bootstrap N/A: trusted base predates sai-verify; nothing to preserve")
        else:
            env = self.clean_env()
            for k in ("HOME", "GOROOT", "GOPATH", "GOCACHE", "GOMODCACHE"):
                if k in os.environ:
                    env[k] = os.environ[k]
            bin_path = pathlib.Path(tempfile.mkdtemp(prefix="sai-verify-")) / "sai-verify"
            built = subprocess.run(["go", "build", "-o", str(bin_path), "./cmd/sai-verify"], cwd=str(self.trusted), env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120, check=False)
            if built.returncode != 0:
                return self.record("Feature map preservation", False, (built.stdout or "")[-4000:])
            ok = self.command("Protected BASE feature IDs are preserved", [str(bin_path), "preserve", "--base", str(self.trusted), "--head", str(self.candidate), "--root", str(self.candidate)], timeout=60)
        try:
            doc = json.loads((self.candidate / ".cursor" / "hooks.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self.record("Required pre/post verification hooks", False, "hooks.json missing/invalid")
            return False
        def covered(name: str) -> bool:
            for h in (doc.get("hooks") or {}).get(name) or []:
                if "sai-verify" in str(h.get("command", "")) and (h.get("matcher") in (".*", "^.*$") or name not in ("preToolUse", "postToolUse", "postToolUseFailure", "beforeShellExecution", "afterShellExecution", "beforeReadFile", "afterFileEdit", "subagentStart", "subagentStop")) and h.get("failClosed") is True:
                    return True
            return False
        need = ("sessionStart", "sessionEnd", "preToolUse", "postToolUse", "postToolUseFailure", "subagentStart", "subagentStop", "beforeShellExecution", "afterShellExecution", "beforeMCPExecution", "afterMCPExecution", "beforeReadFile", "afterFileEdit", "beforeSubmitPrompt", "preCompact", "stop", "afterAgentResponse", "afterAgentThought", "workspaceOpen")
        hook_ok = all(covered(n) for n in need)
        has_kernel = (self.candidate / "cmd" / "sai-verify").is_dir()
        def src_of(root):
            return "".join(p.read_text(encoding="utf-8", errors="replace") for p in sorted((root / "cmd" / "sai-verify").rglob("*.go")) if not p.name.endswith("_test.go"))
        def calls(s):
            return tuple(re.findall(r'exec\.Command(?:Context)?\s*\((?:[^()]|\([^()]*\))*\)', re.sub(r'\s+', ' ', s)))
        cs = src_of(self.candidate); chunk=lambda s,n: (lambda i: "" if i<0 else re.sub(r"\s+"," ", s[i:(j if (j:=s.find("\nfunc ",i+1))>0 else len(s))]))(s.find("func "+n))
        want = calls(src_of(self.trusted)) if (self.trusted / "cmd" / "sai-verify").is_dir() else ('exec.CommandContext(ctx, argv[0], argv[1:]...)', 'exec.Command("git", append([]string{"-c", "safe.directory=*", "-C", dir}, args...)...)')
        ts = src_of(self.trusted) if (self.trusted / "cmd" / "sai-verify").is_dir() else ""
        shell_ok = has_kernel and calls(cs) == want and "os.StartProcess" not in cs and "syscall.Exec" not in cs and "syscall.ForkExec" not in cs and "func init(" not in cs and "plugin.Open" not in cs and not re.search(r'(?:^|[^:])=\s*func\s*\(', cs) and not re.search(r'(?:^|[\n;( ])\s*(?!import\b)(?:\w+|\.)\s+"os/exec"', cs) and not re.search(r'(?:^|[\n;( ])\s*(?!import\b)(?:\w+|\.)\s+"syscall"', cs) and (not ts or all(chunk(cs,n)==chunk(ts,n) for n in ("runRecipe(","allowBin(","parseRecipe(","(r recipe) err(","git(","recipeEnv(")))
        self.record("Required pre/post verification hooks", hook_ok, "")
        self.record("Candidate retains sai-verify kernel", has_kernel, "")
        self.record("Candidate verifier is not a shell evaluator", shell_ok, "")
        return ok and hook_ok and has_kernel and shell_ok

    def run_all(self) -> bool:
        self.json_validity()
        self.no_new_secrets()
        self.gateway_loopback()
        self.connection_truth()
        self.constitution()
        self.scaffold_behavior()
        self.shell_authorization()
        self.agent_operability()
        self.feature_contract()
        return all(result.ok for result in self.results)

    def report(self) -> bool:
        ok = all(result.ok for result in self.results)
        print(f"ANTI-REGRESSION: {'PASS' if ok else 'FAIL'}")
        for result in self.results:
            mark = "PASS" if result.ok else "FAIL"
            print(f"[{mark}] {result.name}")
            if result.detail and not result.ok:
                for line in result.detail.splitlines()[-20:]:
                    print(f"  {line}")
        return ok


def clone_for_mutation(candidate: pathlib.Path, parent: pathlib.Path) -> pathlib.Path:
    dst = parent / "candidate"
    shutil.copytree(candidate, dst, symlinks=True)
    return dst


def expect_failure(label: str, fn) -> Result:
    try:
        detected = fn()
    except Exception as exc:
        return Result(label, False, f"self-test error: {exc}")
    return Result(label, bool(detected), "regression was not detected" if not detected else "")


def mutation_self_test(trusted: pathlib.Path, candidate: pathlib.Path) -> list[Result]:
    outcomes: list[Result] = []

    with tempfile.TemporaryDirectory(prefix="anti-regression-json-") as td:
        root = clone_for_mutation(candidate, pathlib.Path(td))
        bad = root / ".anti-regression-invalid.json"
        bad.write_text("{", encoding="utf-8")
        p = Policy(trusted, root)
        outcomes.append(expect_failure("mutation: malformed JSON is caught", lambda: not p.json_validity(root)))

    with tempfile.TemporaryDirectory(prefix="anti-regression-secret-") as td:
        root = clone_for_mutation(candidate, pathlib.Path(td))
        marker = "-----BEGIN OPENSSH " + "PRIVATE KEY-----\n"
        (root / ".anti-regression-secret.txt").write_text(marker, encoding="utf-8")
        p = Policy(trusted, root)
        outcomes.append(expect_failure("mutation: new secret is caught", lambda: not p.no_new_secrets(root)))

    with tempfile.TemporaryDirectory(prefix="anti-regression-gateway-") as td:
        root = clone_for_mutation(candidate, pathlib.Path(td))
        changed = False
        for path, doc in Policy.json_documents(root):
            if isinstance(doc, dict) and isinstance(doc.get("gateway"), dict) and isinstance(doc.get("dashboard_ingest"), dict):
                if "host" in doc["gateway"]:
                    doc["gateway"]["host"] = "0.0.0.0"
                    doc["dashboard_ingest"]["bind"] = "0.0.0.0"
                    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
                    changed = True
                    break
        p = Policy(trusted, root)
        outcomes.append(expect_failure("mutation: public gateway bind is caught", lambda: changed and not p.gateway_loopback(root)))

    with tempfile.TemporaryDirectory(prefix="anti-regression-ci-") as td:
        root = clone_for_mutation(candidate, pathlib.Path(td))
        budget = Policy.named_workflow(root, "PR line budget")
        changed = False
        if budget:
            path, text = budget
            path.write_text(text.replace('MAX_ADDITIONS: "1200"', 'MAX_ADDITIONS: "999999"'), encoding="utf-8")
            changed = True
        p = Policy(trusted, root)
        outcomes.append(expect_failure("mutation: weakened line budget is caught", lambda: changed and not p.constitution(root)))

    with tempfile.TemporaryDirectory(prefix="anti-regression-scaffold-") as td:
        root = clone_for_mutation(candidate, pathlib.Path(td))
        target = root / "scripts" / "agent-memory-scaffold"
        changed = target.exists()
        if changed:
            target.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
            target.chmod(0o755)
        p = Policy(trusted, root)
        outcomes.append(expect_failure("mutation: scaffold bypass is caught", lambda: changed and not p.scaffold_behavior(root)))

    with tempfile.TemporaryDirectory(prefix="anti-regression-shell-") as td:
        root = clone_for_mutation(candidate, pathlib.Path(td))
        fixture = root / ".ai" / "contracts" / "anti-regression-fixture" / "contract.json"
        fixture.parent.mkdir(parents=True, exist_ok=True)
        fixture.write_text(
            json.dumps({"allow": ["Bash(git branch proj/*)"]}) + "\n", encoding="utf-8"
        )
        p = Policy(trusted, root)
        outcomes.append(expect_failure("mutation: destructive branch allowlist is caught", lambda: not p.shell_authorization(root)))

    with tempfile.TemporaryDirectory(prefix="anti-regression-agent-") as td:
        root = clone_for_mutation(candidate, pathlib.Path(td))
        registry = root / ".ai" / "agents" / "registry.json"
        changed = False
        if registry.exists():
            reg = json.loads(registry.read_text(encoding="utf-8"))
            for agent in reg.get("agents", []):
                if agent.get("status") != "active":
                    continue
                folder = root / (agent.get("folder") or "")
                manifest = folder / "tools.json"
                if not manifest.exists():
                    continue
                m = json.loads(manifest.read_text(encoding="utf-8"))
                rel = m.get("canonical_capabilities_path")
                tools = folder / rel if rel else manifest
                if tools.exists():
                    tools.unlink()
                    changed = True
                    break
        p = Policy(trusted, root)
        outcomes.append(expect_failure("mutation: broken active-agent setup is caught", lambda: changed and not p.agent_operability(root)))

    with tempfile.TemporaryDirectory(prefix="anti-regression-connection-") as td:
        root = clone_for_mutation(candidate, pathlib.Path(td))
        changed = False
        for path in root.rglob("*.md"):
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if "telegram_dm_link" in text:
                lines = text.splitlines()
                for i, line in enumerate(lines):
                    if line.startswith("|") and "pending" in line and not line.startswith("|---"):
                        cols = line.split("|")
                        if len(cols) >= 4:
                            cols[-2] = " yes "
                            lines[i] = "|".join(cols)
                            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                            changed = True
                            break
                if changed:
                    break
        p = Policy(trusted, root)
        outcomes.append(expect_failure("mutation: false connected state is caught", lambda: changed and not p.connection_truth(root)))

    if (trusted / "cmd" / "sai-verify").is_dir():
        with tempfile.TemporaryDirectory(prefix="anti-regression-feature-") as td:
            root = clone_for_mutation(candidate, pathlib.Path(td)); dropped = False
            for path in (root / ".cursor" / "skills" / "verify-sai" / "features").glob("*.md"):
                if path.name != "README.md": path.unlink(); dropped = True; break
            p = Policy(trusted, root); outcomes.append(expect_failure("mutation: protected feature deletion is caught", lambda: dropped and not p.feature_contract()))
            t=pathlib.Path(td)/"t"; shutil.copytree(trusted,t,symlinks=True); shutil.rmtree(t/"cmd"/"sai-verify", ignore_errors=True); bp=Policy(t,candidate); okb=bp.feature_contract() and any(r.ok and "N/A" in (r.detail or "") for r in bp.results if r.name=="Feature map preservation"); bad=pathlib.Path(td)/"bad"; shutil.copytree(candidate,bad,symlinks=True); (bad/"cmd"/"sai-verify"/"helper.go").write_text('package main\nimport "os/exec"\nfunc pwn() { exec.CommandContext(nil, "ba"+"sh", "-l"+"c", "x") }\n'); bp2=Policy(t,bad); sw=pathlib.Path(td)/"sw"; shutil.copytree(candidate,sw,symlinks=True); mp=sw/"cmd"/"sai-verify"/"main.go"; mp.write_text(mp.read_text(encoding="utf-8").replace("exec.CommandContext(ctx, argv[0], argv[1:]...)", 'exec.CommandContext(ctx, "bash", argv[1:]...)', 1), encoding="utf-8"); bp3=Policy(trusted,sw); al=pathlib.Path(td)/"al"; shutil.copytree(candidate,al,symlinks=True); (al/"cmd"/"sai-verify"/"helper.go").write_text('package main\nimport (\n\txe "os/exec"\n)\nfunc pwn() { xe.Command("true") }\n'); bp4=Policy(t,al); ini=pathlib.Path(td)/"ini"; shutil.copytree(candidate,ini,symlinks=True); (ini/"cmd"/"sai-verify"/"helper.go").write_text('package main\nfunc init() {}\n'); bp5=Policy(t,ini); sy=pathlib.Path(td)/"sy"; shutil.copytree(candidate,sy,symlinks=True); (sy/"cmd"/"sai-verify"/"helper.go").write_text('package main\nimport (\n\tsy "syscall"\n)\nfunc pwn() { _, _ = sy.ForkExec("", nil, nil) }\n'); sh=pathlib.Path(td)/"sh"; shutil.copytree(candidate,sh,symlinks=True); hp=sh/"cmd"/"sai-verify"/"main.go"; hp.write_text(hp.read_text(encoding="utf-8").replace("argv := r.argv", 'argv := []string{"bash", "-lc", "true"}', 1), encoding="utf-8"); iv=pathlib.Path(td)/"iv"; shutil.copytree(candidate,iv,symlinks=True); (iv/"cmd"/"sai-verify"/"helper.go").write_text('package main\nvar bootstrap = func() int { return 0 }()\n'); outcomes.append(Result("bootstrap: no BASE kernel is N/A and still checks candidate", okb and not bp2.feature_contract() and not bp3.feature_contract() and not bp4.feature_contract() and not Policy(trusted,al).feature_contract() and not bp5.feature_contract() and not Policy(trusted,sy).feature_contract() and not Policy(t,sy).feature_contract() and not Policy(trusted,sh).feature_contract() and not Policy(trusted,iv).feature_contract() and not Policy(t,iv).feature_contract(), ""))
    return outcomes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trusted", required=True, type=pathlib.Path)
    parser.add_argument("--candidate", required=True, type=pathlib.Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    policy = Policy(args.trusted, args.candidate)
    policy.run_all()
    ok = policy.report()

    if args.self_test:
        print("\nPOLICY MUTATION SELF-TEST")
        mutations = mutation_self_test(args.trusted.resolve(), args.candidate.resolve())
        for result in mutations:
            print(f"[{'PASS' if result.ok else 'FAIL'}] {result.name}")
            if result.detail and not result.ok:
                print(f"  {result.detail}")
        ok = ok and all(result.ok for result in mutations)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
