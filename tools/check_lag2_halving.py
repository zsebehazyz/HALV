#!/usr/bin/env python3
"""C25: single-offset lag2 forecast, complete searched-family controls."""
import hashlib
import json
import numpy as np
from residual_channels import ROOT,nominal_states

TERMS=np.array([64,32,16,8,4,2])%32

def pair_scores(arrays):
    # arrays: batch,8,32; result: batch,6,32 cyclic-shift scores.
    out=np.empty((len(arrays),6,32),dtype=np.int16)
    for b in range(6):
        for shift in range(32):out[:,b,shift]=np.sum(arrays[:,b]==np.roll(arrays[:,b+2],shift,axis=1),axis=1)
    return out

def summaries(scores):
    n=len(scores);windows=[];forecasts=[];training=[];offsets=[]
    for start in range(4):
        windows.append(scores[:,start:start+3].max(axis=2).sum(axis=1))
        aa=np.arange(32)
        fit=scores[:,start,(aa+TERMS[start])%32]+scores[:,start+1,(aa+TERMS[start+1])%32]
        best=fit.argmax(axis=1);trained=fit[np.arange(n),best]
        forecast=scores[np.arange(n),start+2,(best+TERMS[start+2])%32]
        forecasts.append(forecast);training.append(trained);offsets.append(best)
    windows=np.array(windows).T;forecasts=np.array(forecasts).T;training=np.array(training).T
    return {'window_scores':windows,'offsets':np.array(offsets).T,'train':training,'forecast':forecasts,
            'max_descriptive':windows.max(1),'max_forecast_total':(training+forecasts).max(1),
            'middle_forecast':forecasts[:,2],'max_forecast':forecasts.max(1)}

def shuffled_chunks(q,size,draws,rng):
    count=32//size;source=np.broadcast_to(q.reshape(1,8,count,size),(draws,8,count,size))
    orders=rng.permuted(np.broadcast_to(np.arange(count),(draws,8,count)).copy(),axis=2)
    result=np.take_along_axis(source,orders[:,:,:,None],axis=2)
    # A single cell/chunk order is shared across all sample positions within it.
    for b in range(8):
        assert sorted(map(tuple,result[0,b]))==sorted(map(tuple,q[b].reshape(count,size)))
    return result.reshape(draws,8,32)

def main():
    spec=json.loads((ROOT/'research/models/lag2_halving_v1.json').read_text());q=nominal_states().reshape(8,32)
    scores=pair_scores(q[None]);observed=summaries(scores);pairs=[]
    for b in range(6):
        best=int(scores[0,b].max());pairs.append({'blocks_1based':[b+1,b+3],'best_matches':best,
            'best_shifts_right':np.flatnonzero(scores[0,b]==best).tolist(),'all_shift_scores':scores[0,b].tolist()})
    models=[]
    for start in range(4):
        a=int(observed['offsets'][0,start]);shift=int((a+TERMS[start+2])%32);source=q[start+2];target=q[start+4]
        predicted=np.roll(source,-shift);bad=np.flatnonzero(predicted!=target)
        models.append({'window_1based':[start+1,start+5],'offset_a':a,'training_matches_out_of64':int(observed['train'][0,start]),
            'predicted_shift_for_last_pair':shift,'forecast_matches_out_of32':int(observed['forecast'][0,start]),
            'predicted_target_samples':predicted.tolist(),'actual_target_samples':target.tolist(),
            'always_zero_matches_out_of32':int(sum(target==0)),
            'unshifted_source_matches_out_of32':int(sum(source==target)),
            'phase_only_shift2_matches_out_of32':int(scores[0,start+2,2]),
            'mismatching_target_positions':bad.tolist(),'high_bit_errors':int(sum((predicted>>1)!=(target>>1))),
            'low_bit_errors':int(sum((predicted&1)!=(target&1)))})
    a=models[2]['offset_a'];extrapolation=[{'pair_1based':[b+1,b+3],'shift':int((a+TERMS[b])%32),
        'matches_out_of32':int(scores[0,b,(a+TERMS[b])%32])} for b in range(6)]
    assert a%2==0
    scale=128//2**np.arange(8);phi=(2*scale)//3-(a//2)*np.arange(8)
    assert np.array_equal((phi[:-2]-phi[2:])%32,(a+TERMS)%32)
    halves=[]
    for b in [2,3,4]:
        train=[int(sum(q[b,:16]==np.roll(q[b+2],s)[:16])) for s in range(32)];shift=int(np.argmax(train))
        halves.append({'blocks_1based':[b+1,b+3],'shift_fit_on_first16':shift,'first16_matches':train[shift],
                       'last16_matches':int(sum(q[b,16:]==np.roll(q[b+2],shift)[16:]))})
    rng=np.random.default_rng(spec['rng_seed']);controls={};saved={}
    names=['max_descriptive','max_forecast_total','middle_forecast','max_forecast']
    for control in spec['controls']:
        size=control['chunk_samples'];draws=control['draws'];parts={name:[] for name in names}
        for first in range(0,draws,500):
            batch=min(500,draws-first);result=summaries(pair_scores(shuffled_chunks(q,size,batch,rng)))
            for name in names:parts[name].append(result[name])
        record={}
        for name in names:
            values=np.concatenate(parts[name]);threshold=int(observed[name][0]);count=int(sum(values>=threshold))
            record[name]={'observed':threshold,'draws':draws,'as_good':count,'plus_one_fraction':(1+count)/(1+draws),
                          'median':float(np.median(values)),'max':int(values.max())}
            saved[f'chunk{size}_{name}']=values
        controls[str(size)]=record;print('Control chunk size',size,record,flush=True)
    # Half-block swaps are rotations. They cannot supply a nontrivial null for these maxima.
    rotated=q.copy()
    for b in range(8):rotated[b]=np.roll(rotated[b],16*(b%2))
    assert np.array_equal(summaries(pair_scores(rotated[None]))['window_scores'],observed['window_scores'])
    np.savez_compressed(ROOT/'research/data/lag2_control_scores.npz',**saved)
    files=['research/data/pixel_measurements.json','research/models/lag2_halving_v1.json','tools/check_lag2_halving.py','tools/residual_channels.py',
           'research/sources/upload_HALV_uj_felezeses_blokkkapcsolat_jelentes_20261101.md']
    out={'model':'C25','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},'pairs':pairs,
         'window_scores':observed['window_scores'][0].tolist(),'forecast_models':models,'middle_model_extrapolation':extrapolation,
         'equivalent_phase_coordinates':{'formula':'phi_b=floor(2*scale_b/3)-(a/2)*b',
             'phi_unwrapped':phi.tolist(),'phi_mod32':(phi%32).tolist(),
             'normalization':'Roll block b by -phi_b; parity templates align approximately',
             'evidence_status':'Algebraic restatement of the fitted shift rule; does not independently derive a=10'},
         'reported_half_split':halves,'controls':controls,'control_seed':spec['rng_seed'],
         'half_swap_descriptive_rotation_invariance_verified':True,
         'modular_halving_ambiguity':'Given s1=26,s2=18, the modular equation2*s3=3*s2-s1 has solutions14 and30; unique14 uses the explicitly stated amplitude-scale formula and shared offset',
         'no_private_key_search':True,'limitations':spec['limitations']}
    (ROOT/'research/data/lag2_halving_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Window scores',out['window_scores'],'middle model',models[2],flush=True)

if __name__=='__main__':main()
