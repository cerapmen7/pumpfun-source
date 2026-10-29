#!/usr/bin/env python3
"""Basic-block inventory + placement diff for two same-size sBPF functions.

Blocks end at ja / conditional branch / exit. Tokens mask call targets, lddw
section addresses and branch displacements so blocks are comparable across
layouts. Blocks are matched by their exact token tuple (with multiplicity).
usage: blocks.py A.so A_START A_END B.so B_START B_END
"""
import sys, re, struct, collections
sys.path.insert(0, '/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-amm/analysis')
import fn_diff as F

def mask(t):
    t = re.sub(r'(ja r\d+, (?:r\d+|0x[0-9a-f]+), )[+-]0x[0-9a-f]+', r'\1<OFF>', t)
    t = re.sub(r'((?:jeq|jne|jgt|jge|jlt|jle|jsgt|jsge|jslt|jsle|jset)[a-z]* r\d+, (?:r\d+|0x[0-9a-f]+), )[+-]0x[0-9a-f]+', r'\1<OFF>', t)
    return t

def blocks(path, start, end):
    b = open(path, 'rb').read()
    ins = {}; at = start
    while at < end:
        op = b[at]
        w = 16 if op == 0x18 else 8
        ins[at] = (op, b[at+1], struct.unpack_from('<hi', b, at+2))
        at += w
    starts = {start}
    for a, (op, regs, (off, imm)) in ins.items():
        w = 16 if op == 0x18 else 8
        if op == 0x05 or (op & 7) == 5:
            t = a + 8 + off * 8
            if start <= t < end: starts.add(t)
            starts.add(a + w)
    starts = sorted(s for s in starts if s in ins)
    out = []
    for i, s in enumerate(starts):
        e = starts[i+1] if i+1 < len(starts) else end
        toks = []
        a = s
        while a < e:
            if a in ins:
                op, regs, (off, imm) = ins[a]
                w = 16 if op == 0x18 else 8
                # use decoded text from fn_diff for this address
                toks.append(a)
                a += w
            else:
                a += 8
        out.append((s, e, toks))
    return ins, out

# decode tokens once
A = F.decode(sys.argv[1], int(sys.argv[2],0), int(sys.argv[3],0))
B = F.decode(sys.argv[4], int(sys.argv[5],0), int(sys.argv[6],0))
ta = {p: mask(t) for p, t in A}; tb = {p: mask(t) for p, t in B}
insa, ba = blocks(sys.argv[1], int(sys.argv[2],0), int(sys.argv[3],0))
insb, bb = blocks(sys.argv[4], int(sys.argv[5],0), int(sys.argv[6],0))
def sig(bl, tab):
    s, e, toks = bl
    return tuple(tab[p] for p in toks if p in tab)
SA = [sig(x, ta) for x in ba]; SB = [sig(x, tb) for x in bb]
print(f'blocks A={len(ba)} B={len(bb)}  token-multiset equal: {collections.Counter(sum(SA,())) == collections.Counter(sum(SB,()))}')
# match by signature (identical token tuple), in order of first appearance
posA = collections.defaultdict(list); posB = collections.defaultdict(list)
for i, s in enumerate(SA): posA[s].append(i)
for i, s in enumerate(SB): posB[s].append(i)
common = set(SA) & set(SB)
print(f'blocks with identical token tuple: A {sum(1 for s in SA if s in common)}/{len(SA)}  B {sum(1 for s in SB if s in common)}/{len(SB)}')
# report order: for each B block, the A index of the same signature occurrence
used = collections.Counter()
print('\nB index -> A index (same block signature), address/size:')
for j, s in enumerate(SB):
    k = used[s]; used[s] += 1
    ia = posA[s][k] if k < len(posA[s]) else None
    sa, ea, _ = bb[j]
    if ia is None:
        print(f'  B[{j:3d}] {sa:#08x} ({ea-sa:4d}B)  NO MATCH in A')
    else:
        a0, a1, _ = ba[ia]
        if ia != j:
            print(f'  B[{j:3d}] {sa:#08x} ({ea-sa:4d}B)  == A[{ia:3d}] {a0:#08x} ({a1-a0:4d}B)   MOVED {ia}->{j}')
