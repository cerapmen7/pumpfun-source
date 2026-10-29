#!/bin/bash
# usage: build_variant.sh <label> [srcdir]
set -e
LABEL=$1
S=${2:-/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained/work2/ws}
W=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained
OUT=$W/work2/out
SDK=$HOME/.cache/solana/v1.44/platform-tools
OBJCOPY=$HOME/.cache/solana/v1.52/platform-tools/llvm/bin/llvm-objcopy
CH=$HOME/pumpwork/netcargo
mkdir -p "$OUT"
python3 - <<'PY'
from pathlib import Path
src = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained/research/pump-program-creator-notice-qualification-20261028/tools/pump_physical_source_wrapper.py")
dst = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained/work2/wrapper.py")
dst.write_bytes(src.read_bytes().replace(b"\r\n", b"\n"))
PY
rm -f "$OUT/$LABEL-unstripped.so" "$OUT/$LABEL-candidate.so"

export RUSTC_WRAPPER=$W/work2/wrapper.py
export PUMP_LOGICAL_REGISTRY_SRC=$CH/registry/src
export PUMP_SOURCE_WRAPPER_LOG=$OUT/$LABEL-physical.jsonl
export CARGO_HOME=$CH
export CARGO_TARGET_DIR=$HOME/pumpwork/target-work2
export CARGO_BUILD_JOBS=2
export RUSTC=$SDK/rust/bin/rustc
export CC=$SDK/llvm/bin/clang
export AR=$SDK/llvm/bin/llvm-ar
export OBJCOPY=$OBJCOPY
export CARGO_TARGET_SBPF_SOLANA_SOLANA_RUSTFLAGS="-Zremap-cwd-prefix="
unset RUSTFLAGS CARGO_ENCODED_RUSTFLAGS RUSTC_WORKSPACE_WRAPPER

cd "$S"
$SDK/rust/bin/cargo build --manifest-path "$S/programs/pump/Cargo.toml" \
  --locked --offline --release --target sbpf-solana-solana \
  > "$OUT/$LABEL-build.log" 2>&1 || { tail -40 "$OUT/$LABEL-build.log"; exit 1; }
cp "$HOME/pumpwork/target-work2/sbpf-solana-solana/release/pump_recovered.so" "$OUT/$LABEL-unstripped.so"
$OBJCOPY --strip-all "$OUT/$LABEL-unstripped.so" "$OUT/$LABEL-candidate.so"
sha256sum "$OUT/$LABEL-unstripped.so" "$OUT/$LABEL-candidate.so"
python3 "$W/scripts/measure_maintained.py" "$OUT/$LABEL-unstripped.so" "$OUT/$LABEL.json" >/dev/null
python3 - "$OUT/$LABEL.json" "$LABEL" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
print(sys.argv[2], "matched", d["matched"], "raw", d["raw"])
print("targets matched?", [hex(a) for a,_ in d["unmatched"] if a in (0x14f4e0,)])
PY
