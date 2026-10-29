#!/usr/bin/env python3
"""Check that the Windows checkout matches build-inputs.json once CRLF is normalised to LF."""
import json, hashlib
from pathlib import Path

PKT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained/research/pump-program-creator-notice-qualification-20261028")
exp = json.loads((PKT / "build-inputs.json").read_text())["source_inputs"]
src = PKT / "source"
actual = {}
for p in sorted(src.rglob("*")):
    if p.is_file():
        rel = str(p.relative_to(src)).replace("\\", "/")
        b = p.read_bytes().replace(b"\r\n", b"\n")
        actual[rel] = hashlib.sha256(b).hexdigest()
print("expected", len(exp), "actual", len(actual))
missing = [k for k in exp if k not in actual]
extra = [k for k in actual if k not in exp]
bad = [(k, actual[k], exp[k]) for k in exp if k in actual and actual[k] != exp[k]]
print("missing", missing[:5], "extra", extra[:5], "bad", len(bad))
for x in bad[:8]:
    print("BAD", x)
# also wrapper
w = PKT / "tools/pump_physical_source_wrapper.py"
h = hashlib.sha256(w.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
print("wrapper_lf", h)
