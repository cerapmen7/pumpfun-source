#!/usr/bin/env python3
"""Name-mapped call comparison for the 16 pairs (uses the measured original->candidate map)."""
import json, struct, importlib.util
from pathlib import Path

W = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained")
ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
o = Elf(ROOT / "evidence/original/pump/deployed.so")
c = Elf(ROOT / "research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so")
base = json.loads((W / "artifacts/baseline.json").read_text())
pairs = {}
for orig, name, raw in base["pairs"]:
    pairs[int(orig, 16)] = name
PAIRS = [(0x14f4e0, 0x14e680), (0x80df8, 0x997f0), (0x83c00, 0x9ecb8), (0x147ba0, 0x9fe18),
         (0x1489f8, 0xa0ef8), (0x13b9b8, 0x16e58), (0x13f630, 0x1aea8), (0x144508, 0x85e98),
         (0x6cd78, 0x81800), (0x77940, 0x92d20), (0x72810, 0x8d838), (0x5b3b0, 0x67970),
         (0x1e7c0, 0x2c330), (0x22a10, 0x2fd30), (0x4c158, 0x5f438)]

def end_of(e, start):
    i = e.entries.index(start)
    return e.entries[i + 1] if i + 1 < len(e.entries) else e.hi

def call_targets(e, start, size):
    out = []
    for i in range(0, size, 8):
        at = start + i
        if e.b[at] == 0x85 and e.b[at + 1] == 0x10 and e.relocations.get(at, {}).get("type") != 10:
            t = struct.unpack_from("<i", e.b, at + 4)[0]
            out.append(at + 8 + t * 8)
    return out

def name_of_deployed(addr):
    # nearest window start at or before addr that has a measured name
    cands = [a for a in pairs if a <= addr]
    if not cands:
        return "?" + hex(addr)
    a = max(cands)
    return pairs[a]

sym = {}
for f in c.funcs:
    sym.setdefault(f["start"], f["name"])

def short(n):
    if n is None:
        return None
    parts = n.split("..")
    return parts[1] if len(parts) > 2 else n[:70]

rows = []
for da, ca in PAIRS:
    osz = end_of(o, da) - da
    f = next(x for x in c.funcs if x["start"] == ca)
    dn = [short(name_of_deployed(x)) for x in call_targets(o, da, osz)]
    cn = [short(sym.get(x)) for x in call_targets(c, ca, f["size"])]
    from collections import Counter
    d, cc = Counter(dn), Counter(cn)
    only_d = list((d - cc).elements()); only_c = list((cc - d).elements())
    rows.append({"target": hex(da), "candidate": hex(ca), "deployed_calls": dn,
                 "candidate_calls": cn, "only_deployed": only_d, "only_candidate": only_c})
    print("=== %s vs %s : onlyD %d onlyC %d" % (hex(da), hex(ca), len(only_d), len(only_c)))
    for x in sorted(set(only_d)): print("   D-only", x)
    for x in sorted(set(only_c)): print("   C-only", x)
(W / "artifacts/call-name-diff.json").write_text(json.dumps(rows, indent=1) + "\n")
