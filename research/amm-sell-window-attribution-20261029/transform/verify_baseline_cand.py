#!/usr/bin/env python3
"""Measure a candidate symbols.so with the repository metric and write JSON sets.

usage: verify_baseline_cand.py CANDIDATE_SYMBOLS OUT.json [ORIGINAL]
"""
import json, sys
from pathlib import Path
REPO = Path('/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained')
sys.path.insert(0, str(REPO / 'scripts'))
import window_measure as wm

orig = Path(sys.argv[3]) if len(sys.argv) > 3 else REPO / 'evidence/original/pump_amm/deployed.so'
rows = wm.measure(orig, Path(sys.argv[1]))
matched = [int(r['original'], 16) for r in rows if r['match']]
raw = [int(r['original'], 16) for r in rows if r['raw']]
out = dict(total=len(rows), matched=len(matched), raw=len(raw),
           unmatched=[[int(r['original'], 16), r['bytes']] for r in rows if not r['match']],
           matched_set=matched, raw_set=raw)
Path(sys.argv[2]).write_text(json.dumps(out, indent=1) + '\n')
print(json.dumps({k: out[k] for k in ('total', 'matched', 'raw', 'unmatched')}))
