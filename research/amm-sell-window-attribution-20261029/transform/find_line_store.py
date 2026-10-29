import sys, struct
from pathlib import Path
p = sys.argv[1]; lo = int(sys.argv[2],0); hi = int(sys.argv[3],0)
want = int(sys.argv[4],0)
b = Path(p).read_bytes()
at = lo; ins = []
while at < hi:
    op = b[at]; regs = b[at+1]; off, imm = struct.unpack_from('<hi', b, at+2)
    w = 16 if op == 0x18 else 8
    ins.append((at, op, regs, off, imm)); at += w
for i, (a, op, regs, off, imm) in enumerate(ins):
    if op == 0x62 and imm == want:  # stw imm
        ctx = ins[max(0,i-10):i+2]
        has_path = any(o == 0x18 and 0 <= m < len(b) and b'm/sell.rs' in b[m:m+60] for (_, o, _, _, m) in ctx)
        print(f'{a:#08x} stw {want:#x} context_path={has_path}')
        if has_path:
            for (aa, oo, rr, of, mm) in ctx:
                print(f'    {aa:#08x} op{oo:#04x} imm={mm:#x}')
