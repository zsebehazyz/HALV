#!/usr/bin/env python3
"""Byte-range constraints before any cryptographic oracle, for direct base4 sums."""
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
profiles=json.loads((ROOT/'research/data/pair64_profiles.json').read_text())
records=[]
for profile in profiles:
    if profile['family']!='base4':continue
    v=np.array(profile['values64'])
    orders={'adjacent':v,'transpose_8x8_then_adjacent':v.reshape(8,8).T.flatten()}
    pairs={name:(w[::2],w[1::2]) for name,w in orders.items()}
    pairs['global_halves']=(v[:32],v[32:])
    pairs['within_halving_block_halves']=(v.reshape(8,8)[:,:4].flatten(),v.reshape(8,8)[:,4:].flatten())
    for order,(a,b) in pairs.items():
        sums=a+b;bad=np.flatnonzero(sums>255)
        records.append({'profile':profile['parameters'],'pair_order':order,
                        'out_of_range_count':len(bad),'bad_pair_indices':bad.tolist(),
                        'bad_sums':sums[bad].tolist(),'max_pair_sum':int(sums.max())})
minimum=min(r['out_of_range_count'] for r in records)
out={'source_sha256':hashlib.sha256((ROOT/'research/data/pair64_profiles.json').read_bytes()).hexdigest(),
     'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
     'hypotheses':len(records),'minimum_out_of_range_pairs':minimum,
     'closest_range_models':[r for r in records if r['out_of_range_count']==minimum],
     'note':'Structural byte-range check only; no candidate repair and no extra private-key search.'}
(ROOT/'research/data/pair64_range_diagnostics.json').write_text(json.dumps(out,indent=2)+'\n')
print('Direct sums: minimum out-of-range pairs',minimum,'of32; hypotheses',len(records))
