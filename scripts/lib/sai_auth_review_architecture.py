#!/usr/bin/env python3
"""Saul LOCAL_ARCH / IMPACT_ARCH / SYSTEM_ARCH review engine.

Caller supplies repository, base_sha, and head_sha. This module never
defaults the current PR, contract, branch, or SHA. ARCH-* blockers are
in-memory payloads only — no live ledger writes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SCHEMA_ID = "saul-architecture-evidence"
SCHEMA_REL = ".ai/shared/schemas/saul-architecture-evidence.schema.json"
VERDICTS = ("PASS_CURRENT", "FAIL", "STALE", "NOT_APPLICABLE")
REVIEW_KINDS = ("LOCAL_ARCH", "IMPACT_ARCH", "SYSTEM_ARCH")
ARCH_REVIEW_TYPES = frozenset(REVIEW_KINDS) | frozenset({"architecture"})
IDENTITY_KEYS = ("repository", "base_sha", "head_sha")
REQUIRED_EVIDENCE = IDENTITY_KEYS + (
    "schema_id", "local_arch", "impact_arch", "system_arch", "domains",
    "shard_coverage", "convergence", "blockers", "system_arch_required_now",
)
FORBIDDEN_CLEAR_ACTORS = frozenset({
    "cursor", "contractor", "ctr-admin", "cora", "sai", "ceo", "self",
    "primary", "named-contractor", "candidate",
})
REJECT_PROOF_SOURCES = FORBIDDEN_CLEAR_ACTORS
ARCH_CLEARANCE_REASON = "ARCH_CLEARANCE_REQUIRES_AUTHENTIC_SAUL"
DOMAINS = (
    "authorization", "identity", "trust_boundaries", "operational_context",
    "state_ownership", "multi_primary_isolation", "ralph_control_flow",
    "cora_routing", "contractor_isolation", "blocker_lifecycle",
    "saul_review", "sai_governance", "event_routing", "recovery_resume",
    "ci_quality", "workflow_security", "persistence", "interfaces_schemas",
    "observability", "resource_bounds", "dependency_direction",
    "failure_recovery", "portability", "simplicity", "reviewability",
    "requirement_coherence",
)
PATH_RULES = (
    (".ai/authorizations/", ("authorization", "identity", "trust_boundaries")),
    (".ai/_config/authorization", ("authorization", "contractor_isolation")),
    (".ai/_config/", ("ci_quality", "requirement_coherence", "operational_context")),
    (".github/workflows/", ("ci_quality", "workflow_security")),
    ("scripts/lib/sai_auth_blockers", ("blocker_lifecycle", "failure_recovery")),
    ("scripts/lib/sai_auth_saul", ("saul_review", "identity")),
    ("scripts/lib/sai_auth_resume", ("recovery_resume", "ralph_control_flow")),
    ("scripts/lib/sai_auth_cue", ("cora_routing", "event_routing")),
    ("scripts/lib/sai_auth_event", ("event_routing",)),
    ("scripts/lib/sai_auth_runtime", ("multi_primary_isolation", "operational_context")),
    ("scripts/lib/sai_auth", ("authorization", "identity", "trust_boundaries")),
    ("scripts/sai-", ("authorization", "contractor_isolation")),
    (".ai/agents/cora", ("cora_routing", "contractor_isolation")),
    (".ai/agents/sai", ("sai_governance",)),
    (".ai/agents/", ("contractor_isolation", "sai_governance")),
    (".ai/contracts/", ("contractor_isolation", "blocker_lifecycle", "requirement_coherence")),
    (".ai/shared/schemas/", ("interfaces_schemas", "reviewability")),
    (".ai/shared/quality/", ("ci_quality", "saul_review", "requirement_coherence")),
    (".cursor/rules/", ("ralph_control_flow", "operational_context")),
    ("scripts/lib/code-health", ("ci_quality", "resource_bounds")),
    (".ai/runs/", ("observability", "operational_context")),
)
FOUNDATIONAL_PREFIXES = (
    ".ai/authorizations/", ".ai/_config/", ".github/workflows/",
    "scripts/lib/sai_auth", ".ai/agents/", ".cursor/rules/",
)
BROAD_AREA_MIN, BROAD_DOMAIN_MIN = 3, 8
DEFAULT_UNMATCHED = ("reviewability", "simplicity")
NEIGHBOR_KEYS = (
    "owners", "callers", "callees", "interfaces", "schemas", "tests", "persistence",
)


def _paths(value) -> list[str]:
    return [str(p) for p in value] if value else []


def domains_for_path(path: str) -> tuple[str, ...]:
    best, hits = "", []
    for prefix, domains in PATH_RULES:
        if path == prefix.rstrip("/") or path.startswith(prefix):
            if len(prefix) >= len(best):
                best, hits = prefix, list(domains)
    if not hits:
        hits = list(DEFAULT_UNMATCHED)
    out, seen = [], set()
    for d in hits:
        if d not in seen and d in DOMAINS:
            seen.add(d)
            out.append(d)
    return tuple(out)


def infer_neighborhood_node(path: str) -> dict:
    node = {k: [] for k in NEIGHBOR_KEYS}
    node["path"] = path
    if path.startswith("scripts/") and not path.endswith("_test.py"):
        node["tests"] = [str(Path(path).with_name(Path(path).stem + "_test.py"))]
    if path.endswith(".schema.json") or path.startswith(".ai/shared/schemas/"):
        node["schemas"] = [path]
    return node


def local_neighborhood(changed_paths, graph=None) -> list[dict]:
    graph = graph or {}
    out = []
    for path in changed_paths:
        node = infer_neighborhood_node(path)
        extra = graph.get(path) or {}
        for key in NEIGHBOR_KEYS:
            if extra.get(key) is not None:
                node[key] = list(extra[key])
        node["path"] = path
        out.append(node)
    return out


def neighborhood_paths(nodes: list[dict]) -> list[str]:
    found, seen = [], set()
    for node in nodes:
        for key in ("path",) + NEIGHBOR_KEYS:
            raw = node.get(key)
            for item in (raw if isinstance(raw, list) else [raw]):
                if item and isinstance(item, str) and item not in seen:
                    seen.add(item)
                    found.append(item)
    return found


def context_digest(inp: dict, extra=None) -> str:
    body = {
        "base_sha": inp.get("base_sha"),
        "changed_paths": sorted(_paths(inp.get("changed_paths"))),
        "head_sha": inp.get("head_sha"),
        "quality_policy_digest": inp.get("quality_policy_digest") or "",
        "repository": inp.get("repository"),
        "untouched_paths": sorted(_paths(inp.get("untouched_paths"))),
        "extra": extra or {},
    }
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def system_arch_required_now(changed_paths, invalidated) -> bool:
    areas = {
        prefix for path in changed_paths for prefix in FOUNDATIONAL_PREFIXES
        if path == prefix.rstrip("/") or path.startswith(prefix)
    }
    return len(areas) >= BROAD_AREA_MIN or len(set(invalidated)) >= BROAD_DOMAIN_MIN


def _aggregate(verdicts) -> str:
    vals = [v for v in verdicts if v in VERDICTS]
    for tag in ("FAIL", "STALE", "PASS_CURRENT"):
        if tag in vals:
            return tag
    return "NOT_APPLICABLE"


def _prior_current(prior, head_sha, digest) -> bool:
    return (
        isinstance(prior, dict) and prior.get("verdict") == "PASS_CURRENT"
        and str(prior.get("head_sha") or "") == str(head_sha)
        and str(prior.get("context_digest") or "") == str(digest)
    )


def _domain_verdict(*, local, impact, finding, prior, head_sha, digest):
    if finding == "FAIL":
        return "FAIL"
    if finding in VERDICTS and finding != "NOT_APPLICABLE":
        return finding
    if not local and not impact:
        return "NOT_APPLICABLE"
    if impact and not local:
        return "PASS_CURRENT" if _prior_current(prior, head_sha, digest) else "STALE"
    return "PASS_CURRENT"


def arch_blocker_payload(domain, seq, *, head_sha, base_sha, source, description):
    return {
        "blocker_id": f"ARCH-{domain.replace('_', '-').upper()}-{seq:03d}",
        "category": "technical", "severity": "P0", "status": "DISCOVERED",
        "clearance_authority": "saul", "clearance_review_type": "architecture",
        "domain": domain, "source": source, "base_sha": base_sha,
        "head_sha": head_sha, "description": description,
        "implementation_state": "open", "verification_state": "unverified",
        "clearance_review_id": None, "clearance_head": None,
        "ledger_write": False, "self_pass_forbidden": True,
    }


def blockers_from_failures(domains, *, head_sha, base_sha):
    out, counts = [], {}
    for domain, rec in domains.items():
        if rec.get("verdict") != "FAIL":
            continue
        counts[domain] = counts.get(domain, 0) + 1
        src = "LOCAL_ARCH" if rec.get("local") else "IMPACT_ARCH"
        if rec.get("local") and rec.get("impact"):
            src = "LOCAL_ARCH+IMPACT_ARCH"
        out.append(arch_blocker_payload(
            domain, counts[domain], head_sha=head_sha, base_sha=base_sha, source=src,
            description=f"material architecture FAIL in domain {domain}",
        ))
    return out


def actor_forbidden(actor) -> bool:
    name = str(actor or "").strip().lower()
    return (not name) or name in FORBIDDEN_CLEAR_ACTORS or name.startswith("ctr-")


def is_authentic_saul_architecture_proof(proof, blocker=None, exact_head=None) -> bool:
    if not isinstance(proof, dict):
        return False
    att = proof.get("attestation") if isinstance(proof.get("attestation"), dict) else {}
    if (
        proof.get("reviewer") != "saul" or proof.get("runtime") != "codex"
        or proof.get("codex_invoked") is not True or proof.get("synthetic") is not False
        or proof.get("review_type") not in ARCH_REVIEW_TYPES
        or not att or att.get("source") in REJECT_PROOF_SOURCES or not att.get("sig")
    ):
        return False
    if exact_head and str(proof.get("implementation_head") or "") != str(exact_head):
        return False
    if not blocker:
        return True
    domain = blocker.get("domain")
    ids = {blocker.get("blocker_id"), domain}
    finding_ok = any(
        isinstance(f, dict)
        and (f.get("id") or f.get("blocker_id") or f.get("domain")) in ids
        and str(f.get("status") or "").upper() in ("PASS", "PASS_CURRENT")
        for f in (proof.get("findings") or [])
    )
    if domain and domain not in (proof.get("covered_domains") or []) and not finding_ok:
        return str(proof.get("disposition") or "").upper() == "APPROVE"
    return True


def attempt_clear_arch_blocker(blocker, actor, proof=None, exact_head=None):
    """Refuse Cursor/self-clear. Never writes a live ledger file."""
    reject = {
        "status": "REJECT", "reason": ARCH_CLEARANCE_REASON,
        "blocker_id": (blocker or {}).get("blocker_id"), "actor": actor,
        "ledger_write": False,
    }
    if actor_forbidden(actor) or not is_authentic_saul_architecture_proof(
        proof, blocker, exact_head,
    ):
        return reject
    return {
        "status": "AWAITING_LEDGER_WRITE", "reason": "payload_only_no_live_ledger",
        "blocker_id": (blocker or {}).get("blocker_id"), "ledger_write": False,
    }


def shard_coverage_complete(coverage: dict) -> bool:
    coverage = coverage or {}
    expected = list(coverage.get("expected") or [])
    passed = list(coverage.get("passed") or [])
    exp_n = coverage.get("expected_count", len(expected))
    pas_n = coverage.get("passed_count", len(passed))
    return bool(exp_n) and pas_n == exp_n and not (
        coverage.get("missing") or coverage.get("failed")
    )


def evaluate_convergence(evidence: dict) -> tuple[bool, str]:
    shards_ok = shard_coverage_complete(evidence.get("shard_coverage") or {})
    system = evidence.get("system_arch") or {}
    system_ok = system.get("performed") is True and system.get("verdict") == "PASS_CURRENT"
    if shards_ok and not system_ok:
        return False, "NOT_CONVERGED_MISSING_SYSTEM_ARCH"
    if system_ok and not shards_ok:
        return False, "NOT_CONVERGED_MISSING_SHARD"
    if not shards_ok or not system_ok:
        return False, "NOT_CONVERGED"
    for rec in (evidence.get("domains") or {}).values():
        if rec.get("verdict") in ("FAIL", "STALE"):
            return False, f"NOT_CONVERGED_DOMAIN_{rec.get('verdict')}"
    return True, "CONVERGED"


def unchanged_related(changed, untouched) -> list[str]:
    if untouched:
        return list(untouched)
    related = []
    for path in changed:
        node = infer_neighborhood_node(path)
        related.extend(node.get("schemas") or [])
        related.extend(node.get("tests") or [])
    return [p for p in related if p not in changed]


def review_architecture(inp: dict) -> dict:
    if not isinstance(inp, dict):
        raise TypeError("architecture input must be a dict")
    for key in IDENTITY_KEYS:
        if not inp.get(key):
            raise ValueError(f"missing {key}; no implicit identity defaults")
    changed = _paths(inp.get("changed_paths"))
    untouched = _paths(inp.get("untouched_paths"))
    findings = inp.get("domain_findings") or {}
    prior = inp.get("prior_domain_proofs") or {}
    nodes = local_neighborhood(changed, inp.get("component_graph") or {})
    local_domains = set()
    for path in changed:
        local_domains.update(domains_for_path(path))
    impact_domains = set()
    for path in neighborhood_paths(nodes):
        if path not in changed:
            impact_domains.update(domains_for_path(path))
    for path in unchanged_related(changed, untouched):
        impact_domains.update(domains_for_path(path))
    impact_domains |= set(inp.get("explicit_invalidations") or ())
    impact_domains -= local_domains
    digest = context_digest(inp, extra={
        "local": sorted(local_domains), "impact": sorted(impact_domains),
    })
    domains = {}
    for domain in DOMAINS:
        is_local, is_impact = domain in local_domains, domain in impact_domains
        domains[domain] = {
            "verdict": _domain_verdict(
                local=is_local, impact=is_impact, finding=findings.get(domain),
                prior=prior.get(domain), head_sha=inp["head_sha"], digest=digest,
            ),
            "local": is_local, "impact": is_impact,
            "untouched_files": [p for p in untouched if domain in domains_for_path(p)],
        }
    required_now = bool(inp.get("system_arch_required_now")) or system_arch_required_now(
        changed, local_domains | impact_domains,
    )
    sys_proof = inp.get("system_arch_proof") or {}
    sys_performed = bool(sys_proof.get("performed"))
    sys_verdict = sys_proof.get("verdict")
    if sys_performed:
        if sys_verdict not in VERDICTS:
            sys_verdict = "FAIL"
        if str(sys_proof.get("head_sha") or "") not in ("", str(inp["head_sha"])):
            sys_verdict, sys_performed = "STALE", False
    else:
        sys_verdict = "NOT_APPLICABLE"
    local_v = _aggregate(r["verdict"] for r in domains.values() if r["local"])
    impact_v = _aggregate(r["verdict"] for r in domains.values() if r["impact"])
    if not local_domains:
        local_v = _aggregate(
            r["verdict"] for r in domains.values() if r["verdict"] != "NOT_APPLICABLE"
        ) or "PASS_CURRENT"
    evidence = {
        "schema_id": SCHEMA_ID, "schema_version": 1,
        "repository": inp["repository"], "base_sha": inp["base_sha"],
        "head_sha": inp["head_sha"],
        "quality_policy_digest": inp.get("quality_policy_digest") or "",
        "context_digest": digest, "review_kinds": list(REVIEW_KINDS),
        "local_arch": {
            "verdict": local_v, "components": list(changed), "neighborhood": nodes,
        },
        "impact_arch": {
            "verdict": impact_v if impact_domains else "PASS_CURRENT",
            "invalidated_domains": sorted(impact_domains),
        },
        "system_arch": {
            "verdict": sys_verdict, "performed": sys_performed, "required_now": required_now,
        },
        "system_arch_required_now": required_now, "domains": domains,
        "shard_coverage": dict(inp.get("shard_coverage") or {}),
        "blockers": blockers_from_failures(
            domains, head_sha=inp["head_sha"], base_sha=inp["base_sha"],
        ),
        "ledger_write": False,
    }
    converged, reason = evaluate_convergence(evidence)
    evidence["convergence"] = {"converged": converged, "reason": reason}
    return evidence


def validate_evidence(evidence: dict) -> list[str]:
    if not isinstance(evidence, dict):
        return ["evidence must be an object"]
    fails = [f"missing {k}" for k in REQUIRED_EVIDENCE if k not in evidence]
    if evidence.get("schema_id") != SCHEMA_ID:
        fails.append("schema_id mismatch")
    fails.extend(f"empty {k}" for k in IDENTITY_KEYS if not evidence.get(k))
    for kind in ("local_arch", "impact_arch", "system_arch"):
        if (evidence.get(kind) or {}).get("verdict") not in VERDICTS:
            fails.append(f"{kind} verdict invalid")
    for domain, rec in (evidence.get("domains") or {}).items():
        if domain not in DOMAINS:
            fails.append(f"unknown domain {domain}")
        if (rec or {}).get("verdict") not in VERDICTS:
            fails.append(f"{domain} verdict invalid")
    for row in evidence.get("blockers") or []:
        bid = str((row or {}).get("blocker_id") or "")
        if not bid.startswith("ARCH-"):
            fails.append(f"blocker id must be ARCH-*: {bid}")
        if row.get("ledger_write") is True:
            fails.append("architecture blockers must not write the live ledger")
        if row.get("clearance_authority") != "saul":
            fails.append("architecture blocker clearance_authority must be saul")
    return fails


def load_schema(root=None) -> dict:
    base = Path(root) if root else Path(__file__).resolve().parents[2]
    return json.loads((base / SCHEMA_REL).read_text(encoding="utf-8"))


def cmd(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="verify-saul-architecture-quality")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--from-json")
    parser.add_argument("--repository")
    parser.add_argument("--base-sha")
    parser.add_argument("--head-sha")
    args = parser.parse_args(argv)
    if args.self_test:
        from sai_auth_review_architecture_test import run_architecture_fixtures
        run_architecture_fixtures()
        return 0
    if not args.from_json:
        print("FAIL missing --from-json; no implicit PR/contract/branch/SHA", file=sys.stderr)
        return 2
    payload = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
    for key, val in (("repository", args.repository), ("base_sha", args.base_sha),
                     ("head_sha", args.head_sha)):
        if val:
            payload[key] = val
    evidence = review_architecture(payload)
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if evidence["convergence"]["converged"] else 1


if __name__ == "__main__":
    raise SystemExit(cmd())
