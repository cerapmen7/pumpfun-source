#!/usr/bin/env python3
import importlib.util
from pathlib import Path
ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
o = Elf(ROOT / "evidence/original/pump/deployed.so")
c = Elf(ROOT / "research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so")
WANT_D = {(85, 3, 0), (61, 3, 0)}
WANT_C = {(21, 3, 0), (173, 3, 0)}
for label, e, base, size, want in [("D", o, 0x14f4e0, 13224, WANT_D), ("C", c, 0x14e680, 13224, WANT_C)]:
    for i in range(0, size, 8):
        k = (e.b[base+i], e.b[base+i+1] & 0xf, e.b[base+i+1] >> 4)
        if k in want:
            print(label, "idx", i // 8, "addr", hex(base + i), "skeleton", k)
