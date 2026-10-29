#!/usr/bin/env python3
"""Detailed normalized comparison for explicit (deployed target, candidate func) pairs."""
import sys, re, json, struct, difflib, importlib.util
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

def norm_words(e, start, size):
    buf = bytearray(e.b[start:start + size])
    for off in range(0, size, 8):
        at = start + off
        b = buf[off:off + 8]
        r = e.relocations.get(at)
        if b[0] == 0x85:
            buf[off + 4:off + 8] = bytes(4)
        elif r and r["type"] == 8 and b[0] == 0x18 and off + 16 <= size:
            buf[off + 4:off + 8] = bytes(4)
            buf[off + 12:off + 16] = bytes(4)
    return [bytes(buf[i:i + 8]) for i in range(0, size, 8)]

def shape(e, start, size):
    out = []
    for off in range(0, size, 8):
        b = e.b[start + off:start + off + 8]
        out.append((b[0], b[1] & 0xf, b[1] >> 4))
    return out

def literals(e, start, size):
    """Return (path,line,code) tuples, path anchored at the lddw literal."""
    res = []
    for off in range(0, size, 8):
        at = start + off
        b = e.b[at:at + 16]
        if b[0] != 0x18:
            continue
        val = struct.unpack_from("<Q", b, 4)[0]
        if val == 0:
            continue
        sec = next((s for s in e.raw if s[3] <= val < s[3] + s[5]), None)
        if not sec:
            continue
        fo = sec[4] + (val - sec[3])
        blob = e.b[fo:fo + 240]
        m = re.match(rb"(?:programs|src|tests|/home)/[A-Za-z0-9_./-]+?\.rs", blob)
        if not m:
            continue
        path = m.group(0).decode()
        line = code = None
        for k in range(1, 14):
            if off + k * 8 + 8 > size: break
            bb = e.b[at + k * 8: at + k * 8 + 8]
            if bb[0] == 0x62:
                v = struct.unpack_from("<I", bb, 4)[0]
                if 6000 <= v < 6200 and code is None: code = v
                elif 40 <= v < 4000 and line is None: line = v
        if line or code:
            res.append((path, line, code))
    return res

rows = []
for da, ca in PAIRS:
    osz = end_of(o, da) - da
    f = next(x for x in c.funcs if x["start"] == ca)
    csz = f["size"]
    A, B = norm_words(o, da, osz), norm_words(c, ca, csz)
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    ops = sm.get_opcodes()
    replaced = sum((i2 - i1) for tag, i1, i2, j1, j2 in ops if tag == "replace")
    inserted = sum((j2 - j1) for tag, i1, i2, j1, j2 in ops if tag in ("insert", "replace"))
    deleted = sum((i2 - i1) for tag, i1, i2, j1, j2 in ops if tag in ("delete", "replace"))
    equal = sum((i2 - i1) for tag, i1, i2, j1, j2 in ops if tag == "equal")
    ot = literals(o, da, osz); ct = literals(c, ca, csz)
    rows.append({"target": hex(da), "candidate": hex(ca), "symbol": f["name"],
                 "deployed_bytes": osz, "candidate_bytes": csz,
                 "deployed_tuples": ot, "candidate_tuples": ct,
                 "equal_insns": equal, "replaced": replaced, "inserted": inserted,
                 "deleted": deleted, "ops": len(ops)})
    print("=== %s -> %s  %d vs %d B  equal %d  repl %d  ins %d  del %d  ops %d" %
          (hex(da), hex(ca), osz, csz, equal, replaced, inserted, deleted, len(ops)))
    print("   deployed tuples:", [(p.split('/')[-1], l, k) for p, l, k in ot])
    print("   candidate tuples:", [(p.split('/')[-1], l, k) for p, l, k in ct])
Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained/artifacts/pairs.json").write_text(json.dumps(rows, indent=1) + "\n")
