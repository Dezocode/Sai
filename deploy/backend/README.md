# Sai backend deployment
Deploy `cmd/sai` as an immutable artifact. Promotion sequence: test -> build -> safe migration -> staging -> `/health` + `/ready` -> production. Keep runtime secrets outside Git. Container/orchestrator choice remains intentionally open until operational requirements justify it.
