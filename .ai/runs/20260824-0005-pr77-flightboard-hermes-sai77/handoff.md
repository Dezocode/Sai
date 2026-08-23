# Handoff — Flight-board telemetry bars (PR 77, Atomic solution F058)

Applies INBOX/solutions/pr77-F058.patch verbatim, plus two adversarial-review
hardening fixes before push: (1) /prs telemetry accumulates into a local map
committed to FLIGHT only when the WHOLE feed validates — a mid-feed invalid
card can no longer leak agent-sourced flightboard entries into an honest
src=sessions render or persist across polls (reviewer T1/T1b, reproduced on
shipped JS pre-fix); (2) verifierGated switched from unanchored substring
/verifier|aggregator/i (trivially spoofed by agent-authored progress.source)
to anchored allowlist ^(pr[-_])?aggregator$|^sai-verify on lowercased source,
with selftest probes for not-a-verifier / fake-aggregator-lol spoofs.
Evidence preserved: 0215 run consolidated to events.jsonl (HANDOFF event
satisfies verify-merge-handoff); metadata.json restored per
verify-semantic-hierarchy requirement. Gates green on this tree: --check ALL
PASS features=11 incl. 18 flight assertions; node --check emitted JS;
runtime probe ok1-ok7 exit=0; hierarchy OK; merge-handoff OK; 1096+/1200.
Draft only; no merge/ready/force-push.
