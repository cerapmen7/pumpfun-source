import json, hashlib, struct, sys
from pathlib import Path
sys.path.insert(0, '/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained/scripts')
import window_elf_reader as R
W = Path('/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-amm')
rows = []
for label in ('base','a1','a2','a3','a4','c1','c2','a1c1'):
    so = W/'mbuild'/f'out-{label}'/'symbols.so'
    if not so.exists(): continue
    e = R.Elf(so)
    f = next((x for x in e.funcs if 'sell8cashback' in x['name']), None)
    outl = [x for x in e.funcs if 'cold_467' in x['name'] or 'check_467' in x['name']]
    d = json.load(open(W/'mbuild'/f'{label}.json')) if (W/'mbuild'/f'{label}.json').exists() else {}
    # instruction count of the cashback function body
    at = f['start']; end = at + f['size']; n = 0
    while at < end:
        op = e.b[at]; n += 1; at += 16 if op == 0x18 else 8
    rows.append(dict(label=label, sha256=hashlib.sha256((W/'mbuild'/f'out-{label}'/'candidate.so').read_bytes()).hexdigest(),
                     cashback_start=hex(f['start']), cashback_size=f['size'], insns=n,
                     outlined=[(hex(x['start']), x['size'], x['name'].split('8')[-1]) for x in outl],
                     matched=d.get('matched'), raw=d.get('raw'), unmatched=d.get('unmatched')))
print(json.dumps(rows, indent=1))
Path(W/'analysis-m-attr-variants.json').write_text(json.dumps(rows, indent=1)+'\n')
