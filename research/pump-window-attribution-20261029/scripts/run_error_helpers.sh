#!/bin/bash
set -e
P=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained
cd "$P"
for v in e2 e3; do
  echo "===== $v"
  python3 scripts/apply_variant.py "$v" >/dev/null
  bash scripts/build_variant.sh "$v"
  python3 scripts/eval_variant.py "work2/out/$v-unstripped.so" | head -16
done
