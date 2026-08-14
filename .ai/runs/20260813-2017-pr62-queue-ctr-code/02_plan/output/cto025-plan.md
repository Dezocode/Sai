# Plan — CTO-025 merge-activation + quality package (A-010/v10)

Classification: REQUIRED_FOR_CURRENT_BLOCKER (workflows/tests/threat-trace)
and REQUIRED_FOR_FINAL_MERGE_QUALITY (profile, arch review, merge package,
anti-ballooning). Do not PASS. Do not merge. Do not push.

1. Retire `on: pull_request` from `saul-review.yml`; keep `workflow_dispatch`.
2. Harden trusted `pull_request_target` as DATA-only candidate checkout.
3. Replace fixture `transitional-pr-trigger-kept` with
   `candidate-pr-trigger-retired`. Keep evil-run isolation and
   `cto021-not-faked-on-main`.
4. Compact threat-trace, quality-profile, architectural-review,
   merge-readiness under the contract tree. Copy via `sai_auth_package.py`.
5. Warning-only `.ai/_config/pr-ballooning.yaml`.
6. Ledger: reframe CTO-025 to IMPLEMENTED_AWAITING_SAUL; append
   B-META-P0-001 / B-QUALITY-001 / B-MERGE-PKG-001 without PASS.
   Keep CTO-026 TRIAGED. Do not rework CTO-015..021/024/028/029.

Task-ID remains `20260813-2017-pr62-queue-ctr-code`.
