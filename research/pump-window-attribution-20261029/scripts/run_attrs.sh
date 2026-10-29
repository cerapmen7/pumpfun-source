#!/bin/bash
set -e
P=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained
cd "$P"
for v in a2 a3 a4; do
  echo "===== $v"
  python3 scripts/apply_variant.py "$v" >/dev/null
  bash scripts/build_variant.sh "$v"
done
