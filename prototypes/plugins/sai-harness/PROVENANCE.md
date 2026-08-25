# Provenance & license

Sai Harness is a prototype derived from the Atomic CLI harness
(bastani-inc/atomic, MIT) and the OpenBot channel architecture pattern
(CopilotKit/OpenBot, MIT), per .sai/hooks.json provenance block and the
#146 validated experiments (branch prototype/cross-intercom-lane @
74cfd78e2050d848dff058571d962deca210c4b9, converged here per #148 mission).

- License: MIT, inherited from upstream sources; this lane adds no new license terms.
- Removability: deleting prototypes/plugins/sai-harness/ leaves production
  Sai build/test green (standing invariant; T7 gate).
- Authority: this prototype has zero verifier/graduation/merge authority.
  sai-verify remains the sole boundary authority; production .cursor is untouched.
