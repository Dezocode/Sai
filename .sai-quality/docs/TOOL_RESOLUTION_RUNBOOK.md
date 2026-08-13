# Tool Resolution Runbook — Gate G04

`toolchain.lock.json` intentionally ships unresolved. This prevents a stale artifact from pretending that August 2026 tool versions are permanent.

Cursor must, for each enabled or detected tool:

1. open the official source listed in `.sai-quality/provenance/tool-sources.json`;
2. identify the current stable release, not a prerelease;
3. inspect current security advisories relevant to that release;
4. verify current license at the resolved tag/version;
5. choose an execution mode compatible with Cursor Cloud/CI;
6. install into an isolated quality-tool environment or service;
7. record exact version;
8. record container digest, binary checksum, provenance reference, or package-lock integrity as applicable;
9. run `toolchain_manager.py verify-lock`;
10. commit the lock and generated configuration atomically.

Do not commit `latest`. Do not install a deprecated action runtime. Do not silently fall back to a random fork when an official source is unavailable.
