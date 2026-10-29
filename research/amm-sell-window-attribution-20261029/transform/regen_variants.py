#!/usr/bin/env python3
"""Regenerate every tested source variant from the staged base with CRLF preserved.

Each variant changes only the cashback control-flow form; every error-arm line
number is asserted to stay at its maintained/deployed value.
usage: regen_variants.py BASE OUTROOT
"""
import shutil, sys
from pathlib import Path

base, root = Path(sys.argv[1]), Path(sys.argv[2])
REL = 'programs/pump-amm/src/instructions/swap/sell.rs'

def load(p):
    return p.read_bytes().decode('utf-8').split('\r\n')

def save(p, lines):
    p.write_bytes('\r\n'.join(lines).encode('utf-8'))

def variant(name):
    dst = root / f'ws-{name}'
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(base, dst)
    p = dst / REL
    lines = load(p)
    assert lines[466].strip().startswith('require!(ata.is_writable'), lines[466]
    if name == 'v1':
        lines[466] = '    if !ata.is_writable { return err!(PumpAmmError::InvalidCashbackAccumulatorAta); }'
    elif name == 'v7':
        lines[466] = '    match ata.is_writable { false => return err!(PumpAmmError::InvalidCashbackAccumulatorAta), true => {} }'
    elif name == 'v8':
        lines[466] = '    if ata.is_writable == false { return err!(PumpAmmError::InvalidCashbackAccumulatorAta); }'
    elif name == 'v10':
        lines[466] = '    if ata.is_writable { } else { return err!(PumpAmmError::InvalidCashbackAccumulatorAta); }'
    elif name == 'ctl':
        lines[466] = '    require!(ata.is_writable, PumpAmmError::InvalidCashbackAccumulator);'
    elif name in ('v2', 'v4', 'v5', 'v9'):
        assert lines[467].strip() == 'if ata.data_is_empty() {', lines[467]
        assert lines[479].strip() == '}', lines[479]
        body = lines[468:479]
        if name == 'v2':
            lines[479] = '    } else {}'; new = None
        elif name == 'v4':
            new = ['    if !ata.data_is_empty() {', '    } else {'] + body + ['    }']
        elif name == 'v5':
            new = ['    match ata.data_is_empty() {', '        true => {'] + ['    ' + x for x in body] + ['        }', '        false => {}', '    }']
        elif name == 'v9':
            new = ['    match ata.data_is_empty() {', '        false => {}', '        true => {'] + ['    ' + x for x in body] + ['        }', '    }']
        if new is not None:
            extra = len(new) - 13
            lines[467:480] = new
            j = 480; removed = 0
            while removed < extra:
                if lines[j] == '':
                    del lines[j]; removed += 1
                else:
                    j += 1
            assert removed == extra, (removed, extra)
    elif name == 'v12':
        assert lines[444].strip() == 'let data = user_volume_accumulator.try_borrow_data()?;'
        lines[444] = '        let data = match user_volume_accumulator.try_borrow_data() { Ok(d) => d, Err(e) => return Err(e.into()) };'
    else:
        raise SystemExit('unknown ' + name)
    save(p, lines)
    chk = load(p)
    for n in (378, 383, 392, 395, 444, 448, 464, 467, 502):
        print(f'  {name} {n}: {chk[n-1].strip()[:80]}')
    return dst

for n in ('v1', 'v2', 'v4', 'v5', 'v7', 'v8', 'v9', 'v10', 'v12', 'ctl'):
    print('variant', n)
    variant(n)
