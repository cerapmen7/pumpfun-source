#!/usr/bin/env python3
"""Consolidated analysis of the 16 unmatched windows against the maintained candidate."""
import json, re, struct, difflib, importlib.util
from collections import Counter
from pathlib import Path

W = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained")
ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
o = Elf(ROOT / "evidence/original/pump/deployed.so")
c = Elf(ROOT / "research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so")
base = json.loads((W / "artifacts/baseline.json").read_text())
rank = {}
for orig, name, raw in base["pairs"]:
    rank[int(orig, 16)] = name
PAIRS = [(0x1e7c0, 0x2c330), (0x22a10, 0x2fd30), (0x4c158, 0x5f438), (0x5b3b0, 0x67970),
         (0x6cd78, 0x81800), (0x72810, 0x8d838), (0x77940, 0x92d20), (0x80df8, 0x997f0),
         (0x83c00, 0x9ecb8), (0x13b9b8, 0x16e58), (0x13f630, 0x1aea8), (0x144508, 0x85e98),
         (0x147ba0, 0x9fe18), (0x1489f8, 0xa0ef8), (0x14a8a8, 0xa3798), (0x14f4e0, 0x14e680)]

def end_of(e, start):
    i = e.entries.index(start)
    return e.entries[i + 1] if i + 1 < len(e.entries) else e.hi

def skeleton(e, start, size):
    return [(e.b[start + i], e.b[start + i + 1] & 0xf, e.b[start + i + 1] >> 4)
            for i in range(0, size, 8)]

def tuples(e, start, size):
    out = []
    for off in range(0, size, 8):
        at = start + off
        b = e.b[at:at + 16]
        if b[0] != 0x18: continue
        val = struct.unpack_from("<Q", b, 4)[0]
        sec = next((s for s in e.raw if s[3] <= val < s[3] + s[5]), None)
        if not sec: continue
        blob = e.b[sec[4] + (val - sec[3]): sec[4] + (val - sec[3]) + 240]
        m = re.match(rb"(?:programs|src|tests|/home)/[A-Za-z0-9_./-]+?\.rs", blob)
        if not m: continue
        line = code = None
        for k in range(1, 14):
            bb = e.b[at + k * 8: at + k * 8 + 8]
            if len(bb) < 8: break
            if bb[0] == 0x62:
                v = struct.unpack_from("<I", bb, 4)[0]
                if 6000 <= v < 6200 and code is None: code = v
                elif 40 <= v < 4000 and line is None: line = v
        if line or code:
            out.append((m.group(0).decode(), line, code, off // 8))
    return out

def call_targets(e, start, size):
    out = []
    for i in range(0, size, 8):
        at = start + i
        if e.b[at] == 0x85 and e.b[at + 1] == 0x10 and e.relocations.get(at, {}).get("type") != 10:
            out.append(at + 8 + struct.unpack_from("<i", e.b, at + 4)[0] * 8)
    return out

def dep_name(addr):
    cands = [a for a in rank if a <= addr]
    if not cands:
        return "?"
    n = rank[max(cands)]
    parts = n.split("..")
    return parts[1] if len(parts) > 2 else n

sym = {f["start"]: f["name"] for f in c.funcs}
rows = []
for da, ca in PAIRS:
    osz = end_of(o, da) - da
    f = next(x for x in c.funcs if x["start"] == ca)
    ot, ct = tuples(o, da, osz), tuples(c, ca, f["size"])
    ot_set = sorted({(p, l, k) for p, l, k, _ in ot}, key=lambda x: (x[1] or 0, x[2] or 0))
    ct_set = sorted({(p, l, k) for p, l, k, _ in ct}, key=lambda x: (x[1] or 0, x[2] or 0))
    A, B = skeleton(o, da, osz), skeleton(c, ca, f["size"])
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    regs = [x for x in sm.get_opcodes() if x[0] != "equal"]
    eq = sum(i2 - i1 for t, i1, i2, j1, j2 in sm.get_opcodes() if t == "equal")
    anchors = {i: (p, l, k) for p, l, k, i in ot}
    regions = []
    for tag, i1, i2, j1, j2 in regs[:6]:
        pa = max((i for i in anchors if i <= i1), default=None)
        regions.append({"tag": tag, "d_start": i1, "d_end": i2, "c_start": j1,
                        "c_end": j2, "anchor": anchors.get(pa)})
    dc = Counter(dep_name(x) for x in call_targets(o, da, osz))
    cc = Counter((sym.get(x) or "?").split("..")[1] if ".." in (sym.get(x) or "") else sym.get(x)
                 for x in call_targets(c, ca, f["size"]))
    rows.append({
        "target": hex(da), "candidate": hex(ca), "symbol": f["name"],
        "deployed_bytes": osz, "candidate_bytes": f["size"], "delta": f["size"] - osz,
        "tuples_equal": ot_set == ct_set,
        "deployed_tuple_count": len(ot_set), "candidate_tuple_count": len(ct_set),
        "tuple_diff_deployed_only": [list(x) for x in ot_set if x not in ct_set],
        "tuple_diff_candidate_only": [list(x) for x in ct_set if x not in ot_set],
        "skeleton_equal": eq, "skeleton_total": len(A),
        "skeleton_regions": len(regs),
        "first_regions": regions,
        "call_multiset_equal": bool(not (dc - cc) and not (cc - dc)),
        "call_only_deployed": sorted((dc - cc).elements()),
        "call_only_candidate": sorted((cc - dc).elements()),
    })
(W / "artifacts/analysis16.json").write_text(json.dumps(rows, indent=1) + "\n")
print("wrote analysis16.json")
for r in rows:
    print("%-9s %-6d d=%+6d tuples_eq=%-5s skel %4d/%-4d regs %3d calls_eq=%-5s %s" %
          (r["target"], r["deployed_bytes"], r["delta"], r["tuples_equal"],
           r["skeleton_equal"], r["skeleton_total"], r["skeleton_regions"],
           r["call_multiset_equal"], r["symbol"].split("..")[1][:45] if ".." in r["symbol"] else ""))
