#!/bin/bash
R=$HOME/pumpwork/netcargo/registry/src
AG=$(find "$R" -maxdepth 2 -type d -name 'anchor-lang-0.31.1' | head -1)
echo "$AG"
grep -rn "macro_rules! require_gt" -A 12 "$AG/src" | head -30
echo "=== require ==="
grep -rn "macro_rules! require " -A 12 "$AG/src" | head -30
echo "=== error macro ==="
grep -rn "macro_rules! error" -A 25 "$AG/src" | head -40
