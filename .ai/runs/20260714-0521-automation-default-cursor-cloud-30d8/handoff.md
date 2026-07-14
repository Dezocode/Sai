# Handoff — 20260714-0521-automation-default-cursor-cloud-30d8

## State

Initialization now ends, for every agent of any role, with the same
sequence: environment following all hooks and rules in `.ai` → the agent
asks its principal **"What will you name me, and what will my role title
be?"** → states its purpose back for confirmation and sticks to it →
generates and offers a Cursor automation profile built from that identity.
Profiles match the real Automations UI and all embed one identical SAI
protocol block, so agents and automations follow the same Slack, GitHub,
and CI protocols; only the role-specific purpose differs.

## Evidence

- Commit `495f7b4` pushed; `git ls-remote` equals local HEAD.
- Verification matrix in `04_verify/output/verification.md` (9 items):
  generator output reviewed against dezocode's UI screenshots; verifier
  rejects active agents lacking a confirmed purpose; registry restored
  byte-identical after negative tests.
- HANDOFF + profile offer delivered to #agentupdates
  (ts 1784006729.276789); PLAN preceded edits (ts 1784006510.675199).

## Open items

1. dezocode answers the Phase 5 question for this agent (name + role
   title); agent then confirms purpose, regenerates its profile with the
   final identity, and flips its registry entry to `active`.
2. dezocode creates the automation from the offered profile and runs it
   once (`[SAI][VERIFY]` message confirms).
3. Slack token, Drive remote, fork propagation — unchanged.

## Next safe action

Co-founder review of PR #3; dezocode's Phase 5 grant.
