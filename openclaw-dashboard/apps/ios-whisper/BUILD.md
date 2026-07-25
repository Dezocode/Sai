# BUILD — iPhone Whisper app

1. SwiftUI: pair with Gateway on VPS (OpenClaw node pairing flow).
2. Whisper / Speech: voice capture → transcript → send to Gateway session.
3. Push notification for approval requests from VPS tools.
4. Smoke: voice command → VPS log entry → optional Slack `[SAI][VERIFY]` echo.
5. Zero blocking errors on documented flows (organization gate).

Coordinate with `apps/desktop/` for shared auth documentation only — not shared secrets.
