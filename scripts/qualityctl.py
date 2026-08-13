#!/usr/bin/env python3
from pathlib import Path
import json, sys, subprocess, datetime, hashlib, shutil, argparse, os
ROOT=Path(__file__).resolve().parents[1]
Q=ROOT/'.sai-quality'; STATE=Q/'runtime/state.json'; GATES=Q/'gates.json'; POLICY=Q/'policies/quality-policy.json'; EVID=Q/'runtime/evidence'

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def gitsha():
    try: return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except: return None
def load_gates(): return json.loads(GATES.read_text())['gates']
def load_state():
    if not STATE.exists(): init()
    return json.loads(STATE.read_text())
def save(s): STATE.parent.mkdir(parents=True,exist_ok=True); STATE.write_text(json.dumps(s,indent=2)+'\n')
def init():
    STATE.parent.mkdir(parents=True,exist_ok=True)
    if not STATE.exists(): shutil.copy2(Q/'state.template.json',STATE)
    print('state:',STATE.relative_to(ROOT))
def run_cmd(cmd):
    p=subprocess.run(cmd,cwd=ROOT,shell=True,text=True,capture_output=True)
    return {'cmd':cmd,'returncode':p.returncode,'stdout':p.stdout[-20000:],'stderr':p.stderr[-20000:]}
def evidence(gate,status,commands,mode):
    key=gitsha() or 'working-tree'; d=EVID/key/gate; d.mkdir(parents=True,exist_ok=True)
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    data={'gate':gate,'status':status,'timestamp':now(),'git_sha':gitsha(),'mode':mode,'policy_digest':sha(POLICY),'commands':commands}
    p=d/(stamp+'.json'); p.write_text(json.dumps(data,indent=2)+'\n'); return str(p.relative_to(ROOT))
def gate_index(gates,id):
    for i,g in enumerate(gates):
        if g['id']==id:return i
    raise SystemExit('unknown gate '+id)
def execute_gate(g,write=True,mode='fast',include_build=False):
    commands=[]
    if include_build:
        for a in g.get('build',[]):
            r=run_cmd(a['cmd']); r['id']=a['id']; r['phase']='build'; commands.append(r)
            if r['returncode']!=0: break
    if not commands or commands[-1]['returncode']==0:
        for c in g.get('verify',[]):
            # avoid recursive qualityctl deep-preunlock calling itself during non-G15 verification
            if g['id']=='G15' and c['id']=='deep-preunlock' and mode!='deep': continue
            r=run_cmd(c['cmd']); r['id']=c['id']; r['phase']='verify'; commands.append(r)
            if r['returncode']!=0: break
    ok=all(c['returncode']==0 for c in commands)
    status='PASS' if ok else 'FAIL'; ev=evidence(g['id'],status,commands,mode)
    if write:
        s=load_state(); attempts=s.setdefault('attempts',{}); attempts[g['id']]=attempts.get(g['id'],0)+(0 if ok else 1)
        if ok:
            if g['id'] not in s['passed']: s['passed'].append(g['id'])
            s['failed']=[x for x in s.get('failed',[]) if x!=g['id']]
        else:
            if g['id'] not in s['failed']: s['failed'].append(g['id'])
            if attempts[g['id']]>=3: s['status']='BLOCKED'
        s['last_evidence']=ev; save(s)
    print(f"{g['id']} {status} evidence={ev}")
    if not ok:
        bad=next(c for c in commands if c['returncode']!=0)
        print(bad['stdout']); print(bad['stderr'],file=sys.stderr)
    return ok

def cumulative(through,mode='fast',write=False):
    gates=load_gates(); idx=gate_index(gates,through); ok=True
    for g in gates[:idx+1]:
        if not execute_gate(g,write=write,mode=mode,include_build=False): ok=False; break
    return ok

def cmd_build(through):
    gates=load_gates(); end=gate_index(gates,through); s=load_state()
    if s.get('status')=='BLOCKED': print('BLOCKED: clear only after changed strategy and evidence; inspect state/evidence'); return 2
    for i,g in enumerate(gates[:end+1]):
        if g['id'] in s.get('passed',[]): continue
        print('\n=== BUILD '+g['id']+' '+g['name']+' ===')
        if not execute_gate(g,write=True,mode='fast',include_build=True):
            return 1
        # Recursive prior fast invariants
        if not cumulative(g['id'],mode='fast',write=False): return 1
        if g.get('deep_checkpoint'):
            if not cumulative(g['id'],mode='deep',write=False): return 1
        s=load_state(); s['current_gate']=gates[i+1]['id'] if i+1<len(gates) else 'G15'; s['status']='READY'; save(s)
    return 0

def unlock():
    gates=load_gates(); required=[g for g in gates if g.get('required_for_unlock')]
    s=load_state(); missing=[g['id'] for g in required if g['id'] not in s.get('passed',[])]
    if missing: print('UNLOCK BLOCKED gates not passed: '+','.join(missing)); return 1
    if not cumulative(required[-1]['id'],mode='deep',write=False): print('UNLOCK BLOCKED deep cumulative failed'); return 1
    # Always re-run isolated fault injection directly
    r=run_cmd('python3 scripts/fault_injection.py')
    if r['returncode']!=0: print('UNLOCK BLOCKED fault injection failed\n'+r['stdout']); return 1
    marker=Q/'FEATURES_LOCKED'; cert=Q/'FEATURES_UNLOCKED.json'
    data={'status':'UNLOCKED','timestamp':now(),'git_sha':gitsha(),'policy_digest':sha(POLICY),'gates':[g['id'] for g in required],'fault_injection':'PASS'}
    cert.write_text(json.dumps(data,indent=2)+'\n')
    if marker.exists(): marker.unlink()
    print('DONE feature development unlocked; certificate='+str(cert.relative_to(ROOT))); return 0

def selftest():
    required=[GATES,POLICY,Q/'architecture/registry.json',Q/'state.template.json']
    if not all(p.exists() for p in required): print('FAIL missing control files'); return 1
    # test a harmless command runner
    r=run_cmd("python3 -c 'print(123)'")
    if r['returncode'] or '123' not in r['stdout']: print('FAIL command runner'); return 1
    print('PASS qualityctl self-test'); return 0

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True)
    sub.add_parser('init'); sub.add_parser('status'); sub.add_parser('next'); sub.add_parser('self-test'); sub.add_parser('unlock')
    b=sub.add_parser('build'); b.add_argument('--through',default='G15')
    v=sub.add_parser('verify'); v.add_argument('--through',default=None); v.add_argument('--mode',choices=['fast','deep'],default='fast'); v.add_argument('--no-state-write',action='store_true'); v.add_argument('--current-policy',action='store_true')
    a=ap.parse_args()
    if a.cmd=='init': init(); return 0
    if a.cmd=='status':
        s=load_state(); print(json.dumps(s,indent=2)); return 0
    if a.cmd=='next':
        s=load_state(); print(s.get('current_gate','G00')); return 0
    if a.cmd=='self-test': return selftest()
    if a.cmd=='build': return cmd_build(a.through)
    if a.cmd=='unlock': return unlock()
    if a.cmd=='verify':
        gates=load_gates(); through=a.through
        if a.current_policy:
            s=load_state(); passed=s.get('passed',[]); through=passed[-1] if passed else 'G02'
        if not through: through='G15'
        return 0 if cumulative(through,a.mode,write=not a.no_state_write and False) else 1
if __name__=='__main__': sys.exit(main())
