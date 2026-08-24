# Handoff — 20260824-0624-saul-97341070772-pages-concurrency-atomic-ox-alpha

## What changed - feature-maps-pages.yml concurrency group: pages-<head-sha> -> pages-<event_name>-<head-sha>. Push and pull_request runs for the same SHA share the old key; either could cancel the other, leaving PR validation without a build result. Mirrors the icm- fix pattern. ## Verification YAML parses; workflow triggers unchanged otherwise. Handoff backfilled cooperatively so verify-merge-ha
