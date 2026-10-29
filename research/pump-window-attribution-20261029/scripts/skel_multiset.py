#!/usr/bin/env python3
import importlib.util, collections
from pathlib import Path
ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
o = Elf(ROOT / "evidence/original/pump/deployed.so")
c = Elf(ROOT / "research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so")
PAIRS = [(0x14f4e0, 0x14e680), (0x80df8, 0x997f0), (0x83c00, 0x9ecb8), (0x14a8a8, 0xa3798)]
def end_of(e, s):
    i = e.entries.index(s); return e.entries[i+1] if i+1 < len(e.entries) else e.hi
def skel(e, s, n):
    return [(e.b[s+i], e.b[s+i+1] & 0xf, e.b[s+i+1] >> 4) for i in range(0, n, 8)]
for d, ca in PAIRS:
    n = end_of(o, d) - d
    f = next(x for x in c.funcs if x["start"] == ca)
    a, b = collections.Counter(skel(o, d, n)), collections.Counter(skel(c, ca, f["size"]))
    print(hex(d), "skel onlyD", sum((a-b).values()), "onlyC", sum((b-a).values()))
    for k, v in (a-b).items(): print("   D", k, v)
    for k, v in (b-a).items(): print("   C", k, v)
