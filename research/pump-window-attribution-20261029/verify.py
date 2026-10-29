#!/usr/bin/env python3
"""Verify the Pump window-attribution packet: file integrity and internal
consistency of the recorded measurements. Stdlib only; no network.

Pinned identities of the measured state:
  deployed          7a19affaa2c6187e04a5fe0ea298cee81fa5eb8c24cfcc30d85f615e89f7b02d
  published unstripped 0f50faa8c325104dc77898ed84866dec2ad1eec475b6abba72c475cf7bf9bab6
  published measure 1019/1035 matched, 188 raw, 16 unmatched targets
  linux rebuilds    same 1019 matched set, 183 raw (documented host-tool delta)
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
    baseline = load("artifacts/baseline.json")
    before = load("artifacts/before.json")
    after = load("artifacts/after.json")
    require(baseline.get("matched") == 1019, "published baseline matched != 1019")
    require(baseline.get("raw") == 188, "published baseline raw != 188")
    require(baseline.get("total") == 1035, "published baseline total != 1035")
    require(len(baseline.get("unmatched", [])) == 16, "published baseline unmatched != 16")
    require(before.get("matched") == 1019, "linux before matched != 1019")
    require(after.get("matched") == 1019, "linux after matched != 1019")
    for key in ("matched_set",):
        require(set(map(str, before[key])) == set(map(str, after[key])), f"{key} changed before->after")
        require(set(map(str, baseline[key])) == set(map(str, before[key])), f"{key} differs published vs linux")
    require(set(map(str, before["raw_set"])) == set(map(str, after["raw_set"])), "raw_set changed before->after")
    require(abs(len(baseline.get("raw_set", [])) - len(before.get("raw_set", []))) <= 8, "raw delta published vs linux unexpected")


def check_no_source_change():
    diff = P / "source-diff.patch"
    require(diff.is_file(), "source-diff.patch missing")
    require(diff.stat().st_size == 0, "source-diff.patch must stay empty (no source change)")


if __name__ == "__main__":
    check_manifest()
    check_sums()
    check_no_source_change()
    check_measurements()
    print("verify: OK (pump-window-attribution-20261029)")
