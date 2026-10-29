#!/bin/bash
W=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-amm
L=$1
python3 "$W/analysis/list_funcs.py" "$W/mbuild/out-$L/symbols.so" "cashback|cold_467|check_467" > "$W/mbuild/$L-funcs.txt" 2>&1 || true
cat "$W/mbuild/$L-funcs.txt"
echo "--- sha256"
sha256sum "$W/mbuild/out-$L/candidate.so"
echo "--- text size"
python3 "$W/analysis/sections.py" "$W/mbuild/out-$L/candidate.so" | grep "\.text"
