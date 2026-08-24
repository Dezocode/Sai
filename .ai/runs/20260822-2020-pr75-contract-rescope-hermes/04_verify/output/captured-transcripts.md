== rescope evidence ==
$ git rev-parse HEAD
5389fbdb5e2527048ac9691ee5347445e8177cf6
[before staging handoff/evidence files]

$ scripts/verify-semantic-hierarchy
verify-semantic-hierarchy: OK
[exit=0]

$ scripts/verify-agent-audit -n 20 HEAD
verify-agent-audit: OK (-n 20 HEAD)
[exit=0]

$ scripts/verify-merge-handoff origin/main..HEAD
FAIL 5389fbd: task-id 20260822-2020-pr75-contract-rescope-hermes has no handoff.md or HANDOFF event
verify-merge-handoff: FAILED (1 problem(s))
[exit=1 expected: this run's handoff not yet staged]
