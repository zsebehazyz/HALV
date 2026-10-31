#!/usr/bin/env python3
"""C17: independently audit the newly supplied layered-structure observations."""
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def entropy(values):
    return -sum((v/len(values))*math.log2(v/len(values)) for v in Counter(values).values())

def main():
    spec=json.loads((ROOT/'research/models/layered_structure_v1.json').read_text())
    p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    fit=next(f for f in p['fits'] if f['start_x']==92 and f['step_px']==3
             and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1)
    blocks=np.array(fit['states']).reshape(8,32);rows=[];lattices=[]
    draws=spec['surrogate_draws'];rng=np.random.default_rng(spec['rng_seed']);maximum=np.zeros(draws)
    selected_probability={}
    for b,values in enumerate(blocks):
        zeros=values==0;z=int(sum(zeros));surrogates=rng.permuted(np.tile(zeros,(draws,1)),axis=1)
        assert np.all(surrogates.sum(1)==z)
        phase=(2-b)%4
        rows.append({'block_1based':b+1,'state_counts':[int(sum(values==i)) for i in range(4)],
                     'state_entropy_bits':entropy(values.tolist()),'high_bit_entropy_bits':entropy((values>>1).tolist()),
                     'zero_positions':np.flatnonzero(zeros).tolist(),
                     'phase':phase,'off_phase_low_ones':sum(int(v%2) for i,v in enumerate(values) if i%4!=phase)})
        rows[-1]['zero_counts_by_phase']=[int(sum(zeros[r::4])) for r in range(4)]
        rows[-1]['predicted_zero_phase']=(phase+1)%4
        if 2<=b<=6:
            assert rows[-1]['zero_counts_by_phase'][(phase+1)%4]==8
            assert rows[-1]['off_phase_low_ones']==0
        for period in range(2,11):
            for residue in range(period):
                positions=list(range(residue,32,period));k=len(positions)
                if k<4 or k>z:continue
                probability=math.comb(z,k)/math.comb(32,k);score=-math.log(probability)
                matched=bool(np.all(zeros[positions]))
                surrogate_matched=surrogates[:,positions].all(1)
                maximum=np.maximum(maximum,np.where(surrogate_matched,score,0))
                if matched:lattices.append({'block_1based':b+1,'period':period,'residue':residue,'positions':positions,
                                             'fixed_lattice_probability':probability,'score':score})
                if (b,period,residue) in [(7,7,0),(1,8,6)]:
                    selected_probability[str((b+1,period,residue))]={'matches':matched,'fixed_lattice_probability':probability,'sample_count':k}
    best=max(lattices,key=lambda r:r['score']);as_good=int(sum(maximum>=best['score']-1e-12))
    for item in selected_probability.values():
        threshold=-math.log(item['fixed_lattice_probability'])
        count=int(sum(maximum>=threshold-1e-12))
        item['as_good_family_control']=count
        item['family_control_fraction']=count/draws
    edge=[0,1,7];middle=[2,3,4,5,6]
    observed=float(np.mean([rows[i]['state_entropy_bits'] for i in edge])-np.mean([rows[i]['state_entropy_bits'] for i in middle]))
    contrasts=[]
    for selected in itertools.combinations(range(8),3):
        contrasts.append(sum(rows[i]['state_entropy_bits'] for i in selected)/3-sum(rows[i]['state_entropy_bits'] for i in range(8) if i not in selected)/5)
    date='20042402';mask=''.join(str(int(c!='0')) for c in date);bd='10111101'
    permutations=set(itertools.permutations(date));distances=Counter()
    for order in permutations:
        m=''.join(str(int(c!='0')) for c in order);distances[sum(a!=b for a,b in zip(m,bd))]+=1
    half=''.join(str(int(c)//2) for c in date)
    assert mask==''.join(str(int(c!='0')) for c in half)
    edge_selection=''.join(mask[i] for i in edge)
    files=['research/sources/user_layered_notes_20261031.txt','research/data/pixel_measurements.json',
           'research/models/layered_structure_v1.json','tools/check_layered_structure.py']
    out={'model':'C17','input_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
         'blocks':rows,'entropy_contrast':{'edge_mean':float(np.mean([rows[i]['state_entropy_bits'] for i in edge])),
             'middle_mean':float(np.mean([rows[i]['state_entropy_bits'] for i in middle])),
             'difference':observed,'three_block_choices':56,'as_good_descriptive':sum(v>=observed-1e-12 for v in contrasts),
             'not_an_independent_significance_test':True},
         'specified_lattices':selected_probability,'all_complete_zero_lattices':lattices,'strongest_lattice_in_family':best,
         'family_control':{'draws':draws,'seed':spec['rng_seed'],'as_good':as_good,'fraction':as_good/draws,
                           'maximum_scores_file':'research/data/layered_zero_surrogates.npz'},
         'date_bd':{'date':date,'halved_digitwise':half,'nonzero_mask':mask,'mask_hex':f'{int(mask,2):02x}',
                    'bd':bd,'hamming_distance':sum(a!=b for a,b in zip(mask,bd)),
                    'distinct_permutations':len(permutations),'distance_histogram':dict(distances),
                    'as_good':sum(v for k,v in distances.items() if k<=1),
                    'fraction':sum(v for k,v in distances.items() if k<=1)/len(permutations),
                    'edge_bit_selection_both':edge_selection,'halving_does_not_change_nonzero_mask':True,
                    'agreement_on_edges_not_independent_of_overall_mask_agreement':True},
         'bit_budget':{'middle_cells':40,'high_bit_positions_per_cell':4,'fixed_zero_high_bit_positions_per_cell':1,
                       'variable_high_bit_positions_per_cell':3,'additional_variable_low_bits_per_cell':1,
                       'middle_variable_bit_positions':160,'high_only_output_bits_including_fixed_zeros':160,
                       'middle_low_flag40_hex_as_5_bytes':hex(int(''.join(str(int(blocks[b,j]%2)) for b in middle for j in range((2-b)%4,32,4)),2)),
                       'edge_one_bit_selection_output_bits':96,
                       'warning':'The additional always-zero phase makes3H+1L lossless in the middle; choosing only one bit per edge sample remains an unproved rule'},
         'user_reported_candidate_counts_not_reproduced':[1032,10368,35436],
         'no_private_key_search':True,'limitations':spec['limitations']}
    np.savez_compressed(ROOT/'research/data/layered_zero_surrogates.npz',maximum_scores=maximum)
    (ROOT/'research/data/layered_structure_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['blocks','all_complete_zero_lattices','input_sha256']},indent=2))

if __name__=='__main__':main()
