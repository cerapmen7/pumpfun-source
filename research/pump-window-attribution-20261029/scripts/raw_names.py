#!/usr/bin/env python3
import importlib.util
from pathlib import Path
ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
c = Elf(ROOT / "research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so")
for a in [0x188d30, 0x188fe0, 0x1891d8, 0x189340, 0x18de90, 0x18e568, 0x1a7b00, 0x199af0, 0x199b18]:
    f = next((x for x in c.funcs if x["start"] == a), None)
    print(hex(a), f["size"] if f else None, f["name"] if f else None)
