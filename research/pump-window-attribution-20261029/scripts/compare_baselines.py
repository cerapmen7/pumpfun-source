#!/usr/bin/env python3
"""Compare published baseline vs Linux-host build; emit markdown table for the 16 windows."""
import json, hashlib
from pathlib import Path

W = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained")
pub = json.loads((W / "artifacts/baseline.json").read_text())
lin = json.loads((W / "artifacts/baseline-linux01.json").read_text())
ms_p, ms_l = set(pub["matched_set"]), set(lin["matched_set"])
rs_p, rs_l = set(pub["raw_set"]), set(lin["raw_set"])
print("matched equal:", ms_p == ms_l, len(ms_p), len(ms_l))
print("raw lost:", sorted(hex(x) for x in rs_p - rs_l))
print("raw gained:", sorted(hex(x) for x in rs_l - rs_p))
diff = {"matched_equal": ms_p == ms_l,
        "matched_only_published": sorted(ms_p - ms_l),
        "matched_only_linux": sorted(ms_l - ms_p),
        "raw_only_published": sorted(rs_p - rs_l),
        "raw_only_linux": sorted(rs_l - rs_p)}
(W / "artifacts/published-vs-linux.json").write_text(json.dumps(diff, indent=1) + "\n")

rows = json.loads((W / "artifacts/analysis16.json").read_text())
lines = ["| Adresse | Taille (B) | Fonction candidate | Δ octets | Tuples = | Squelette = | Régions | Appels = |",
         "|---|---:|---|---:|---|---:|---:|---|"]
for r in rows:
    name = r["symbol"].split("..")[1] if ".." in r["symbol"] else r["symbol"][:40]
    lines.append("| `%s` | %d | `%s` | %+d | %s | %d/%d | %d | %s |" % (
        r["target"], r["deployed_bytes"], name, r["delta"],
        "oui" if r["tuples_equal"] else "non", r["skeleton_equal"], r["skeleton_total"],
        r["skeleton_regions"], "oui" if r["call_multiset_equal"] else "non"))
(W / "artifacts/table16.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
