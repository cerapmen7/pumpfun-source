#!/bin/bash
set -e
P=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained
python3 "$P/scripts/measure_maintained.py" "$P/work/linux01/unstripped.so" "$P/artifacts/baseline-linux01.json" >/dev/null
python3 - "$P/artifacts/baseline-linux01.json" <<'PY'
import json, sys, hashlib
d = json.load(open(sys.argv[1]))
print({k: d[k] for k in ("total", "matched", "raw")})
print("unmatched", [hex(a) for a, b in d["unmatched"]])
for k in ("matched_set", "raw_set"):
    digest = hashlib.sha256(json.dumps(d[k], separators=(",", ":")).encode()).hexdigest()
    print(k, digest)
PY
