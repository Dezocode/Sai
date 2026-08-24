# Internal Browser pane

Cursor's built-in Browser is the internal pane. Attach it with `@Browser` in chat. The built-in Browser subagent drives it through MCP so noisy DOM snapshots stay out of the parent context.

On Cloud Agent VMs, GUI proof also goes through the `computerUse` subagent (mouse and keyboard on the remote desktop). This image has Chrome at `/usr/bin/google-chrome` and `/usr/bin/google-chrome-stable`.

## When to use which

| Need | Use |
|---|---|
| Read a page the user already opened in the IDE Browser pane | `@Browser` context the user attached |
| Click, type, or snapshot a live page without a product UI | Built-in Browser subagent |
| Prove a GUI change on this Cloud Agent desktop | `Task` `subagent_type: "computerUse"` plus `RecordScreen` for walkthroughs |
| Fetch a public docs URL as Markdown | `WebFetch` or Bright Data `scrape_as_markdown` |
| Search Google/Bing/Yandex | Bright Data `search_engine`, never scrape the SERP URL |

## Cloud Agent rules

- Do not claim a Browser pane demo unless `computerUse` or `@Browser` actually ran.
- Do not kill Chrome or desktop processes by name. If a process must stop, use its PID.
- Leave apps running after GUI tests so the operator can continue.
- Artifacts go under `/opt/cursor/artifacts/` with snake_case names. Reference images with HTML `img` tags and videos with HTML `video` tags.

## Environment

The personal Cloud Agent environment already includes Chrome. Do not add `chromeExecutablePath` to a committed `environment.json`. That field is not in the current public schema, and a repo `environment.json` would override the dashboard environment. See `environment.md`.
