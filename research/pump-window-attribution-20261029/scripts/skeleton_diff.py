#!/usr/bin/env python3
"""Skeleton (opcode+registers) diff with source-anchor annotation, per pair."""
import sys, struct, difflib, importlib.util
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

def skeleton(e, start, size):
    out = []
    for off in range(0, size, 8):
        b = e.b[start + off:start + off + 8]
        out.append((b[0], b[1] & 0xf, b[1] >> 4))
    return out

def tuples_by_index(e, start, size):
    res = {}
    for off in range(0, size, 8):
        at = start + off
        b = e.b[at:at + 16]
        if b[0] != 0x18: continue
        val = struct.unpack_from("<Q", b, 4)[0]
        sec = next((s for s in e.raw if s[3] <= val < s[3] + s[5]), None)
        if not sec: continue
        fo = sec[4] + (val - sec[3])
        blob = e.b[fo:fo + 240]
        import re
        m = re.match(rb"(?:programs|src|tests|/home)/[A-Za-z0-9_./-]+?\.rs", blob)
        if not m: continue
        line = code = None
        for k in range(1, 14):
            bb = e.b[at + k * 8: at + k * 8 + 8]
            if len(bb) < 8: break
            if bb[0] == 0x62:
                v = struct.unpack_from("<I", bb, 4)[0]
                if 6000 <= v < 6200 and code is None: code = v
                elif 40 <= v < 4000 and line is None: line = v
        res[off // 8] = (m.group(0).decode().split("/")[-1], line, code)
    return res

for da, ca in PAIRS:
    osz = end_of(o, da) - da
    f = next(x for x in c.funcs if x["start"] == ca)
    A, B = skeleton(o, da, osz), skeleton(c, ca, f["size"])
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    ops = [x for x in sm.get_opcodes() if x[0] != "equal"]
    ta, tb = tuples_by_index(o, da, osz), tuples_by_index(c, ca, f["size"])
    print("=== %s vs %s  %d/%d  regions %d  skeleton-equal %d/%d" %
          (hex(da), hex(ca), osz, f["size"], len(ops),
           sum(i2 - i1 for t, i1, i2, j1, j2 in sm.get_opcodes() if t == "equal"), len(A)))
    for tag, i1, i2, j1, j2 in ops[:8]:
        pa = max((i for i in ta if i <= i1), default=None)
        pb = max((j for j in tb if j <= j1), default=None)
        print("   %-7s D[%d:%d] C[%d:%d]  after D%s C%s" %
              (tag, i1, i2, j1, j2, ta.get(pa), tb.get(pb)))
