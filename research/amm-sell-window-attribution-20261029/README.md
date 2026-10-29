# PumpSwap: the last window `0x4c750` (sell) — gap reduced to one block-placement decision

Research packet. No source change is retained: this package records a
byte-identical reproduction of the maintained build, the exact remaining gap and
documented negative results.

Detailed record: [`RESULT.md`](RESULT.md) (French). Everything below is a summary
of its measured numbers.

## Scope

The maintained AMM checkpoint matches **784/785** original windows, all
raw-identical. This packet studies the single remaining window **`0x4c750`**
(deployed sell body, 9,024 bytes / 1,075 instructions at offset 313,168)
against `research/amm-layout-closure-20261028/results/build-a/`.

## Baseline reproduction (measured)

- The sealed recipe (`workspace_recipe_v3.py` staging, same flags, same
  `ordered.ld`, same `rust-lld`) reproduces the maintained candidate
  **byte-identically**: `candidate.so` `86dbc2c64e81…`, `symbols.so`
  `7271aaf8…`, and a cold rebuild from a fresh target is identical too.
  (Podman absent; the same sealed recipe ran natively with only `/out` →
  `$AMM_OUT` path adaptation in two wrappers.)
- `ordered.ld` in the checkout is CRLF; after `tr -d '\r'` it matches its
  recorded hash `b8a35889…`.
- Repo metric (`scripts/window_measure.py`): **785 windows, 784 matched,
  784 raw**, unmatched = `0x4c750` only.

## Findings — the exact remaining gap

Not size, not lines, not relocations:

- identical window address, size (9,024 B), instruction count (1,075), 47
  relocation rows and all 10 baked `sell.rs` tuples
  (378/383/392/395/444/448/464/467/502×2);
- instruction multisets are identical **except one encoding** at `0x4d450`:
  `jeqr r2,r3,+1; ja` (deployed) vs `jner r2,r3,far` (candidate);
- 47/47 relocation rows pair by payload; 26 offsets are identical and **21 are
  shifted** — this is exactly the `21 relocation-offset rows` named in the
  checkpoint README;
- one block-placement decision explains both: the error arm at `sell.rs:467`
  sits in the cold queue in the deployed (`0x4e718`) but is inlined in the
  candidate (`0x4e2a0`), and the create/join order is inverted. In the emitted
  IR, `bb68` (join) is emitted before `bb65` (create), so `MachineBlockPlacement`
  keeps join as fallthrough. No semantic difference.

## Documented negatives (10 source variants measured)

All frontend-level rewrites of the surrounding conditions (`if !…`, `else {}`,
`== false`, `match` on `is_writable`/`data_is_empty`, inverted if/else) compile
to the **byte-identical** binary `86dbc2c6…` — the frontend canonicalizes them.
One variant (`match try_borrow_data()` instead of `?`) perturbs global layout
(`.text` −24 B, raw collapses 784 → 257) and was rejected. A control variant
changing an error code produces a different binary, confirming the rebuild loop.

## Non-regression

No retained source change; every retained build keeps the 784 raw-identical
windows (`matched_set`/`raw_set` recorded in `measurements/base.json`).

## Contents

- `RESULT.md` — full measured record (gap analysis, relocation ledger, IR block
  evidence, variants table, commands, toolchain, limits).
- `measurements/` — baseline and variant measurements with sets and hashes.
- `analysis/` — window gap, block sequence diff, instruction multiset,
  relocation ledgers (deployed/candidate/pairing), error tuples, IR block
  dump, verification transcript, toolchain/recipe record.
- `variants/` — the ten measured source patches (none retained).
- `transform/` — staging, build, measurement and analysis scripts with asserts.
- `SHA256SUMS` — checksums for every file above.

Note: some helper scripts embed absolute paths of the research host; adjust them
before running elsewhere. Exact reproduction commands are in `RESULT.md` §6.

## Limits

The window is not gained. The remaining difference is an IR/`llc` block-ordering
decision; the per-function-section reorder path used by `ordered.ld` could not be
exercised with the SDK `llc` (monolithic `.text` + `.text.unlikely`). The exact
historical source form that produces the deployed ordering is not found; no
runtime behavior is claimed or changed.
