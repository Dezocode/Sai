# Requests — task authorization intake (Layer 3/4)

Tracked task requests live at `.ai/requests/<task-id>/request.yaml`
(schema: `.ai/shared/schemas/task-request.schema.json`).

An unbound Cursor Cloud runtime may create a request and run
`scripts/sai-authorize-task`. If no applicable implementation agent
exists, the request state becomes `CONTRACT_REQUIRED` and Cora
(`ctr-admin`) must be assumed to draft a versioned contract.

Session cache `.git/sai-session.json` is not an authorization source.
Hooks and CI replay leases, revisions, and registry from Git.
