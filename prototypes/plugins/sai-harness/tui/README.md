# tui — consolidated from validated cross-intercom prototype (.sai/hooks), behavior preserved, prototype tier failClosed:false.

## Owner attach & steer doors
- Attach: `tmux attach -t <session>` — read-only observation by default; the
  owner's keystrokes are the only write path into a repl besides the audited
  gateway. Agents never attach to each other.
- Steer/prompt: via the TUI (i=inject prompt, s=steer) or directly through
  `gateway/audit-gateway.sh owner-steer` — every delivery is decided+recorded
  in the audit ledger before acting. Delivery to a dead session is refused and
  parked for replay (never silently dropped).
