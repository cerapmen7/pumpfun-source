#!/bin/bash
set -e
P=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained
cd "$P"
find . -type f ! -name SHA256SUMS -printf '%P\n' | sort | while read -r f; do
  sha256sum "$f"
done > SHA256SUMS
wc -l SHA256SUMS
