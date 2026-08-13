#!/usr/bin/env python3
from pathlib import Path
import json, sys
root=Path(__file__).resolve().parents[1]
files=list((root/'.sai-quality').rglob('*.json'))
errs=[]
for p in files:
    try: json.loads(p.read_text())
    except Exception as e: errs.append(f'{p.relative_to(root)}: {e}')
if errs:
    print('\n'.join(errs)); sys.exit(1)
needed=['.sai-quality/gates.json','.sai-quality/policies/quality-policy.json','.sai-quality/architecture/registry.json','.sai-quality/toolchain.lock.json']
for n in needed:
    if not (root/n).exists(): errs.append('missing '+n)
if errs:
    print('\n'.join(errs)); sys.exit(1)
print(f'PASS JSON/config integrity ({len(files)} JSON files)')
