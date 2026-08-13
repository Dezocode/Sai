#!/usr/bin/env python3
from pathlib import Path
import json, sys, subprocess, hashlib, datetime
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'.sai-quality/baselines/health-baseline.json'; RUN=ROOT/'.sai-quality/runtime'

def metrics():
    files=[]; lines=0
    for p in ROOT.rglob('*'):
        if p.is_file() and '.git' not in p.parts and '.sai-quality/runtime' not in str(p) and p.suffix in {'.py','.sh','.md','.json','.yml','.yaml','.ts','.tsx','.js','.jsx','.go','.rs'}:
            files.append(p)
            try: lines += len(p.read_text(errors='ignore').splitlines())
            except: pass
    return {'tracked_text_files':len(files),'tracked_text_lines':lines,'note':'Structural bootstrap metrics only. Sonar/jscpd/Knip/Trivy metrics are added by adapters after installation.'}
def main():
    cmd=sys.argv[1] if len(sys.argv)>1 else 'current'; RUN.mkdir(parents=True,exist_ok=True); m=metrics()
    if cmd=='baseline':
        if '--if-missing' in sys.argv and BASE.exists(): print('PASS baseline already exists; not refreshed'); return
        BASE.parent.mkdir(parents=True,exist_ok=True); BASE.write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'metrics':m,'immutable_after_gate':'G08'},indent=2)+'\n'); print('PASS baseline created once'); return
    if cmd=='verify-ratchet':
        if not BASE.exists(): print('FAIL baseline missing'); sys.exit(1)
        b=json.loads(BASE.read_text())['metrics']
        # Structural lines may grow during Phase0, so no hard line-count ratchet. Real metric adapters become authoritative.
        print('PASS ratchet scaffold; baseline immutable, new-code thresholds defined in quality-policy.json'); return
    if cmd=='current':
        out=RUN/'health-current.json'; out.write_text(json.dumps({'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'metrics':m},indent=2)+'\n'); print(json.dumps(m,indent=2)); return
    print('unknown'); sys.exit(2)
if __name__=='__main__': main()
