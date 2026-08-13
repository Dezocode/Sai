# Scalability Contract

## 1. The orchestrator is language-neutral

`qualityctl` reads JSON registries and executes adapter commands. It must not accumulate framework-specific logic.

## 2. Every responsibility has one canonical owner

Capability registration is a uniqueness constraint, not documentation.

## 3. Tools are replaceable behind capability interfaces

The policy asks for `sast`, `secret_scan`, `dependency_graph`, `dead_code`, `duplication`, `sbom`, etc. A concrete tool fulfills each capability. Replacing a tool must not require rewriting product code.

## 4. Fast and deep planes

Fast checks are deterministic and PR-safe. Deep checks may be expensive and run on architecture/security changes, every third Phase-0 gate, nightly, and before unlock/release.

## 5. Ratchets, not permanent historical exemptions

Existing debt can be snapshotted once. New code cannot increase debt. Baselines are commit-addressed, reviewable, and cannot be silently refreshed.

## 6. Evidence is append-only

Each run writes under `.sai-quality/runtime/evidence/<commit-or-working-tree>/<gate>/`. CI artifacts may retain the same evidence externally. Do not overwrite historical evidence to make a later result look green.

## 7. Sharding

Adapters declare whether they support changed-path execution, workspace sharding, cache keys, and full-scan mode. The global policy determines when full scan is mandatory.

## 8. No product dependency on QA infrastructure

SAI runtime code must never import SonarQube, Semgrep, qualityctl, scanners, or health-dashboard internals. Quality infrastructure is development/control-plane only.
