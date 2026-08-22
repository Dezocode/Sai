# Sai
The app for parents to give their children safe, parent-guided access to the internet and AI tools.

## Application foundation
The production application is being built as a native Apple client plus a Go core:

- **SwiftUI** for macOS, iPhone, and iPad presentation and Apple-framework adapters.
- **Go** for authoritative backend/domain behavior, APIs, persistence boundaries, integrations, and event processing.
- **Sai Design Language** as a single CI-enforced visual and interaction contract shared by every Apple surface.
- **`sai-verify`** remains independent repository verification infrastructure; it is not the product backend.

Start with [`docs/architecture/SAI-APP-FOUNDATION.md`](docs/architecture/SAI-APP-FOUNDATION.md).
