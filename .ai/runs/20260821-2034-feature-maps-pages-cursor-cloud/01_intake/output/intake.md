# Intake — feature maps GitHub Pages

Requester: dezocode (U0BHYH0NMCY)
Agent: cursor-cloud (`bc-e0e95991-dee1-4019-a799-278f28c332aa`)
Do not reuse: `bc-98be4562-0631-4643-875d-5b8831b8e95f`
Do not update: Dezocode/Sai#73

## Product purpose (held)

Sai is the app for parents to give their children access to the internet and AI tools safely. This PR does not add product features. Consistency of maps, CI, SDL, and Go is how agents keep that product from forking.

## Repo facts (command-backed)

- Canonical: `github.com/Dezocode/Sai` (not a fork). Local remote `origin` is Dezocode/Sai.
- Default branch: `main` (protected).
- START_HEAD: `bb39842bf30bdb08ab0cf859bb4f5f39f379f8f9` (GitHub `get_commit` sha=main, `git fetch origin main`, local HEAD). Equals OBSERVED_START_HEAD. Main did not move.
- Worktree: isolated Cloud Agent VM. Clean at intake except this run directory.
- Open PR 73 (`foundation/sai-app-skeleton` @ `1012afb`) stays untouched.

## Requested outcome

Generator + non-required Pages workflow that, from exact HEAD maps, builds one Origin-light `feature-maps.html` (index) and deploys from `main` after merge. PR runs build-only without the `github-pages` environment.

## Constraints

- GitHub is canonical. `.cursor/skills/verify-sai/features/` is the map. `cmd/sai-verify` is the only machine parser. Do not invent a second feature list. Do not hand-author stale HTML.
- Origin chrome: cool light IDE (`#f8f8f8` / `#f3f3f3` / `#141414` / Code-button `#34785c`). Sai SDL tokens stay in a constitution chip.
- Hostinger stays Saul-go. Pages on Dezocode/Sai. Draft PR. Budget ≤ 1200 additions.
- Org Free Pages may need a public repo; deploy failure must not be a required check.
- Do not edit Apple/Go/SDL product code.
