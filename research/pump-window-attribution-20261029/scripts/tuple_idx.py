import struct, re, importlib.util
from pathlib import Path
ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
o = Elf(ROOT / "evidence/original/pump/deployed.so")
c = Elf(ROOT / "research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so")
def tuples(e, start, size):
    out = []
    for off in range(0, size, 8):
        at = start + off
        b = e.b[at:at+16]
        if b[0] != 0x18: continue
        val = struct.unpack_from("<Q", b, 4)[0]
        sec = next((s for s in e.raw if s[3] <= val < s[3]+s[5]), None)
        if not sec: continue
        blob = e.b[sec[4]+val-sec[3]:sec[4]+val-sec[3]+200]
        m = re.match(rb"(?:programs|src|tests|/home)/[A-Za-z0-9_./-]+?\.rs", blob)
        if not m: continue
        line = code = None
        for k in range(1,14):
            bb = e.b[at+k*8:at+k*8+8]
            if len(bb)<8: break
            if bb[0]==0x62:
                v = struct.unpack_from("<I", bb, 4)[0]
                if 6000 <= v < 6200 and code is None: code = v
                elif 40 <= v < 4000 and line is None: line = v
        if line or code:
            out.append((off//8, hex(at), m.group(0).decode().split("/")[-1], line, code))
    return out
for label, e, base in (("D", o, 0x14f4e0), ("C", c, 0x14e680)):
    print("==", label)
    for t in tuples(e, base, 13224):
        print("  idx %4d addr %s %s line=%s code=%s" % t)
