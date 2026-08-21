# Production Go internals

Create focused packages here as product behavior arrives. Planned domains are `api`, `auth`, `family`, `policy`, `devices`, `activity`, `notifications`, `persistence`, and `integrations`. Do not pre-build empty abstraction layers: create a package when it owns real behavior and tests.

Dependency direction is transport -> domain/service -> persistence/integration ports. `internal/app` owns process composition/lifecycle, not product policy.
