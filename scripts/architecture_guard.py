#!/usr/bin/env python3
from pathlib import Path
import json, sys, tempfile, shutil
ROOT=Path(__file__).resolve().parents[1]

def validate(root:Path, reg:dict, policy:dict):
    errs=[]
    owners={}
    for cap, spec in reg.get('capabilities',{}).items():
        owner=spec.get('owner')
        if not owner: errs.append(f'capability {cap} has no owner'); continue
        if owner in owners: errs.append(f'duplicate capability owner path {owner}: {owners[owner]} and {cap}')
        owners[owner]=cap
    contract_owners={}
    for name,spec in reg.get('contracts',{}).items():
        owner=spec.get('owner')
        if not owner: errs.append(f'contract {name} has no owner'); continue
        if owner in contract_owners: errs.append(f'duplicate contract owner {owner}: {contract_owners[owner]} and {name}')
        contract_owners[owner]=name
    # path anti-entropy for product roots
    badtokens=policy['architecture'].get('forbidden_path_tokens',[])
    for rr in policy['feature_lock']['product_roots']:
        p=root/rr
        if not p.exists(): continue
        for d in [x for x in p.rglob('*') if x.is_dir()]:
            low=d.name.lower()
            for tok in badtokens:
                if tok in low:
                    errs.append(f'forbidden parallel-path token {tok} in {d.relative_to(root)}')
    return errs

def main():
    cmd=sys.argv[1] if len(sys.argv)>1 else 'check'
    reg=json.loads((ROOT/'.sai-quality/architecture/registry.json').read_text())
    pol=json.loads((ROOT/'.sai-quality/policies/quality-policy.json').read_text())
    if cmd=='check':
        errs=validate(ROOT,reg,pol)
        if errs: print('ARCHITECTURE FAIL\n'+'\n'.join('- '+e for e in errs)); sys.exit(1)
        print('PASS architecture registry uniqueness/path policy'); return
    if cmd=='self-test':
        # Negative: duplicate owner must fail
        bad=json.loads(json.dumps(reg)); bad['capabilities']['synthetic-duplicate']={'owner':bad['capabilities']['quality-control-plane']['owner']}
        if not validate(ROOT,bad,pol): print('SELFTEST FAIL duplicate owner not caught'); sys.exit(1)
        # Positive: original must pass current structure
        if validate(ROOT,reg,pol): print('SELFTEST FAIL baseline registry invalid'); sys.exit(1)
        print('PASS architecture guard positive + negative tests'); return
    print('usage: architecture_guard.py check|self-test'); sys.exit(2)
if __name__=='__main__': main()
