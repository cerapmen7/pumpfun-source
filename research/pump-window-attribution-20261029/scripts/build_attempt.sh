#!/bin/bash
R=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained
P=$R/research/pump-program-creator-notice-qualification-20261028
W=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained/work
OUT=$W/build-attempt-01
rm -rf "$OUT"
cd "$R"
python3 -B "$P/build.py" \
  --source-directory "$P/source" \
  --sdk "$HOME/.cache/solana/v1.44/platform-tools" \
  --cargo-home "$HOME/pumpwork/netcargo" \
  --target-library-profile linux-v1.44-sbpf \
  --target-libraries "$HOME/.cache/solana/v1.44/platform-tools/rust/lib/rustlib/sbpf-solana-solana/lib" \
  --wrapper "$P/tools/pump_physical_source_wrapper.py" \
  --output "$OUT" \
  --jobs 2 2>&1 | tail -40
echo "exit=${PIPESTATUS[0]}"
