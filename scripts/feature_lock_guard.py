#!/usr/bin/env python3
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[1]

def check(root: Path, policy=None):
    root = Path(root)
    if policy is None:
        policy = json.loads((root/'.sai-quality/policies/quality-policy.json').read_text())['feature_lock']
    marker = root / policy['marker']
    cert = root / policy['unlock_certificate']
    allowed = set(policy['allowed_when_locked'])
    errs = []
    if marker.exists():
        for rr in policy['product_roots']:
            p = root / rr
            if not p.exists():
                continue
            for f in p.rglob('*'):
                if f.is_file() and f.name not in allowed:
                    errs.append(str(f.relative_to(root)))
        return errs
    if not cert.exists():
        return ['marker absent but unlock certificate missing']
    try:
        c = json.loads(cert.read_text())
    except Exception as e:
        return [f'invalid unlock certificate: {e}']
    if c.get('status') != 'UNLOCKED':
        return ['certificate not UNLOCKED']
    return []

def main():
    policy = json.loads((ROOT/'.sai-quality/policies/quality-policy.json').read_text())['feature_lock']
    marker = ROOT / policy['marker']
    errs = check(ROOT, policy)
    if marker.exists():
        if errs:
            print('FEATURE LOCK FAIL product implementation exists while locked:')
            print('\n'.join(' - '+x for x in errs[:100]))
            sys.exit(1)
        print('PASS feature lock active; no product implementation detected')
        sys.exit(0)
    if errs:
        print('FEATURE LOCK FAIL', '; '.join(errs))
        sys.exit(1)
    print('PASS feature unlock certificate present')

if __name__ == '__main__':
    main()
