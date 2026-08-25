# Prototype hook event vocabulary (declared, not fabricated)

Scope: the canonical Sai Harness prototype hook bus (#150). This declares the
event vocabulary the prototype bus normalizes. Production root `.cursor`
authority is untouched; nothing here bypasses or replaces `sai-verify` hooks.
Prototype tier is failClosed:false — hooks are observers and must never block
a user prompt.

## Events (from the validated cross-intercom prototype, .sai/hooks.json)

| Event | Payload (normalized) | Sync | Notes |
|---|---|---|---|
| sessionStart | cwd, session id, agent identity | sync | lane-connector reconcile binds here |
| sessionEnd | cwd, session id | sync | triggers grokbot hook |
| beforeSubmitPrompt | prompt text, aspect hints | sync | aspectizer binds here |
| preToolUse | tool name, args digest | sync | matcher `.*` required; empty matcher fails hooks_ok |
| postToolUse | tool name, result digest, duration | sync | |
| postToolUseFailure | tool name, error class | sync | 2 consecutive → debugger hook (§9) |
| beforeShellExecution | command, cwd | sync | |
| afterShellExecution | command, exit code, duration | sync | |
| beforeMCPExecution | server, tool, args digest | sync | |
| afterMCPExecution | server, tool, status | sync | |
| beforeReadFile | path | sync | |
| afterFileEdit | path, diff digest | sync | |
| subagentStart | agent name, task digest | sync | |
| subagentStop | agent name, outcome | sync | |
| preCompact | token usage, keep-target | sync | |
| stop | turn summary | sync | grokbot tick fires (wake contract, loop_limit) |
| afterAgentResponse | response digest | sync | grokbot tick fires |
| afterAgentThought | thought digest | sync | |
| workspaceOpen | path | sync | grokbot flightboard fires |
| harnessTick | tick number, interval | async | Harness-native; 600s daemon authoritative |
| harnessHeartbeat | pid, timestamp | async | Harness-native; stale → respawn |

## Declared unsupported (never fabricated)

Cloud Agents do not run sessionStart/sessionEnd, before/afterMCPExecution, or
workspaceOpen. Any runtime surface not listed above is declared unsupported in
adapter docs rather than synthesized. Adapters (#150 scope) map runtime-native
events onto this vocabulary; events with no runtime source stay declared-absent.

## Invariants
- Prototype-local only; production `.cursor/hooks.json` sai-verify wiring is authority.
- Unsupported ≠ skipped: absence is declared, observable, and testable.
- Bounded queues; no busy-poll; the 600s daemon remains the authoritative scheduler.
