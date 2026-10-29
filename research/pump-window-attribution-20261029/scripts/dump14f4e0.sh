#!/bin/bash
D=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained/evidence/original/pump/deployed.so
C=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained/research/pump-program-creator-notice-qualification-20261028/artifacts/unstripped.so
S=/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained/scripts/dump_range.py
echo "== D 350-375"
python3 $S $D 0x150008 0x150070
echo "== C 350-375"
python3 $S $C 0x14F1A8 0x14F210
echo "== D 395-455"
python3 $S $D 0x150138 0x150318
echo "== C 395-425"
python3 $S $C 0x14F2D8 0x14F3D0
echo "== D 998-1010"
python3 $S $D 0x151410 0x151450
echo "== C 998-1010"
python3 $S $C 0x1505B0 0x1505F0
