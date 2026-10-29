import json, struct, hashlib, importlib.util
from pathlib import Path
ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
o = Elf(ROOT / "evidence/original/pump/deployed.so")
W = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained")
pub = json.loads((W / "artifacts/baseline.json").read_text())
rank = {int(a, 16): n for a, n, r in pub["pairs"]}
def end_of(a):
    i = o.entries.index(a); return o.entries[i+1] if i+1 < len(o.entries) else o.hi
def calls(start, size):
    out = []
    for i in range(0, size, 8):
        at = start + i
        if o.b[at] == 0x85 and o.b[at+1] == 0x10 and o.relocations.get(at, {}).get("type") != 10:
            out.append(at + 8 + struct.unpack_from("<i", o.b, at+4)[0]*8)
    return out
for target in (0x147ba0, 0x1489f8):
    z = end_of(target)
    print("==", hex(target))
    seen = set()
    for t in calls(target, z - target):
        if t in seen: continue
        seen.add(t)
        sig = hashlib.sha256(o.normalized[t:end_of(t)]).hexdigest()[:12]
        if sig in ("2ede91602362", "b2370683ab92"):
            print("  ", hex(t), end_of(t)-t, sig, rank.get(t))
