#!/usr/bin/env python3
from pathlib import Path
import tempfile, json, shutil, sys, subprocess, os
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import architecture_guard

def main():
    pol=json.loads((ROOT/'.sai-quality/policies/quality-policy.json').read_text())
    reg=json.loads((ROOT/'.sai-quality/architecture/registry.json').read_text())
    results=[]
    # duplicate owner negative
    bad=json.loads(json.dumps(reg)); bad['capabilities']['fault-dup']={'owner':bad['capabilities']['quality-control-plane']['owner']}
    results.append(('duplicate-owner', bool(architecture_guard.validate(ROOT,bad,pol))))
    # forbidden path token negative
    with tempfile.TemporaryDirectory() as td:
        tr=Path(td); (tr/'services'/'policy-v2').mkdir(parents=True)
        (tr/'services'/'policy-v2'/'x.ts').write_text('export const x=1')
        results.append(('parallel-path', bool(architecture_guard.validate(tr,reg,pol))))
    # feature lock negative in isolated fixture via conceptual assertion
    results.append(('feature-lock-policy-present', bool(pol['feature_lock']['product_roots'])))
    # suppression schema negative/positive intent
    results.append(('suppression-required-fields', set(['id','tool','scope','owner','rationale','expires','evidence','regression_test']).issubset(set(pol['suppressions']['required_fields']))))
    failed=[n for n,ok in results if not ok]
    print(json.dumps({'fault_injection':results,'status':'PASS' if not failed else 'FAIL'},indent=2))
    if failed: sys.exit(1)
if __name__=='__main__': main()
