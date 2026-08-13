#!/usr/bin/env python3
from pathlib import Path
import tempfile, json, shutil, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import architecture_guard
import feature_lock_guard

def main():
    pol=json.loads((ROOT/'.sai-quality/policies/quality-policy.json').read_text())
    reg=json.loads((ROOT/'.sai-quality/architecture/registry.json').read_text())
    results=[]
    bad=json.loads(json.dumps(reg)); bad['capabilities']['fault-dup']={'owner':bad['capabilities']['quality-control-plane']['owner']}
    results.append(('duplicate-owner', bool(architecture_guard.validate(ROOT,bad,pol))))
    with tempfile.TemporaryDirectory() as td:
        tr=Path(td); (tr/'services'/'policy-v2').mkdir(parents=True)
        (tr/'services'/'policy-v2'/'x.ts').write_text('export const x=1')
        results.append(('parallel-path', bool(architecture_guard.validate(tr,reg,pol))))
    with tempfile.TemporaryDirectory() as td:
        tr=Path(td)
        (tr/'.sai-quality/policies').mkdir(parents=True)
        shutil.copy2(ROOT/'.sai-quality/policies/quality-policy.json', tr/'.sai-quality/policies/quality-policy.json')
        (tr/'.sai-quality'/'FEATURES_LOCKED').write_text('locked\n')
        (tr/'apps'/'demo').mkdir(parents=True)
        (tr/'apps'/'demo'/'x.ts').write_text('export const x=1\n')
        results.append(('feature-lock-product-file', bool(feature_lock_guard.check(tr))))
    results.append(('suppression-required-fields', set(['id','tool','scope','owner','rationale','expires','evidence','regression_test']).issubset(set(pol['suppressions']['required_fields']))))
    failed=[n for n,ok in results if not ok]
    print(json.dumps({'fault_injection':results,'status':'PASS' if not failed else 'FAIL'},indent=2))
    if failed: sys.exit(1)
if __name__=='__main__': main()
