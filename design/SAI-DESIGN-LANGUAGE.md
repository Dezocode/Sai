# Sai Design Language

Single design authority for the production Sai Apple app. Separate from the OpenClaw prototype.

**Feature code may select Sai-approved choices; it may not create new design choices.**

Machine authority is `sai-design-language.json` (grid, type, color, borders, elevation, controls, layout, motion, accessibility, components, layers, visualization, media, source policy). Status is `foundation-draft` with `featureUIAllowed=false`. Numbers are a provisional grammar, not final aesthetic approval.

`apps/apple/Packages/SaiKit/Sources/SaiDesignLanguage/` is the only Swift tree allowed to translate raw visual values into semantic APIs. Enforcement roots are verifier-owned in `cmd/sai-design-check`; candidate JSON cannot widen them or skip bind. Missing `SaiDesignLanguage.swift` fails closed. While draft, product Views are locked outside that authority, including in `SaiMac`/`SaiIOS` shells. Thin shells may compose `SaiCanvas`/`SaiText`; they may not declare product Views. `SaiText` scales with Dynamic Type via `@ScaledMetric`.

Outside the authority, CI rejects raw hex, numeric padding/radii/frames/shadows/z-index, and raw system font sizes. Platform differences (macOS density vs iOS touch targets, compact/regular/wide) belong in the language, not in features.

`.github/workflows/sai-design-language.yml` is one result named **Sai Design Language**: schema, tests, source policy, `SaiKit` compile, `SaiMac`/`SaiIOS` compile. Later visual fixtures belong behind this same check.

To add a visual behavior: change the contract/component, update fixtures/tests, pass CI, then consume it. Do not bypass with a local one-off value.
