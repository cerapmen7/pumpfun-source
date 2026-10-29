#!/bin/bash
set -e
P=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained
R=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained
python3 "$P/scripts/measure_maintained.py" \
  "$R/research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so" \
  "$P/artifacts/baseline.json" > /dev/null
python3 - <<'PY'
import json,hashlib
d=json.load(open('/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained/artifacts/baseline.json'))
print({k:d[k] for k in ('total','matched','raw')})
print('unmatched',len(d['unmatched']))
for a,b in d['unmatched']: print(hex(a),b)
for k in ('matched_set','raw_set'):
    print(k,hashlib.sha256(json.dumps(d[k],separators=(",",":")).encode()).hexdigest())
PY
