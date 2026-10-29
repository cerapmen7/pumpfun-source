#!/bin/bash
# Analyze a variant's cashback window against the deployed window.
set -e
W=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-amm
L=$1
O=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained/evidence/original/pump_amm/deployed.so
S=$W/mbuild/out-$L/symbols.so
python3 "$W/analysis/list_funcs.py" "$S" "sell8cashback" > "$W/mbuild/$L-funcs.txt" || true
cat "$W/mbuild/$L-funcs.txt"
read START SIZE <<<"$(python3 - "$W/mbuild/$L-funcs.txt" <<'PY'
import re, sys
for l in open(sys.argv[1]):
    if l.split()[-1].endswith('sell8cashback'):
        a = int(l.split()[0], 16); z = int(l.split()[1]); print(a, z); break
PY
)"
echo "cashback start=$START size=$SIZE"
python3 "$W/analysis/multiset_diff.py" "$O" 0x4c750 0x4ea90 "$S" "$START" "$SIZE" || true
