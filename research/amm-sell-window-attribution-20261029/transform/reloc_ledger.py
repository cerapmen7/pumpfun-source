#!/usr/bin/env python3
"""Relocation ledger for a text range: type, site offset, and the data pointed to
by the associated lddw (string preview / section). Read-only."""
import sys, struct, json
from pathlib import Path

def elf(b):
    shoff, = struct.unpack_from('<Q', b, 40)
    es, shnum, si = struct.unpack_from('<HHH', b, 58)
    secs = [struct.unpack_from('<IIQQQQIIQQ', b, shoff+i*es) for i in range(shnum)]
    ns = secs[si]; names = b[ns[4]:ns[4]+ns[5]]
    return {names[s[0]:].split(b'\0',1)[0].decode(): s for s in secs}

path, start, size = sys.argv[1], int(sys.argv[2],0), int(sys.argv[3],0)
b = Path(path).read_bytes(); S = elf(b)
sec_ranges = [(n, s[3], s[3]+s[5]) for n, s in S.items() if s[5] and s[1] != 8]
def sec_of(v):
    for n, a, z in sec_ranges:
        if a <= v < z: return n
    return None
rel = {}
if '.rel.dyn' in S:
    s = S['.rel.dyn']
    for at in range(s[4], s[4]+s[5], 16):
        site, info = struct.unpack_from('<QQ', b, at)
        rel[site] = dict(type=info & 0xffffffff, symidx=info >> 32)
# section symbols
syms = {}
if '.dynsym' in S:
    ds = S['.dynsym']; dstr = S['.dynstr']
    for i in range(ds[5]//24):
        n, info, other, shndx, val, sz = struct.unpack_from('<IBBHQQ', b, ds[4]+i*24)
        syms[i] = b[dstr[4]+n:].split(b'\0',1)[0].decode('latin1')
rows = []
for site in sorted(rel):
    if not (start <= site < start+size): continue
    r = rel[site]
    # the lddw at site (if any) carries an addend/pointer
    ptr = None
    if b[site] == 0x18:
        lo, = struct.unpack_from('<i', b, site+4); hi, = struct.unpack_from('<i', b, site+12)
        ptr = (lo & 0xffffffff) | (hi << 32)
    preview = ''
    path = None
    if ptr is not None and 0 <= ptr < len(b):
        t = b[ptr:ptr+96].split(b'\0',1)[0]
        if t and all(32 <= c < 127 for c in t): preview = t.decode()
        raw = b[ptr:ptr+400].split(b'\0',1)[0]
        if b'.rs' in raw[:400]:
            path = raw[:raw.index(b'.rs')+3].decode('latin1')
    rows.append(dict(site=site, off=site-start, type=r['type'], sym=r['symidx'],
                     symname=syms.get(r['symidx'], ''), ptr=ptr, ptr_section=sec_of(ptr) if ptr is not None else None,
                     preview=preview, path=path, opcode=b[site]))
out = dict(file=path, start=start, size=size, count=len(rows), rows=rows)
print(json.dumps(out, indent=1))
