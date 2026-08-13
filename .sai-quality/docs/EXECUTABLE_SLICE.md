# Executable slice

Until co-founders approve G04+ (decision 0005):

```bash
python3 scripts/bootstrap_phase0.sh
python3 scripts/qualityctl.py build --through G03
python3 scripts/fault_injection.py
```

`build --through G15` must exit 3 at G04 `DEFERRED`. Unlock stays blocked. Docs in this directory; do not put Quality OS runbooks back at the repository root.
