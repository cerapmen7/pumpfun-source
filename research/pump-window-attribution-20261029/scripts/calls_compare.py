#!/usr/bin/env python3
"""Compare internal call targets of each deployed target window vs its candidate function."""
import struct, importlib.util
from pathlib import Path

ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
o = Elf(ROOT / "evidence/original/pump/deployed.so")
c = Elf(ROOT / "research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so")
PAIRS = [(0x14f4e0, 0x14e680), (0x80df8, 0x997f0), (0x83c00, 0x9ecb8), (0x147ba0, 0x9fe18),
         (0x1489f8, 0xa0ef8), (0x13b9b8, 0x16e58), (0x13f630, 0x1aea8), (0x144508, 0x85e98),
         (0x6cd78, 0x81800), (0x77940, 0x92d20), (0x72810, 0x8d838), (0x5b3b0, 0x67970),
         (0x1e7c0, 0x2c330), (0x22a10, 0x2fd30), (0x4c158, 0x5f438)]

def end_of(e, start):
    i = e.entries.index(start)
    return e.entries[i + 1] if i + 1 < len(e.entries) else e.hi

def calls(e, start, size):
    out = []
    for i in range(0, size, 8):
        at = start + i
        if e.b[at] == 0x85 and e.b[at + 1] == 0x10:
            if e.relocations.get(at, {}).get("type") == 10:
                continue
            t = struct.unpack_from("<i", e.b, at + 4)[0]
            out.append(at + 8 + t * 8)
    return out

sym = {}
for f in c.funcs:
    sym.setdefault(f["start"], f["name"])

def short(n):
    parts = n.split("..")
    return parts[1] if len(parts) > 2 else n[20:70]

for da, ca in PAIRS:
    osz = end_of(o, da) - da
    f = next(x for x in c.funcs if x["start"] == ca)
    oc, cc = calls(o, da, osz), calls(c, ca, f["size"])
    oset, cset = set(oc), set(cc)
    print("=== %s vs %s  calls D=%d C=%d" % (hex(da), hex(ca), len(oc), len(cc)))
    print("   D targets:", sorted({hex(x) for x in oset}))
    print("   C targets:", [short(sym.get(x, hex(x))) for x in sorted(cset)])
    print("   only D:", [hex(x) for x in sorted(oset - cset)])
    print("   only C:", [short(sym.get(x, hex(x))) for x in sorted(cset - oset)])
