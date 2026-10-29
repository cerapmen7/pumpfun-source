# Pump: attribution of the 16 remaining unmatched windows

Research packet. No source change is retained (`source-diff.patch` is empty): this
package records measurements, attribution and documented negative results only.

Detailed record: [`RESULT.md`](RESULT.md) (French). Everything below is a summary
of its measured numbers.

## Scope

The maintained Pump checkpoint matches **1,019/1,035** original function windows
(188 raw). This packet studies the **16 remaining unmatched windows** of
`evidence/original/pump/deployed.so` against the maintained candidate built from
`research/pump-program-creator-notice-qualification-20261028/`.

## Baseline reproduction (measured)

- The published artifact (`artifacts/unstripped.so`, `0f50faa8…`) measures
  **1,019 matched / 188 raw** with `scripts/window_measure.py`; the 16 unmatched
  windows are exactly the published targets.
- A Linux rebuild of the same 65/65 source inputs (after LF normalization of
  checkout CRLF; wrapper and 25/25 SBPF libraries verified against their recorded
  hashes) reproduces the **identical matched set of 1,019** and 183 raw (7 lost /
  2 gained raw rows, all std/alloc/metaplex bodies). Two fresh target directories
  produce byte-identical outputs.
- The published build itself locks **macOS host tools** and is not reproducible on
  this Linux/Windows host; only host binaries differ.

## Findings

- All 16 windows are whole function bodies called from the Anchor dispatcher at
  `0x11b758`: `create_v2`, `admin_cto`, a `migrate_v2` helper, `multi_hop_swap`,
  `sell`, `sweep`, `claim_token_incentives`, `sell_v2`, `buy_v2` (×2),
  `trade_v3` (×3 + 2 helpers) and legacy `buy_exact_sol_in`.
- 96 `(path, line, code)` tuples baked by `error!`/`require!` identify the source
  modules and line ranges of each window.
- 8 windows share identical callee signatures with their local counterparts
  (`0x4c158, 0x80df8, 0x83c00, 0x13b9b8, 0x13f630, 0x144508, 0x14a8a8, 0x14f4e0`);
  the divergence is intra-body.
- `0x14f4e0` (`buy_exact_sol_in`) is within **4 instructions** of parity (same
  size 13,224 B, identical tuples and callees, 1,627/1,653 skeleton, 8 regions):
  two complementary branch polarities and cold error-block placement.
  **Five source variants were built and measured**; none matched. Findings:
  LLVM canonicalizes `if cond {…} else {…}` and `if !cond {…}` to the same
  output (source condition inversion does not control branch polarity), and the
  remaining difference is a `MachineBlockPlacement` cold-block ordering.
- Helpers `0x80df8`/`0x83c00` are called by `0x147ba0`/`0x1489f8`; closing the
  helper pair could therefore close four windows (minimal induced graph).
- Documented negative: `transfer_to_user`/`transfer_to_recipient` (and the
  `*_from_*` pair) have identical normalized bytes, so their exchange is
  invisible to the window metric.

## Non-regression

`matched_set` is bit-identical across the published artifact, both Linux builds
and every measured variant (SHA-256 of the set recorded in `artifacts/`).
`raw_set` is identical between before/after builds. No retained source change.

## Contents

- `RESULT.md` — full measured record (tables, per-window causes, commands,
  toolchain identity with hashes, explicit limits).
- `artifacts/` — measurement JSONs (sets included), per-window analysis,
  callee signatures, target call graph, build identities, environment notes.
- `scripts/` — measurement, Linux build and analysis scripts with asserts,
  including `verify_packet.py`.
- `experiment-v*/` patches and `measure-*.json` — the five measured variants of
  `0x14f4e0`, none retained.
- `SHA256SUMS` — checksums for every file above.

Note: some helper scripts embed absolute paths of the research host; adjust them
before running elsewhere. Exact reproduction commands are in `RESULT.md` §6.

## Limits

No window is gained by this packet. Function-body decomposition and IR block
ordering remain the open causes; historical Rust spelling and the unique original
build recipe remain unproven. No runtime behavior is claimed or changed.
