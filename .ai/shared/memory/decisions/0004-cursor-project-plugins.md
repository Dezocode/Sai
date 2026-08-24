# 0004 — Cursor project plugins via `.cursor/settings.json`

- Date: 2026-08-13
- Task-ID: 20260813-0113-pstack-plugin-install-cursor-cloud
- Status: accepted
- Approver: dezocode (requested `/add-plugin pstack` and install into `.ai`
  for cloud and local command input, 2026-08-13)

## Decision

Enable Cursor Marketplace plugins for this repository by committing
`.cursor/settings.json` with `plugins.<slug>.enabled: true`. Index each
enabled plugin under `.ai/plugins/<slug>/` as ICM documentation. Do not
treat `.ai/` as a Cursor plugin loader.

## Context

dezocode asked to install pstack so it is executable from command input in
Cloud Agent and local Cursor sessions, and also recorded under `.ai/`.
Cursor Cloud VMs do not inherit user-scoped `/add-plugin` installs from a
laptop. Project-scoped enablement in the repo is the path that both
environments read.

## Alternatives considered

- **User-scoped `/add-plugin pstack` only** — rejected; Cloud Agents do not
  get `~/.cursor` from the operator's machine.
- **Vendor the full pstack tree into `.ai/plugins/pstack/`** — rejected as
  the load path; Cursor does not scan `.ai/` for slash commands. A vendored
  copy would go stale and would not register `/poteto-mode`.
- **Copy pstack skills into `.cursor/skills/`** — rejected; duplicates
  marketplace skill names in the `/` picker once the plugin also loads.
- **`environment.json` plugins key** — rejected; that schema has no
  `plugins` field.

## Rationale

`.cursor/settings.json` is the documented project-scope install (pstack's
own `FOR_AGENTS.md` writes the same snippet). `.ai/plugins/` keeps ICM
Layer 0/3 maps honest: agents can see which Cursor plugins this repo
enables without confusing documentation with the loader.

## Consequences

- First plugin: pstack (`/poteto-mode` and related skills).
- New Cloud Agents on a commit that includes the settings file should
  materialize the plugin into the VM cache. The enabling session itself
  cannot hot-load it.
- `/setup-pstack` user-home rules do not apply in Cloud Agents; shared
  model routing belongs in `.cursor/rules/pstack-models.mdc` if desired.
- Adding another plugin follows `.ai/plugins/README.md`.

## Supersedes

Nothing. Complements decision 0002 (runtime adapters): Cursor-specific
plugin enablement stays in `.cursor/`, with an ICM index under `.ai/`.
