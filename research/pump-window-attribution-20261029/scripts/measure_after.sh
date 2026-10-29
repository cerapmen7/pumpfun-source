#!/bin/bash
set -e
P=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained
python3 "$P/scripts/measure_maintained.py" "$P/work/linux02/unstripped.so" "$P/artifacts/after.json" >/dev/null
python3 - "$P/artifacts/before.json" "$P/artifacts/after.json" "$P/artifacts/baseline.json" <<'PY'
import json, sys, hashlib
def load(p): return json.load(open(p))
b, a, pub = load(sys.argv[1]), load(sys.argv[2]), load(sys.argv[3])
for tag, d in (("before(linux01)", b), ("after(linux02)", a), ("published", pub)):
    print(tag, {k: d[k] for k in ("total", "matched", "raw")})
    for k in ("matched_set", "raw_set"):
        print("  ", k, hashlib.sha256(json.dumps(d[k], separators=(",", ":")).encode()).hexdigest())
print("before/after matched sets equal:", set(b["matched_set"]) == set(a["matched_set"]))
print("before/after raw sets equal:", set(b["raw_set"]) == set(a["raw_set"]))
print("linux matched == published matched:", set(a["matched_set"]) == set(pub["matched_set"]))
print("raw lost vs published:", [hex(x) for x in sorted(set(pub["raw_set"]) - set(a["raw_set"]))])
print("raw gained vs published:", [hex(x) for x in sorted(set(a["raw_set"]) - set(pub["raw_set"]))])
PY
