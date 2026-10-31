#!/usr/bin/env python3
"""C8: marker byte BD -> codepage half-sign -> explicit sample-halving operations."""
import hashlib
import itertools
import json
from pathlib import Path
from bitcoin_oracle import TARGET,ORDER,addresses,sha256,selftest

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    q=next(f['states'] for f in p['fits'] if f['start_x']==92 and f['step_px']==3
           and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1)
    spec=json.loads((ROOT/'research/models/bd_halving_v1.json').read_text())
    bits=[int(c) for c in format(int(spec['marker_byte'],16),'08b')]
    blocks=[q[i:i+32] for i in range(0,256,32)]
    recipes={'global_even':q[::2],'global_odd':q[1::2],
             'global_first_half':q[:128],'global_last_half':q[128:],
             'block_first_half':[v for b in blocks for v in b[:16]],
             'block_last_half':[v for b in blocks for v in b[16:]]}
    for inverse in [False,True]:
        flags=[b^int(inverse) for b in bits]
        suffix='_inverted' if inverse else ''
        recipes['block_half_by_marker'+suffix]=[v for b,flag in zip(blocks,flags) for v in b[16*flag:16*flag+16]]
        recipes['block_phase_by_marker'+suffix]=[v for b,flag in zip(blocks,flags) for v in b[flag::2]]
    candidates={};by_recipe={}
    def add(raw,label):
        for order,b in [('normal',raw),('byte_reverse',raw[::-1])]:
            for final,key in [('raw',b),('sha256',sha256(b))]:
                if 0<int.from_bytes(key,'big')<ORDER:
                    candidates.setdefault(key,label+'/'+order+'/'+final)
                    by_recipe.setdefault(label.split('/')[0],set()).add(key)
    for name,s in recipes.items():
        assert len(s)==128
        for reverse in [False,True]:
            sequence=s[::-1] if reverse else s
            for perm in itertools.permutations(range(4)):
                v=[perm[x] for x in sequence]
                raw=bytes(sum(v[i+j]<<(6-2*j) for j in range(4)) for i in range(0,128,4))
                add(raw,name+f'/reverse={reverse}/perm='+''.join(map(str,perm)))
    for reverse in [False,True]:
        sequence=q[::-1] if reverse else q
        for perm in itertools.permutations(range(4)):
            for inverse in [False,True]:
                selected=[(perm[v]>>((bits[i//32]^int(inverse))))&1 for i,v in enumerate(sequence)]
                raw=int(''.join(map(str,selected)),2).to_bytes(32,'big')
                add(raw,f'bitplane_by_marker/reverse={reverse}/inverse={inverse}/perm='+''.join(map(str,perm)))
    verification=selftest();matches=[]
    for key,label in candidates.items():
        for fmt,address in addresses(key).items():
            if address==TARGET:matches.append({'recipe':label,'format':fmt,'key_hex':key.hex()})
    files=['research/sources/cryptoHALV.png','research/data/pixel_measurements.json','research/models/bd_halving_v1.json','tools/check_bd_halving.py']
    out={'model':'C8','input_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
         'codepage_readings':{c:bytes([0xbd]).decode(c) for c in ['latin1','cp1252']},
         'utf8_half_hex':'½'.encode('utf8').hex(),'marker_bits':bits,
         'unique_valid_scalars':len(candidates),'public_key_formats':2,
         'unique_per_recipe':{k:len(v) for k,v in by_recipe.items()},
         'candidate_set_sha256':sha256(b''.join(sorted(candidates))).hex(),
         'oracle_selftest':verification,'matches':matches,
         'limitations':spec['limitations']}
    (ROOT/'research/data/bd_halving_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
