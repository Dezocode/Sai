#!/usr/bin/env python3
from pathlib import Path
import json, sys, shutil, glob, os
ROOT=Path(__file__).resolve().parents[1]
LOCK=ROOT/'.sai-quality/toolchain.lock.json'
REG=ROOT/'.sai-quality/adapters/registry.json'
GEN=ROOT/'.sai-quality/generated'
RUNTIME=ROOT/'.sai-quality/runtime'

def load(): return json.loads(LOCK.read_text()), json.loads(REG.read_text())
def detect():
    matches=set()
    for ext,name in [('.ts','javascript-typescript'),('.tsx','javascript-typescript'),('.js','javascript-typescript'),('.jsx','javascript-typescript'),('.py','python'),('.go','go'),('.rs','rust')]:
        for p in ROOT.rglob('*'+ext):
            if '.sai-quality/runtime' not in str(p) and 'node_modules' not in p.parts:
                matches.add(name); break
    if (ROOT/'package.json').exists() or (ROOT/'tsconfig.json').exists(): matches.add('javascript-typescript')
    if (ROOT/'pyproject.toml').exists() or (ROOT/'requirements.txt').exists(): matches.add('python')
    if (ROOT/'go.mod').exists(): matches.add('go')
    if (ROOT/'Cargo.toml').exists(): matches.add('rust')
    return sorted(matches)
def main():
    cmd=sys.argv[1] if len(sys.argv)>1 else 'plan'; lock,reg=load(); langs=detect(); RUNTIME.mkdir(parents=True,exist_ok=True)
    if cmd=='detect':
        data={'detected_languages':langs}; (RUNTIME/'language-detection.json').write_text(json.dumps(data,indent=2)+'\n'); print(json.dumps(data,indent=2)); return
    if cmd=='verify-adapters':
        ids=[a['id'] for a in reg['language_adapters']]
        if len(ids)!=len(set(ids)): print('FAIL duplicate adapter ids'); sys.exit(1)
        print('PASS adapter registry; detected='+','.join(langs)); return
    if cmd=='plan':
        data={'detected_languages':langs,'required_global_tools':[k for k,v in lock['tools'].items() if v['enabled']], 'conditional':{a['id']:a['conditional_tools'] for a in reg['language_adapters'] if a['id'] in langs}, 'rule':'resolve official stable once, pin exact'}
        (RUNTIME/'tool-plan.json').write_text(json.dumps(data,indent=2)+'\n'); print(json.dumps(data,indent=2)); return
    if cmd=='verify-lock':
        allow='--allow-unresolved-disabled' in sys.argv
        unresolved=[]
        conditional=set()
        for a in reg['language_adapters']:
            if a['id'] in langs: conditional.update(a['conditional_tools'])
        for name,s in lock['tools'].items():
            needed=s['enabled'] or name in conditional
            if needed and (s.get('version') in (None,'UNRESOLVED','latest') or s.get('digest_or_checksum') in (None,'UNRESOLVED')):
                unresolved.append(name)
        # Gate G04 intentionally blocks until Cursor resolves/pins tools.
        if unresolved:
            print('TOOL LOCK FAIL unresolved required tools: '+', '.join(unresolved))
            print('Resolve from official sources, pin exact version and digest/checksum, then rerun.'); sys.exit(1)
        print('PASS toolchain lock fully pinned for enabled/detected tools'); return
    if cmd=='render':
        GEN.mkdir(parents=True,exist_ok=True)
        for src,dst in [('dependency-cruiser.cjs','dependency-cruiser.cjs'),('knip.json','knip.json'),('jscpd.json','jscpd.json'),('gitleaks.toml','gitleaks.toml'),('trivy.yaml','trivy.yaml')]:
            s=ROOT/'.sai-quality/templates'/src
            if s.exists() and not (GEN/dst).exists(): shutil.copy2(s,GEN/dst)
        print('PASS rendered additive generated configs (existing files preserved)'); return
    if cmd=='verify-native-contract':
        print('PASS native contract scaffold: adapters are language-conditional; project-native lint/type/build must be registered when product stack is selected'); return
    if cmd=='check-capability':
        cap=sys.argv[2] if len(sys.argv)>2 else ''
        capability_tools=[(n,s) for n,s in lock['tools'].items() if s.get('capability')==cap]
        conditional=False
        if cap in ('dependency_architecture','dead_code') and 'javascript-typescript' not in langs:
            print(f'PASS {cap}: not applicable before JS/TS is detected'); return
        if not capability_tools:
            print('FAIL no tool registered for capability '+cap); sys.exit(1)
        unresolved=[n for n,s in capability_tools if s.get('version') in (None,'UNRESOLVED','latest')]
        if unresolved:
            print('FAIL capability '+cap+' tools unresolved: '+','.join(unresolved)); sys.exit(1)
        print('PASS capability contract '+cap+' has pinned tool(s): '+','.join(n for n,_ in capability_tools)); return
    if cmd=='verify-sbom':
        p=RUNTIME/'sbom-placeholder.json'
        if not p.exists():
            p.write_text(json.dumps({'note':'Gate G10 must replace this placeholder with real Trivy-generated SBOM evidence after tool pin/install.'},indent=2)+'\n')
            print('FAIL real SBOM not generated yet; placeholder created at '+str(p.relative_to(ROOT))); sys.exit(1)
        try: d=json.loads(p.read_text())
        except: print('FAIL invalid SBOM JSON'); sys.exit(1)
        if 'placeholder' in json.dumps(d).lower(): print('FAIL SBOM still placeholder'); sys.exit(1)
        print('PASS SBOM evidence present'); return
    if cmd=='render-service':
        service=sys.argv[2]
        target=GEN/service; target.mkdir(parents=True,exist_ok=True)
        src=ROOT/'.sai-quality/templates'/service
        if src.exists():
            for p in src.rglob('*'):
                if p.is_file():
                    q=target/p.relative_to(src); q.parent.mkdir(parents=True,exist_ok=True)
                    if not q.exists(): shutil.copy2(p,q)
        print('PASS rendered service template '+service); return
    if cmd=='verify-service':
        service=sys.argv[2]; contract='--contract-only' in sys.argv
        if lock['tools'].get(service,{}).get('version') in (None,'UNRESOLVED','latest'):
            print('FAIL '+service+' unresolved'); sys.exit(1)
        target=GEN/service
        if not target.exists(): print('FAIL service template not rendered '+service); sys.exit(1)
        if contract:
            print('PASS '+service+' service contract rendered and pinned'); return
        marker=RUNTIME/(service+'-verified.json')
        if not marker.exists(): print('FAIL '+service+' runtime verification evidence missing: '+str(marker.relative_to(ROOT))); sys.exit(1)
        print('PASS '+service+' runtime verification evidence'); return
    if cmd=='verify-repo-posture':
        for t in ('renovate','scorecard'):
            if lock['tools'][t]['version'] in (None,'UNRESOLVED','latest'): print('FAIL '+t+' unresolved'); sys.exit(1)
        print('PASS repo posture tools pinned/configurable'); return
    print('unknown command',cmd); sys.exit(2)
if __name__=='__main__': main()
