#!/usr/bin/env python3
"""C21: exact feasibility plus genuine held-out edge-block predictions."""
import hashlib
import itertools
import json
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from residual_channels import ROOT,nominal_states,positions,extract,restore,nibble_values,packed,edge_residual
from bitcoin_oracle import ORDER,TARGET,addresses,selftest

def lookup_predict(a,y,train,test):
    groups=defaultdict(list)
    for i in train:groups[int(a[i])].append(int(y[i]))
    majority={k:min(Counter(v),key=lambda value:(-v.count(value),value)) for k,v in groups.items()}
    predicted=np.array([majority.get(int(a[i]),0) for i in test])
    return np.array([[(v>>s)&1 for s in [3,2,1,0]] for v in predicted]),majority

def affine_feasibility(a,y):
    x=np.c_[np.ones(64,dtype=int),a];aug=np.c_[x,y].copy();row=0
    for col in range(x.shape[1]):
        hits=np.flatnonzero(aug[row:,col])
        if not len(hits):continue
        pivot=row+hits[0];aug[[row,pivot]]=aug[[pivot,row]]
        for j in range(64):
            if j!=row and aug[j,col]:aug[j]^=aug[row]
        row+=1
    bad=np.flatnonzero((aug[:,:5].sum(1)==0)&(aug[:,5:].sum(1)>0))
    return {'design_rank':row,'output_relation_consistent':len(bad)==0,'contradictory_reduced_rows':len(bad)}

def features(a):
    prev=np.vstack([np.zeros((1,4),int),a[:-1]]);nxt=np.vstack([a[1:],np.zeros((1,4),int)])
    coords=np.array([[(i//8>>s)&1 for s in [2,1,0]]+[(i%8>>s)&1 for s in [2,1,0]] for i in range(64)])
    return np.c_[a,prev,nxt,coords]

def parity_bank(x):
    masks=[]
    for n in range(4):
        masks.extend(sorted(sum(1<<i for i in group) for group in itertools.combinations(range(18),n)))
    predictions=[];recipes=[]
    for mask in masks:
        indices=[i for i in range(18) if mask>>i&1]
        base=np.bitwise_xor.reduce(x[:,indices],axis=1) if indices else np.zeros(64,int)
        for complement in [0,1]:
            predictions.append(base^complement);recipes.append({'input_mask':mask,'indices':indices,'complement':complement})
    return np.array(predictions).T,recipes

def metrics(states,a,true,pred,frame,indices):
    correct=pred[indices]==true[indices];truth=true[indices]
    actual_z=[];pred_z=[]
    reconstructed=restore(a,pred,frame)
    for i in indices:
        z=positions(i//8,frame)[0];actual_z.append(int(states[i,z]));pred_z.append(int(reconstructed[i,z]))
    nz=np.array(actual_z)!=0
    return {'tested_cells':len(indices),'exact_cells':int(np.all(correct,axis=1).sum()),
            'tested_residual_bits':int(correct.size),'correct_bits':int(correct.sum()),
            'true_one_bits':int(truth.sum()),'true_one_bits_recovered':int(((pred[indices]==1)&(truth==1)).sum()),
            'false_one_bits':int(((pred[indices]==1)&(truth==0)).sum()),
            'zero_phase_values_exact':sum(x==y for x,y in zip(actual_z,pred_z)),
            'nonzero_zero_phase_values':int(nz.sum()),
            'nonzero_zero_phase_values_exact':sum(x==y for x,y,n in zip(actual_z,pred_z,nz) if n),
            'false_nonzero_zero_phase_values':sum(y!=0 and x==0 for x,y in zip(actual_z,pred_z))}

def main():
    spec=json.loads((ROOT/'research/models/residual_predictors_v1.json').read_text());states=nominal_states()
    frames={};candidates={};candidate_frames=defaultdict(set)
    for frame in spec['frames']:
        a,res=extract(states,frame);assert np.array_equal(restore(a,res,frame),states)
        raw=packed(a);rr=edge_residual(res)
        if frame=='absolute':
            assert raw==(ROOT/'research/data/uniform_primary32.bin').read_bytes()
            assert rr==(ROOT/'research/data/uniform_edge_residual12.bin').read_bytes()
        (ROOT/f'research/data/{frame}_primary32.bin').write_bytes(raw)
        (ROOT/f'research/data/{frame}_residual12.bin').write_bytes(rr)
        av=nibble_values(a);rv=nibble_values(res);groups=defaultdict(list)
        for i,(v,w) in enumerate(zip(av,rv)):groups[int(v)].append((i,int(w)))
        conflicts={str(v):[{'cell':i,'residual':w} for i,w in rows] for v,rows in groups.items() if len({w for _,w in rows})>1}
        bank,recipes=parity_bank(features(a));lookup_oof=np.zeros_like(res);parity_oof=np.zeros_like(res);folds=[]
        allindices=np.arange(64);edge_indices=np.r_[0:16,56:64]
        for b in [0,1,7]:
            test=np.arange(8*b,8*b+8);train=allindices[~np.isin(allindices,test)]
            guess,lookup=lookup_predict(av,rv,train,test);lookup_oof[test]=guess
            choices=[]
            for bit in range(4):
                errors=np.sum(bank[train]!=res[train,bit,None],axis=0);best=int(np.argmin(errors))
                parity_oof[test,bit]=bank[test,best]
                choices.append({**recipes[best],'training_errors':int(errors[best]),'heldout_errors':int(np.sum(bank[test,best]!=res[test,bit]))})
            folds.append({'heldout_block_1based':b+1,'training_cells':56,'selected_parity_rules':choices,
                          'lookup':{str(k):v for k,v in lookup.items()},
                          'lookup_metrics':metrics(states,a,res,lookup_oof,frame,test),
                          'parity_metrics':metrics(states,a,res,parity_oof,frame,test)})
        full_min=[int(np.min(np.sum(bank!=res[:,bit,None],axis=0))) for bit in range(4)]
        frames[frame]={'primary_hex':raw.hex(),'residual_hex':rr.hex(),'states_roundtrip_checked':256,
            'memoryless_conflicting_primary_values':len(conflicts),'memoryless_conflicts':conflicts,
            'affine_current_nibble_feasibility':affine_feasibility(a,res),
            'parity_candidates_per_output_bit':bank.shape[1],'full_data_minimum_bit_errors':full_min,
            'folds':folds,'heldout_zero_baseline':metrics(states,a,res,np.zeros_like(res),frame,edge_indices),
            'heldout_lookup':metrics(states,a,res,lookup_oof,frame,edge_indices),
            'heldout_sparse_parity':metrics(states,a,res,parity_oof,frame,edge_indices),
            'oof_predictions':{'cell_indices':edge_indices.tolist(),'lookup_residual_nibbles':nibble_values(lookup_oof)[edge_indices].tolist(),
                               'parity_residual_nibbles':nibble_values(parity_oof)[edge_indices].tolist()}}
        for perm in itertools.permutations(range(4)):
            for rc,rb,ro in itertools.product([False,True],repeat=3):
                parts=[]
                for b in range(8):
                    cells=a[8*b:8*b+8];cells=cells[::-1] if rc else cells
                    bits=cells[:,perm].flatten();parts.append(bits[::-1] if rb else bits)
                bits=np.concatenate(parts[::-1] if ro else parts)
                key=int(''.join(map(str,bits)),2).to_bytes(32,'big')
                if 0<int.from_bytes(key,'big')<ORDER:
                    candidates.setdefault(key,{'frame':frame,'permutation':perm,'reverse_cells':rc,'reverse_block_bits':rb,'reverse_blocks':ro})
                    candidate_frames[frame].add(key)
    verification=selftest();matches=[]
    old=json.loads((ROOT/'research/data/uniform_phase_layers_check.json').read_text())
    reproduced_control=hashlib.sha256(b''.join(sorted(candidate_frames['absolute']))).hexdigest()==old['candidate_set_sha256']
    assert reproduced_control
    for key,recipe in candidates.items():
        for fmt,address in addresses(key).items():
            if address==TARGET:matches.append({'recipe':recipe,'format':fmt,'key_hex':key.hex()})
    files=['research/data/pixel_measurements.json','research/data/uniform_phase_layers_check.json',
           'research/models/residual_predictors_v1.json','tools/residual_channels.py','tools/check_residual_predictors.py','tools/bitcoin_oracle.py']
    out={'model':'C21','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
         'frames':frames,'unique_valid_scalars':len(candidates),'unique_scalars_per_frame':{k:len(v) for k,v in candidate_frames.items()},
         'absolute_frame_reproduces_c20_candidate_set':reproduced_control,
         'candidate_set_sha256':hashlib.sha256(b''.join(sorted(candidates))).hexdigest(),'public_key_formats':2,
         'hash_finalization_used':False,'oracle_selftest':verification,'matches':matches,'limitations':spec['limitations']}
    (ROOT/'research/data/residual_predictors_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'model':'C21','frames':{k:{field:v[field] for field in ['primary_hex','residual_hex',
          'memoryless_conflicting_primary_values','affine_current_nibble_feasibility','full_data_minimum_bit_errors',
          'heldout_zero_baseline','heldout_lookup','heldout_sparse_parity']} for k,v in frames.items()},
          'unique_valid_scalars':len(candidates),'matches':matches},indent=2))

if __name__=='__main__':main()
