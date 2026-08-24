# Sai prototype plugin lane

Status: **merged enabling contract**. PR #75 established the architectural permission and authority boundaries for a non-shipping prototype-plugin lane. The `prototype/lane-enforcement` successor must now make that permission mechanically real before Sai Author UI work begins.

## Goal

Monaecode must be able to build real SwiftUI product prototypes under one canonical non-shipping plugin root while production remains protected by the Sai Design Language and `featureUIAllowed=false`. Canonical prototype root: `prototypes/plugins/`. Sai Author is the first prototype plugin; the lane must support fast product discovery without allowing experimental code or design choices to become production authority accidentally.

## Design inheritance: prototype from Sai, do not fork Sai

Sai Author is expected to become a Sai plugin feature. Prototype work therefore **should use and build on `SaiDesignLanguage` whenever an appropriate token, component, adaptive rule, accessibility primitive, motion rule, or interaction pattern already exists**. Existing Sai primitives are the default choice, not something to recreate locally.

Prototype freedom exists for genuine gaps. When the approved Sai Design Language cannot express an exploratory concept without distorting production design, the prototype may introduce a narrowly scoped plugin-local experimental primitive. Those experiments are discovery evidence only: they do not become Sai Design Language authority, may not be imported by shipping Sai targets, and must be explicitly upstreamed into `SaiDesignLanguage` (or deliberately rejected) before the concept graduates into production.

The desired migration path is: `SaiDesignLanguage` reuse -> plugin-local experiment only for missing concepts -> validate product direction -> upstream reusable primitive to SaiDesignLanguage -> production/plugin integration.


## Successor work

1. **`prototype/lane-enforcement` — current successor.** Implement the verifier-owned fail-closed exemption for `prototypes/plugins/`, near-prefix/path-escape rejection, candidate-JSON hardening, design-inheritance rules, production-to-prototype dependency isolation, CI triggers, and `sai-verify` mapping/proofs.
2. **`prototype/sai-author-shell` — only after lane enforcement merges.** Add a minimal runnable/buildable Sai Author prototype under `prototypes/plugins/author/`, prove macOS and iOS Simulator builds, and establish the continuation point for Monaecode.
3. Follow-on product prototyping: rich/structured editing, selection-aware AI actions, command palette, document library, provider configuration, and other Author product exploration.

## Required architecture

1. Production `SaiDesignLanguage`, `SaiFeatures`, `SaiMac`, and `SaiIOS` authority boundaries remain intact; `featureUIAllowed=false` is not globally changed merely to permit prototypes.
2. The prototype exemption/root is verifier-owned, fail-closed, and cannot be relocated or widened by candidate JSON, plugin metadata, symlinks, path traversal, or near-prefix naming; SwiftUI is permitted only inside the canonical lane while the production draft UI lock stays intact.
3. Prototype UI reuses `SaiDesignLanguage` by default; any plugin-local experimental design surface is narrow, explicit, and mechanically isolated from production. Shipping Sai targets must not depend on prototype modules — mechanically tested.
4. `sai-verify` maps the prototype tree and meaningful prototype build/proof surface without weakening trusted-kernel semantics; Go/OpenAPI remain authoritative for production domain/backend behavior.
5. Prototype visual/product decisions are exploratory evidence, not production authority; code cannot graduate to production by file move alone — graduation requires an explicit production PR and normal production verification.

## Sai Author bootstrap

The smallest real Sai Author prototype establishes a continuation point for product development across macOS and iOS/iPadOS. A root/editor placeholder and settings/configuration placeholder are sufficient for the `prototype/sai-author-shell` successor PR; do not build the full editor, AI workflows, persistence, collaboration, marketplace, downloadable-code runtime, or final plugin platform in either enabling successor.

## Adversarial acceptance and independent review gate

The successor's required adversarial matrix and its independent review gate are owned by `SAI-PROTOTYPE-LANE-ENFORCEMENT.md` and must be proven mechanically there; this contract does not restate them. The review bar is unchanged: draft until genuine independent Saul review passes on the exact final HEAD through the real Hostinger/Codex path with P0=P1=P2=0; older-head results are historical only, and any HEAD change resets the gate to pending.

## Merge gate

`prototype/lane-enforcement` is owner-ready only when its dedicated enforcement contract is satisfied mechanically on the exact final HEAD. `prototype/sai-author-shell` then carries the runnable/buildable Author requirements on its own exact final HEAD. Neither successor may mark itself ready or merge automatically; owner choice remains final.
