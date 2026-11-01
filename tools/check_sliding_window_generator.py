#!/usr/bin/env python3
"""C37: exact common-stream overlap consistency, then honest heldout coverage."""
import hashlib
import json
import numpy as np
from residual_channels import ROOT,nominal_states

TRAIN=[2,3,4,5]
TEST=[0,1,6,7]


def starts_for(a,policy):
    scales=128//2**np.arange(8);starts=[0,0];shifts=[];displacements=[]
    for b in range(6):
        s=int((a+scales[b]//2)%32)
        if policy=='principal_signed':d=(s+16)%32-16
        elif policy=='nonnegative':d=s
        elif policy=='nonpositive':d=s if s==0 else s-32
        else:raise ValueError(policy)
        shifts.append(s);displacements.append(d);starts.append(starts[b]+d)
    return starts,shifts,displacements


def fit_templates(q,starts,train):
    templates=[{},{}];conflicts=[]
    for b in train:
        for k,value in enumerate(q[b]):
            coordinate=int(starts[b]+k);stream=templates[b%2];value=int(value)
            if coordinate in stream and stream[coordinate]!=value:
                conflicts.append({'block_1based':b+1,'local_index':k,'stream':b%2,
                                  'coordinate':coordinate,'previous_value':stream[coordinate],'new_value':value})
            else:stream[coordinate]=value
    return templates,conflicts


def forecast(q,starts,templates,test):
    rows=[]
    for b in test:
        values=[templates[b%2].get(starts[b]+k) for k in range(32)]
        known=[k for k,v in enumerate(values) if v is not None]
        correct=[k for k in known if values[k]==int(q[b,k])]
        true_nonzero=[k for k in range(32) if q[b,k]!=0]
        rows.append({'block_1based':b+1,'predicted':values,'actual':q[b].tolist(),
                     'known_cells':len(known),'correct_cells':len(correct),
                     'known_nonzero_truth':int(sum(k in known for k in true_nonzero)),
                     'correct_nonzero_truth':int(sum(k in correct for k in true_nonzero)),
                     'false_nonzero_predictions':int(sum(values[k]!=0 and q[b,k]==0 for k in known)),
                     'full_exact':len(correct)==32})
    return rows


def exact_linear_overlaps(a,b):
    rows=[]
    for d in range(-31,32):
        first=max(0,d);last=min(32,d+32)
        equal=sum(int(a[k])==int(b[k-d]) for k in range(first,last))
        rows.append({'displacement_target_start':d,'overlap_samples':last-first,
                     'exact_samples':equal,'whole_overlap_exact':equal==last-first})
    exact=[r for r in rows if r['whole_overlap_exact']]
    longest=max([r['overlap_samples'] for r in exact],default=0)
    return {'all_displacements':rows,'longest_exact_whole_overlap':longest,
            'maximal_exact_overlaps':[r for r in exact if r['overlap_samples']==longest]}


def calibrate():
    starts,_,_=starts_for(10,'principal_signed')
    def symbol(parity,i):return (i*i+3*i+parity)%4
    q=np.array([[symbol(b%2,starts[b]+k) for k in range(32)] for b in range(8)])
    streams,conflicts=fit_templates(q,starts,TRAIN);assert not conflicts
    predictions=forecast(q,starts,streams,TEST)
    assert all(r['correct_cells']==r['known_cells'] for r in predictions)
    assert any(r['known_cells']==32 for r in predictions)
    assert any(r['known_cells']<32 for r in predictions)
    bad=q.copy();bad[4,10]=(bad[4,10]+1)%4
    assert fit_templates(bad,starts,TRAIN)[1]
    # Two disjoint windows cannot contradict each other or forecast the gap.
    disjoint_starts=[100*b for b in range(8)]
    streams,conflicts=fit_templates(q,disjoint_starts,TRAIN);assert not conflicts
    assert all(r['known_cells']==0 for r in forecast(q,disjoint_starts,streams,TEST))
    known=exact_linear_overlaps(np.zeros(32,int),np.zeros(32,int))
    assert known['longest_exact_whole_overlap']==32
    return {'synthetic_known_stream_forecast':True,'injected_overlap_conflict_detected':True,
            'unknown_coordinates_not_filled':True,'no_overlap_not_promoted':True,'exact_overlap_known_answer':True}


def main():
    spec=json.loads((ROOT/'research/models/sliding_window_generator_v1.json').read_text());checks=calibrate()
    q=nominal_states().reshape(8,32);records=[];fits=[];strong=[];successes=[]
    for policy in spec['displacement_policies']:
        for a in range(32):
            starts,shifts,ds=starts_for(a,policy);templates,conflicts=fit_templates(q,starts,TRAIN)
            overlaps=[32-abs(ds[b]) for b in [2,3]];requirement=min(overlaps)>=16
            row={'policy':policy,'offset_a':a,'starts':starts,'shifts_mod32':shifts,
                 'displacements':ds,'training_pair_overlaps':overlaps,
                 'meets_minimum_training_overlap':requirement,'training_conflicts':len(conflicts),
                 'first_conflict':conflicts[0] if conflicts else None,
                 'unique_training_coordinates':[len(t) for t in templates],
                 'training_exact':not conflicts}
            if not conflicts:
                predictions=forecast(q,starts,templates,TEST);row['heldout']=predictions
                row['all_heldout_128_exact']=all(r['full_exact'] for r in predictions)
                fits.append(row)
                if requirement:strong.append(row)
                if requirement and row['all_heldout_128_exact']:successes.append(row)
            records.append(row)
    diagnostics=[]
    for b,c in [(2,4),(3,5),(4,6)]:
        diagnostics.append({'blocks_1based':[b+1,c+1],**exact_linear_overlaps(q[b],q[c])})
    names=['research/models/sliding_window_generator_v1.json','research/data/pixel_measurements.json',
           'research/data/lag2_halving_check.json','tools/check_sliding_window_generator.py','tools/residual_channels.py']
    out={'model':'C37','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in names},
         'calibration':checks,'configurations':len(records),'training_exact_fits':fits,
         'strong_training_exact_fits':strong,'first_strong_training_fit':strong[0] if strong else None,
         'all_128_heldout_successes':successes,'linear_overlap_diagnostics':diagnostics,
         'all_trials':records,'no_private_key_search':True,'limitations':spec['limitations']}
    (ROOT/'research/data/sliding_window_generator_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'model':'C37','configurations':len(records),'exact_training_fits':len(fits),
                      'strong_training_fits':len(strong),'full_heldout_successes':len(successes),
                      'longest_exact_overlaps':[(r['blocks_1based'],r['longest_exact_whole_overlap']) for r in diagnostics],
                      'weak_fits':fits,'calibration':checks},indent=2))


if __name__=='__main__':main()
