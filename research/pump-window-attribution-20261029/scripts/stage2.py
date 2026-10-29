#!/usr/bin/env python3
"""Stage the maintained packet source into a scratch workspace (LF) for targeted builds."""
import hashlib, json, shutil, tomllib
from pathlib import Path

PKT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained/research/pump-program-creator-notice-qualification-20261028")
W = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained/work2")
src = PKT / "source"
exp = json.loads((PKT / "build-inputs.json").read_text())
files = {}
for p in sorted(src.rglob("*")):
    if p.is_file():
        rel = str(p.relative_to(src)).replace("\\", "/")
        files[rel] = p.read_bytes().replace(b"\r\n", b"\n")
for rel, d in exp["source_inputs"].items():
    assert hashlib.sha256(files[rel]).hexdigest() == d, rel
assert len(files) == 65

for name in ("pristine", "ws"):
    if (W / name).exists():
        shutil.rmtree(W / name)
for name in ("pristine", "ws"):
    root = W / name
    for rel, data in files.items():
        if rel in ("Cargo.toml", "Cargo.lock"):
            continue
        dst = root / "programs/pump" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
    text = files["Cargo.toml"].decode()
    ps, wsi = text.index("[profile.release]"), text.index("[workspace]")
    release = text[ps:wsi].strip() + "\n"
    (root / "programs/pump/Cargo.toml").write_bytes(text[:ps].rstrip().encode() + b"\n")
    (root / "Cargo.toml").write_bytes(b'[workspace]\nmembers = ["programs/pump"]\nresolver = "2"\n\n' + release.encode())
    (root / "Cargo.lock").write_bytes(files["Cargo.lock"])
print("staged pristine and ws")
