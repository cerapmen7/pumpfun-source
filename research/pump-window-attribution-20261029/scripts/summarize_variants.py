#!/usr/bin/env python3
"""Summarize the 0x14f4e0 variants: metric, size, skeleton, regions, multiset deltas."""
import json, difflib, hashlib, importlib.util
from collections import Counter
from pathlib import Path
W = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained")
OUT = W / "work2/out"
ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
o = Elf(ROOT / "evidence/original/pump/deployed.so")
def end_of(e, s):
    i = e.entries.index(s); return e.entries[i+1] if i+1 < len(e.entries) else e.hi
osz = end_of(o, 0x14f4e0) - 0x14f4e0
def skel(e, s, n):
    return [(e.b[s+i], e.b[s+i+1] & 0xf, e.b[s+i+1] >> 4) for i in range(0, n, 8)]
A = skel(o, 0x14f4e0, osz)
rows = []
for label in ["v0", "v1", "v1c", "v1d", "v2c", "v3c"]:
    so = OUT / (label + "-unstripped.so")
    if not so.exists():
        continue
    c = Elf(so)
    cands = [x for x in c.funcs if "buy_exact_sol_in" in x["name"]]
    f = min(cands, key=lambda x: abs(x["size"] - 13224))
    B = skel(c, f["start"], f["size"])
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    eq = sum(i2-i1 for t,i1,i2,j1,j2 in sm.get_opcodes() if t == "equal")
    regs = [x for x in sm.get_opcodes() if x[0] != "equal"]
    a, b = Counter(A), Counter(B)
    meas = json.loads((OUT / (label + ".json")).read_text())
    rows.append({
        "variant": label,
        "candidate_sha256": hashlib.sha256(so.read_bytes()).hexdigest(),
        "function_start": hex(f["start"]), "size": f["size"], "delta": f["size"] - osz,
        "matched": meas["matched"], "raw": meas["raw"],
        "target_matched": not any(a == 0x14f4e0 for a, _ in meas["unmatched"]),
        "skeleton_equal": eq, "skeleton_total": len(A), "regions": len(regs),
        "skel_only_deployed": [[list(k), v] for k, v in (a - b).items()],
        "skel_only_candidate": [[list(k), v] for k, v in (b - a).items()],
    })
(W / "artifacts/variants-0x14f4e0.json").write_text(json.dumps(rows, indent=1) + "\n")
for r in rows:
    print("%-4s size %5d d=%+4d skel %4d/%-4d regs %2d D/C %d/%d matched %d raw %d target %s" %
          (r["variant"], r["size"], r["delta"], r["skeleton_equal"], r["skeleton_total"],
           r["regions"], len(r["skel_only_deployed"]), len(r["skel_only_candidate"]),
           r["matched"], r["raw"], r["target_matched"]))
