# Handoff — 20260824-0640-pr77-spoof-pr-close-ox-alpha

## What changed - loadPrs flattening: {...a,pr:pk} — parent group's validated key wins; an agent row carrying its own pr ("__proto__", other numbers) can no longer misattribute itself to another PR card (Saul 97342571251). - --check needle updated from out.push({pr:pk,...a}) to the new spread order; selftest adds spoof-row lock. ## Verification py_compile OK; --selftest ALL PASS; --check ALL PASS 
