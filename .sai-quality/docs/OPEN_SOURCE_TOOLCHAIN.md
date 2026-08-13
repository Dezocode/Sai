# Open-Source Toolchain Integration

The bundle deliberately uses a portfolio of specialist tools. No single OSS project covers SAI's complete architecture/quality/security problem.

| Capability | Preferred tool | Integration mode |
|---|---|---|
| central quality gate / complexity / duplication / coverage | SonarQube Community Build | isolated service + scanner |
| custom/static security analysis | Semgrep Community Edition | pinned CLI/container |
| vulnerabilities / misconfig / secrets / licenses / SBOM | Trivy | pinned CLI/container |
| secret prevention and git-history scanning | Gitleaks | pinned CLI + pre-commit/CI |
| JS/TS dependency architecture | dependency-cruiser | isolated Node tooling |
| JS/TS dead files/exports/dependencies | Knip | isolated Node tooling |
| language-agnostic-ish copy/paste detection | jscpd | isolated Node/Rust CLI as selected |
| dependency update automation | Renovate | GitHub App/service or pinned self-hosted runner |
| repository security posture | OpenSSF Scorecard | pinned action/CLI |
| SBOM intelligence | OWASP Dependency-Track | isolated service |

## Installation rule

At Gate G04, resolve a current stable release **from the tool's official project/registry**, write the exact version into `.sai-quality/toolchain.lock.json`, and where container digests/checksums/provenance are available record those as well. After resolution, committed workflows use the pin, not `latest`.

## License rule

Quality tools are build/control-plane dependencies, not SAI runtime dependencies. Maintain `.sai-quality/provenance/tool-licenses.json`; any reciprocal/copyleft tool is isolated as a process/service unless legal review explicitly approves a different integration.

## Suppression rule

Every suppression requires: finding ID, tool, exact scope, owner, rationale, expiry, ADR/evidence link, and regression test where applicable. A global ignore is forbidden unless the policy explicitly names it.
