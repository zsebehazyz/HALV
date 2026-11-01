#!/usr/bin/env python3
"""C31-C33: exact causal bridges with training-only fitting and full logs."""
import gzip
import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
import numpy as np
from residual_channels import ROOT,nominal_states,extract,nibble_values
from check_lag2_residual_bridge import middle_code,as_bits


def solve(columns,target):
    """Exact GF2 column-span solution, with coefficient nullspace."""
    basis={};null=[]
    for i,value in enumerate(columns):
        coefficient=1<<i
        while value:
            pivot=value.bit_length()-1
            if pivot not in basis:
                basis[pivot]=(value,coefficient);break
            vector,mask=basis[pivot];value^=vector;coefficient^=mask
        if not value:null.append(coefficient)
    coefficient=0;value=target
    while value:
        pivot=value.bit_length()-1
        if pivot not in basis:return None,len(basis),value
        vector,mask=basis[pivot];value^=vector;coefficient^=mask
    solutions=[coefficient]
    for vector in null:solutions += [v^vector for v in solutions]
    return solutions,len(basis),0


def bitword(bits):return sum(int(b)<<i for i,b in enumerate(bits))


def history(bits,t,lag,reset,width=32):
    j=t-lag
    return int(bits[j]) if j>=0 and (not reset or j//width==t//width) else 0


def features(x,y,reset):
    return ([bitword([history(x,t,k,reset) for t in range(64)]) for k in range(5)]
            +[bitword([history(y,t,k,reset) for t in range(64)]) for k in range(1,5)]
            +[(1<<64)-1])


def forecast(x,y,reset,p,m,coefficient):
    out=list(map(int,y[:64]))
    for t in range(64,96):
        values=[history(x,t,k,reset) for k in range(p+1)]
        values += [history(out,t,k,reset) for k in range(1,m+1)]+[1]
        out.append(sum(v*((coefficient>>i)&1) for i,v in enumerate(values))%2)
    return bitword(out[64:])


def carry_run(s,r,mode,seed,reset):
    state=seed;out=[]
    for i,(sv,rv) in enumerate(zip(s,r)):
        if reset and i%8==0:state=seed
        sv=int(sv);rv=int(rv)
        if mode=='add_carry':
            total=sv+rv+state;value=total%16;state=total//16
        elif mode=='subtract_borrow':
            total=sv-rv-state;value=total%16;state=-(total//16)
        elif mode=='prefix_xor_R':state^=rv;value=sv^state
        else:
            state=(state+(rv if mode=='prefix_sum_R' else -rv))%16
            value=(sv+state)%16
        out.append(value)
    return out


def calibrate():
    rng=np.random.default_rng(311101)
    for _ in range(100):
        columns=[int(v) for v in rng.integers(0,256,5)];target=int(rng.integers(0,256))
        found,_,_=solve(columns,target)
        expected=[]
        for mask in range(32):
            v=0
            for i,col in enumerate(columns):
                if mask>>i&1:v^=col
            if v==target:expected.append(mask)
        assert sorted(found or [])==expected
    x=rng.integers(0,2,96);y=[]
    # Known two-input-tap, one-output-tap causal generator.
    for t in range(96):y.append(history(x,t,0,False)^history(x,t,2,False)^history(y,t,1,False))
    f=features(x,y,False);solutions,_,_=solve([f[i] for i in [0,1,2,5,9]],bitword(y[:64]))
    assert solutions and all(forecast(x,y,False,2,1,c)==bitword(y[64:]) for c in solutions)
    for order in [False,True]:
        a=list(range(8))*3;b=[15]*24
        if order:a=a[::-1];b=b[::-1]
        def integer(v):return sum(n<<(4*i) for i,n in enumerate(v))
        for mode,expected in [('add_carry',integer(a)+integer(b)),('subtract_borrow',integer(a)-integer(b))]:
            out=carry_run(a,b,mode,0,False)
            assert integer(out)==expected%(1<<96)
    return {'GF2_bruteforce_cases':100,'known_causal_generator_forecast':True,'carry_integer_checks':4}


def area4(row):
    h=np.r_[row,row[-1]]
    return np.array([3*(h[4*c]+2*sum(h[4*c+1:4*c+4])+h[4*c+4]) for c in range(8)])


def main():
    spec=json.loads((ROOT/'research/models/stateful_bridge_v1.json').read_text());calibration=calibrate()
    states=nominal_states();q=states.reshape(8,32)
    lag=json.loads((ROOT/'research/data/lag2_halving_check.json').read_text())
    offset=lag['forecast_models'][2]['offset_a'];assert offset==10
    shifts=[(offset+v)%32 for v in [16,8,4]]
    frames={};areas=[];pairs=[]
    for b,shift in zip([2,3,4],shifts):
        source=q[b];target=np.roll(q[b+2],shift)
        difference=target-source;quadrants=area4(target)-area4(source)
        assert np.array_equal(quadrants,area4(difference))
        pairs.append({'blocks_1based':[b+1,b+3],'shift_right_target':shift,
                      'source_samples':source.tolist(),'aligned_target_samples':target.tolist(),
                      'high_error_positions_aligned':np.flatnonzero((source>>1)!=(target>>1)).tolist(),
                      'low_error_positions_aligned':np.flatnonzero((source&1)!=(target&1)).tolist(),
                      'signed_area_change_quarter_numerators':quadrants.tolist()})
        areas.append(quadrants)
    for frame in spec['coordinates']['middle_frames']:
        s=[];t=[]
        for b,shift in zip([2,3,4],shifts):
            s.append(nibble_values(middle_code(q[b].reshape(8,4),b,frame)))
            t.append(nibble_values(middle_code(np.roll(q[b+2],shift).reshape(8,4),b,frame)))
        s=np.array(s);t=np.array(t);words=[]
        for rowa,rowb in zip(s,t):
            value=(int(''.join(f'{v:x}' for v in rowb),16)-int(''.join(f'{v:x}' for v in rowa),16))%2**32
            words.append([int(c,16) for c in f'{value:08x}'])
        frames[frame]=(s,t,{'xor':s^t,'word_subtract_mod2pow32':np.array(words)})
    counts=Counter();fits=[];strong=[];carry_fits=[];area_fits=[];coordinates=[]
    logpath=ROOT/'research/data/stateful_bridge_trials.jsonl.gz'
    with gzip.GzipFile(filename=str(logpath),mode='wb',mtime=0) as log:
        def record(row):log.write((json.dumps(row,separators=(',',':'))+'\n').encode())
        for rf in spec['coordinates']['residual_frames']:
            _,r=extract(states,rf);outer=nibble_values(r).reshape(8,8)[[0,1,7]]
            for mf,(s,t,targets) in frames.items():
                for assignment in itertools.permutations(range(3)):
                    for reverse in [False,True]:
                        selected=outer[list(assignment)];selected=selected[:,::-1] if reverse else selected
                        for rotation in range(8):
                            residual=np.roll(selected,rotation,axis=1)
                            recipe={'residual_frame':rf,'middle_frame':mf,'assignment':assignment,
                                    'reverse_cells':reverse,'common_rotation':rotation}
                            cid=len(coordinates);coordinates.append(recipe)
                            for operation,yvalues in targets.items():
                                for little in [False,True]:
                                    xb=as_bits(residual.flatten());yb=as_bits(yvalues.flatten())
                                    if little:xb=xb[:,::-1];yb=yb[:,::-1]
                                    x=xb.flatten();y=yb.flatten();truth=bitword(y[64:])
                                    for reset in [False,True]:
                                        ff=features(x,y,reset)
                                        for p,m in itertools.product(range(5),repeat=2):
                                            columns=[ff[i] for i in range(p+1)]+[ff[4+j] for j in range(1,m+1)]+[ff[9]]
                                            solutions,rank,contradiction=solve(columns,bitword(y[:64]));counts['C31_configurations']+=1
                                            row={'model':'C31','coordinate_id':cid,'operation':operation,'little_bits':little,
                                                 'reset':reset,'input_memory':p,'output_memory':m,'rank':rank}
                                            if solutions is None:row['status']='training_inconsistent'
                                            else:
                                                predictions=sorted({forecast(x,y,reset,p,m,c) for c in solutions})
                                                row.update({'status':'training_exact','coefficient_solutions':solutions,
                                                            'heldout_prediction_words':predictions,'heldout_truth':truth,
                                                            'heldout_all_solutions_exact':predictions==[truth]})
                                                fits.append(row.copy())
                                                if predictions==[truth]:strong.append(row.copy())
                                            record(row)
                            for direction in [False,True]:
                                ss=s[:,::-1] if direction else s;tt=t[:,::-1] if direction else t
                                rr=residual[:,::-1] if direction else residual
                                for reset,mode,seed in itertools.product([False,True],spec['C32']['modes'],range(16)):
                                    prediction=carry_run(ss.flatten(),rr.flatten(),mode,seed,reset)
                                    counts['C32_configurations']+=1
                                    row={'model':'C32','coordinate_id':cid,'reverse_processing':direction,'reset':reset,'mode':mode,'seed':seed}
                                    exact=prediction[:16]==tt.flatten()[:16].tolist()
                                    row['training_exact']=exact
                                    if exact:
                                        row['heldout_predicted']=prediction[16:];row['heldout_actual']=tt.flatten()[16:].tolist()
                                        row['heldout_exact']=row['heldout_predicted']==row['heldout_actual'];carry_fits.append(row.copy())
                                    record(row)
                            # C33: one exact affine map of raw residual nibble to signed area change.
                            xx=residual.flatten();yy=np.array(areas).flatten();counts['C33_configurations']+=1
                            i=next((i for i in range(1,16) if xx[i]!=xx[0]),None)
                            alpha=Fraction(int(yy[i]-yy[0]),int(xx[i]-xx[0])) if i is not None else Fraction(0)
                            beta=Fraction(int(yy[0]))-alpha*int(xx[0])
                            exact=all(alpha*int(v)+beta==int(w) for v,w in zip(xx[:16],yy[:16]))
                            row={'model':'C33','coordinate_id':cid,'training_exact':exact}
                            if exact:
                                row.update({'alpha':str(alpha),'beta':str(beta),'heldout_exact':all(alpha*int(v)+beta==int(w) for v,w in zip(xx[16:],yy[16:]))});area_fits.append(row.copy())
                            record(row)
    files=['research/models/stateful_bridge_v1.json','research/data/pixel_measurements.json',
           'research/data/lag2_halving_check.json','tools/check_stateful_bridge.py','tools/residual_channels.py','tools/check_lag2_residual_bridge.py']
    result={'models':['C31','C32','C33'],'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
            'calibration':calibration,'counts':dict(counts),'coordinate_views':coordinates,
            'C31_exact_training_fits':fits,'C31_first_training_fit':fits[0] if fits else None,'C31_unique_exact_heldout':strong,
            'C32_exact_training_fits':carry_fits,'C32_first_training_fit':carry_fits[0] if carry_fits else None,
            'C33_exact_training_fits':area_fits,'geometric_consequences':pairs,
            'trial_log':str(logpath.relative_to(ROOT)),'trial_log_sha256':hashlib.sha256(logpath.read_bytes()).hexdigest(),
            'no_private_key_search':True,'limitations':spec['limitations']}
    (ROOT/'research/data/stateful_bridge_check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'counts':dict(counts),'C31_training_fits':len(fits),'C31_unique_heldout':len(strong),
                      'C32_training_fits':len(carry_fits),'C33_training_fits':len(area_fits),'calibration':calibration},indent=2),flush=True)


if __name__=='__main__':main()
