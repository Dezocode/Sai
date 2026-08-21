# Sai Design Language

This directory is the **single design authority for the production Sai Apple app**. It is intentionally separate from the OpenClaw dashboard prototype.

## Rule

**Feature code may select from Sai-approved design choices; feature code may not create new design choices.**

The machine authority is `sai-design-language.json`. It defines the spacing grid, typography roles, colors, borders/radii, elevation, controls and states, adaptive widths/layout rules, motion, accessibility, component vocabulary, layers, data visualization, media treatment, and source-code policy.

The current status is `foundation-draft` and `featureUIAllowed=false`. The numbers in the JSON establish a complete provisional grammar for design work and CI, but they are not final aesthetic approval. Product feature UI stays locked until the design phase explicitly changes that flag after the language, fixtures, and baselines are approved.

## Source ownership

`apps/apple/Packages/SaiKit/Sources/SaiDesignLanguage/` is the only Swift location allowed to translate raw visual values into semantic APIs such as `SaiSpacing.section`, `SaiTextStyle.body`, `SaiButton`, or `SaiAdaptiveLayout`.

Outside that authority, CI rejects common arbitrary visual literals: raw hex colors, numeric padding, numeric corner radii, raw system font sizes, fixed numeric frame geometry, shadow radii, and z-index values. This starts strict and should gain AST-aware checks as the Swift implementation grows.

Platform differences are part of the language, not exceptions invented by features. macOS may use denser pointer controls while iOS preserves minimum touch targets; compact/regular/wide behavior is chosen by shared adaptive components.

## One CI result

`.github/workflows/sai-design-language.yml` reports one required result named **Sai Design Language**. Internally it validates the contract, runs verifier tests, scans Swift source policy, and compiles the shared Swift package on macOS.

Visual regression belongs behind the same check when canonical fixtures are implemented: component/state galleries at fixed macOS, iPhone, and iPad sizes with intentional baseline updates.

## Changing the language

When a feature needs a visual behavior the contract does not contain:

1. change the design contract/component first;
2. add or update its fixture and tests;
3. make the design CI pass;
4. then consume it from feature code.

Do not bypass the contract with a local one-off value.
