import re, sys
p = sys.argv[1]
vals = []
for l in open(p):
    m = re.match(r'\s+0x([0-9a-f]+) -> 0x([0-9a-f]+)\s+drift ([+-]0x[0-9a-f]+)', l)
    if m:
        a, b = int(m.group(1), 16), int(m.group(2), 16)
        vals.append(b - a)
print('paired rows:', len(vals))
print('drift min', hex(min(vals)), 'max', hex(max(vals)))
print('rows with zero drift:', sum(1 for v in vals if v == 0))
print('distinct drifts:', sorted(set(vals)))
