#!/usr/bin/env python3
"""Normalized instruction-sequence diff between two sBPF ranges.

Masking (same idea as the window metric): call targets become <CALL>; lddw
pointers into any section become <ADDR>; everything else (regs, offsets,
immediates like line/error codes) is compared literally.

usage: fn_diff.py A.so A_START A_END B.so B_START B_END [--context N]
"""
import sys, struct, difflib, re
from pathlib import Path

LD = {0x61: 'ldxw', 0x69: 'ldxh', 0x71: 'ldxb', 0x79: 'ldxdw', 0x18: 'lddw'}
ST = {0x62: 'stw', 0x6a: 'sth', 0x72: 'stb', 0x7a: 'stdw',
      0x63: 'stxw', 0x6b: 'stxh', 0x73: 'stxb', 0x7b: 'stxdw'}
ALU = {0x04:'add32',0x0c:'add32r',0x14:'sub32',0x1c:'sub32r',0x24:'mul32',0x2c:'mul32r',0x34:'div32',0x3c:'div32r',
       0x44:'or32',0x4c:'or32r',0x54:'and32',0x5c:'and32r',0x64:'lsh32',0x6c:'lsh32r',0x74:'rsh32',0x7c:'rsh32r',
       0x84:'neg32',0x94:'mod32',0x9c:'mod32r',0xa4:'xor32',0xac:'xor32r',0xb4:'mov32',0xbc:'mov32r',0xc4:'arsh32',0xcc:'arsh32r',
       0x07:'add64',0x0f:'add64r',0x17:'sub64',0x1f:'sub64r',0x27:'mul64',0x2f:'mul64r',0x37:'div64',0x3f:'div64r',
       0x47:'or64',0x4f:'or64r',0x57:'and64',0x5f:'and64r',0x67:'lsh64',0x6f:'lsh64r',0x77:'rsh64',0x7f:'rsh64r',
       0x87:'neg64',0x97:'mod64',0x9f:'mod64r',0xa7:'xor64',0xaf:'xor64r',0xb7:'mov64',0xbf:'mov64r',0xc7:'arsh64',0xcf:'arsh64r'}
JMP = {0x05:'ja',0x15:'jeq',0x1d:'jeqr',0x25:'jgt',0x2d:'jgtr',0x35:'jge',0x3d:'jger',0x45:'jset',0x4d:'jsetr',
       0x55:'jne',0x5d:'jner',0x65:'jsgt',0x6d:'jsgtr',0x75:'jsge',0x7d:'jsger',0xa5:'jlt',0xad:'jltr',
       0xb5:'jle',0xbd:'jler',0xc5:'jslt',0xcd:'jsltr',0xd5:'jsle',0xdd:'jsler'}

def load(path):
    b = Path(path).read_bytes()
    shoff, = struct.unpack_from('<Q', b, 40); es, shnum, si = struct.unpack_from('<HHH', b, 58)
    secs = [struct.unpack_from('<IIQQQQIIQQ', b, shoff+i*es) for i in range(shnum)]
    ns = secs[si]; names = b[ns[4]:ns[4]+ns[5]]
    S = {names[s[0]:].split(b'\0',1)[0].decode(): s for s in secs}
    return b, S

def decode(path, lo, hi):
    b, S = load(path)
    ranges = [(s[3], s[3]+s[5]) for n, s in S.items() if s[5] and s[1] != 8]
    def masked(v):
        return any(a <= v < z for a, z in ranges)
    out = []; at = lo
    while at < hi:
        op = b[at]; regs = b[at+1]; dst, src = regs & 0xf, regs >> 4
        off, imm = struct.unpack_from('<hi', b, at+2)
        if op == 0x18:
            h, = struct.unpack_from('<i', b, at+12)
            v = (imm & 0xffffffff) | (h << 32)
            val = '<ADDR>' if masked(v) else hex(v)
            out.append((at, f'lddw r{dst}, {val}'))
            at += 16; continue
        if op == 0x85:
            out.append((at, f'call<{src}>' if src == 1 else f'syscall {imm:#x}'))
        elif op in LD:
            out.append((at, f'{LD[op]} r{dst}, [r{src}{off:+#x}]'))
        elif op in ST:
            v = f'r{src}' if (op & 3) == 3 else hex(imm)
            out.append((at, f'{ST[op]} [r{dst}{off:+#x}], {v}'))
        elif op == 0x95:
            out.append((at, 'exit'))
        elif op in ALU:
            v = f'r{src}' if (op & 8) else hex(imm)
            out.append((at, f'{ALU[op]} r{dst}, {v}'))
        elif op in JMP:
            v = f'r{src}' if (op & 8) else hex(imm)
            out.append((at, f'{JMP[op]} r{dst}, {v}, {off:+#x}'))
        elif op == 0x8d:
            out.append((at, f'callx r{imm}'))
        else:
            out.append((at, f'op{op:#04x}'))
        at += 8
    return out

def main():
    a = decode(sys.argv[1], int(sys.argv[2],0), int(sys.argv[3],0))
    b = decode(sys.argv[4], int(sys.argv[5],0), int(sys.argv[6],0))
    if '--fp' in sys.argv:
        # mask r10-relative frame offsets (frame layouts differ between builds)
        a = [(p, re.sub(r'r10(?:\+?-[0-9a-fx]+)', 'r10-FP', t)) for p, t in a]
        b = [(p, re.sub(r'r10(?:\+?-[0-9a-fx]+)', 'r10-FP', t)) for p, t in b]
    ctx = 3
    if '--context' in sys.argv: ctx = int(sys.argv[sys.argv.index('--context')+1])
    print(f'A={len(a)} insns  B={len(b)} insns  sizes {int(sys.argv[3],0)-int(sys.argv[2],0)} vs {int(sys.argv[6],0)-int(sys.argv[5],0)}')
    sm = difflib.SequenceMatcher(None, [x[1] for x in a], [x[1] for x in b], autojunk=False)
    print('similarity ratio', round(sm.ratio(), 4))
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal': continue
        print(f'\n## {tag} A[{i1}:{i2}] ({a[i1][0]:#x}..)  B[{j1}:{j2}] ({b[j1][0] if j1<len(b) else 0:#x}..)')
        for k in range(max(0,i1-ctx), min(len(a), i2+ctx)):
            print(f'  A {a[k][0]:#08x} {a[k][1]}')
        for k in range(max(0,j1-ctx), min(len(b), j2+ctx)):
            print(f'  B {b[k][0]:#08x} {b[k][1]}')

if __name__ == '__main__':
    main()

