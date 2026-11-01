#!/usr/bin/env python3
"""C34: separate nonlinear memorization from causal heldout prediction."""
import gzip
import hashlib
import itertools
import json
from collections import Counter
import numpy as np
from residual_channels import ROOT,extract,nominal_states,nibble_values
from check_lag2_residual_bridge import middle_code


def context(x,y,t,kind,reset,source=None):
    def prior(values,lag):
        j=t-lag
        return 0 if j<0 or (reset and j//8!=t//8) else values[j]
    values=[x[t]]
    if kind in ['Rcurrent_Rprevious','Rcurrent_Rprevious_Yprevious']:values.append(prior(x,1))
    if kind in ['Rcurrent_Yprevious','Rcurrent_Rprevious_Yprevious','Rcurrent_Yprevious2']:values.append(prior(y,1))
    if kind=='Rcurrent_Yprevious2':values.append(prior(y,2))
    if source is not None:values.append(source[t])
    return None if any(v is None for v in values) else tuple(int(v) for v in values)


def lookup_run(x,y,kind,reset,source=None):
    mapping={}
    for t in range(16):
        key=context(x,y,t,kind,reset,source);value=int(y[t])
        if key in mapping and mapping[key]!=value:return None
        mapping[key]=value
    pred=list(map(int,y[:16]));known=[];correct=[]
    for t in range(16,24):
        key=context(x,pred,t,kind,reset,source)
        value=mapping.get(key) if key is not None else None
        pred.append(value);known.append(value is not None);correct.append(value==int(y[t]) if value is not None else False)
    return {'training_contexts':len(mapping),'heldout_predicted':pred[16:],
            'known_cells':sum(known),'correct_cells':sum(correct),
            'heldout_exact':all(correct),'truth':list(map(int,y[16:]))}


def main():
    spec=json.loads((ROOT/'research/models/nonlinear_context_v1.json').read_text())
    previous=json.loads((ROOT/'research/data/stateful_bridge_check.json').read_text())
    q=nominal_states().reshape(8,32);frames={};outer={}
    # Synthetic nonlinear rule must extrapolate, while an unseen context stays unknown.
    x=np.array([0,1,2,3]*6);y=(x*x+3*x+1)%16
    check=lookup_run(x,y,'Rcurrent',False);assert check['heldout_exact']
    x2=x.copy();x2[16:]=15
    assert lookup_run(x2,y,'Rcurrent',False)['known_cells']==0
    counts=Counter();hist=Counter();first=None;successes=[]
    for rf in ['absolute','phase_relative']:
        _,r=extract(nominal_states(),rf);outer[rf]=nibble_values(r).reshape(8,8)[[0,1,7]]
    for frame in ['absolute','phase_relative','filled_zero_position']:
        source=[];target=[]
        for b,shift in zip([2,3,4],[26,18,14]):
            source.append(nibble_values(middle_code(q[b].reshape(8,4),b,frame)))
            target.append(nibble_values(middle_code(np.roll(q[b+2],shift).reshape(8,4),b,frame)))
        s=np.array(source);t=np.array(target);dif=[]
        for a,b in zip(s,t):
            word=(int(''.join(f'{v:x}' for v in b),16)-int(''.join(f'{v:x}' for v in a),16))%2**32
            dif.append([int(c,16) for c in f'{word:08x}'])
        frames[frame]=(s,{'xor':s^t,'word_subtract_mod2pow32':np.array(dif)})
    path=ROOT/'research/data/nonlinear_context_trials.jsonl.gz'
    with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as log:
        for cid,recipe in enumerate(previous['coordinate_views']):
            rr=outer[recipe['residual_frame']][list(recipe['assignment'])]
            if recipe['reverse_cells']:rr=rr[:,::-1]
            rr=np.roll(rr,recipe['common_rotation'],axis=1)
            s,targets=frames[recipe['middle_frame']]
            for operation,yvalue in targets.items():
                for reverse in [False,True]:
                    x=(rr[:,::-1] if reverse else rr).flatten()
                    y=(yvalue[:,::-1] if reverse else yvalue).flatten()
                    ss=(s[:,::-1] if reverse else s).flatten()
                    for reset,kind,condition in itertools.product([False,True],spec['contexts'],[False,True]):
                        counts['configurations']+=1
                        row={'coordinate_id':cid,'operation':operation,'reverse_processing':reverse,
                             'reset':reset,'context':kind,'source_conditioned':condition}
                        result=lookup_run(x,y,kind,reset,ss if condition else None)
                        row['training_exact']=result is not None
                        if result is not None:
                            counts['training_exact']+=1;row.update(result)
                            hist[(result['known_cells'],result['correct_cells'])]+=1
                            if first is None:first=row.copy()
                            if result['heldout_exact']:successes.append(row.copy())
                        log.write((json.dumps(row,separators=(',',':'))+'\n').encode())
    names=['research/models/nonlinear_context_v1.json','research/data/stateful_bridge_check.json',
           'research/data/lag2_halving_check.json','research/data/pixel_measurements.json',
           'tools/check_nonlinear_context.py','tools/check_lag2_residual_bridge.py','tools/residual_channels.py']
    out={'model':'C34','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in names},
         'counts':dict(counts),'first_training_exact_configuration':first,
         'heldout_coverage_histogram':[{'known_cells':k,'correct_cells':c,'configurations':n} for (k,c),n in sorted(hist.items())],
         'strong_successes':successes,'calibration':{'nonlinear_known_rule':True,'unseen_context_not_filled':True},
         'trial_log':str(path.relative_to(ROOT)),'trial_log_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
         'no_private_key_search':True,'limitations':spec['limitations']}
    (ROOT/'research/data/nonlinear_context_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'counts':dict(counts),'strong_successes':len(successes),'first_training_fit':first,
                     'coverage_histogram':out['heldout_coverage_histogram']},indent=2))


if __name__=='__main__':main()
