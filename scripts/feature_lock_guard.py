#!/usr/bin/env python3
from pathlib import Path
import json, sys
root=Path(__file__).resolve().parents[1]
policy=json.loads((root/'.sai-quality/policies/quality-policy.json').read_text())['feature_lock']
marker=root/policy['marker']; cert=root/policy['unlock_certificate']
allowed=set(policy['allowed_when_locked'])
if marker.exists():
    bad=[]
    for rr in policy['product_roots']:
        p=root/rr
        if not p.exists(): continue
        for f in p.rglob('*'):
            if f.is_file() and f.name not in allowed:
                bad.append(str(f.relative_to(root)))
    if bad:
        print('FEATURE LOCK FAIL product implementation exists while locked:')
        print('\n'.join(' - '+x for x in bad[:100])); sys.exit(1)
    print('PASS feature lock active; no product implementation detected'); sys.exit(0)
if not cert.exists():
    print('FEATURE LOCK FAIL marker absent but unlock certificate missing'); sys.exit(1)
try: c=json.loads(cert.read_text())
except Exception as e:
    print('FEATURE LOCK FAIL invalid unlock certificate',e); sys.exit(1)
if c.get('status')!='UNLOCKED':
    print('FEATURE LOCK FAIL certificate not UNLOCKED'); sys.exit(1)
print('PASS feature unlock certificate present')
