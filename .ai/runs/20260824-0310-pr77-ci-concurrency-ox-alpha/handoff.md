# Handoff — 20260824-0310-pr77-ci-concurrency-ox-alpha

Saul P1 (codex, check 97307834166): push trigger scoping removed pre-PR branch enforcement. Fix: restore push branches ['**'] in agent-audit.yml + feature-maps-pages.yml; add concurrency group keyed on head SHA with cancel-in-progress so the dual-event duplicate collapses to one surviving run per SHA with zero coverage gap. YAML validated; all ICM verifiers green locally.
