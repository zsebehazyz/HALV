#!/usr/bin/env python3
"""C10: 64 12px cells, Level5-inspired normalization, 32 direct pair sums."""
import csv
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
import numpy as np
from bitcoin_oracle import ORDER,TARGET,addresses,sha256,selftest

ROOT=Path(__file__).resolve().parents[1]

def linear_cell_areas(q,anchor):
    nodes=92+3*np.arange(256)
    result=[]
    for i in range(64):
        left=anchor+12*i;right=left+12
        xs=np.r_[left,nodes[(nodes>left)&(nodes<right)],right]
        ys=np.interp(xs,nodes,q,left=q[0],right=q[-1])
        result.append(float(np.sum(np.diff(xs)*(ys[:-1]+ys[1:])/2)))
    return np.array(result)

def main():
    p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    q=np.array(next(f['states'] for f in p['fits'] if f['start_x']==92 and f['step_px']==3
                   and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1),dtype=int)
    spec=json.loads((ROOT/'research/models/pair64_v1.json').read_text())
    control=json.loads((ROOT/'research/data/level5_geometry_verification.json').read_text())
    assert control['published_key_match'] and control['expected_address_match'] and control['geometry_reference_matches']==64
    profiles=[]
    for reverse in [False,True]:
        s=q[::-1] if reverse else q
        for perm in itertools.permutations(range(4)):
            values=np.array([perm[v] for v in s]).reshape(64,4)
            for little in [False,True]:
                digits=values[:,::-1] if little else values
                v=digits@np.array([64,16,4,1])
                profiles.append(('base4',f'reverse={reverse}/perm={perm}/quad_reverse={little}',v))
    geometry={'sample_sum':q.reshape(64,4).sum(1),
              'zero_order_hold_area':3*q.reshape(64,4).sum(1),
              'energy_sum':(q.reshape(64,4)**2).sum(1)}
    for anchor in spec['linear_area_anchors_px']:
        area=linear_cell_areas(q,anchor)
        geometry[f'linear_area_radius/anchor={anchor}']=area
        geometry[f'linear_area_diameter/anchor={anchor}']=2*area
    rounders={'floor':np.floor,'ceil':np.ceil,'nearest_ties_even':np.rint}
    for name,values in geometry.items():
        for rounding,fn in rounders.items():
            for reverse in [False,True]:
                v=fn(values).astype(int)
                profiles.append(('geometry',f'{name}/rounding={rounding}/reverse={reverse}',v[::-1] if reverse else v))
    pairings={
        'adjacent':lambda v:(v[::2],v[1::2]),
        'global_halves':lambda v:(v[:32],v[32:]),
        'within_halving_block_halves':lambda v:(v.reshape(8,8)[:,:4].flatten(),v.reshape(8,8)[:,4:].flatten()),
        'transpose_8x8_then_adjacent':lambda v:(v.reshape(8,8).T.flatten()[::2],v.reshape(8,8).T.flatten()[1::2])}
    normalizers={
        'direct':lambda a,b:a+b,
        'half_sum_floor':lambda a,b:(a+b)//2,
        'half_sum_ceil':lambda a,b:(a+b+1)//2,
        'half_sum_ties_even':lambda a,b:np.rint((a+b)/2).astype(int),
        'halve_each_floor_then_sum':lambda a,b:a//2+b//2,
        'halve_each_ceil_then_sum':lambda a,b:(a+1)//2+(b+1)//2,
        'byte_wrap_control':lambda a,b:(a+b)%256}
    candidates={};attempts=Counter();rejected=Counter();valid_by_model={};profiles_manifest=[]
    for family,label,values in profiles:
        profiles_manifest.append({'family':family,'parameters':label,'values64':values.tolist()})
        assert len(values)==64
        for pair_name,pair in pairings.items():
            a,b=pair(values)
            for norm,fn in normalizers.items():
                group=family+'/'+norm;attempts[group]+=1
                out=fn(a,b)
                if np.any(out<0) or np.any(out>255):rejected[group]+=1;continue
                key=bytes(int(v) for v in out)
                assert len(key)==32
                if not 0<int.from_bytes(key,'big')<ORDER:rejected[group]+=1;continue
                valid_by_model.setdefault(group,set()).add(key)
                candidates.setdefault(key,f'{family}/{label}/{pair_name}/{norm}')
    verification=selftest();matches=[]
    for key,label in candidates.items():
        for fmt,address in addresses(key).items():
            if address==TARGET:matches.append({'recipe':label,'format':fmt,'key_hex':key.hex()})
    files=['research/sources/cryptoHALV.png','research/data/pixel_measurements.json',
           'research/data/level5_geometry_verification.json','research/models/pair64_v1.json','tools/check_pair64.py']
    out={'model':'C10','input_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
         'positive_control':{'level5_geometry_matches':64,'level5_full_pipeline_verified':True},
         'cell_count':64,'nominal_cell_width_px':12,'states_per_cell':4,
         'value_profiles':len(profiles),'attempts_including_duplicates':sum(attempts.values()),
         'groups':{g:{'attempts':attempts[g],'out_of_range_or_invalid_rejections':rejected[g],
                      'unique_valid_scalars':len(valid_by_model.get(g,()))} for g in sorted(attempts)},
         'unique_valid_scalars':len(candidates),'public_key_formats':2,'hash_finalization_used':False,
         'candidate_set_sha256':sha256(b''.join(sorted(candidates))).hex(),
         'oracle_selftest':verification,'matches':matches,'limitations':spec['limitations']}
    (ROOT/'research/data/pair64_check.json').write_text(json.dumps(out,indent=2)+'\n')
    (ROOT/'research/data/pair64_profiles.json').write_text(json.dumps(profiles_manifest,indent=2)+'\n')
    with (ROOT/'research/data/halv_64_cells.csv').open('w') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['cell','halving_block','q0','q1','q2','q3','base4_identity','sum','radius_area_anchor91','radius_area_anchor92'])
        aa=linear_cell_areas(q,91);bb=linear_cell_areas(q,92)
        for i,row in enumerate(q.reshape(64,4)):
            w.writerow([i,i//8,*row.tolist(),int(row@np.array([64,16,4,1])),int(sum(row)),aa[i],bb[i]])
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
