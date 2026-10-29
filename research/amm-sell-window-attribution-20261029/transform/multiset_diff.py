import sys, re, collections
sys.path.insert(0, '/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-amm/analysis')
import fn_diff as F

def mask(t):
    t = re.sub(r'(ja r\d+, (?:r\d+|0x[0-9a-f]+), )[+-]0x[0-9a-f]+', r'\1<OFF>', t)
    t = re.sub(r'((?:jeq|jne|jgt|jge|jlt|jle|jsgt|jsge|jslt|jsle|jset)[a-z]* r\d+, (?:r\d+|0x[0-9a-f]+), )[+-]0x[0-9a-f]+', r'\1<OFF>', t)
    return t

a = F.decode(sys.argv[1], int(sys.argv[2],0), int(sys.argv[3],0))
b = F.decode(sys.argv[4], int(sys.argv[5],0), int(sys.argv[6],0))
A = collections.Counter(mask(t) for _, t in a)
B = collections.Counter(mask(t) for _, t in b)
print('insns', len(a), len(b))
print('only in A:')
for k, v in sorted((A - B).items(), key=lambda kv: -kv[1]):
    print(f'  {v:3d}  {k}')
print('only in B:')
for k, v in sorted((B - A).items(), key=lambda kv: -kv[1]):
    print(f'  {v:3d}  {k}')
print('multiset equal:', A == B)
