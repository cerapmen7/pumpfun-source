#!/usr/bin/env python3
"""a4: #[cold] on the whole cashback function; a5: #[inline(never)] on cashback.
The attribute replaces an existing blank line so that every arm line is unchanged.
"""
import shutil, sys
from pathlib import Path
base, root, name = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
REL = 'programs/pump-amm/src/instructions/swap/sell.rs'
dst = root / f'ws-{name}'
if dst.exists(): shutil.rmtree(dst)
shutil.copytree(base, dst)
p = dst / REL
lines = p.read_bytes().decode('utf-8').split('\r\n')
i = next(k for k, l in enumerate(lines) if l.startswith('fn cashback'))
assert lines[i-1].strip().startswith('#[allow(clippy::too_many_arguments)]'), lines[i-1]
# replace a preceding blank line (360-362 are blank) with the attribute
j = i - 2
while lines[j] != '':
    j -= 1
assert j >= 355
lines[j] = '#[cold]' if name == 'a4' else '#[inline(never)]'
p.write_bytes('\r\n'.join(lines).encode('utf-8'))
chk = p.read_bytes().decode('utf-8').split('\r\n')
for n in (378, 383, 392, 395, 444, 448, 464, 467, 502):
    print(n, chk[n-1].strip()[:70])
