# Verification gates
CI and pre-push run fail-closed Bash verifiers for trailers, ICM structure, merge handoff, agent setup, scaffold safety, and contract shell allowlists.
## Sub-features
- `verify-audit` `scripts/verify-agent-audit [<range>]` agent commits need `Task-ID` + `Agent` trailers; JSONL well-formed.
- `verify-hierarchy` `scripts/verify-semantic-hierarchy [root]` ICM files, six stages, registry, run grammar, no secrets in `.ai/`.
- `verify-handoff` `scripts/verify-merge-handoff [<range>|--main-tip]` each agent Task-ID has `handoff.md` or HANDOFF event.
- `verify-setup` `scripts/verify-agent-setup [root]` profiles, caps paths, SDK scaffold, contracts (`SAI_CI_STRICT_CONTRACTS`).
- `verify-scaffold-safety` `scripts/verify-scaffold-safety` negative tests for path traversal and review-pass lies.
- `verify-shell-allowlist` `scripts/verify-contract-shell-allowlist` reject `Bash(git branch prefix*)` destructive patterns.
- `path-guards` `scripts/lib/agent-path-guards.sh` sourced by scaffolds and contract-review.
## How to get to it (user POV)
- Local: run the script named above from repo root.
- Pre-push to `main`: `.githooks/pre-push` invokes audit + hierarchy + handoff.
- CI: `.github/workflows/agent-audit.yml` job `icm-enforcement`.
## Driving it with verify-sai
Preconditions: `git fetch` not required for hierarchy/setup; audit needs a rev range.
- **Hierarchy.** `scripts/verify-semantic-hierarchy`; exit 0.
- **Setup.** `SAI_CI_STRICT_CONTRACTS=1 SAI_CI_REQUIRE_SDK_SMOKE=0 scripts/verify-agent-setup`; exit 0.
- **Scaffold.** `scripts/verify-scaffold-safety`; exit 0.
- **Allowlist.** `scripts/verify-contract-shell-allowlist`; exit 0.
- **Audit range.** `scripts/verify-agent-audit -n 5 HEAD`; exit 0 or FAIL lines for missing trailers.
- **Handoff.** `scripts/verify-merge-handoff origin/main..HEAD`; requires this run's `handoff.md` once agent commits exist.
- **Proof.** `bash -n scripts/verify-semantic-hierarchy scripts/verify-agent-audit scripts/verify-merge-handoff`
## Gotchas
- Cloud identity `cursoragent@cursor.com` is an agent commit: trailers are mandatory.
- `verify-merge-handoff` fails if Task-ID has neither `handoff.md` nor a HANDOFF event.
- Do not weaken these scripts to hide a map gap.
