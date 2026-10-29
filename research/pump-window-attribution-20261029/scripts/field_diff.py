#!/usr/bin/env python3
"""Field-level diff between a deployed target window and a candidate function."""
import sys, importlib.util, collections
from pathlib import Path

ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
import struct

o = Elf(ROOT / "evidence/original/pump/deployed.so")
c = Elf(ROOT / "research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so")
PAIRS = [
    (0x14f4e0, 0x14e680, "buy_exact_sol_in"),
    (0x4c158, 0x5f438, "migrate_v2::create_token_account_v2"),
    (0x80df8, 0x997f0, "trade::v3_buy_costs"),
    (0x83c00, 0x9ecb8, "trade::v3_execute_buy"),
    (0x147ba0, 0x9fe18, "trade::buy"),
    (0x1489f8, 0xa0ef8, "trade::buy_exact_quote"),
    (0x13b9b8, 0x16e58, "buy_v2::buy_handler"),
    (0x13f630, 0x1aea8, "buy_v2::buy_exact_quote_in_handler"),
    (0x144508, 0x85e98, "sell_v2::execute"),
    (0x6cd78, 0x81800, "legacy_sell::process_cashback_inner"),
    (0x77940, 0x92d20, "claim cashback_v2?"),
    (0x72810, 0x8d838, "sweep::execute"),
    (0x5b3b0, 0x67970, "multi_hop_curve::swap_hop"),
    (0x1e7c0, 0x2c330, "create_v2::execute"),
    (0x22a10, 0x2fd30, "admin_cto::execute"),
]

def insns(e, start, size):
    out = []
    for off in range(0, size, 8):
        b = e.b[start + off:start + off + 8]
        imm = struct.unpack_from("<i", b, 4)[0]
        out.append((b[0], b[1] & 0xf, b[1] >> 4, struct.unpack_from("<h", b, 2)[0], imm, b.hex()))
    return out

for da, ca, label in PAIRS:
    z = o.entries[o.entries.index(da) + 1] if da in o.entries and o.entries.index(da) + 1 < len(o.entries) else o.hi
    osz = z - da
    f = next((x for x in c.funcs if x["start"] == ca), None)
    if f is None:
        print(hex(da), "candidate missing"); continue
    csz = f["size"]
    A, B = insns(o, da, osz), insns(c, ca, csz)
    n = min(len(A), len(B))
    cats = collections.Counter()
    examples = collections.defaultdict(list)
    for i in range(n):
        a, b = A[i], B[i]
        if a[5] == b[5]:
            continue
        if a[0] != b[0] or a[1] != b[1] or a[2] != b[2]:
            k = "opcode_or_regs"
        elif a[3] != b[3]:
            k = "branch_or_store_off"
        elif a[4] != b[4]:
            k = "immediate"
        else:
            k = "other"
        cats[k] += 1
        if len(examples[k]) < 6:
            examples[k].append((i, a[5], b[5]))
    print("=== %s  deployed %s %d B  cand %s %d B  d=%+d  common %d insns" %
          (label, hex(da), osz, hex(ca), csz, csz - osz, n))
    print("   diffs:", dict(cats), " total", sum(cats.values()))
    for k, ex in examples.items():
        print("   ", k)
        for i, x, y in ex:
            print("      insn %d  %s -> %s" % (i, x, y))
