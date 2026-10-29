#!/usr/bin/env python3
"""Multiset test: are the two functions identical instruction multisets (pure ordering),
or do they differ in actual instructions/operands?"""
import json, struct, collections, importlib.util
from pathlib import Path

ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
o = Elf(ROOT / "evidence/original/pump/deployed.so")
c = Elf(ROOT / "research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so")
PAIRS = [
    (0x14f4e0, 0x14e680), (0x4c158, 0x5f438), (0x80df8, 0x997f0), (0x83c00, 0x9ecb8),
    (0x147ba0, 0x9fe18), (0x1489f8, 0xa0ef8), (0x13b9b8, 0x16e58), (0x13f630, 0x1aea8),
    (0x144508, 0x85e98), (0x6cd78, 0x81800), (0x77940, 0x92d20), (0x72810, 0x8d838),
    (0x5b3b0, 0x67970), (0x1e7c0, 0x2c330), (0x22a10, 0x2fd30),
]

def end_of(e, start):
    i = e.entries.index(start)
    return e.entries[i + 1] if i + 1 < len(e.entries) else e.hi

def insns(e, start, size):
    out = []
    for off in range(0, size, 8):
        at = start + off
        b = e.b[at:at + 8]
        imm = struct.unpack_from("<i", b, 4)[0]
        op, regs = b[0], b[1]
        out.append((op, regs, struct.unpack_from("<h", b, 2)[0], imm))
    return out

for da, ca in PAIRS:
    osz = end_of(o, da) - da
    f = next(x for x in c.funcs if x["start"] == ca)
    A, B = insns(o, da, osz), insns(c, ca, f["size"])
    ca_, cb_ = collections.Counter(A), collections.Counter(B)
    only_a = ca_ - cb_; only_b = cb_ - ca_
    # mask call/lddw immediates and compare again
    def mask(seq, e, start):
        out = []
        for i, x in enumerate(seq):
            at = start + i * 8
            b = e.b[at:at + 8]
            if b[0] == 0x85:
                x = (x[0], x[1], x[2], 0)
            r = e.relocations.get(at)
            if r and r["type"] == 8 and b[0] == 0x18:
                x = (x[0], x[1], x[2], 0)
            out.append(x)
        return out
    Am, Bm = mask(A, o, da), mask(B, c, ca)
    ma, mb = collections.Counter(Am), collections.Counter(Bm)
    print("%s vs %s: sizes %d/%d | raw multiset onlyA %d onlyB %d | masked onlyA %d onlyB %d" %
          (hex(da), hex(ca), osz, f["size"], sum(only_a.values()), sum(only_b.values()),
           sum((ma - mb).values()), sum((mb - ma).values())))
    for k, v in list((ma - mb).items())[:5]:
        print("   only-deployed", k, "x", v)
    for k, v in list((mb - ma).items())[:5]:
        print("   only-candidate", k, "x", v)
