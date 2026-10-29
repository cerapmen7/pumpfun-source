import sys, struct
from pathlib import Path
def text(p):
    b = Path(p).read_bytes()
    shoff, = struct.unpack_from('<Q', b, 40); es, n, si = struct.unpack_from('<HHH', b, 58)
    secs = [struct.unpack_from('<IIQQQQIIQQ', b, shoff+i*es) for i in range(n)]
    ns = secs[si]; names = b[ns[4]:ns[4]+ns[5]]
    S = {names[s[0]:].split(b'\0',1)[0].decode(): s for s in secs}
    t = S['.text']; return b[t[4]:t[4]+t[5]]
a = text(sys.argv[1]); b = text(sys.argv[2])
n = min(len(a), len(b))
diff = sum(1 for i in range(n) if a[i] != b[i])
print('lens', len(a), len(b), 'identical_prefix_diff_bytes', diff)
