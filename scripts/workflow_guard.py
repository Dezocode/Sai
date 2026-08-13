#!/usr/bin/env python3
from pathlib import Path
import sys,re
ROOT=Path(__file__).resolve().parents[1]
required=['.github/workflows/sai-quality-os.yml','.github/workflows/sai-quality-nightly.yml']
errs=[]
for r in required:
    p=ROOT/r
    if not p.exists(): errs.append('missing '+r); continue
    s=p.read_text()
    if 'permissions:' not in s: errs.append(r+' missing permissions')
    if re.search(r'permissions:\s*write-all',s): errs.append(r+' uses write-all')
    for ref in re.findall(r'uses:\s*([^\s#]+)', s):
        if '@' in ref:
            ver=ref.rsplit('@',1)[1]
            if not re.fullmatch(r'[0-9a-fA-F]{40}', ver):
                errs.append(r+' unpinned action ref '+ref+' (G14 requires commit SHA)')
if errs:
    print('WORKFLOW FAIL\n'+'\n'.join(errs)); sys.exit(1)
print('PASS workflow structure/minimal-permission/action-pin guard')
