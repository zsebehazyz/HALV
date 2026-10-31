#!/usr/bin/env python3
"""C11: marker-controlled regional half normalization before direct 64-to-32 sums."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import numpy as np
from bitcoin_oracle import ORDER,TARGET,addresses,sha256,selftest

ROOT=Path(__file__).resolve().parents[1]

def main():
    profiles=json.loads((ROOT/'research/data/pair64_profiles.json').read_text())
    marker=json.loads((ROOT/'research/data/timing_lattice_check.json').read_text())['marker']
    bits=marker['bits'];assert marker['byte_hex']=='BD' and len(bits)==8
    candidates={};counts=Counter();rejections=Counter();valid={}
    for profile in profiles:
        source=np.array(profile['values64'],dtype=int)
        for inverse in [False,True]:
            selected=np.repeat(np.array(bits,dtype=bool)^inverse,8)
            for rounding,fn in [('floor',np.floor),('ceil',np.ceil),('nearest_ties_even',np.rint)]:
                values=source.copy();values[selected]=fn(source[selected]/2).astype(int)
                pairs={'adjacent':(values[::2],values[1::2]),'global_halves':(values[:32],values[32:]),
                       'within_halving_block_halves':(values.reshape(8,8)[:,:4].flatten(),values.reshape(8,8)[:,4:].flatten()),
                       'transpose_8x8_then_adjacent':(values.reshape(8,8).T.flatten()[::2],values.reshape(8,8).T.flatten()[1::2])}
                for order,(a,b) in pairs.items():
                    group=profile['family']+'/inverse='+str(inverse)+'/'+rounding
                    counts[group]+=1;out=a+b
                    if np.any(out>255) or np.any(out<0):rejections[group]+=1;continue
                    key=bytes(int(v) for v in out)
                    if not 0<int.from_bytes(key,'big')<ORDER:rejections[group]+=1;continue
                    candidates.setdefault(key,profile['family']+'/'+profile['parameters']+f'/BD_inverse={inverse}/{rounding}/{order}')
                    valid.setdefault(group,set()).add(key)
    verification=selftest();matches=[]
    for key,label in candidates.items():
        for fmt,address in addresses(key).items():
            if address==TARGET:matches.append({'recipe':label,'format':fmt,'key_hex':key.hex()})
    files=['research/data/pair64_profiles.json','research/data/timing_lattice_check.json',
           'research/models/bd_pair64_v1.json','tools/check_bd_pair64.py']
    out={'model':'C11','input_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
         'groups':{k:{'attempts':counts[k],'invalid_or_out_of_range':rejections[k],'unique_scalars':len(valid.get(k,()))} for k in sorted(counts)},
         'attempts_including_duplicates':sum(counts.values()),'unique_valid_scalars':len(candidates),
         'public_key_formats':2,'candidate_set_sha256':sha256(b''.join(sorted(candidates))).hex(),
         'hash_finalization_used':False,'oracle_selftest':verification,'matches':matches,
         'limitations':json.loads((ROOT/'research/models/bd_pair64_v1.json').read_text())['limitations']}
    (ROOT/'research/data/bd_pair64_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print('C11 attempts',sum(counts.values()),'unique scalars',len(candidates),'matches',len(matches))

if __name__=='__main__':main()
