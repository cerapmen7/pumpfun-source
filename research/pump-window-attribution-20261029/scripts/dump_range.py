#!/usr/bin/env python3
"""Dump sBPF instructions for an address range using sbftool."""
import sys
sys.path.insert(0, "/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-re/tools")
from sbftool import Prog

so, start, end = sys.argv[1], int(sys.argv[2], 0), int(sys.argv[3], 0)
p = Prog(so)
for a in range(start, end, 8):
    pc = a // 8
    if pc in p.ins:
        print("%08x  %s" % (a, p.ins[pc]))
