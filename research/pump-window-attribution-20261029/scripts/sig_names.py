import importlib.util, hashlib
from pathlib import Path
ROOT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained")
spec = importlib.util.spec_from_file_location("welf", ROOT / "scripts/window_elf_reader.py")
welf = importlib.util.module_from_spec(spec); spec.loader.exec_module(welf)
Elf = welf.Elf
c = Elf(ROOT / "research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so")
want = {"2ede91602362", "b2370683ab92", "492abf204c6b", "f3f977e76d3d",
        "36bece918471", "548a45328978", "7925616ac4ff", "7c46e4214f17", "94f1d24b7672",
        "07e08bc5f613", "1a4ad11b35ea", "384476bdc0f9", "e382909a4c59", "f5d13f40f514"}
for f in c.funcs:
    s = hashlib.sha256(c.normalized[f["start"]:f["start"] + f["size"]]).hexdigest()[:12]
    if s in want:
        print(s, f["size"], f["name"])
