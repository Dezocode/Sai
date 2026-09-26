# App Build Manager — implementation source

This prototype lane entry is a registration, not a vendored copy. The full
implementation lives in its own repository and deployment, which keeps the
prototype lane's one-way isolation mechanically clean.

- **Source repo:** `dezocode-ui-collections`
- **Deploy, container, local paths, live URL:** private runbook only — never
  committed to this public repository.

Key paths inside the implementation:

| Path | What it is |
|---|---|
| `app.py` | Flask server: auth, library-state API, git ops, workbooks |
| `static/town3d.js` | The 3D canon town + tamagotchi care engine + agent event bus |
| `static/app.js` | SPA: splash, flows, Figma canvas, parent screens |
| `static/styles.css` | Liquid Glass UI, matte light/dark, zero green |
| `static/vendor/three.min.js` | Three.js r128 (MIT, see THIRD-PARTY-NOTICES.md) |
| `content/canon.json` | Canon manifest + SHA baselines (drift detection) |
| `ci/abm-check.py` | Zero-bug sweep: every route at 390×844, fails loudly |
| `LIBRARY.md` | Agent surface docs (events, jobs, care API) |

If the prototype graduates, graduation requires an explicit production PR and
normal production verification — code never graduates by file move alone.
