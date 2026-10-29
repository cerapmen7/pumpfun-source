#!/usr/bin/env python3
"""Extract Anchor error tuples (path, path_len, line, code) from an sBPF range."""
import sys, struct
from pathlib import Path
p, lo, hi = sys.argv[1], int(sys.argv[2], 0), int(sys.argv[3], 0)
b = Path(p).read_bytes()
ins = []; at = lo
while at < hi:
    op = b[at]; regs = b[at+1]; dst, src = regs & 0xf, regs >> 4
    off, imm = struct.unpack_from('<hi', b, at+2)
    if op == 0x18:
        h, = struct.unpack_from('<i', b, at+12)
        ins.append((at, op, dst, src, 0, ((imm & 0xffffffff) | (h << 32)))); at += 16; continue
    ins.append((at, op, dst, src, off, imm)); at += 8

def printable(v):
    if not (0 <= v < len(b)): return None
    t = b[v:v+300].split(b'\0', 1)[0]
    if 0 < len(t) and all(32 <= c < 127 for c in t): return t.decode()
    return None

rows = []
for i, (at, op, dst, src, off, imm) in enumerate(ins):
    if op != 0x18: continue
    s = printable(imm)
    if not s or '.rs' not in s: continue
    path = s[:s.index('.rs') + 3]
    seq = ins[i+1:i+10]
    if not any(o == 0x7b for (a2, o, d2, s2, o2, m2) in seq): continue  # stxdw file ptr
    line = plen = None
    stws = [m2 for (a2, o, d2, s2, o2, m2) in seq if o == 0x62]
    stdws = [m2 for (a2, o, d2, s2, o2, m2) in seq if o == 0x7a]
    if len(path) in stdws: plen = len(path)
    if plen is None: continue
    if len(stws) >= 2:
        line = stws[1]
    rows.append((at, path, plen, line, stws[0] if stws else None))
for r in rows:
    print(f'{r[0]:#08x} len={r[2]} line={r[3]} code={r[4]} {r[1]}')
print('total', len(rows))
