#!/usr/bin/env python3
"""Block-sequence diff (see blocks.py for the block definition)."""
import sys, re, struct, collections, difflib
sys.path.insert(0, '/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-amm/analysis')
import fn_diff as F

def mask(t):
    t = re.sub(r'(ja r\d+, (?:r\d+|0x[0-9a-f]+), )[+-]0x[0-9a-f]+', r'\1<OFF>', t)
    t = re.sub(r'((?:jeq|jne|jgt|jge|jlt|jle|jsgt|jsge|jslt|jsle|jset)[a-z]* r\d+, (?:r\d+|0x[0-9a-f]+), )[+-]0x[0-9a-f]+', r'\1<OFF>', t)
    return t

def load(path, start, end):
    b = open(path, 'rb').read()
    ins = {}; at = start
    while at < end:
        op = b[at]; w = 16 if op == 0x18 else 8
        ins[at] = w; at += w
    starts = {start}
    for a in ins:
        op = b[a]; off, imm = struct.unpack_from('<hi', b, a+2)
        if op == 0x05 or (op & 7) == 5:
            t = a + 8 + off*8
            if start <= t < end: starts.add(t)
            starts.add(a + (16 if op == 0x18 else 8))
    starts = sorted(s for s in starts if s in ins)
    out = []
    for i, s in enumerate(starts):
        e = starts[i+1] if i+1 < len(starts) else end
        out.append((s, e))
    return out

A = F.decode(sys.argv[1], int(sys.argv[2],0), int(sys.argv[3],0))
B = F.decode(sys.argv[4], int(sys.argv[5],0), int(sys.argv[6],0))
ta = {p: mask(t) for p, t in A}; tb = {p: mask(t) for p, t in B}
ba = load(sys.argv[1], int(sys.argv[2],0), int(sys.argv[3],0))
bb = load(sys.argv[4], int(sys.argv[5],0), int(sys.argv[6],0))
SA = [tuple(ta[p] for p in range(s, e) if p in ta) for s, e in ba]
SB = [tuple(tb[p] for p in range(s, e) if p in tb) for s, e in bb]
sm = difflib.SequenceMatcher(None, SA, SB, autojunk=False)
print(f'blocks A={len(SA)} B={len(SB)} similarity={sm.ratio():.4f}')
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal': continue
    print(f'\n## {tag} A[{i1}:{i2}] B[{j1}:{j2}]')
    for i in range(max(0,i1-1), min(len(SA), i2+1)):
        s, e = ba[i]
        print(f'   A[{i:3d}] {s:#08x} {e-s:4d}B  {len(SA[i]):2d} insns  first: {SA[i][0] if SA[i] else "-"}')
    for j in range(max(0,j1-1), min(len(SB), j2+1)):
        s, e = bb[j]
        print(f'   B[{j:3d}] {s:#08x} {e-s:4d}B  {len(SB[j]):2d} insns  first: {SB[j][0] if SB[j] else "-"}')
