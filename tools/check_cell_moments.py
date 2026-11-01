#!/usr/bin/env python3
"""C43: exact local moment information, regular/full alphabets and residuals."""
import hashlib
import itertools
import json
from collections import defaultdict
from fractions import Fraction as F
import numpy as np
from residual_channels import ROOT,nominal_states,positions


def weights(k):
    result=[F(0) for _ in range(5)]
    for j in range(4):
        a=F((j+1)**(k+1)-j**(k+1),k+1)
        b=F((j+1)**(k+2)-j**(k+2),k+2)
        result[j]+=((j+1)*a-b)/2;result[j+1]+=(b-j*a)/2
    return result


def moments(nodes,ww):return tuple(sum(w*(q if isinstance(q,F) else F(int(q))) for w,q in zip(row,nodes)) for row in ww)


def reverse_decode(features,ww,domain):
    """Receives only exact features; no original q or saved right-node values."""
    alphabet=list(itertools.product(range(4),repeat=4));out=[];cache={}
    for cell in range(63,-1,-1):
        scale=128//2**(cell//8) if domain=='physical_nodes' else 1
        signature=tuple(v/scale for v in features[cell]);n=len(signature)
        if cell==63:
            lookup={moments(list(v)+[v[-1]],ww)[:n]:v for v in alphabet}
        else:
            right=out[0];next_scale=128//2**((cell+1)//8) if domain=='physical_nodes' else 1
            factor=F(next_scale,scale);key=(right,factor,n)
            if key not in cache:
                cache[key]={moments(list(v)+[F(right)*factor],ww)[:n]:v for v in alphabet}
            lookup=cache[key]
        assert len(lookup)==256
        out=list(lookup[signature])+out
    return np.array(out)


def collision_stats(cells,ww):
    records=[]
    for n in range(1,5):
        groups=defaultdict(list)
        for q in cells:groups[moments(list(q)+[0],ww)[:n]].append(list(q))
        bad=[v for v in groups.values() if len(v)>1]
        records.append({'moment_count':n,'distinct_signatures':len(groups),'cell_patterns':len(cells),
                        'injective':not bad,'ambiguous_signature_groups':len(bad),
                        'largest_collision_group':max(map(len,groups.values())),
                        'first_collision_example':bad[0][:2] if bad else None})
    return records


def main():
    spec=json.loads((ROOT/'research/models/cell_moment_identifiability_v1.json').read_text());ww=[weights(k) for k in range(4)]
    # q=2 is unit radius; q=2u is radiusu on local coordinate0..4.
    assert moments([2]*5,ww)==tuple(F(4**(k+1),k+1) for k in range(4))
    assert moments([0,2,4,6,8],ww)==tuple(F(4**(k+2),k+2) for k in range(4))
    first=moments([0,0,2,0,0],ww);second=moments([0,1,0,1,0],ww)
    assert first[:2]==second[:2] and first[2]!=second[2]
    cells=list(itertools.product(range(4),repeat=4));full=collision_stats(cells,ww)
    minimum=next(r['moment_count'] for r in full if r['injective'])
    regular=[]
    for z in range(4):
        r=(z-1)%4;hp=[i for i in range(4) if i!=z];patterns=[]
        for bits in itertools.product([0,1],repeat=4):
            q=[0]*4
            for p,bit in zip(hp,bits[:3]):q[p]=2*bit
            q[r]+=bits[3];patterns.append(tuple(q))
        regular.append({'zero_phase':z,'lower_phase':r,'stats':collision_stats(patterns,ww)})
    q=nominal_states().flatten();extended=np.r_[q,q[-1]];profiles=json.loads((ROOT/'research/data/fractional_area_profiles.json').read_text())
    old=next(p for p in profiles if p['domain']=='normalized_nodes' and p['channel']=='half_q_corrected' and p['anchor']==92 and p['extent']=='radius')
    actual=[];physical_values=[];normal_values=[]
    old_physical=next(p for p in profiles if p['domain']=='physical_nodes' and p['channel']=='half_q_corrected' and p['anchor']==92 and p['extent']=='radius')
    for i in range(64):
        nodes=extended[4*i:4*i+5];value=moments(nodes,ww)
        scale=128//2**(i//8);right_index=min(4*i+4,255);right_scale=128//2**(right_index//32)
        physical_nodes=[F(int(v)*scale) for v in nodes[:4]]+[F(int(nodes[4])*right_scale)]
        physical_value=moments(physical_nodes,ww)
        assert 3*physical_value[0]==F(old_physical['values64_exact'][i])
        normal_values.append(value[:minimum]);physical_values.append(physical_value[:minimum])
        assert 3*value[0]==F(old['values64_exact'][i])
        boundary=int(nodes[-1]);lookup={moments(list(cell)+[boundary],ww)[:minimum]:cell for cell in cells}
        assert len(lookup)==256 and lookup[value[:minimum]]==tuple(map(int,nodes[:4]))
        z,r,hp,lp=positions(i//8,'absolute')
        regular_cell=nodes[z]==0 and all(nodes[p]%2==0 for p in range(4) if p!=r)
        actual.append({'cell':i,'block_1based':i//8+1,'q':nodes[:4].tolist(),'conditioned_right_q':boundary,
                       'regular3plus1':bool(regular_cell),'J_normalized_height_exact':[str(v) for v in value],
                       'normalized_height_pixel_x_M_exact':[str(v*3**(k+1)) for k,v in enumerate(value)],
                       'J_physical_height_exact':[str(v) for v in physical_value],
                       'physical_M_exact':[str(v*3**(k+1)) for k,v in enumerate(physical_value)]})
    assert sum(r['regular3plus1'] for r in actual)==44
    terminal=[]
    for n in range(1,5):
        count=len({moments(list(v)+[v[-1]],ww)[:n] for v in cells})
        terminal.append({'moment_count':n,'distinct_signatures':count,'injective':count==256})
    assert np.array_equal(reverse_decode(normal_values,ww,'normalized_nodes'),q)
    assert np.array_equal(reverse_decode(physical_values,ww,'physical_nodes'),q)
    examples=json.loads((ROOT/'research/data/stateful_bridge_integrity.json').read_text())['nontrivial_zero_area_cells']
    changes=[]
    for example in examples:
        value=moments(example['five_difference_nodes'],ww);assert value[0]==0
        changes.append({**example,'J_exact':[str(v) for v in value],
                        'normalized_height_pixel_x_M_exact':[str(v*3**(k+1)) for k,v in enumerate(value)]})
    names=['research/models/cell_moment_identifiability_v1.json','research/data/pixel_measurements.json',
           'research/data/fractional_area_profiles.json','research/data/stateful_bridge_integrity.json',
           'tools/check_cell_moments.py','tools/residual_channels.py']
    out={'model':'C43','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in names},
         'weights_exact':[[str(v) for v in row] for row in ww],
         'calibration':{'constant_profile':True,'linear_profile':True,'explicit_area_and_firstmoment_collision':True,
                        'C16_area_vectors_matched':128},
         'full_alphabet':full,'regular_alphabets':regular,'minimum_injective_moments_full_alphabet':minimum,
         'actual_cell_count':64,'regular_cells':44,'nonregular_cells':20,
         'conditioned_reconstructions_exact':64,'actual_cells':actual,'zero_area_examples':changes,
         'terminal_continuation_alphabet':terminal,
         'reverse_reconstruction_without_original_nodes':{'moment_count_per_cell':minimum,
             'normalized_nodes_states_recovered':256,'physical_nodes_states_recovered':256,
             'uses_saved_right_nodes':False,'uses_measured_scale_schedule':True,
             'endpoint_continuation_is_an_assumption':True},
         'no_private_key_search':True,'limitations':spec['limitations']}
    (ROOT/'research/data/cell_moments_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'model':'C43','full_alphabet':full,
                      'minimum_regular_moments_by_phase':[next(r['moment_count'] for r in v['stats'] if r['injective']) for v in regular],
                      'zero_area_examples':changes,'actual_reconstructions':64},indent=2))


if __name__=='__main__':main()
