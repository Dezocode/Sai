#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys, json
root=Path(__file__).resolve().parents[1]
required=['.ai','.cursor','.github','AGENTS.md','.sai-quality']
missing=[p for p in required if not (root/p).exists()]
if not (root/'.sai-quality/FEATURES_LOCKED').exists() and not (root/'.sai-quality/FEATURES_UNLOCKED.json').exists():
    missing.append('.sai-quality/FEATURES_LOCKED or FEATURES_UNLOCKED.json')
if missing:
    print('PREFLIGHT FAIL missing:', ', '.join(missing)); sys.exit(1)
try:
    top=subprocess.check_output(['git','rev-parse','--show-toplevel'], cwd=root, text=True).strip()
    if Path(top).resolve()!=root.resolve():
        print('PREFLIGHT FAIL wrong git root', top); sys.exit(1)
    branch=subprocess.check_output(['git','branch','--show-current'], cwd=root, text=True).strip()
    status=subprocess.check_output(['git','status','--porcelain'], cwd=root, text=True)
except Exception as e:
    print('PREFLIGHT FAIL git unavailable:',e); sys.exit(1)
print(json.dumps({'status':'PASS','root':str(root),'branch':branch,'dirty':bool(status.strip()),'note':'dirty state is evidence, not automatic failure; preserve existing changes'}, indent=2))
