from pathlib import Path
import struct
p = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/pumpfun-source-maintained/evidence/original/pump/deployed.so")
b = p.read_bytes()
shoff = struct.unpack_from("<Q", b, 40)[0]
shnum = struct.unpack_from("<H", b, 60)[0]
shstr = struct.unpack_from("<H", b, 62)[0]
secs = [struct.unpack_from("<IIQQQQIIQQ", b, shoff + i * 64) for i in range(shnum)]
names = b[secs[shstr][4]:secs[shstr][4] + secs[shstr][5]]
for s in secs:
    n = names[s[0]:].split(b"\0", 1)[0].decode()
    if n in (".text", ".rodata", ".dynsym", ".symtab"):
        print(n, "addr", hex(s[3]), "off", hex(s[4]), "size", hex(s[5]))
for a in (0x14f4e0, 0x150008, 0x150160, 0x14fff8):
    print(hex(a), b[a:a+8].hex())
