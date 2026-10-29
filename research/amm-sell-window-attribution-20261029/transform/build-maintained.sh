#!/bin/bash
# Native reproduction of the maintained layout build (host adaptation of the
# sealed podman recipe: /out -> $AMM_OUT, everything else identical).
# usage: build-maintained.sh LABEL WORKSPACE [TARGET_DIR]
set -e
W=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-amm
REPO=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained
P=$HOME/.cache/solana/v1.44/platform-tools
Q=$HOME/.cache/solana/v1.52/platform-tools
L=$1; S=$2
T=${3:-$HOME/pumpwork/target-m-$L}
OUT=$W/mbuild/out-$L
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$W/mbuild/harness/rustc_wrapper.py" "$W/mbuild/harness/linker_wrapper.py" "$OUT/"
cp "$REPO/research/amm-layout-closure-20261028/ordered.ld" "$OUT/"
chmod +x "$OUT/rustc_wrapper.py" "$OUT/linker_wrapper.py"

export PATH=$P/rust/bin:/usr/local/bin:/usr/bin:/bin
export RUSTC=$P/rust/bin/rustc
export CC=$P/llvm/bin/clang
export AR=$P/llvm/bin/llvm-ar
export CARGO_HOME=$HOME/pumpwork/netcargo
export CARGO_TARGET_DIR=$T
export CARGO_BUILD_JOBS=3
export RUSTC_WRAPPER=$OUT/rustc_wrapper.py
export AMM_OUT=$OUT
export CARGO_TARGET_SBPF_SOLANA_SOLANA_RUSTFLAGS=" -Zremap-cwd-prefix="
unset RUSTFLAGS CARGO_ENCODED_RUSTFLAGS
export CARGO_NET_OFFLINE=true

cd "$S"
$P/rust/bin/cargo build --release --target sbpf-solana-solana --locked --offline --verbose \
  > "$OUT/build.log" 2>&1 || { tail -40 "$OUT/build.log"; exit 1; }

$Q/llvm/bin/llvm-objcopy --strip-all "$T/sbpf-solana-solana/release/pump_amm_recovered.so" "$OUT/candidate.so"
cp "$T/sbpf-solana-solana/release/pump_amm_recovered.so" "$OUT/symbols.so"
sha256sum "$OUT/candidate.so" "$OUT/symbols.so"
