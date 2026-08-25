# Handoff — hook event vocabulary declaration
Task-ID: 20260825-0745-hook-vocabulary-grunt
PR: Dezocode/Sai#150 (draft, grunt-owned)
Author: grunt (ox-alpha)
## What
docs/hook-vocabulary.md: declares the 19 validated prototype events + 2 Harness-native events, normalized payloads, declared-unsupported rule, production-authority invariants.
## Why
#150 contract requires the typed event vocabulary before adapter work; declaration over fabrication per roadmap.
## Verify
Table covers all 19 hooks.json events (count them); unsupported surfaces declared; no production .cursor changes in this commit.
