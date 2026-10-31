#!/usr/bin/env python3
"""C9: arithmetic pooling after the marker's possible half-sign instruction."""
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
from bitcoin_oracle import ORDER,TARGET,addresses,sha256,selftest

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    q=np.array(next(f['states'] for f in p['fits'] if f['start_x']==92 and f['step_px']==3
                   and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1),dtype=int)
    blocks=q.reshape(8,32)
    pairings={'adjacent':(q[::2],q[1::2]),'global_halves':(q[:128],q[128:]),
              'within_block_halves':(blocks[:,:16].flatten(),blocks[:,16:].flatten())}
    operators={'mean_floor':lambda a,b:(a+b)//2,'mean_ceil':lambda a,b:(a+b+1)//2,
               'mean_ties_even':lambda a,b:np.rint((a+b)/2).astype(int),
               'absolute_difference':lambda a,b:abs(a-b),'minimum':np.minimum,'maximum':np.maximum,
               'xor':lambda a,b:a^b,'sum_mod4':lambda a,b:(a+b)%4,
               'difference_mod4':lambda a,b:(b-a)%4}
    candidates={};counts={}
    for pairing,(a,b) in pairings.items():
        for operator,fn in operators.items():
            s=fn(a,b).tolist();assert len(s)==128 and all(0<=v<=3 for v in s)
            label=pairing+'/'+operator;seen=set()
            for reverse in [False,True]:
                seq=s[::-1] if reverse else s
                for perm in itertools.permutations(range(4)):
                    v=[perm[x] for x in seq]
                    raw=bytes(sum(v[i+j]<<(6-2*j) for j in range(4)) for i in range(0,128,4))
                    for byte_reverse in [False,True]:
                        payload=raw[::-1] if byte_reverse else raw
                        for final,key in [('raw',payload),('sha256',sha256(payload))]:
                            if 0<int.from_bytes(key,'big')<ORDER:
                                seen.add(key);candidates.setdefault(key,label+f'/reverse={reverse}/perm={perm}/byte_reverse={byte_reverse}/'+final)
            counts[label]=len(seen)
    verification=selftest();matches=[]
    for key,label in candidates.items():
        for fmt,address in addresses(key).items():
            if address==TARGET:matches.append({'recipe':label,'format':fmt,'key_hex':key.hex()})
    files=['research/sources/cryptoHALV.png','research/data/pixel_measurements.json',
           'research/models/halving_pairs_v1.json','tools/check_halving_pairs.py']
    out={'model':'C9','input_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
         'unique_valid_scalars':len(candidates),'public_key_formats':2,'unique_per_recipe':counts,
         'candidate_set_sha256':sha256(b''.join(sorted(candidates))).hex(),
         'oracle_selftest':verification,'matches':matches,
         'limitations':json.loads((ROOT/'research/models/halving_pairs_v1.json').read_text())['limitations']}
    (ROOT/'research/data/halving_pairs_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print('C9 unique scalars',len(candidates),'matches',len(matches))

if __name__=='__main__':main()
