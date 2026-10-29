#!/usr/bin/env python3
"""Summarize attribute variants: matched/raw, set deltas vs baseline, 0x14f4e0 status."""
import json, hashlib, difflib, importlib.util
from collections import Counter
from pathlib import Path
W = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained")
OUT = W / "work2/out"
ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
o = Elf(ROOT / "evidence/original/pump/deployed.so")
pub = json.loads((W / "artifacts/baseline.json").read_text())
pub_matched = set(pub["matched_set"]); pub_raw = set(pub["raw_set"])
names = {int(a, 16): n for a, n, r in pub["pairs"]}
def end_of(e, s):
    i = e.entries.index(s); return e.entries[i+1] if i+1 < len(e.entries) else e.hi
osz = end_of(o, 0x14f4e0) - 0x14f4e0
def skel(e, s, n):
    return [(e.b[s+i], e.b[s+i+1] & 0xf, e.b[s+i+1] >> 4) for i in range(0, n, 8)]
A = skel(o, 0x14f4e0, osz)
rows = []
for label in ["a1", "a2", "a3", "a4", "e1", "e2", "e3"]:
    so = OUT / (label + "-unstripped.so")
    d = json.loads((OUT / (label + ".json")).read_text())
    ms, rs = set(d["matched_set"]), set(d["raw_set"])
    c = Elf(so)
    cands = [x for x in c.funcs if "buy_exact_sol_in" in x["name"]]
    f = min(cands, key=lambda x: abs(x["size"] - 13224))
    B = skel(c, f["start"], f["size"])
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    eq = sum(i2-i1 for t,i1,i2,j1,j2 in sm.get_opcodes() if t == "equal")
    regs = [x for x in sm.get_opcodes() if x[0] != "equal"]
    a, b = Counter(A), Counter(B)
    rows.append({
        "variant": label,
        "candidate_sha256": hashlib.sha256(so.read_bytes()).hexdigest(),
        "matched": d["matched"], "raw": d["raw"],
        "matched_lost": [{"address": hex(x), "name": names.get(x)} for x in sorted(pub_matched - ms)],
        "matched_gained": [hex(x) for x in sorted(ms - pub_matched)],
        "raw_lost": [hex(x) for x in sorted(pub_raw - rs)],
        "raw_gained": [hex(x) for x in sorted(rs - pub_raw)],
        "size": f["size"], "delta": f["size"] - osz,
        "skeleton_equal": eq, "skeleton_total": len(A), "regions": len(regs),
        "skel_only_deployed": sum((a - b).values()),
        "skel_only_candidate": sum((b - a).values()),
    })
(W / "artifacts/variants-attributes.json").write_text(json.dumps(rows, indent=1) + "\n")
for r in rows:
    print("%-3s matched %4d raw %3d | lost %d gained %d | size %5d d=%+4d skel %4d/%-4d regs %2d D/C %d/%d" %
          (r["variant"], r["matched"], r["raw"], len(r["matched_lost"]), len(r["matched_gained"]),
           r["size"], r["delta"], r["skeleton_equal"], r["skeleton_total"], r["regions"],
           r["skel_only_deployed"], r["skel_only_candidate"]))
    for l in r["matched_lost"]:
        print("     lost", l["address"], (l["name"] or "")[:80])
