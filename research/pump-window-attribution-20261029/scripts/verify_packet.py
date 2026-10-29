#!/usr/bin/env python3
"""Self-verification of the maintained-round packet, with hard asserts."""
import json, sys, hashlib
from pathlib import Path

P = Path(__file__).resolve().parents[1]
TARGETS = [0x1e7c0,0x22a10,0x4c158,0x5b3b0,0x6cd78,0x72810,0x77940,0x80df8,0x83c00,
           0x13b9b8,0x13f630,0x144508,0x147ba0,0x1489f8,0x14a8a8,0x14f4e0]
MATCHED_SHA = "9bcaaca813bf87b19551505bfa345c886c189719301ef2a4bc46502c8a59867d"

def load(name):
    return json.loads((P / "artifacts" / name).read_text())

def set_sha(v):
    return hashlib.sha256(json.dumps(v, separators=(",", ":")).encode()).hexdigest()

pub = load("baseline.json")
before = load("before.json")
after = load("after.json")

assert pub["total"] == 1035 and pub["matched"] == 1019 and pub["raw"] == 188, "published baseline"
assert {a for a, _ in pub["unmatched"]} == set(TARGETS), "published unmatched != targets"
assert set_sha(pub["matched_set"]) == MATCHED_SHA

for tag, d in (("before", before), ("after", after)):
    assert d["total"] == 1035 and d["matched"] == 1019 and d["raw"] == 183, tag
    assert set_sha(d["matched_set"]) == MATCHED_SHA, tag + " matched set"
    assert {a for a, _ in d["unmatched"]} == set(TARGETS), tag + " unmatched"
assert before["matched_set"] == after["matched_set"], "matched set changed"
assert before["raw_set"] == after["raw_set"], "raw set changed"

diff = load("published-vs-linux.json")
assert diff["matched_equal"] is True
assert len(diff["raw_only_published"]) == 7 and len(diff["raw_only_linux"]) == 2

rows = load("analysis16.json")
assert [r["target"] for r in rows] == [hex(t) for t in TARGETS]
closest = next(r for r in rows if r["target"] == "0x14f4e0")
assert closest["delta"] == 0 and closest["skeleton_equal"] == 1627
assert closest["skeleton_total"] == 1653 and closest["skeleton_regions"] == 8
assert closest["tuples_equal"] is True

b1 = load("build-linux01.json"); b2 = load("build-linux02.json")
assert b1["unstripped_sha256"] == b2["unstripped_sha256"] == "297ef41e784ca5db96e6813345e7f6342b554efd46ccab47be4b26f63cbe47d9"
assert b1["candidate_sha256"] == b2["candidate_sha256"] == "aa5b10d7e40bbb6a87d7055ca26aae85177d10dc00b9a55dc517aefa47624cf6"
assert b1["published_unstripped_sha256"] == "0f50faa8c325104dc77898ed84866dec2ad1eec475b6abba72c475cf7bf9bab6"
assert b1["published_candidate_sha256"] == "d0377d7cef5b7378063f8bfabac5dc9c08d29eeaaaaa14022d36909688ff5e1b"

assert (P / "source-diff.patch").read_bytes() == b"", "source diff is not empty"

variants = load("variants-0x14f4e0.json")
ids = [v["variant"] for v in variants]
assert ids == ["v0", "v1", "v1c", "v1d", "v2c", "v3c"], ids
for v in variants:
    assert v["matched"] == 1019 and v["raw"] == 183, v["variant"]
    assert v["target_matched"] is False, v["variant"]
base = variants[0]
assert base["size"] == 13224 and base["delta"] == 0
assert base["skeleton_equal"] == 1627 and base["regions"] == 8
inv = next(v for v in variants if v["variant"] == "v1c")
assert inv["size"] == 13224 and inv["skeleton_equal"] == 1629 and inv["regions"] == 5
for v in variants[1:]:
    assert (P / "artifacts" / ("measure-" + v["variant"] + ".json")).is_file()

attrs = load("variants-attributes.json")
assert [v["variant"] for v in attrs] == ["a1", "a2", "a3", "a4", "e1", "e2", "e3"]
by = {v["variant"]: v for v in attrs}
assert by["a1"]["matched"] == 1014 and len(by["a1"]["matched_lost"]) == 5
assert by["a2"]["matched"] == 1013 and len(by["a2"]["matched_lost"]) == 6
assert by["a3"]["matched"] == 1014
for k in ("a4", "e1", "e2", "e3"):
    assert by[k]["matched"] == 1019 and by[k]["raw"] == 183, k
assert by["e2"]["candidate_sha256"] == "297ef41e784ca5db96e6813345e7f6342b554efd46ccab47be4b26f63cbe47d9"
assert by["e1"]["delta"] == 40 and by["e3"]["delta"] == 72
assert by["a4"]["skeleton_equal"] == 1581 and by["a4"]["regions"] == 23

print("verify_packet: OK")
print("  published 1019/1035 matched, 188 raw; 16 unmatched = targets")
print("  linux01/02 1019/1035 matched (same set), 183 raw; byte-identical builds")
print("  0x14f4e0: delta 0 B, skeleton 1627/1653, 8 regions, tuples equal")
print("  source diff empty")
