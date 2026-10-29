#!/usr/bin/env python3
"""Pair relocation rows of two text ranges by the payload they reference.

Key:
  * a path only when the referenced bytes literally start with 'programs/' and
    contain '.rs' within the first 80 bytes (error-site path string);
  * otherwise the first 24 printable characters of the packed target, plus the
    target section.
"""
import sys, json, collections

a = json.load(open(sys.argv[1])); b = json.load(open(sys.argv[2]))

def key(r):
    p = r['preview'] or ''
    if p.startswith('programs/') and '.rs' in p[:80]:
        return ('path', p[:p.index('.rs')+3])
    return ('str', p[:24])

A = a['rows']; B = b['rows']
ca = collections.Counter(key(r) for r in A)
cb = collections.Counter(key(r) for r in B)
print(f"deployed rows={len(A)} candidate rows={len(B)}")
print('\n-- payload counts (deployed / candidate):')
for k in sorted(set(ca) | set(cb), key=str):
    print(f'  {ca.get(k,0):2d} / {cb.get(k,0):2d}  {k}')

used = set(); pairs = []; only_a = []
for ra in A:
    k = key(ra)
    hit = next((j for j, rb in enumerate(B) if j not in used and key(rb) == k), None)
    if hit is None: only_a.append(ra)
    else: used.add(hit); pairs.append((ra, B[hit]))
only_b = [rb for j, rb in enumerate(B) if j not in used]
print(f'\n-- paired by payload: {len(pairs)}; deployed-only: {len(only_a)}; candidate-only: {len(only_b)}')
print('\n-- deployed-only rows:')
for r in only_a:
    print(f"  site {r['site']:#08x} off {r['off']:#06x} type {r['type']} key {key(r)} preview {r['preview'][:50]!r}")
print('\n-- candidate-only rows:')
for r in only_b:
    print(f"  site {r['site']:#08x} off {r['off']:#06x} type {r['type']} key {key(r)} preview {r['preview'][:50]!r}")
print('\n-- offset drift of paired rows:')
for ra, rb in pairs:
    d = rb['off'] - ra['off']
    print(f"   {ra['off']:#06x} -> {rb['off']:#06x}  drift {d:+#06x}  {str(key(ra)[-1])[:48]}")
