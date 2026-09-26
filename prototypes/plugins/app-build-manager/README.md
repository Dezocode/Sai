# App Build Manager — Sai prototype plugin

**Status: prototype. UI only. Nothing else on the Sai task sheet is claimed done by this PR.**

App Build Manager (ABM) is the open-source UI-collections site builder for Dezocode
repos: a repo-carousel splash, per-repo Sai-format workbooks, click-through user-flow
experiences, a Figma-like canvas, live OpenKnowledge/GitNexus panels, and an
anti-regression/tasksheet surface. Its first UI makeover target is the Sai repo —
a living 3D canon town (Three.js) behind every screen, with the seven Sai personas
as procedural 3D creatures that behave like tamagotchis (mood driven by real
interaction time + the parent's daily schedule, never random).

- **Live prototype:** Tailscale-only deployment — access details live in the
  private runbook, not in this public repository.
- **Implementation source:** the `dezocode-ui-collections` repo (deploy paths,
  container, and local paths live in the private runbook).
- **Lane:** `prototypes/plugins/` — one-way isolation: production Sai must never
  import prototype code. Terminal outcomes for this prototype: archive it,
  integrate it into production Sai via an explicit production PR, or keep it as
  the independent repository it already is.

## What this PR delivers

- This prototype registration (charter, manifest, source pointer).
- Agent-agnostic skills below: how any agent manages assets, does version
  control, and validates work using ABM within Sai.
- A proposed main-branch CI workflow (`prototype-app-build-manager.yml`) that
  keeps the prototype honest after merge.
- A remaining-work list (PR description): what it takes to polish and get the
  Sai app functional. UI is one slice; the rest of the task sheet is explicitly
  **not** claimed.

## Skill 1 — Asset management (agent-agnostic)

Any agent (human-directed, any model, any harness) manages ABM/Sai UI assets
with this playbook. No tribal knowledge required.

1. **Canon is a file, not a vibe.** `content/canon.json` is the source of truth:
   named assets, their SHA-256 baselines, and the design rules they carry
   (real 3D geometry only, zero green, matte light/dark, deterministic motion).
   Read it before touching any visual.
2. **All assets are 3D geometry.** Characters, portals, trees, furniture, props —
   procedural Three.js in `static/town3d.js`. Never commit a PNG/JPEG/MP4 as a
   world asset or character sprite. Flat pictures are rejected, no exceptions.
3. **One rig, seven accessories.** All Sai personas share the Meta Muse creature
   rig (cream fluffy body, face plate, dot eyes, smile, pink cheeks, stubby
   limbs, no ears/tail). Personas differ by exactly one procedural accessory
   each (see `personaAccessory()`).
4. **Adding an asset:** build it as geometry in `town3d.js`, register it in
   `content/canon.json`, refresh the SHA baseline, and note vendored
   third-party code in `THIRD-PARTY-NOTICES.md` (currently: Three.js r128, MIT).
5. **Retire, don't delete.** Rejected canon goes to the archive; locked source
   canon is never deleted. `content/canon.json` records what superseded what.
6. **Deterministic motion only.** No AI-generated production animation, no
   randomness in shipped behavior. Animation is state-driven (e.g. tamagotchi
   mood tiers pick the pose) or on fixed scheduler loops.

## Skill 2 — Version control (agent-agnostic)

1. **Branches, never main.** All work happens on branches; PRs only. Never push
   to `main`. Never fix filed issues from a prototype branch unless explicitly
   asked.
2. **Prototype lane:** branches are named `prototype/<name>` and land under
   `prototypes/plugins/<name>/`. Production Sai must never depend on prototype
   code — the lane CI enforces this mechanically.
3. **1,200 added lines max per PR.** Hard budget (`pr-line-budget.yml`). Big
   work ships as slice stacks, each independently green. Deletions are free.
4. **Checks are green, non-negotiable.** Every status check on the PR must pass
   before merge. CI data-baseline jobs stay informational, never blocking.
5. **Backups before risk:** `/api/git/backup` tags the live VPS tree; the
   Latest / Last-approved toggle in the site UI switches between `main` tip
   and the approved tag. Approve a version from the version menu only after
   real-device review.
6. **Point releases:** each project's done level includes a new point release.

## Skill 3 — Validating work (agent-agnostic)

Run these in order. A step that fails stops the line — do not announce "done"
until all pass.

1. **Static syntax.** `node --check` every touched JS file; `python3 -m py_compile`
   every touched Python file.
2. **Headless harnesses.** Drive the real code in headless Chromium at 390×844
   (iPhone viewport): boot the town, fire the semantic events your change adds
   (`view.agentEvent(...)`), screenshot, and assert zero page errors. See
   `ci/` for the harness pattern.
3. **Endpoint sweep.** Against the deployed container: `/healthz` → 200,
   `/static/*` → 200, authenticated `/api/library/state` → 200 with
   `canon.drift: false`. Unauthenticated calls must 401 cleanly.
4. **Canon drift.** Recompute SHA baselines in `content/canon.json` after any
   visual change; the library-state endpoint must report no drift.
5. **Full traversal.** `ci/abm-check.py` walks every route at iPhone size and
   fails loudly on any page error, failed request, or blank render.
6. **Smooth live video.** Record one continuous 390×844 flow with zero crashes;
   watch the whole thing yourself before sending it on.
7. **Physical iPhone.** Browser proof is necessary but not sufficient. Done means
   zero bugs on Dezmond's physical iPhone — his approval is the gate before
   anything from ABM touches the Sai repo beyond this prototype lane.

## The tamagotchi contract (current UI behavior)

Characters are mood-driven, never random: per-persona mood 0–1 from real
interaction time in their portal plus the parent's daily schedule per activity
(parent approvals screen, 5-minute steppers). Mood decays with wall-clock
neglect; tiers pick the pose (happy bounce / idle / lonely droop). Characters
hang around their own portal at the round table; every third loop one
portal-visits a friend. Chat hero is tiny (0.45 scale): hops on the user bubble,
dives on reply, reads through the chat with a book. Semantic events:
`chat-user`, `chat-reply`, `task-done`/`quiz-correct`, `portal-enter`,
`portal-exit`, `travel`, `schedule` — all via `view.agentEvent(name, data)` or
the `window.__dcAgentEvent` broadcast.
