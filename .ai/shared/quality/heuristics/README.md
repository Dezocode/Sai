# Heuristic quality CI

Heuristic CI supplements deterministic checks for recurring Saul defect classes that are not cheaply or perfectly decidable. It is subordinate to the Decision-0005 registry and must not become a parallel framework.

A heuristic check must be bounded, reproducible enough for CI, scoped to a named invariant/defect class, and prove usefulness with positive and negative fixtures. It must report what evidence triggered the finding and avoid claiming certainty it does not possess.

Preferred order:

1. parser/schema/static invariant;
2. AST/import/dependency/state-graph analysis;
3. bounded semantic heuristic over structured facts;
4. model-assisted heuristic only when cheaper deterministic approaches cannot establish the needed property and the cost/trigger is explicitly bounded.

A heuristic that repeatedly produces false positives or can be trivially bypassed is itself a quality defect. Exemptions must be centralized and reviewed; inline convenience ignores are not the default escape hatch.

Every heuristic is registered in `.ai/_config/code-health.yaml` with its command, activation state, fixture contract, owner, and the Saul finding/defect class that caused its creation.
