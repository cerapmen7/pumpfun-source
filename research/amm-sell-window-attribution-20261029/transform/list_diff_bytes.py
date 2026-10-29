import sys, struct
from pathlib import Path
def secs(p):
    b = Path(p).read_bytes()
    shoff, = struct.unpack_from('<Q', b, 40); es, n, si = struct.unpack_from('<HHH', b, 58)
    S = [struct.unpack_from('<IIQQQQIIQQ', b, shoff+i*es) for i in range(n)]
    ns = S[si]; names = b[ns[4]:ns[4]+ns[5]]
    return b, {names[s[0]:].split(b'\0',1)[0].decode(): s for s in S}
b1, S1 = secs(sys.argv[1]); b2, S2 = secs(sys.argv[2])
t1 = S1['.text']; t2 = S2['.text']
a = b1[t1[4]:t1[4]+t1[5]]; c = b2[t2[4]:t2[4]+t2[5]]
d = [i for i in range(min(len(a), len(c))) if a[i] != c[i]]
print('text bytes differing:', len(d))
print('offsets (file):', ' '.join(hex(t1[4]+i) for i in d))
for i in d:
    print(f'  {t1[4]+i:#08x}: {a[i]:02x} -> {c[i]:02x}')
