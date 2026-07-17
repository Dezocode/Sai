# Plan — CTO P1 push destination / refspec bypass

## Problem

`Bash(git push origin proj/splunk-clone/*)` matches
`git push origin proj/splunk-clone/ctr-code-splunky/x:main`, letting a
provisional contractor update `main`.

## Approach

1. Add Layer 3 `bash_deny_patterns` for push refspecs, force, delete, and
   direct pushes to `main`.
2. Mirror deny list in Splunky Claude settings and contract bootstrap.
3. Extend `scripts/verify-contractor-shell-allowlist` to evaluate allow∧¬deny
   and regression-test the refspec bypass.
