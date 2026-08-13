# Master Execution — SAI Quality OS Phase 0

## Objective

Create an indefinitely extensible quality control plane that can govern a monorepo, multiple languages, multiple applications, many services, AI-generated changes, and later multiple deployment targets without central scripts becoming an unmaintainable `if/elif` tree.

The architecture is **registry + adapters + policies + evidence**.

```text
                     existing SAI ICM
                 identity / runs / handoffs
                           |
                           v
                  SAI QUALITY CONTROL PLANE
      +--------------------+--------------------+
      |                    |                    |
 architecture registry  policy registry      tool registry
      |                    |                    |
      +----------+---------+----------+---------+
                 |                    |
                 v                    v
          language adapters       OSS engines
                 |                    |
           JS/TS Python ...    Semgrep / Trivy / ...
                 |                    |
                 +---------+----------+
                           v
                     evidence lake
                           |
                           v
                    release/unlock gate
```

## Chronological gates

### G00 — Repository preflight and preservation
Prove canonical repo, clean/dirty state, existing governance ownership, and feature lock. Take inventory before edits.

### G01 — Quality control-plane skeleton
Install `.sai-quality/`, schemas, policy/registry structure, runtime state isolation, and `qualityctl`. Self-test orchestration.

### G02 — Canonical architecture registry
Establish reserved roots, capability ownership semantics, contract ownership semantics, architectural migration rules, duplicate-owner rejection, and no-product-code lock.

### G03 — Adapter framework and language detection
Detect languages/frameworks without choosing a product stack. Enable only applicable adapters. Adapters expose `detect`, `install`, `fast_check`, `deep_check`, `report` contracts.

### G04 — Tool provenance and immutable pinning
Resolve current stable tools from official sources. Record exact versions and, for container/binary tools where available, immutable digests/checksums/provenance. Refuse mutable `latest` in committed execution.

### G05 — Formatting, lint, type/build contract
Wire project-native compiler/linter/formatter once languages exist. Until product code exists, validate governance scripts and configuration. Establish fail-closed adapter semantics.

### G06 — Dependency architecture
For JS/TS use dependency-cruiser. For future languages add equivalent adapters; never bake JS assumptions into the global orchestrator. Reject cycles, unresolvable imports, forbidden layer direction, and undeclared architectural edges.

### G07 — Dead-code and orphan control
For JS/TS use Knip. Add language-specific adapters later. Establish entrypoint declarations, orphan rules, unused dependency/export policies, and no-ignore-without-ADR rule.

### G08 — Duplication and complexity ratchets
Use jscpd for copy/paste duplication; SonarQube for central quality metrics/complexity where supported. Baseline existing governance debt once, then forbid regression. Greenfield product code begins with zero inherited debt.

### G09 — SAST and secret prevention
Semgrep CE + Gitleaks. Local/pre-commit/CI coverage. SAI custom rules are separate from community rule packs. No suppressions without reason, owner, expiry, and evidence.

### G10 — Vulnerability, misconfiguration, license, SBOM
Trivy repository/filesystem scans, CycloneDX/SPDX outputs as supported, license policy, high/critical failure policy, SBOM artifact generation.

### G11 — Central quality service
Bring up SonarQube Community Build via isolated Docker Compose or connect an explicitly configured remote instance. Configure quality gate and scanner integration. Never commit admin credentials.

### G12 — Supply-chain posture and dependency automation
OpenSSF Scorecard, Renovate configuration, pinned Actions, minimal token permissions, SECURITY policy checks, dependency update policy.

### G13 — Dependency intelligence service
Prepare OWASP Dependency-Track for SBOM ingestion. It may run locally/centrally; product code remains independent of this service. Prove an SBOM can be generated and the upload adapter validates payloads before any network write.

### G14 — CI aggregation, scheduled health, and evidence retention
Install separate workflows for PR fast gates and scheduled deep gates. Produce machine-readable health summary. Preserve evidence by commit SHA.

### G15 — Adversarial fault injection + unlock proof
Intentionally create violations in an isolated temporary fixture: duplicate owner, locked product file, cycle fixture where adapter supports it, duplicated source, fake secret pattern, insecure config fixture, known policy violation. The system must catch what it claims to catch. Run all cumulative DEEP checks, then and only then permit `qualityctl unlock`.

## Recursive rule

A gate does not merely test itself.

```text
build G08
  -> verify G08
  -> re-run FAST checks G00..G08
  -> if checkpoint: DEEP checks G00..G08
  -> evidence
```

Repairs use:

```text
FAIL
 -> diagnose root cause
 -> minimal repair
 -> re-run failing check
 -> re-run owning gate
 -> re-run cumulative FAST
 -> if architecture/security changed, force DEEP
```

No "fix by exclusion" unless the policy explicitly permits an exception and the exception has an ADR, owner, rationale, expiry, and regression test.

## Infinite scaling interpretation

"Infinite" here means no fixed architectural ceiling is encoded in the control plane. Adding app #20 or language #6 should mean registering another owner/adapter, not rewriting the orchestrator. The actual compute and CI cost still scales with repository size; the system supports sharding, changed-path fast scans, cached graphs, and scheduled full scans to control cost.
