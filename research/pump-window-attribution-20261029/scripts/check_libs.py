#!/usr/bin/env python3
import json,hashlib
from pathlib import Path
spec=json.load(open('/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained/research/pump-program-creator-notice-qualification-20261028/tools/pump_linux_v144_sbpf_libraries.json'))
d=Path('/home/tc147/.cache/solana/v1.44/platform-tools/rust/lib/rustlib/sbpf-solana-solana/lib')
exp=spec['target_libraries']
ok=0;bad=[];missing=[]
for name,meta in exp.items():
    p=d/name
    if not p.is_file(): missing.append(name); continue
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h==meta: ok+=1
    else: bad.append((name,h,meta))
extra=sorted(x.name for x in d.iterdir() if x.is_file() and x.name not in exp)
print('expected',len(exp),'ok',ok,'bad',len(bad),'missing',len(missing),'extra',extra)
for b in bad[:5]: print('BAD',b)
for m in missing[:5]: print('MISS',m)
