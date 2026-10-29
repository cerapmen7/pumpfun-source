#!/usr/bin/env python3
"""Evaluate one variant for window 0x14f4e0 (buy_exact_sol_in)."""
import sys, struct, difflib, importlib.util, hashlib
from pathlib import Path
ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
o = Elf(ROOT / "evidence/original/pump/deployed.so")
c = Elf(Path(sys.argv[1]))
cands = [x for x in c.funcs if "buy_exact_sol_in" in x["name"]]
f = min(cands, key=lambda x: abs(x["size"] - 13224))
def end_of(e, s):
    i = e.entries.index(s); return e.entries[i+1] if i+1 < len(e.entries) else e.hi
osz = end_of(o, 0x14f4e0) - 0x14f4e0
def skel(e, s, n):
    return [(e.b[s+i], e.b[s+i+1] & 0xf, e.b[s+i+1] >> 4) for i in range(0, n, 8)]
A, B = skel(o, 0x14f4e0, osz), skel(c, f["start"], f["size"])
sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
eq = sum(i2-i1 for t,i1,i2,j1,j2 in sm.get_opcodes() if t == "equal")
regs = [x for x in sm.get_opcodes() if x[0] != "equal"]
# normalized window signature check against official measure
rows = welf.Elf
import importlib.util as iu
sp = iu.spec_from_file_location("wm", ROOT / "scripts/window_measure.py")
wm = iu.module_from_spec(sp); sp.loader.exec_module(wm)
res = wm.measure(ROOT / "evidence/original/pump/deployed.so", Path(sys.argv[1]))
row = next(r for r in res if int(r["original"], 16) == 0x14f4e0)
print("candidate_sha", hashlib.sha256(c.b).hexdigest())
print("fn", hex(f["start"]), f["size"], "deployed", osz, "delta", f["size"] - osz)
print("MATCHED", bool(row["match"]), "RAW", bool(row["raw"]))
print("skeleton_equal %d/%d regions %d" % (eq, len(A), len(regs)))
for t,i1,i2,j1,j2 in regs[:12]:
    print("  ", t, "D[%d:%d]" % (i1,i2), "C[%d:%d]" % (j1,j2))
# instruction multiset diff (skeleton)
from collections import Counter
a, b = Counter(A), Counter(B)
print("skel onlyD", sum((a-b).values()), "onlyC", sum((b-a).values()))
for k,v in (a-b).items(): print("   D", k, v)
for k,v in (b-a).items(): print("   C", k, v)
