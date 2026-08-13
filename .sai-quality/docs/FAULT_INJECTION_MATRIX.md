# Fault Injection Matrix

G15 must prove the control plane fails closed. The Python bundle includes core synthetic tests and Cursor must extend them as each external scanner is installed.

| Fault | Expected detector |
|---|---|
| duplicate capability owner | SAI Architecture Guard |
| `policy-v2` parallel service path | SAI Architecture Guard |
| product source file while `FEATURES_LOCKED` | Feature Lock Guard |
| circular JS/TS dependency | dependency-cruiser |
| unresolved JS/TS import | dependency-cruiser |
| unused product file/export/dependency | Knip |
| oversized source file | Code Budget Guard |
| duplicated 30+ line block | jscpd / SonarQube |
| hardcoded fake high-entropy credential fixture | Gitleaks + Trivy secret scanner |
| known Semgrep-positive insecure fixture | Semgrep CE |
| intentionally vulnerable fixture dependency | Trivy (isolated fixture only) |
| forbidden/restricted license fixture | Trivy license policy |
| malformed SBOM upload payload | Dependency-Track adapter validation |
| unpinned/mutable CI dependency | Scorecard/workflow guard |
| manual deletion of feature lock without certificate | Feature Lock Guard |

Every negative fixture must be synthetic and non-secret. Never place a real credential in fault-injection data.
