#!/usr/bin/env python3
"""Verify the maintained baseline with the repository metric.

usage: verify_baseline.py REPO [--json out.json]
Writes/prints total, matched, raw, unmatched windows.
"""
import json, sys
from pathlib import Path
repo = Path(sys.argv[1])
sys.path.insert(0, str(repo / 'scripts'))
import window_measure as wm

o = repo / 'evidence/original/pump_amm/deployed.so'
c = repo / 'research/amm-layout-closure-20261028/results/build-a/symbols.so'
rows = wm.measure(o, c)
matched = [r for r in rows if r['match']]
raw = [r for r in rows if r['raw']]
un = [r for r in rows if not r['match']]
out = dict(total=len(rows), matched=len(matched), raw=len(raw),
           unmatched=[[int(r['original'], 16), r['bytes']] for r in un],
           matched_set=[int(r['original'], 16) for r in matched],
           raw_set=[int(r['original'], 16) for r in raw])
print(json.dumps({k: v for k, v in out.items() if k not in ('matched_set', 'raw_set')}, indent=1))
if '--json' in sys.argv:
    Path(sys.argv[sys.argv.index('--json') + 1]).write_text(json.dumps(out, indent=1) + '\n')
