import struct, importlib.util
from pathlib import Path
ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
o = Elf(ROOT / "evidence/original/pump/deployed.so")
T = [0x1e7c0,0x22a10,0x4c158,0x5b3b0,0x6cd78,0x72810,0x77940,0x80df8,0x83c00,
     0x13b9b8,0x13f630,0x144508,0x147ba0,0x1489f8,0x14a8a8,0x14f4e0]
def end_of(a):
    i = o.entries.index(a); return o.entries[i+1] if i+1 < len(o.entries) else o.hi
for t in T:
    z = end_of(t)
    out = []
    for i in range(0, z-t, 8):
        at = t+i
        if o.b[at] == 0x85 and o.b[at+1] == 0x10 and o.relocations.get(at, {}).get("type") != 10:
            tgt = at + 8 + struct.unpack_from("<i", o.b, at+4)[0]*8
            if tgt in T: out.append(tgt)
    if out:
        print(hex(t), "->", sorted({hex(x) for x in out}))
