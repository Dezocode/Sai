# Tool Adapter Recipes

These recipes give Cursor a deterministic integration target without hardcoding stale versions into this ZIP.

## Isolated Node tooling
Create `.sai-quality/tooling/package.json`; install exact resolved versions of dependency-cruiser, Knip, jscpd, and Renovate there. Commit the package manifest and lockfile, not `node_modules`. Tool execution points at that isolated environment so application dependency manifests stay clean.

## Semgrep
Create `.sai-quality/runtime/venv`; install the exact resolved Semgrep CE version. Record version and environment evidence. CI may instead use a pinned official container, but must produce equivalent SARIF/JSON evidence.

## Trivy / Gitleaks / Scorecard
Prefer official release binaries with published checksums/provenance or immutable container digests. Record the artifact checksum/digest in `toolchain.lock.json`. Do not accept a mutable tag as the final pin.

## SonarQube
Use the generated Docker Compose service for local/self-hosted evaluation or an explicit remote SonarQube Community Build endpoint. Use Postgres, persistent volumes, non-default credentials from environment, and a pinned SonarQube image. Gate G11 requires real runtime verification evidence, not only a compose file.

## Dependency-Track
At G13 fetch the official current compose definition, review it, pin image digests, and validate a synthetic SBOM payload locally before enabling network upload. Dependency-Track is an external control-plane service; SAI runtime code must not depend on it.

## Capability checks
Each adapter must eventually provide: `install`, `version`, `fast_check`, `deep_check`, `machine_report`, and `fault_fixture`. Gate G15 is incomplete until every enabled adapter has a negative fixture that the tool actually rejects.
