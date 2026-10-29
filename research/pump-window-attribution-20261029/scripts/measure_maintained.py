#!/usr/bin/env python3
"""Measure the maintained candidate against the deployed pump ELF with the
repository's own scripts/window_measure.py (stdlib only).

usage: measure_maintained.py <candidate_with_symbols.so> [out.json]
"""
import json, sys, importlib.util
from pathlib import Path

ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
P = ROOT / "scripts/window_measure.py"
spec = importlib.util.spec_from_file_location("window_measure", P)
wm = importlib.util.module_from_spec(spec); spec.loader.exec_module(wm)

orig = ROOT / "evidence/original/pump/deployed.so"
cand = Path(sys.argv[1])
rows = wm.measure(orig, cand)
matched = [r for r in rows if r["match"]]
raw = [r for r in rows if r["raw"]]
out = {
    "candidate": str(cand),
    "total": len(rows),
    "matched": len(matched),
    "raw": len(raw),
    "matched_set": [int(r["original"], 16) for r in matched],
    "raw_set": [int(r["original"], 16) for r in raw],
    "unmatched": [[int(r["original"], 16), r["bytes"]] for r in rows if not r["match"]],
    "pairs": [[r["original"], r["match"], r["raw"]] for r in matched],
}
print(json.dumps(out))
if len(sys.argv) > 2:
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1) + "\n")
