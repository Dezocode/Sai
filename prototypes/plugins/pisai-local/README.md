# PiS AI local harness prototype

This directory is an isolated prototype for routing Pi requests to a Mac-hosted
OpenAI-compatible gateway. It is not imported by Sai production code and does
not install, download, or serve model weights.

The Mac owns inference, model residency, RAM/swap safety, and route telemetry.
Pi owns user-facing hook selection, task metadata, and local durable memory.
Hostinger remains a control-plane/API consumer only; this prototype does not
copy or duplicate the Mac inference API onto Hostinger.

## Contract

1. Pi sends requests to the configured gateway URL, never directly to a model.
2. A Pi hook may select `coding`, `vision`, or `compact`; the gateway resolves
   the selected role to the model catalog currently available on the Mac.
3. The gateway must verify selected model, resident model, context, and memory
   state before forwarding.
4. Every request and hook emits the same correlation ID and a redacted,
   structured telemetry event.
5. Unavailable or unsafe routes fail closed; there is no silent fallback.
6. Long history is compacted in bounded chunks. Only a bounded active spec and
   structured ledgers are eligible for Pi memory; raw transcripts are not.

See [ARCHITECTURE.md](docs/ARCHITECTURE.md), [the environment contract](config/pisai-router.env.example), and [the routing schema](config/model-routing.schema.json).

The implementation and mocked end-to-end proof are supplied by the follow-up
router PR.
