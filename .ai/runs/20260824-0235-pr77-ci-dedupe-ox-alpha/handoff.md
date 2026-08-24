# Handoff — CI duplicate-run dedupe (PR 77)

## What changed
- agent-audit.yml and feature-maps-pages.yml: push trigger scoped from
  ["**"] to [main]. Both workflows previously ran on pull_request AND
  push for every PR-head commit, doubling identical runner compute
  (icm-enforcement, merge-handoff-slack, build, deploy each x2 per SHA).
- PR validation still via pull_request event; main keeps deploy +
  server-side push confirmation; workflow_dispatch retained.

## Verification at authoring time
YAML diff-only change (2 lines); no job logic touched. Post-push runs on
ad89aed confirm single run per workflow per commit.

## Next
CI + real-Codex Saul re-bind on pushed HEAD; stay draft.
