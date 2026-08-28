# PR contract — Foundry owner UX

PRD: [`docs/prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md`](../../prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md)
Roadmap: [`00-sai-harness-foundry-sequence.md`](00-sai-harness-foundry-sequence.md)

## Mission

Expose the Foundry's trusted mechanics through a human-facing owner workflow: **Integrate into Sai**, **Spin Off as App**, and **Delete / Archive**, with dry-run first, dependency explanations, exact-head provenance, execution recovery and explicit confirmation. The UI may display Harness/#141 telemetry, but telemetry can never substitute for planner/verifier/executor authority.

## Acceptance

- [ ] Prototype developer surface shows Integrate, Spin Off and Delete/Archive only for prototypes whose manifest declares the relevant path.
- [ ] First action is always dry-run/plan generation or display; no destructive/publishing effect occurs on initial click.
- [ ] UI explains every REUSE/PROMOTE/EXPORT/REMOTE/PROMOTE_SHARED/DROP decision and unresolved blocker.
- [ ] Integrate preview shows proposed production files/packages/API/design/domain changes and required production-authority PRs.
- [ ] Spin Off preview shows standalone tree, dependency closure, remote-service assumptions and independent-build evidence.
- [ ] Delete/Archive preview shows zero-production-dependency proof and expected cleanup impact.
- [ ] Exact source repo/base/full HEAD, graph/plan hash, tool/schema version and current plan freshness are visible.
- [ ] Authority-changing execution requires explicit owner confirmation after preview and revalidates exact HEAD/target state immediately before execution.
- [ ] Execution status exposes exact stage, created branch/PR/repo candidate, checks/review state, failures and safe retry/resume path without fabricating completion.
- [ ] Sessions API / Sai Harness / Crosscom may supply live agent, CI, Saul and progress telemetry, but absent/stale telemetry renders unavailable/stale and cannot grant readiness or graduation permission.
- [ ] UI cannot directly push to main, auto-mark ready, auto-merge, self-approve or silently publish a repository.
- [ ] Credential-bearing operations remain behind the graduation engine; browser/prototype UI never receives privileged secrets.
- [ ] Owner cancel is respected before irreversible stages and leaves an auditable terminal/cancelled state.
- [ ] Accessibility/adaptive UI follows SaiDesignLanguage and native platform requirements.
- [ ] Audit links expose source HEAD, manifest/graph, plan artifact, generated PR/repo candidate and verification evidence.
- [ ] Failure injection/UI tests cover stale plan, changed HEAD, missing telemetry, executor refusal, partial failure, retry/resume, unsupported graduation path and owner cancel.
- [ ] End-to-end fixture exercises Sai Harness and Sai Author through dry-run + confirmed paths without bypassing normal production/standalone verification.
- [ ] Exact-head CI/preservation + genuine independent review converge before owner-ready.

## Non-goals

- No generic no-code builder, marketplace, billing or arbitrary downloadable-code runtime.
- No automatic merge/ready/App Store/TestFlight/notarization.
- No new policy authority in the UI.
