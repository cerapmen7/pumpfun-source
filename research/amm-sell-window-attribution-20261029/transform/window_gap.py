#!/usr/bin/env python3
"""Precise gap of deployed window 0x4c750 vs the maintained candidate window.

Compares, at the same address:
  * normalized bytes (call/lddw immediates zeroed) -> diff runs + instruction decode
  * relocation pattern rows (offset, type, symbol)
  * raw bytes
usage: window_gap.py ORIG.so CAND.so START SIZE [--json out]
"""
import sys, json, struct
from pathlib import Path
sys.path.insert(0, '/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained/scripts')
import window_elf_reader as R

o = R.Elf(Path(sys.argv[1])); c = R.Elf(Path(sys.argv[2]))
start, size = int(sys.argv[3], 0), int(sys.argv[4], 0)
a, b = start, start + size
on = o.normalized[a:b]; cn = c.normalized[a:b]
assert len(on) == len(cn) == size

diff = [i for i in range(size) if on[i] != cn[i]]
runs = []
for i in diff:
    if runs and i == runs[-1][1]:
        runs[-1][1] = i + 1
    else:
        runs.append([i, i + 1])

def insn_at(e, off):
    at = a + off
    op = e.b[at]
    if op == 0x18:
        lo, = struct.unpack_from('<i', e.b, at + 4); hi, = struct.unpack_from('<i', e.b, at + 12)
        return at, 16, f'lddw {(lo & 0xffffffff) | (hi << 32):#x}'
    imm, = struct.unpack_from('<i', e.b, at + 4)
    return at, 8, f'op{op:#04x} imm={imm:#x}'

po = {(r['offset'], r['type'], r.get('symbol', '')) for r in o.pattern(a, size)}
pc = {(r['offset'], r['type'], r.get('symbol', '')) for r in c.pattern(a, size)}
print(json.dumps(dict(
    start=hex(start), size=size,
    normalized_diff_bytes=len(diff),
    normalized_diff_runs=len(runs),
    raw_equal=o.b[a:b] == c.b[a:b],
    reloc_rows_original=len(po), reloc_rows_candidate=len(pc),
    reloc_rows_equal=po == pc,
    reloc_only_original=sorted(po - pc),
    reloc_only_candidate=sorted(pc - po),
), indent=1))
print('-- normalized diff runs (instruction-aligned):')
for s, e in runs:
    at, w, txt = insn_at(o, s)
    cat, wc, tc = insn_at(c, s)
    print(f'  {at:#08x} +{s:#06x} bytes {e-s}: O {txt} | C {tc}')
if '--json' in sys.argv:
    Path(sys.argv[sys.argv.index('--json') + 1]).write_text(json.dumps(dict(
        start=start, size=size, normalized_diff_bytes=len(diff),
        runs=runs, raw_equal=o.b[a:b] == c.b[a:b],
        reloc_only_original=sorted(po - pc), reloc_only_candidate=sorted(pc - po)), indent=1))
