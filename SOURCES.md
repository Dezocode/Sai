# Primary Sources Used to Design This Bundle

Checked 2026-08-12 unless otherwise noted.

- pstack skill and workflow: https://github.com/no-session/pstack/blob/main/SKILL.md
- pstack repository/license: https://github.com/no-session/pstack
- SonarQube Community Build Docker installation: https://docs.sonarsource.com/sonarqube-community-build/server-installation/from-docker-image/installation-overview
- SonarQube quality gates: https://docs.sonarsource.com/sonarqube-community-build/quality-standards-administration/managing-quality-gates/introduction-to-quality-gates
- Semgrep Community Edition: https://semgrep.dev/products/community-edition/
- Trivy filesystem scanning/SBOM: https://trivy.dev/docs/latest/target/filesystem/
- Trivy license scanning: https://www.trivy.dev/docs/latest/scanner/license/
- Gitleaks: https://github.com/gitleaks/gitleaks
- dependency-cruiser rules: https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md
- Knip architecture/unused graph: https://knip.dev/explanations/how-knip-works
- jscpd: https://github.com/kucherenko/jscpd and https://jscpd.dev/
- Renovate self-hosted configuration: https://docs.renovatebot.com/self-hosted-configuration/
- OpenSSF Scorecard: https://github.com/ossf/scorecard
- Dependency-Track Docker deployment: https://docs.dependencytrack.org/getting-started/deploy-docker/

The execution gate requires Cursor to re-check official sources before resolving tool versions because versions, actions, container tags, licenses, and security advisories can change.
