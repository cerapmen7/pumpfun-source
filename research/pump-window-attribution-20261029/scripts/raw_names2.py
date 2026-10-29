import json
from pathlib import Path
W = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained")
pub = json.loads((W / "artifacts/baseline.json").read_text())
m = {int(a, 16): n for a, n, r in pub["pairs"]}
for a in [0x188d30, 0x188fe0, 0x1891d8, 0x189340, 0x18de90, 0x18e568, 0x1a7b00, 0x199af0, 0x199b18]:
    print(hex(a), m.get(a))
