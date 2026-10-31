#!/usr/bin/env python3
"""C12: parity recurrence, exact phase reference, image constraints and pixel cross-fit."""
import hashlib
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/halv-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/halv-cache')
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]

def costs(a,offset):
    yy=np.arange(85,866);out=np.empty((255,4,4));scales=128/2.**(np.arange(256)//32)
    for k in range(255):
        obs=a[85:866,92+3*k+offset]/255
        for u in range(4):
            for v in range(4):
                start=u*scales[k];slope=(v*scales[k+1]-start)/3;amplitude=start+slope*offset
                d=np.minimum(abs(yy-(475-amplitude)),abs(yy-(475+amplitude)))/np.sqrt(1+slope*slope)
                pred=np.interp(d,[0,1,2,3],[1,113/255,20/255,0])
                out[k,u,v]=np.mean((obs-pred)**2)
    return out

def solve(c,allowed=None):
    allowed=np.ones((256,4),bool) if allowed is None else allowed
    forward=np.where(allowed[0],0.,np.inf);parents=[]
    for k in range(255):
        z=forward[:,None]+c[k];parents.append(np.argmin(z,axis=0))
        forward=np.min(z,axis=0);forward[~allowed[k+1]]=np.inf
    state=int(np.argmin(forward));total=float(forward[state]);path=[state]
    for row in parents[::-1]:state=int(row[state]);path.append(state)
    return np.array(path[::-1]),total

def parity(q):
    return np.array([np.bincount(np.flatnonzero(b&1)%4,minlength=4) for b in q.reshape(8,32)])

def allowed_law(first=0,last=8,intercept=2):
    mask=np.ones((256,4),bool)
    for b in range(first,last):
        for j in range(32):
            if (j+b)%4!=intercept:mask[32*b+j,[1,3]]=False
    return mask

def main():
    p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    baseline=next(f for f in p['fits'] if f['start_x']==92 and f['step_px']==3 and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1)
    q=np.array(baseline['states']);a=np.array(Image.open(ROOT/'research/sources/cryptoHALV.png'),float)
    counts=parity(q);total=counts.sum(1);phase_table=[]
    for b in range(8):
        phase_table.append({'block_1based':b+1,'odd_positions':np.flatnonzero(q[b*32:b*32+32]&1).tolist(),
                            'counts_by_phase':counts[b].tolist(),'predicted_phase':(2-b)%4,
                            'predicted_law_violations':int(total[b]-counts[b,(2-b)%4])})
    shifts=np.indices((4,)*8,dtype=np.int8).reshape(8,-1).T
    reference=np.full(len(shifts),256);observed_best=256;best_models=[]
    for start in range(4):
        bs=np.arange(start,start+5)
        for slope in range(4):
            for intercept in range(4):
                phases=(intercept+slope*bs)%4
                violation=int(np.sum(total[bs]-counts[bs,phases]))
                ref=np.sum(total[bs][None,:]-counts[bs[None,:],(phases[None,:]-shifts[:,bs])%4],axis=1)
                reference=np.minimum(reference,ref)
                record={'start_block_1based':start+1,'slope_mod4':slope,'intercept_mod4':intercept,'violations':violation}
                if violation<observed_best:observed_best=violation;best_models=[record]
                elif violation==observed_best:best_models.append(record)
    c1=costs(a,1);c2=costs(a,2);full=(c1+c2)/2
    recovered,objective=solve(full)
    assert np.array_equal(recovered,q) and np.isclose(objective/255,baseline['mean_segment_mse'],atol=1e-14)
    within=(np.arange(255)+1)%32!=0
    cross=[]
    for train,test,offset in [(c1,c2,1),(c2,c1,2)]:
        training=train.copy();training[~within]=0
        fitted,_=solve(training)
        mse=float(np.mean(test[np.arange(255)[within],fitted[:-1][within],fitted[1:][within]]))
        # Fixed reference: shuffle within block, compare on the same held-out columns.
        rng=np.random.default_rng(20261031+offset);loss=[]
        for _ in range(1000):
            s=np.concatenate([rng.permutation(b) for b in fitted.reshape(8,32)])
            loss.append(float(np.mean(test[np.arange(255)[within],s[:-1][within],s[1:][within]])))
        cross.append({'fit_offset':offset,'validation_offset':3-offset,'training_columns':248,'validation_columns':248,
                      'states':fitted.tolist(),'different_state_indices':np.flatnonzero(fitted!=q).tolist(),
                      'parity_by_block':parity(fitted).tolist(),'validation_pixel_mse':mse,
                      'shuffled_median_mse':float(np.median(loss)),
                      'reference_fraction':float((1+sum(v<=mse for v in loss))/1001)})
    phase_audits=[]
    for b in range(8):
        values=[]
        for phase in range(4):
            mask=np.ones((256,4),bool)
            for j in range(32):
                if j%4!=phase:mask[b*32+j,[1,3]]=False
            fitted,cost=solve(full,mask)
            values.append({'phase':phase,'objective_increase':cost-objective,
                           'changed_indices':np.flatnonzero(fitted!=q).tolist()})
        phase_audits.append({'block_1based':b+1,'phase_constraints':values})
    constrained=[]
    for name,first in [('predicted_middle_and_last',2),('predicted_all_blocks',0)]:
        fitted,cost=solve(full,allowed_law(first=first))
        changed=np.flatnonzero(fitted!=q)
        constrained.append({'model':name,'objective_increase':cost-objective,'relative_objective_increase':(cost-objective)/objective,
                            'changed_indices':changed.tolist(),'states':fitted.tolist()})
    endpoints=[float(q[(b+1)*32]/2) if b<7 else float(q[-1]) for b in range(8)]
    files=['research/sources/cryptoHALV.png','research/data/pixel_measurements.json','research/models/parity_phase_v1.json','tools/analyze_parity_phase.py']
    out={'model':'C12','input_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
         'parity_table':phase_table,'high_bit_hex':int(''.join(map(str,(q>>1).tolist())),2).to_bytes(32,'big').hex(),
         'law':'(local_index + zero_based_block_index) % 4 == 2 at odd amplitudes',
         'phase_reference':{'count':len(shifts),'searched_models':64,'observed_min_violations':observed_best,
                            'best_models':best_models,'as_good_count':int(np.sum(reference<=observed_best)),
                            'fraction':float(np.mean(reference<=observed_best)),
                            'scope':'Exact conditional reference over independent block phases; not global research-adjusted significance.'},
         'crossfit':cross,'phase_constraint_audits':phase_audits,'constrained_models':constrained,
         'logical_33_point_interpretation':{'endpoint_if_shared_next_node':endpoints,
            'noninteger_endpoint_blocks_1based':[b+1 for b,v in enumerate(endpoints) if v!=int(v)],
            'limitation':'Adding b to sample index aligns the middle-block phase, but does not prove eight independent missing samples; endpoints are shared geometric constraints.'},
         'user_amplitude_errors_not_reproduced':'0.0404 and shuffle median 0.858 require the exact medial-line estimator; this run reports explicit pixel MSE instead.',
         'no_private_key_search':True}
    (ROOT/'research/data/parity_phase_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Parity reference',out['phase_reference'])
    for row in cross:print('Crossfit',row['fit_offset'],'state differences',row['different_state_indices'],'validation MSE',row['validation_pixel_mse'])
    for row in constrained:print('Constraint',row['model'],'relative increase',row['relative_objective_increase'],'changes',len(row['changed_indices']))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(3,1,figsize=(13,9),layout='constrained')
    axes[0].imshow((q.reshape(8,32)>>1),cmap='gray',vmin=0,vmax=1,aspect='auto');axes[0].set(title='High bit of nominal amplitude',ylabel='Block (zero based)')
    axes[1].imshow((q.reshape(8,32)&1),cmap='gray',vmin=0,vmax=1,aspect='auto');axes[1].set(title='Low bit; red marks predict phase (2 - block) modulo 4',ylabel='Block (zero based)')
    for b in range(8):axes[1].scatter(np.arange((2-b)%4,32,4),np.full(8,b),marker='|',c='red',s=40)
    axes[2].plot(range(1,9),[min(v['objective_increase'] for v in r['phase_constraints']) for r in phase_audits],'.-',label='Best of four constrained phases')
    axes[2].set(title='Image-fit cost of requiring one parity phase per block',xlabel='Block (one based)',ylabel='Increase in summed pixel MSE');axes[2].legend()
    fig.savefig(ROOT/'research/data/parity_phase_audit.png',dpi=150)

if __name__=='__main__':main()
