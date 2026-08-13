# Code health runtime evaluation

`scripts/verify-code-health --self-test` builds temporary git trees and
asserts:

| Fixture | Detector | Expected |
|---|---|---|
| oversized `.md` | bloat | FAIL |
| small `.md` | bloat | PASS |
| two identical files | duplicates | FAIL |
| two distinct files | duplicates | PASS |
| unreferenced `scripts/*` | orphans | FAIL |
| script mentioned in README | orphans | PASS |
| workflow missing `ci_marker` | ci-coverage | FAIL |
| workflow contains marker | ci-coverage | PASS |

CI runs `--self-test` **before** the live scan so a broken detector cannot
silently pass an empty or already-green tree.

Live scan (no fixtures committed — they would themselves trip bloat):

```
scripts/verify-code-health
```

Registry: `.ai/_config/code-health.yaml`. Policy: `.ai/shared/references/code-health.md`.
