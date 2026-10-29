#!/usr/bin/env python3
"""Classify the instruction-level diff of two same-size sBPF functions.

Uses the fn_diff decoder, then re-runs difflib with branch displacements masked
so that pure block-placement differences collapse to 'equal'. Reports:
  * layout-only difference (same instruction multiset modulo displacements)
  * real instruction substitutions / inserts / deletes.

usage: classify_diff.py A.so A_START A_END B.so B_START B_END
"""
import sys, difflib, re
sys.path.insert(0, '/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-amm/analysis')
import fn_diff as F

a = F.decode(sys.argv[1], int(sys.argv[2], 0), int(sys.argv[3], 0))
b = F.decode(sys.argv[4], int(sys.argv[5], 0), int(sys.argv[6], 0))

def mask(t):
    # branch displacements and ja offsets -> <OFF>
    t = re.sub(r'(ja r\d+, r\d+, )[+-]0x[0-9a-f]+', r'\1<OFF>', t)
    t = re.sub(r'((?:jeq|jne|jgt|jge|jlt|jle|jsgt|jsge|jslt|jsle|jset)[a-z]* r\d+, (?:r\d+|0x[0-9a-f]+), )[+-]0x[0-9a-f]+', r'\1<OFF>', t)
    return t

A = [mask(t) for _, t in a]; B = [mask(t) for _, t in b]
sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
print(f'instructions A={len(A)} B={len(B)}  masked-similarity={sm.ratio():.4f}')
real = 0
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal': continue
    real += max(i2 - i1, j2 - j1)
    print(f'\n## {tag}  A[{i1}:{i2}] @ {a[i1][0]:#x}   B[{j1}:{j2}] @ {b[j1][0]:#x}')
    for k in range(max(0, i1-2), min(len(a), i2+2)):
        print(f'   A {a[k][0]:#08x} {a[k][1]}')
    for k in range(max(0, j1-2), min(len(b), j2+2)):
        print(f'   B {b[k][0]:#08x} {b[k][1]}')
print(f'\nreal (non-layout) differing instruction slots: {real}')
