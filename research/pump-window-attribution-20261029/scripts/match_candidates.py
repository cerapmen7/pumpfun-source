#!/usr/bin/env python3
"""For each target window, find the closest candidate function by normalized
instruction-stream comparison, and report instruction-level differences."""
import sys, json, difflib, importlib.util
from pathlib import Path

ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf

CAND = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so"
TARGETS = [0x1e7c0,0x22a10,0x4c158,0x5b3b0,0x6cd78,0x72810,0x77940,0x80df8,0x83c00,
           0x13b9b8,0x13f630,0x144508,0x147ba0,0x1489f8,0x14a8a8,0x14f4e0]
o = Elf(ROOT / "evidence/original/pump/deployed.so")
c = Elf(CAND)
ow = list(zip(o.entries, o.entries[1:] + [o.hi]))

def words(e, start, size):
    return [e.b[start + i:start + i + 8].hex() for i in range(0, size, 8)]

def shape(e, start, size):
    out = []
    for i in range(0, size, 8):
        b = e.b[start + i:start + i + 8]
        op = b[0]
        out.append("%02x.%d.%d" % (op, b[1] & 0xf, b[1] >> 4))
    return out

res = []
for t in TARGETS:
    z = dict(ow)[t]
    n = z - t
    a = shape(o, t, n)
    cands = []
    for f in c.funcs:
        if f["size"] < n * 0.5 or f["size"] > n * 1.5:
            continue
        b = shape(c, f["start"], f["size"])
        r = difflib.SequenceMatcher(None, a, b, autojunk=False).quick_ratio()
        cands.append((r, f))
    cands.sort(key=lambda x: -x[0])
    best = []
    for r, f in cands[:5]:
        b = shape(c, f["start"], f["size"])
        ratio = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
        # count differing 8-byte words for equal-size functions
        if f["size"] == n:
            wa, wb = words(o, t, n), words(c, f["start"], n)
            diff = sum(x != y for x, y in zip(wa, wb))
        else:
            diff = None
        best.append({"address": hex(f["start"]), "size": f["size"], "delta": f["size"] - n,
                     "shape": round(ratio, 3), "diff_words": diff, "name": f["name"]})
    res.append({"target": hex(t), "bytes": n, "instructions": n // 8, "candidates": best})
    print("===", hex(t), n, "B", n // 8, "insns")
    for b in best:
        print("   %-9s %6d B d=%+6d shape %.3f diff %s  %s" %
              (b["address"], b["size"], b["delta"], b["shape"], b["diff_words"], b["name"][:90]))
Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained/artifacts/candidate-match.json").write_text(json.dumps(res, indent=1) + "\n")
