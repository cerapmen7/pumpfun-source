#!/usr/bin/env python3
"""Compare candidate helper variants that the 16 windows call differently."""
import importlib.util, hashlib
from pathlib import Path
ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
c = Elf(ROOT / "research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so")
WANT = ["transfer_to_user", "transfer_to_recipient", "transfer_to_owned",
        "transfer_from_user", "transfer_from_user_recipient", "transfer_from_user_owned",
        "fit_post_complete", "net_quote_for_budget", "v3_buy_costs", "v3_execute_buy"]
for w in WANT:
    hits = [f for f in c.funcs if w in f["name"]]
    for f in hits:
        raw = c.b[f["start"]:f["start"] + f["size"]]
        norm = c.normalized[f["start"]:f["start"] + f["size"]]
        print("%-32s %-9s %6d  raw %s  norm %s" % (w, hex(f["start"]), f["size"],
              hashlib.sha256(raw).hexdigest()[:16], hashlib.sha256(norm).hexdigest()[:16]))
