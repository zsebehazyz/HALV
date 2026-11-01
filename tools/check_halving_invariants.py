#!/usr/bin/env python3
"""C35: exact rounding identities and permutation-invariant template bounds."""
import hashlib
import itertools
import json
from fractions import Fraction as F
import numpy as np
from residual_channels import ROOT,nominal_states


def quantize(x,kind):
    lo=x.numerator//x.denominator;rem=x-lo
    if kind=='floor':return lo
    if kind=='ceil':return lo+int(rem!=0)
    if kind=='nearest_ties_even':return lo+int(rem>F(1,2) or (rem==F(1,2) and lo%2))
    if kind=='nearest_ties_up':return lo+int(rem>=F(1,2))
    raise ValueError(kind)


def permutation_witness(a,b):
    remaining=list(range(len(a)));perm=[None]*len(b)
    for j,value in enumerate(b):
        hit=next((i for i in remaining if a[i]==value),None)
        if hit is not None:perm[j]=hit;remaining.remove(hit)
    for j in range(len(b)):
        if perm[j] is None:perm[j]=remaining.pop(0)
    assert sorted(perm)==list(range(len(a)))
    matches=sum(a[i]==value for i,value in zip(perm,b))
    return perm,matches


def calibration():
    vectors=[(F(1,2),[0,1,0,1]),(F(3,2),[1,2,2,2]),
             (F(-1,2),[-1,0,0,0]),(F(-3,2),[-2,-1,-2,-1]),(F(7,4),[1,2,2,2])]
    names=['floor','ceil','nearest_ties_even','nearest_ties_up']
    for value,expected in vectors:assert [quantize(value,n) for n in names]==expected
    rng=np.random.default_rng(351101)
    for _ in range(30):
        a=rng.integers(0,4,6).tolist();b=rng.integers(0,4,6).tolist()
        bound=sum(min(a.count(v),b.count(v)) for v in range(4))
        brute=max(sum(a[i]==value for i,value in zip(p,b)) for p in itertools.permutations(range(6)))
        witness,score=permutation_witness(a,b);assert score==bound==brute
    return {'quantizer_vectors':len(vectors),'histogram_exhaustive_cases':30,'permutations_per_case':720}


def main():
    spec=json.loads((ROOT/'research/models/halving_invariants_v1.json').read_text());tests=calibration()
    q=nominal_states().reshape(8,32);scales=128//2**np.arange(8)
    lag=json.loads((ROOT/'research/data/lag2_halving_check.json').read_text());a=lag['forecast_models'][2]['offset_a']
    identities=0;rows=[]
    for b in range(6):
        shift=int((a+scales[b]//2)%32);pred=np.roll(q[b],-shift);actual=q[b+2]
        scale=int(scales[b+2]);height=pred*scale;physical_target=actual*scale
        for value in range(4):
            raw=F(int(value*scales[b]),4)
            assert raw.denominator==1
            for kind in spec['quantizers']:
                direct=quantize(raw,kind)
                staged=quantize(F(quantize(F(int(value*scales[b]),2),kind),2),kind)
                assert direct==staged==value*scale;identities+=2
        bad=np.flatnonzero(pred!=actual);high=np.flatnonzero((pred>>1)!=(actual>>1));low=np.flatnonzero((pred&1)!=(actual&1))
        rows.append({'blocks_1based':[b+1,b+3],'predicted_shift':shift,'target_scale_px':scale,
                     'predicted_samples':pred.tolist(),'target_samples':actual.tolist(),
                     'exact_matches':32-len(bad),'different_positions_target_frame':bad.tolist(),
                     'high_bit_errors':len(high),'low_bit_errors':len(low),
                     'absolute_height_differences_px':[int(abs(height[i]-physical_target[i])) for i in bad],
                     'mismatch_count_explained_by_declared_rounding':0})
    hist=[np.bincount(row,minlength=4).tolist() for row in q];pairs=[]
    for b,c in itertools.combinations(range(8),2):
        bound=sum(min(x,y) for x,y in zip(hist[b],hist[c]));perm,score=permutation_witness(q[b].tolist(),q[c].tolist())
        assert score==bound
        pairs.append({'blocks_1based':[b+1,c+1],'maximum_matches_under_any_permutation':bound,
                      'minimum_changed_samples':32-bound,'optimal_source_index_permutation':perm})
    assert all(row['minimum_changed_samples']>0 for row in pairs)
    files=['research/models/halving_invariants_v1.json','research/data/pixel_measurements.json',
           'research/data/lag2_halving_check.json','tools/check_halving_invariants.py','tools/residual_channels.py']
    out={'model':'C35','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
         'calibration':tests,'exact_quantizer_identity_checks':identities,
         'histograms_by_block':hist,'lag2_pairs':rows,'all_block_pair_bounds':pairs,
         'all8_histograms_distinct':len({tuple(h) for h in hist})==8,
         'one_template_even_with_arbitrary_permutation_possible':False,
         'two_parity_templates_even_with_arbitrary_permutation_possible':False,
         'no_private_key_search':True,'limitations':spec['limitations']}
    (ROOT/'research/data/halving_invariants_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'model':'C35','calibration':tests,'exact_quantizer_identity_checks':identities,
                      'histograms_by_block':hist,'lag2_matches':[r['exact_matches'] for r in rows],
                      'last_middle_pair':rows[4],'all8_histograms_distinct':out['all8_histograms_distinct']},indent=2))


if __name__=='__main__':main()
