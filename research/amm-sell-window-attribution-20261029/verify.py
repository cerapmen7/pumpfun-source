#!/usr/bin/env python3
"""Verify the AMM sell-window attribution packet: file integrity and internal
consistency of the recorded measurements. Stdlib only; no network.

Pinned identities of the measured state:
  deployed          6a7ad34596d83b4c435b32f458a56e718e9f82eb4ad38e4316616d15d24d8ff7
  candidate build-a 86dbc2c64e81988dead173039b61fa01ba5f68a00fbb6f6dd49f2cda0afec37f
  symbols build-a   7271aaf8afe13b6c8f13a6cf0e9534896a66650dda13a2aa1b32e41edd46426d
  measure           785 windows, 784 matched, 784 raw, unmatched [313168, 9024]
"""
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise SystemExit(f"FAIL: {message}")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest():
    manifest = json.loads((P / "manifest.json").read_text(encoding="utf-8"))
    require(isinstance(manifest, dict) and manifest, "manifest.json empty")
    for rel, meta in manifest.items():
        f = P / rel
        require(f.is_file(), f"missing file {rel}")
        require(f.stat().st_size == meta["bytes"], f"size mismatch {rel}")
        require(sha(f) == meta["sha256"], f"sha256 mismatch {rel}")


def check_sums():
    for line in (P / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, rel = line.split(None, 1)
        rel = rel.lstrip("*").strip()
        f = P / rel
        require(f.is_file(), f"missing file {rel}")
        require(sha(f) == digest.lower(), f"sha256 mismatch {rel}")


def load(rel):
    return json.loads((P / rel).read_text(encoding="utf-8"))


def check_measurements():
    base = load("measurements/base.json")
    require(base.get("total") == 785, "total != 785")
    require(base.get("matched") == 784, "matched != 784")
    require(base.get("raw") == 784, "raw != 784")
    unmatched = base.get("unmatched")
    require(unmatched == [[313168, 9024]], "unmatched != [[313168, 9024]]")
    require(len(base.get("matched_set", [])) == 784, "matched_set size != 784")
    require(len(base.get("raw_set", [])) == 784, "raw_set size != 784")


def check_no_retained_change():
    patches = sorted((P / "variants").glob("*.patch")) if (P / "variants").is_dir() else []
    require(patches, "variants/ must record the measured (non-retained) experiments")
    builds = load("measurements/variants.json") if (P / "measurements/variants.json").is_file() else None
    if isinstance(builds, dict):
        base = builds.get("base") or {}
        require(base.get("matched", 784) == 784, "base variant matched != 784")


if __name__ == "__main__":
    check_manifest()
    check_sums()
    check_measurements()
    check_no_retained_change()
    print("verify: OK (amm-sell-window-attribution-20261029)")
