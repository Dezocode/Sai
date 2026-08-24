# /goals — cross-intercom prototype lane (successor PR)

Owner: dezocode · Agent: **her** · Effort: **xhigh** · Tier: prototype (`prototypes/plugins/cross-intercom/`)

## Goals

- [ ] **Aspectizer hook on user-request receipt**: `beforeSubmitPrompt` fires `aspectizer.sh`, which decomposes the incoming request into named aspects and returns them as structured hook context. Prototype wiring lives in this plugin's `.cursor/` + `.sai/`; production `.cursor/` is untouched.
- [ ] **Local gh auth for lane participation**: agent identity + credential come from the local `gh` CLI (`gh auth token`, `gh api user`) — no secrets in the repo, no embedded tokens; the connector authenticates as the local GitHub identity.
- [ ] **Sessions-API connection (local vs repo side), xhigh effort**: `lane-connector.sh` reads the public planes of the hermes-sessions-api (`/api/hermes-sessions/sessions|prs|health`) and upserts a `sai-sessions-v2` row tagged `side=local|repo`, `monitors:["crosscom"]`, authenticated by the local gh Bearer token. Server-side acceptance of gh-Bearer credentials is defined here as the contract for the API lane (PR #141 work) and is intentionally NOT implemented in this repo.
- [ ] **Crosscomming convergence**: one session identity per Task-ID across both sides — connector reconciles local rows against `/prs` cards so a local agent and its repo-side session share `id` lineage.
- [ ] **Prototype-tier containment**: every file under `prototypes/plugins/cross-intercom/**`; feature-map claims added; zero production `.cursor/`, verifier, or Go changes.

## Goals — this round

- [x] **Crosscomm skill codified + optimized**: intercom-hooking patterns between subagents, runtimes, and all agents captured as an agent skill — including Atomic intercom mechanics as exercised by her + pr141-grunt-lead (exact-session-id send/reply semantics, fleet groups + bridge membership, non-interactive queue acks, re-intro compression, owner-routed decisions) — and incorporated into the plugin at `.sai/skills/crosscomm/SKILL.md`.
- [x] **Structure benchmark vs `.cursor` and `.agents`**: `.sai` benchmarked against `.cursor` @ origin/main (19-event hooks schema, hooks/, skills/, rules/, settings.json) and `~/.agents` (flat persona docs + skills/); results in `.sai/bench/BENCHMARK.md`; Atomic CLI cloned shallow into ignored `bench/atomic/` for the comparison (MIT; clone uncommitted).
- [ ] **Sai Harness naming + `.sai/` folder**: hook implementations live in `.sai/hooks/*`; `.sai/hooks.json` carries harness provenance (Atomic CLI derivation); `.cursor/hooks.json` delegates to it.
- [ ] **Design-check green at every push** (`go run ./cmd/sai-design-check`, plain + trusted-base).

- [x] **OpenBot channel architecture adopted**: `.sai/agents.yaml` fleet registration (channel-per-agent), composer park-and-drain inbox semantics, `audit-gateway.sh` decide→record→act gate, bot-id charset rule, take-the-wheel/needs-you flightboard states. Source: [CopilotKit/OpenBot](https://github.com/CopilotKit/OpenBot) (MIT), cloned to ignored `bench/openbot/` for reference.

## Goals — next round (atomic-cli)

- [ ] **Atomic CLI integration into the plugin**: embed Atomic CLI as the local runtime for Sai Harness hooks (license verified MIT © 2025 Bastani, Inc., bastani-inc/atomic; attribution clause noted in README).

## Open instructions requested from dezocode

1. Confirm gh-Bearer-as-write-credential is the desired auth direction for the API side (vs issuing per-agent lane tokens).
2. Aspect output schema: free-text aspect names vs typed `{name, intent, target_lane}[]`.
3. Connector cadence: event-driven per prompt vs periodic reconcile loop.
