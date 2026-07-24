# Tab: GitHub — branches + CI dashboard

| Field | Value |
|---|---|
| **Deliverable** | A8 |
| **Research** | [§9](../../../.ai/contracts/20260722-openclaw-dashboard-dezocode/research-integration-methods.md#9-github-branch-and-ci-tracking) |
| **Services** | `services/github-watch/` |
| **Desktop route** | `/github` |

## Owner requirement

Live tracking for **Dezocode/Sai** and **monaecode/Sai**:

- Branches (including `proj/*` contractor branches)
- CI status / checks
- **Failure error rates** per project slug over rolling window
- Permission via GitHub App (read + actions read)

## Tech stack

| Layer | Choice |
|---|---|
| API | GitHub App installation on both repos |
| Ingest | Webhooks + poll fallback → activity-ingest |
| UI | Branch list, PR badges, failure rate charts |

## Dependencies

- A3 tracking ingest (shared pipeline)
- A11 GitHub OAuth for user-scoped views

## Verification

- [ ] Shows bootstrap branch CI live
- [ ] Failure rate updates on test dispatch
- [ ] monaecode fork parity when synced SHA

Build: [BUILD.md](./BUILD.md)
