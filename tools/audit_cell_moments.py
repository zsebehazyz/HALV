#!/usr/bin/env python3
"""C43 independent exact polynomial integration and reverse reconstruction."""
import hashlib
import itertools
import json
import math
from fractions import Fraction as F
import numpy as np
from residual_channels import ROOT,nominal_states


def integrate(nodes,k):
    total=F(0)
    for j in range(4):
        a=F(nodes[j]);delta=F(nodes[j+1])-a
        for ell in range(k+1):
            total+=F(math.comb(k,ell)*j**(k-ell),2)*(a/F(ell+1)+delta/F(ell+2))
    return total


def signature(nodes,n=3):return tuple(integrate(nodes,k) for k in range(n))


def reconstruct(rows,domain):
    alphabet=list(itertools.product(range(4),repeat=4));out=[];cache={}
    for cell in range(63,-1,-1):
        scale=128//2**(cell//8) if domain=='physical_nodes' else 1
        values=tuple(v/scale for v in rows[cell])
        if cell==63:key='end'
        else:
            next_scale=128//2**((cell+1)//8) if domain=='physical_nodes' else 1
            key=(out[0],F(next_scale,scale))
        if key not in cache:
            lookup={}
            for q in alphabet:
                right=F(q[-1]) if cell==63 else F(key[0])*key[1]
                lookup[signature(list(q)+[right])]=q
            assert len(lookup)==256;cache[key]=lookup
        out=list(cache[key][values])+out
    return np.array(out)


def main():
    data=json.loads((ROOT/'research/data/cell_moments_check.json').read_text())
    for name,digest in data['input_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    alphabet=list(itertools.product(range(4),repeat=4));counts=[]
    for n in range(1,5):
        counts.append(len({signature(list(q)+[0],n) for q in alphabet}))
        assert counts[-1]==data['full_alphabet'][n-1]['distinct_signatures']
    # Two independent integrations per cell; reconstructors consume only features.
    normalized=[];physical=[]
    for row in data['actual_cells']:
        cell=row['cell'];nodes=list(row['q'])+[row['conditioned_right_q']]
        assert [str(integrate(nodes,k)) for k in range(4)]==row['J_normalized_height_exact']
        scale=128//2**(cell//8);right_scale=128//2**(min(cell*4+4,255)//32)
        px=[F(v*scale) for v in row['q']]+[F(row['conditioned_right_q']*right_scale)]
        assert [str(integrate(px,k)) for k in range(4)]==row['J_physical_height_exact']
        normalized.append(tuple(F(v) for v in row['J_normalized_height_exact'][:3]))
        physical.append(tuple(F(v) for v in row['J_physical_height_exact'][:3]))
    q=nominal_states().flatten()
    assert np.array_equal(reconstruct(normalized,'normalized_nodes'),q)
    assert np.array_equal(reconstruct(physical,'physical_nodes'),q)
    out={'purpose':'Independent polynomial moment and source-free reverse audit',
         'distinct_full_alphabet_signatures':counts,'exactly_integrated_cells_in_both_domains':128,
         'reverse_recovered_states_normalized':256,'reverse_recovered_states_physical':256,
         'original_nodes_not_used_by_reverse_function':True,'no_key_decoder_claim':True,
         'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                         ['research/data/cell_moments_check.json','tools/audit_cell_moments.py']}}
    (ROOT/'research/data/cell_moments_integrity.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
