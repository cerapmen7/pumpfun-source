#!/bin/bash
P=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained
R=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained
{
echo "== date"; date -u
echo "== host"; uname -a
echo "== repo HEAD"; cat "$R/.git/HEAD"; cat "$R/.git/refs/heads/main"
echo "== sparse"; cat "$R/.git/info/sparse-checkout"
echo "== deployed sha"; sha256sum "$R/evidence/original/pump/deployed.so"
echo "== published artifacts"
sha256sum "$R/research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so" \
          "$R/research/pump-program-creator-notice-qualification-20261028/artifacts/candidate.so"
echo "== linux01/02 artifacts"
sha256sum "$P/work/linux01/unstripped.so" "$P/work/linux01/candidate.so" \
          "$P/work/linux02/unstripped.so" "$P/work/linux02/candidate.so"
echo "== toolchain"
~/.cache/solana/v1.44/platform-tools/rust/bin/rustc --version
~/.cache/solana/v1.44/platform-tools/rust/bin/cargo --version
~/.cache/solana/v1.44/platform-tools/llvm/bin/clang --version | head -1
sha256sum ~/.cache/solana/v1.44/platform-tools/rust/bin/rustc \
          ~/.cache/solana/v1.44/platform-tools/rust/bin/cargo \
          ~/.cache/solana/v1.44/platform-tools/llvm/bin/clang \
          ~/.cache/solana/v1.52/platform-tools/llvm/bin/llvm-objcopy
} > "$P/artifacts/environment.txt" 2>&1
python3 "$P/scripts/check_source_lf.py" > "$P/artifacts/source-lf-check.txt" 2>&1
python3 "$P/scripts/check_libs.py" > "$P/artifacts/target-libs-check.txt" 2>&1
cat "$P/artifacts/source-lf-check.txt" "$P/artifacts/target-libs-check.txt"
