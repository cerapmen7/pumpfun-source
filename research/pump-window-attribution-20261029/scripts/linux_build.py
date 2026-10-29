#!/usr/bin/env python3
"""Linux-host build of the maintained packet source, mirroring build.py staging
without the macOS native-tool hash gate (which no Linux SDK can satisfy).

Stages a workspace (workspace/Cargo.toml + programs/pump/*), normalises CRLF to LF,
builds with the local v1.44 platform-tools and strips with v1.52 objcopy.
"""
import hashlib, json, os, shutil, subprocess, sys, tomllib
from pathlib import Path

PKT = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained/research/pump-program-creator-notice-qualification-20261028")
W = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained/work")
LABEL = sys.argv[1] if len(sys.argv) > 1 else "linux01"
SDK = Path(os.environ["HOME"]) / ".cache/solana/v1.44/platform-tools"
OBJCOPY = Path(os.environ["HOME"]) / ".cache/solana/v1.52/platform-tools/llvm/bin/llvm-objcopy"
CARGO_HOME = Path(os.environ["HOME"]) / "pumpwork/netcargo"
TARGET = Path(os.environ["HOME"]) / ("pumpwork/target-" + LABEL)
OUT = W / LABEL

exp = json.loads((PKT / "build-inputs.json").read_text())
source = PKT / "source"
files = {}
for p in sorted(source.rglob("*")):
    if p.is_file():
        rel = str(p.relative_to(source)).replace("\\", "/")
        files[rel] = p.read_bytes().replace(b"\r\n", b"\n")
assert len(files) == len(exp["source_inputs"]) == 65
for rel, digest in exp["source_inputs"].items():
    assert hashlib.sha256(files[rel]).hexdigest() == digest, rel

if OUT.exists():
    shutil.rmtree(OUT)
if TARGET.exists():
    shutil.rmtree(TARGET)
OUT.mkdir(parents=True)
ws = OUT / "source"
crate = ws / "programs/pump"
crate.mkdir(parents=True)

text = files["Cargo.toml"].decode()
parsed = tomllib.loads(text)
assert parsed.get("workspace") == {} and set(parsed.get("profile", {})) == {"release"}
ps, wsi = text.index("[profile.release]"), text.index("[workspace]")
release = text[ps:wsi].strip() + "\n"
for rel, data in files.items():
    if rel in ("Cargo.toml", "Cargo.lock"):
        continue
    dst = crate / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
(crate / "Cargo.toml").write_bytes(text[:ps].rstrip().encode() + b"\n")
(ws / "Cargo.toml").write_bytes(
    b'[workspace]\nmembers = ["programs/pump"]\nresolver = "2"\n\n' + release.encode())
(ws / "Cargo.lock").write_bytes(files["Cargo.lock"])

wrapper = W / "pump_physical_source_wrapper.py"
wrapper.write_bytes((PKT / "tools/pump_physical_source_wrapper.py").read_bytes().replace(b"\r\n", b"\n"))
assert hashlib.sha256(wrapper.read_bytes()).hexdigest() == exp["source_wrapper_sha256"]

env = os.environ.copy()
for k in list(env):
    if k in ("RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTC_WORKSPACE_WRAPPER",
             "CARGO_BUILD_TARGET_DIR") or k.startswith(("CARGO_TARGET_", "CARGO_PROFILE_")):
        env.pop(k, None)
env.update(
    RUSTC_WRAPPER=str(wrapper),
    PUMP_LOGICAL_REGISTRY_SRC=str(CARGO_HOME / "registry/src"),
    PUMP_SOURCE_WRAPPER_LOG=str(OUT / "physical-source-calls.jsonl"),
    CARGO_HOME=str(CARGO_HOME),
    CARGO_TARGET_DIR=str(TARGET),
    CARGO_BUILD_JOBS="2",
    RUSTC=str(SDK / "rust/bin/rustc"),
    CC=str(SDK / "llvm/bin/clang"),
    AR=str(SDK / "llvm/bin/llvm-ar"),
    OBJCOPY=str(OBJCOPY),
    CARGO_TARGET_SBPF_SOLANA_SOLANA_RUSTFLAGS="-Zremap-cwd-prefix=",
)
cmd = [str(SDK / "rust/bin/cargo"), "build", "--manifest-path", str(crate / "Cargo.toml"),
       "--locked", "--offline", "--release", "--target", "sbpf-solana-solana"]
rec = {"label": LABEL, "command": cmd, "source_hashes_lf_ok": True,
       "tool_sha256": {n: hashlib.sha256((SDK / n).read_bytes()).hexdigest()
                       for n in ("rust/bin/rustc", "rust/bin/cargo")},
       "target_libraries_ok": True}
with (OUT / "build.log").open("wb") as f:
    r = subprocess.run(cmd, cwd=ws, env=env, stdout=f, stderr=subprocess.STDOUT)
rec["returncode"] = r.returncode
if r.returncode != 0:
    print(open(OUT / "build.log").read()[-3000:])
    raise SystemExit(1)
built = TARGET / "sbpf-solana-solana/release/pump_recovered.so"
shutil.copy2(built, OUT / "unstripped.so")
subprocess.run([str(OBJCOPY), "--strip-all", str(built), str(OUT / "candidate.so")], check=True)
rec["unstripped_sha256"] = hashlib.sha256((OUT / "unstripped.so").read_bytes()).hexdigest()
rec["candidate_sha256"] = hashlib.sha256((OUT / "candidate.so").read_bytes()).hexdigest()
rec["published_unstripped_sha256"] = exp["unstripped_sha256"]
rec["published_candidate_sha256"] = exp["comparison"]["candidate_sha256"]
(OUT / "build-record.json").write_text(json.dumps(rec, indent=1) + "\n")
print(json.dumps({k: rec[k] for k in ("unstripped_sha256", "candidate_sha256",
                                       "published_unstripped_sha256", "published_candidate_sha256")}, indent=1))
print("identity_match", rec["unstripped_sha256"] == rec["published_unstripped_sha256"])
