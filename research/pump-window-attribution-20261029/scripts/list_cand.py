#!/usr/bin/env python3
"""Candidate functions per module for the 16 targets (maintained candidate)."""
import sys, re, json, importlib.util, collections
from pathlib import Path

ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf

CAND = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so"
c = Elf(CAND)
KW = {
 "0x1e7c0": ["create_v2"],
 "0x22a10": ["admin_cto"],
 "0x4c158": ["migrate_v2"],
 "0x5b3b0": ["multi_hop_curve"],
 "0x6cd78": ["sell"],
 "0x72810": ["sweep"],
 "0x77940": ["claim_token_incentives", "token_incentives"],
 "0x80df8": ["trade"],
 "0x83c00": ["trade"],
 "0x13b9b8": ["buy_v2"],
 "0x13f630": ["buy_v2"],
 "0x144508": ["sell_v2"],
 "0x147ba0": ["trade"],
 "0x1489f8": ["trade"],
 "0x14a8a8": ["trade"],
 "0x14f4e0": ["buy"],
}

def demangle(n):
    m = re.search(r"\.\.([A-Za-z0-9_]+)\.\.([A-Za-z0-9_]+?)(?:\d|$)", n)
    if m: return m.group(1) + "::" + m.group(2)
    m = re.search(r"(\d+)([a-z_0-9]+)\d+(\d+)([a-z_0-9]+)[0-9a-f]{16}E", n)
    return n

for a, kws in KW.items():
    print("===", a, kws)
    rows = []
    for f in c.funcs:
        n = f["name"]
        if any(k in n for k in kws):
            rows.append(f)
    rows.sort(key=lambda f: -f["size"])
    for f in rows[:8]:
        print("   %-9s %6d B  %s" % (hex(f["start"]), f["size"], f["name"][:110]))
