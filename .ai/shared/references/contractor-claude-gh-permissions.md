# Contractor Claude Code — `gh` Bash permissions (Layer 3)

Provisional contractors (`registry.json` → `status: provisional`) must **not**
use blanket `Bash(gh *)` in Claude Code `permissions.allow`. That pattern
permits PR merge/close, repository deletion, releases, and other access-affecting
mutations covered by `.ai/_config/security-policy.md` hard review gates.

## Provisional allowlist (read + open PR only)

Use explicit entries in `splunk-clone/.claude/settings.json` (or contract
`claude-desktop-bootstrap.json` before owner merge):

- `Bash(gh auth status*)` — verify CLI identity before sensitive reads
- `Bash(gh repo view*)` — fork topology and default branch
- `Bash(gh pr view*)`, `Bash(gh pr list*)`, `Bash(gh pr checks*)` — PR inspection
- `Bash(gh pr create*)` — open PRs (never merge/close without owner approval)
- `Bash(gh run list*)`, `Bash(gh run view*)`, `Bash(gh workflow view*)` — CI evidence
- `Bash(gh status*)` — working tree vs remote (when used with git)

## After persona gate + Sai VERIFY PASS (`status: active`)

Owners may expand `permissions.allow` in a reviewed amendment. Each new `gh`
pattern must be recorded in `runtimes/claude/tools.json` with verified evidence
(Phase 5B). Mutations (merge, close, delete, release, secret/org admin) still
require explicit co-founder approval per commit.

## CI

`scripts/verify-scaffold-safety` rejects tracked `Bash(gh *)` in contractor
Claude settings/bootstrap templates.
