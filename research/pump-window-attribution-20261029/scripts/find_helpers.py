#!/usr/bin/env python3
"""Find and print helper definitions and their call sites in the maintained source."""
import re
from pathlib import Path

S = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained/research/pump-program-creator-notice-qualification-20261028/source")
PATS = ["fn transfer_to_user", "fn transfer_to_recipient", "fn transfer_to_owned",
        "fn transfer_from_user", "fn transfer_from_user_recipient",
        "fn fit_post_complete", "fn net_quote_for_budget", "fn v3_buy_costs",
        "fn v3_execute_buy"]
for p in sorted(S.rglob("*.rs")):
    text = p.read_text(errors="replace").splitlines()
    for i, line in enumerate(text, 1):
        for pat in PATS:
            if pat in line:
                print("%s:%d: %s" % (p.relative_to(S), i, line.strip()[:220]))
