#!/usr/bin/env python3
"""C38: independent H/L window streams, requiring both to predict a q-state."""
import hashlib
import itertools
import json
import numpy as np
from residual_channels import ROOT,nominal_states
from check_sliding_window_generator import starts_for,fit_templates,forecast,TRAIN,TEST


def joint_forecast(q,high,low):
    out=[]
    for h,l in zip(high,low):
        assert h['block_1based']==l['block_1based'];b=h['block_1based']-1
        pred=[None if x is None or y is None else 2*x+y for x,y in zip(h['predicted'],l['predicted'])]
        known=[i for i,v in enumerate(pred) if v is not None]
        correct=[i for i in known if pred[i]==int(q[b,i])]
        out.append({'block_1based':b+1,'predicted':pred,'known_cells':len(known),'correct_cells':len(correct),
                    'correct_nonzero_truth':int(sum(q[b,i]!=0 for i in correct)),
                    'full_exact':len(correct)==32})
    return out


def calibration():
    rng=np.random.default_rng(381101);planes=[];predictions=[]
    for a in [10,6]:
        starts,_,_=starts_for(a,'principal_signed')
        keys=sorted({(b%2,starts[b]+k) for b in range(8) for k in range(32)})
        stream={key:int(rng.integers(0,2)) for key in keys}
        p=np.array([[stream[(b%2,starts[b]+k)] for k in range(32)] for b in range(8)])
        t,conflicts=fit_templates(p,starts,TRAIN);assert not conflicts
        planes.append(p);predictions.append(forecast(p,starts,t,TEST))
    q=2*planes[0]+planes[1];rows=joint_forecast(q,*predictions)
    assert all(r['correct_cells']==r['known_cells'] for r in rows)
    changed=json.loads(json.dumps(predictions[1]));changed[0]['predicted']=[None]*32
    assert joint_forecast(q,predictions[0],changed)[0]['known_cells']==0
    return {'independent_plane_synthetic_generation':True,'missing_plane_not_zero_filled':True}


def main():
    spec=json.loads((ROOT/'research/models/two_plane_window_v1.json').read_text());tests=calibration()
    q=nominal_states().reshape(8,32);by_plane={};all_trials=[]
    for name,plane in [('high',q>>1),('low',q&1)]:
        fits=[];strong=[]
        for policy in ['principal_signed','nonnegative','nonpositive']:
            for a in range(32):
                starts,_,ds=starts_for(a,policy);streams,conflicts=fit_templates(plane,starts,TRAIN)
                overlaps=[32-abs(ds[b]) for b in [2,3]]
                row={'plane':name,'policy':policy,'offset_a':a,'starts':starts,
                     'training_pair_overlaps':overlaps,'training_conflicts':len(conflicts),
                     'strong_overlap':min(overlaps)>=16,'training_exact':not conflicts}
                if not conflicts:
                    row['heldout']=forecast(plane,starts,streams,TEST)
                    row['heldout_total_known']=sum(v['known_cells'] for v in row['heldout'])
                    row['heldout_total_correct']=sum(v['correct_cells'] for v in row['heldout'])
                    row['heldout_correct_nonzero_truth']=sum(v['correct_nonzero_truth'] for v in row['heldout'])
                    fits.append(row)
                    if row['strong_overlap']:strong.append(row)
                all_trials.append(row)
        by_plane[name]={'exact_training_fits':fits,'strong_training_fits':strong,
                        'first_strong_training_fit':strong[0] if strong else None,
                        'heldout_zero_baseline_correct_bits':sum(int(np.sum(plane[b]==0)) for b in TEST)}
    primary=None;combined=[];successes=[]
    high=by_plane['high']['strong_training_fits'];low=by_plane['low']['strong_training_fits']
    for h,l in itertools.product(high,low):
        rows=joint_forecast(q,h['heldout'],l['heldout'])
        row={'high_recipe':{k:h[k] for k in ['policy','offset_a']},'low_recipe':{k:l[k] for k in ['policy','offset_a']},
             'heldout':rows,'all_heldout_128_exact':all(r['full_exact'] for r in rows)}
        combined.append(row)
        if primary is None:primary=row
        if row['all_heldout_128_exact']:successes.append(row)
    names=['research/models/two_plane_window_v1.json','research/models/sliding_window_generator_v1.json',
           'research/data/pixel_measurements.json','tools/check_two_plane_window.py',
           'tools/check_sliding_window_generator.py','tools/residual_channels.py']
    out={'model':'C38','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in names},
         'calibration':tests,'plane_configurations':len(all_trials),'planes':by_plane,
         'strong_composite_configurations':len(combined),'primary_training_selected_composite':primary,
         'full_heldout_successes':successes,'composite_results':combined,'all_plane_trials':all_trials,
         'no_private_key_search':True,'limitations':spec['limitations']}
    (ROOT/'research/data/two_plane_window_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'model':'C38','plane_configurations':len(all_trials),'plane_counts':{
        k:{'exact':len(v['exact_training_fits']),'strong':len(v['strong_training_fits']),
           'zero_baseline':v['heldout_zero_baseline_correct_bits']} for k,v in by_plane.items()},
        'strong_composite_configurations':len(combined),'full_successes':len(successes),'calibration':tests},indent=2))


if __name__=='__main__':main()
