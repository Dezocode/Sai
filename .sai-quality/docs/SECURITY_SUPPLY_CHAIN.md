# Security and Supply-Chain Contract

- Fetch only from official repositories, registries, or vendor documentation.
- Resolve once, pin exact versions, and prefer immutable digests/checksums.
- Treat scanner updates as supply-chain changes that must pass the same gate system.
- CI actions must be pinned to a commit SHA once Phase 0 is complete; a human-readable version comment may accompany it.
- GitHub workflow permissions default to read-only and are elevated per job only when necessary.
- No secrets in repo, examples, test evidence, screenshots, logs, SBOM uploads, or tool configuration.
- Gitleaks + Trivy secret scanning are defense in depth; do not disable one because the other exists.
- Semgrep custom SAI rules live under `.sai-quality/rules/semgrep/` and are tested against positive and negative fixtures.
- SBOMs are generated as evidence; Dependency-Track ingestion is an external write and uses credentials only from environment/secrets.
- Security findings marked HIGH/CRITICAL cannot be baselined into greenfield product code.
