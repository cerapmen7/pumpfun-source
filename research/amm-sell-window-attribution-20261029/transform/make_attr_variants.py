#!/usr/bin/env python3
"""Attribute-based variants for the cashback 467 error arm.

All variants keep every error-arm line (378/383/392/395/444/448/464/467/502) and
the semantics. CRLF is preserved. Padding only removes blank lines between the
create block and the 502 arm.

  a1   #[cold] #[inline(never)] nested helper holding the 467 arm (error! on 467)
  a2   #[inline(always)] nested helper (counter-test)
  a3   #[cold] #[inline(never)] nested helper for the whole is_writable check
  c1   one-line match instead of `?` on try_borrow_data (explicit From)
  c2   `.map_err(|e| Error::from(e))?` form of the same `?`
  a1c1 a1 + c1

usage: make_attr_variants.py BASE OUTROOT NAME
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

assert lines[466].strip().startswith('require!(ata.is_writable'), lines[466]
assert lines[446].strip().startswith('if data.len() < 8'), lines[446]

def fix_502():
    j = next(i for i, l in enumerate(lines) if 'ok_or(error!(PumpAmmError::Overflow))' in l)
    need = 502 - (j + 1)
    if need > 0:
        k = next(i for i, l in enumerate(lines) if l.strip().startswith('accumulator.user = user.key();'))
        lines[k:k] = [''] * need
    elif need < 0:
        removed = 0; k = j - 1
        while removed < -need:
            if lines[k] == '':
                del lines[k]; removed += 1
            k -= 1
            if k < 430: raise SystemExit('no blanks')
    j = next(i for i, l in enumerate(lines) if 'ok_or(error!(PumpAmmError::Overflow))' in l)
    assert j + 1 == 502, (j + 1, 502)

if name in ('a1', 'a2', 'a1c1'):
    if name == 'a2':
        head = ['    #[inline(always)]', '']
    else:
        head = ['    #[cold]', '    #[inline(never)]']
    new = head + [
        '    fn cold_467() -> Result<()> { Err(error!(PumpAmmError::InvalidCashbackAccumulatorAta)) }',
        '    if !ata.is_writable { return cold_467(); }',
    ]
    assert lines[464] == '' and lines[465] == '', (lines[464], lines[465])
    lines[464:467] = new
    fix_502()

if name == 'a3':
    new = [
        '    #[cold]',
        '    #[inline(never)]',
        '    fn check_467(ata: &AccountInfo) -> Result<()> { if !ata.is_writable { return Err(error!(PumpAmmError::InvalidCashbackAccumulatorAta)); } Ok(()) }',
        '    check_467(ata)?;',
    ]
    assert lines[464] == '' and lines[465] == ''
    lines[464:467] = new
    fix_502()

if name in ('c1', 'a1c1'):
    assert lines[444].strip() == 'let data = user_volume_accumulator.try_borrow_data()?;', lines[444]
    lines[444] = ('        let data = match user_volume_accumulator.try_borrow_data() '
                  '{ Ok(d) => d, Err(e) => return Err(anchor_lang::error::Error::from(e)) };')

if name == 'c2':
    assert lines[444].strip() == 'let data = user_volume_accumulator.try_borrow_data()?;'
    lines[444] = ('        let data = user_volume_accumulator.try_borrow_data()'
                  '.map_err(|e| anchor_lang::error::Error::from(e))?;')

if name not in ('a1','a2','a1c1','a3','c1','c2'):
    raise SystemExit('unknown ' + name)

p.write_bytes('\r\n'.join(lines).encode('utf-8'))
chk = p.read_bytes().decode('utf-8').split('\r\n')
for n in (378, 383, 392, 395, 444, 448, 464, 467, 502):
    print(f'{n}: {chk[n-1].strip()[:110]}')
