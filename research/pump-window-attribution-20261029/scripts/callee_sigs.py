#!/usr/bin/env python3
"""Alias-free callee comparison: multiset of callee window/function signatures."""
import json, struct, hashlib, importlib.util
from collections import Counter
from pathlib import Path
ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
o = Elf(ROOT / "evidence/original/pump/deployed.so")
c = Elf(ROOT / "research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so")
W = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained")
PAIRS = [(0x1e7c0, 0x2c330), (0x22a10, 0x2fd30), (0x4c158, 0x5f438), (0x5b3b0, 0x67970),
         (0x6cd78, 0x81800), (0x72810, 0x8d838), (0x77940, 0x92d20), (0x80df8, 0x997f0),
         (0x83c00, 0x9ecb8), (0x13b9b8, 0x16e58), (0x13f630, 0x1aea8), (0x144508, 0x85e98),
         (0x147ba0, 0x9fe18), (0x1489f8, 0xa0ef8), (0x14a8a8, 0xa3798), (0x14f4e0, 0x14e680)]

def end_of(e, s):
    i = e.entries.index(s)
    return e.entries[i + 1] if i + 1 < len(e.entries) else e.hi

def osig(addr):
    z = end_of(o, addr)
    return hashlib.sha256(o.normalized[addr:z]).hexdigest()[:12]

def csig(f):
    return hashlib.sha256(c.normalized[f["start"]:f["start"] + f["size"]]).hexdigest()[:12]

def calls(e, start, size):
    out = []
    for i in range(0, size, 8):
        at = start + i
        if e.b[at] == 0x85 and e.b[at + 1] == 0x10 and e.relocations.get(at, {}).get("type") != 10:
            out.append(at + 8 + struct.unpack_from("<i", e.b, at + 4)[0] * 8)
    return out

csig_by_addr = {f["start"]: csig(f) for f in c.funcs}
rows = []
for da, ca in PAIRS:
    osz = end_of(o, da) - da
    f = next(x for x in c.funcs if x["start"] == ca)
    # deployed callee signature: use the callee window's normalized bytes
    ds = Counter(osig(t) for t in calls(o, da, osz) if t in o.entries)
    cs = Counter(csig_by_addr[t] for t in calls(c, ca, f["size"]) if t in csig_by_addr)
    rows.append({"target": hex(da), "candidate": hex(ca), "callee_multiset_equal": ds == cs,
                 "only_deployed": sorted((ds - cs).elements()),
                 "only_candidate": sorted((cs - ds).elements())})
    print(hex(da), "callee_multiset_equal", ds == cs,
          "onlyD", sorted((ds - cs).elements())[:6], "onlyC", sorted((cs - ds).elements())[:6])
(W / "artifacts/callee-signatures.json").write_text(json.dumps(rows, indent=1) + "\n")
