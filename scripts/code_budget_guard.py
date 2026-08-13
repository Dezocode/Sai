#!/usr/bin/env python3
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
pol=json.loads((ROOT/'.sai-quality/policies/quality-policy.json').read_text())
maxlines=pol['complexity']['source_file_hard_max_lines']
exts={'.py','.ts','.tsx','.js','.jsx','.go','.rs','.java','.kt','.swift'}
roots=[ROOT/'.sai-quality', ROOT/'scripts'] + [ROOT/r for r in pol['feature_lock']['product_roots']]
viol=[]
for base in roots:
    if not base.exists(): continue
    for p in base.rglob('*'):
        if not p.is_file() or p.suffix not in exts: continue
        if any(x in p.parts for x in ('node_modules','dist','build','coverage','runtime','generated','vendor')): continue
        try: n=len(p.read_text(errors='ignore').splitlines())
        except Exception: continue
        if n>maxlines: viol.append((str(p.relative_to(ROOT)),n))
if viol:
    print('CODE BUDGET FAIL hard file-size limit exceeded:')
    for f,n in viol: print(f' - {f}: {n} > {maxlines}')
    sys.exit(1)
print('PASS hard source-file budget')
