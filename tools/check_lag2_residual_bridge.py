#!/usr/bin/env python3
"""C26: learn on two transition corrections, predict the third from outer R."""
import hashlib
import itertools
import json
import numpy as np
from residual_channels import ROOT,nominal_states,positions,extract,nibble_values

def as_bits(values):return np.array([[(int(v)>>s)&1 for s in [3,2,1,0]] for v in values])

def middle_code(cells,b,frame):
    z,r,hp,_=positions(b,'phase_relative' if frame=='phase_relative' else 'absolute')
    out=[]
    for cell in cells:
        assert cell[z]==0 and all(cell[j]%2==0 for j in range(4) if j!=r)
        if frame=='filled_zero_position':
            bits=(cell>>1).copy();bits[z]=cell[r]&1;out.append(bits)
        else:out.append([cell[j]>>1 for j in hp]+[cell[r]&1])
    return np.array(out)

def exact_affine(x,y,test):
    design=np.c_[np.ones(len(x),int),x];aug=np.c_[design,y].copy();pivots=[];row=0
    for col in range(5):
        hit=np.flatnonzero(aug[row:,col])
        if not len(hit):continue
        k=row+int(hit[0]);aug[[row,k]]=aug[[k,row]]
        for j in range(len(aug)):
            if j!=row and aug[j,col]:aug[j]^=aug[row]
        pivots.append(col);row+=1
    if np.any((aug[:,:5].sum(1)==0)&(aug[:,5:].sum(1)>0)):return None
    coefficient=np.zeros((5,4),int)
    for j,col in enumerate(pivots):coefficient[col]=aug[j,5:]
    null=[]
    for col in range(5):
        if col in pivots:continue
        vector=np.zeros(5,int);vector[col]=1
        for j,pivot in enumerate(pivots):vector[pivot]=aug[j,col]
        null.append(vector)
    test_design=np.c_[np.ones(len(test),int),test];pred=(test_design@coefficient)%2
    unique=np.ones(len(test),bool) if not null else np.all((test_design@np.array(null).T)%2==0,axis=1)
    return {'rank':len(pivots),'coefficient':coefficient.tolist(),'predicted_nibbles':nibble_values(pred).tolist(),
            'uniquely_predicted_cells':int(unique.sum()),'all_predictions_unique':bool(unique.all())}

def exact_lookup(x,y,test):
    mapping={}
    for v,w in zip(nibble_values(x),nibble_values(y)):
        v=int(v);w=int(w)
        if v in mapping and mapping[v]!=w:return None
        mapping[v]=w
    pred=[mapping.get(int(v)) for v in nibble_values(test)]
    return {'mapping':mapping,'predicted_nibbles':pred,'uniquely_predicted_cells':sum(v is not None for v in pred),
            'all_predictions_unique':all(v is not None for v in pred)}

def main():
    spec=json.loads((ROOT/'research/models/lag2_residual_bridge_v1.json').read_text());states=nominal_states();q=states.reshape(8,32)
    lag=json.loads((ROOT/'research/data/lag2_halving_check.json').read_text());a=lag['forecast_models'][2]['offset_a']
    shifts=[(a+v)%32 for v in [16,8,4]];corrections={};raw_xor_ones=None
    for frame in spec['middle_frames']:
        for operation in spec['transition_corrections']:
            words=[]
            for b,shift in zip([2,3,4],shifts):
                source=middle_code(q[b].reshape(8,4),b,frame);target=middle_code(np.roll(q[b+2],shift).reshape(8,4),b,frame)
                sv=nibble_values(source);tv=nibble_values(target)
                if operation=='xor':bits=source^target
                elif operation=='nibble_subtract_mod16':bits=as_bits((tv-sv)%16)
                else:
                    si=int(''.join(f'{v:x}' for v in sv),16);ti=int(''.join(f'{v:x}' for v in tv),16)
                    bits=as_bits([int(c,16) for c in f'{(ti-si)%2**32:08x}'])
                words.append(bits)
            corrections[(frame,operation)]=np.array(words)
            if frame=='phase_relative' and operation=='xor':raw_xor_ones=[int(word.sum()) for word in words]
    tested=0;fits=[];successes=[];counts={name:0 for name in ['affine','lookup']}
    for rframe in spec['residual_frames']:
        _,rr=extract(states,rframe);outer=rr.reshape(8,8,4)[[0,1,7]]
        for mframe in spec['middle_frames']:
            for operation in spec['transition_corrections']:
                target=corrections[(mframe,operation)];truth=nibble_values(target[2]).tolist()
                for order in itertools.permutations(range(3)):
                    selected=outer[list(order)]
                    for reverse in [False,True]:
                        rev=selected[:,::-1] if reverse else selected
                        for rotation in range(8):
                            candidate=np.roll(rev,rotation,axis=1);train=candidate[:2].reshape(16,4);test=candidate[2];tested+=1
                            recipe={'residual_frame':rframe,'middle_frame':mframe,'operation':operation,
                                    'residual_word_order':order,'reverse_cells':reverse,'common_cell_rotation':rotation}
                            for name,fn in [('affine',exact_affine),('lookup',exact_lookup)]:
                                result=fn(train,target[:2].reshape(16,4),test)
                                if result is None:continue
                                counts[name]+=1;hit=result['all_predictions_unique'] and result['predicted_nibbles']==truth
                                record={'predictor':name,'recipe':recipe,'prediction':result,'actual_heldout_nibbles':truth,'heldout_full_match':hit}
                                fits.append(record)
                                if hit:successes.append(record)
    files=['research/data/pixel_measurements.json','research/data/lag2_halving_check.json',
           'research/models/lag2_residual_bridge_v1.json','tools/check_lag2_residual_bridge.py','tools/residual_channels.py']
    correction_manifest=[{'frame':f,'operation':o,'nibbles_by_transition':nibble_values(v.reshape(24,4)).reshape(3,8).tolist()}
                         for (f,o),v in corrections.items()]
    out={'model':'C26','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
         'common_offset_from_training':a,'shifts':shifts,'residual_word_bit_weights':[12,5,12],
         'xor_transition_bit_weights':raw_xor_ones,
         'pure_bit_permutation_impossible':sum(raw_xor_ones)!=29,
         'coordinate_configurations':tested,'exact_training_fit_counts':counts,'exact_training_fits':fits,
         'first_exact_training_fit_without_holdout_selection':fits[0] if fits else None,
         'full_heldout_successes':successes,'correction_words':correction_manifest,
         'no_private_key_search':True,'limitations':spec['limitations']}
    (ROOT/'research/data/lag2_residual_bridge_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['model','shifts','residual_word_bit_weights','xor_transition_bit_weights',
                 'coordinate_configurations','exact_training_fit_counts','full_heldout_successes']},indent=2))

if __name__=='__main__':main()
