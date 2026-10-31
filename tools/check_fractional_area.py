#!/usr/bin/env python3
"""C16: exact half-unit geometry, preserving fractions before rounding/pairing."""
import hashlib
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from bitcoin_oracle import ORDER,TARGET,addresses,selftest

ROOT=Path(__file__).resolve().parents[1]

def integrate(heights,left,right,origin=92,step=3):
    """Exact trapezoids at all internal nodes; constant endpoint continuation."""
    nodes=[origin+step*i for i in range(len(heights))]
    def at(x):
        if x<=nodes[0]:return F(heights[0])
        if x>=nodes[-1]:return F(heights[-1])
        i=(x-origin)//step;t=F(x-nodes[i],step)
        return heights[i]*(1-t)+heights[i+1]*t
    knots=[left]+[x for x in nodes if left<x<right]+[right]
    return sum((F(b-a,2)*(at(a)+at(b)) for a,b in zip(knots,knots[1:])),F(0))

def rounded(v,kind):
    lo=v.numerator//v.denominator;rem=v-lo
    if kind=='floor':return lo
    if kind=='ceil':return lo+(rem>0)
    if rem<F(1,2):return lo
    if rem>F(1,2):return lo+1
    return lo+(lo%2 if kind=='nearest_ties_even' else 1)

def pair_indices(name):
    if name=='adjacent':return list(zip(range(0,64,2),range(1,64,2)))
    if name=='global_halves':return list(zip(range(32),range(32,64)))
    if name=='within_halving_block_halves':return [(8*b+i,8*b+i+4) for b in range(8) for i in range(4)]
    if name=='transpose_8x8_then_adjacent':
        order=[8*r+c for c in range(8) for r in range(8)]
        return list(zip(order[::2],order[1::2]))
    raise ValueError(name)

def arithmetic_checks():
    assert integrate([F(0),F(1)],0,3,origin=0)==F(3,2)
    assert integrate([F(0),F(1),F(0)],0,6,origin=0)==3
    assert integrate([F(1),F(1)],-1,4,origin=0)==5
    values=[F(0),F(1,3),F(1,2),F(3,2),F(5,2),F(8,3)]
    known={'floor':[0,0,0,1,2,2],'ceil':[0,1,1,2,3,3],
           'nearest_ties_even':[0,0,0,2,2,3],'nearest_ties_up':[0,0,1,2,3,3]}
    for kind,expected in known.items():assert [rounded(v,kind) for v in values]==expected
    for name in ['adjacent','global_halves','within_halving_block_halves','transpose_8x8_then_adjacent']:
        assert sorted(i for pair in pair_indices(name) for i in pair)==list(range(64))
    return {'integral_known_answers':3,'rounder_known_answers':24,'pairing_partition_checks':4}

def main():
    arithmetic=arithmetic_checks()
    spec=json.loads((ROOT/'research/models/fractional_area_v1.json').read_text())
    p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    fit=next(f for f in p['fits'] if f['start_x']==92 and f['step_px']==3
             and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1)
    q=fit['states'];assert len(q)==256 and q[-1]==0
    profiles=[];decompositions=[]
    for domain in spec['domains']:
        scales=[F(1) if domain=='normalized_nodes' else F(128,2**(i//32)) for i in range(256)]
        high=[F(v//2)*s for v,s in zip(q,scales)]
        low=[F(v%2,2)*s for v,s in zip(q,scales)]
        corrected=[F(v,2)*s for v,s in zip(q,scales)]
        for anchor in spec['cell_anchors_px']:
            cellsets={name:[integrate(heights,anchor+12*i,anchor+12*(i+1)) for i in range(64)]
                      for name,heights in [('half_q_corrected',corrected),('high_bit_only_control',high),('low_half_correction',low)]}
            assert all(a==b+c for a,b,c in zip(*cellsets.values()))
            decompositions.append({'domain':domain,'anchor':anchor,
                'cells_with_nonzero_low_correction':sum(v!=0 for v in cellsets['low_half_correction']),
                'low_correction_radius_areas_exact':[str(v) for v in cellsets['low_half_correction']],
                'correction_sum_exact':str(sum(cellsets['low_half_correction']))})
            for channel in spec['height_channels']:
                for extent,factor in spec['extents'].items():
                    vals=[v*factor for v in cellsets[channel]]
                    profiles.append({'label':f'{domain}/{channel}/anchor={anchor}/{extent}',
                        'domain':domain,'channel':channel,'anchor':anchor,'extent':extent,
                        'values64_exact':[str(v) for v in vals],
                        'noninteger_area_count':sum(v.denominator!=1 for v in vals)})
    candidates={};attempts=Counter();rejected=Counter();valid_by_group={};recipes=[];order_effects=[]
    for profile in profiles:
        vals=[F(v) for v in profile['values64_exact']]
        comparisons=0;changed=0;largest_difference=0
        for direction in spec['directions']:
            values=vals if direction=='forward' else vals[::-1]
            for pairing in spec['pairings']:
                for rounding in spec['rounders']:
                    previous_result=None
                    for rounding_order in spec['rounding_orders']:
                        result=[]
                        for i,j in pair_indices(pairing):
                            v=(rounded(values[i],rounding)+rounded(values[j],rounding)
                               if rounding_order=='round_each_then_sum' else rounded(values[i]+values[j],rounding))
                            result.append(v)
                        if previous_result is not None:
                            comparisons+=1;changed+=result!=previous_result
                            largest_difference=max(largest_difference,max(abs(a-b) for a,b in zip(result,previous_result)))
                        previous_result=result
                        group=profile['domain']+'/'+profile['channel'];attempts[group]+=1
                        recipe={'profile':profile['label'],'direction':direction,'pairing':pairing,
                                'rounding':rounding,'rounding_order':rounding_order}
                        overflow=[i for i,v in enumerate(result) if not 0<=v<=255]
                        if overflow:
                            rejected[group]+=1;recipes.append({**recipe,'overflow_indices':overflow,'output_min':min(result),'output_max':max(result)});continue
                        key=bytes(result)
                        if not 0<int.from_bytes(key,'big')<ORDER:
                            rejected[group]+=1;recipes.append({**recipe,'invalid_scalar':True});continue
                        candidates.setdefault(key,recipe);valid_by_group.setdefault(group,set()).add(key)
                        recipes.append({**recipe,'key_hex':key.hex()})
        order_effects.append({'profile':profile['label'],'recipe_pairs_compared':comparisons,
                             'pairs_with_different_outputs':changed,'largest_byte_difference':largest_difference})
    oracle=selftest();matches=[]
    for key,recipe in candidates.items():
        for fmt,address in addresses(key).items():
            if address==TARGET:matches.append({'recipe':recipe,'format':fmt,'key_hex':key.hex()})
    files=['research/sources/cryptoHALV.png','research/data/pixel_measurements.json',
           'research/models/fractional_area_v1.json','tools/check_fractional_area.py','tools/bitcoin_oracle.py']
    out={'model':'C16','input_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
         'arithmetic_checks':arithmetic,'decomposition_checks':256,'value_profiles':len(profiles),
         'attempts_including_duplicates':sum(attempts.values()),
         'groups':{g:{'attempts':attempts[g],'out_of_range_or_invalid_rejections':rejected[g],
                       'unique_valid_scalars':len(valid_by_group.get(g,()))} for g in attempts},
         'decompositions':decompositions,'rounding_order_effects':order_effects,'unique_valid_scalars':len(candidates),
         'candidate_set_sha256':hashlib.sha256(b''.join(sorted(candidates))).hexdigest(),
         'public_key_formats':2,'hash_finalization_used':False,'oracle_selftest':oracle,
         'matches':matches,'limitations':spec['limitations']}
    (ROOT/'research/data/fractional_area_check.json').write_text(json.dumps(out,indent=2)+'\n')
    (ROOT/'research/data/fractional_area_profiles.json').write_text(json.dumps(profiles,indent=2)+'\n')
    (ROOT/'research/data/fractional_area_recipes.json').write_text(json.dumps(recipes,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['decompositions','rounding_order_effects']},indent=2))

if __name__=='__main__':main()
