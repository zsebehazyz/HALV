#!/usr/bin/env python3
"""Full eight-block dominant phase, residual channel and local constraint costs."""
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
from PIL import Image
from analyze_parity_phase import costs

ROOT=Path(__file__).resolve().parents[1]
p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
q=np.array(next(f['states'] for f in p['fits'] if f['start_x']==92 and f['step_px']==3 and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1))
r=json.loads((ROOT/'research/data/parity_phase_check.json').read_text())
counts=np.array([x['counts_by_phase'] for x in r['parity_table']]);dominant=np.argmax(counts,axis=1)
assert all(np.sum(row==row.max())==1 for row in counts)
shifts=np.indices((4,)*8,dtype=np.int8).reshape(8,-1).T
reference=np.full(len(shifts),8);best=8;models=[]
for slope in range(4):
    for intercept in range(4):
        predicted=(intercept+slope*np.arange(8))%4
        errors=int(np.sum(predicted!=dominant))
        reference=np.minimum(reference,np.sum((dominant[None,:]+shifts)%4!=predicted[None,:],axis=1))
        if errors<best:best=errors;models=[{'slope':slope,'intercept':intercept}]
        elif errors==best:models.append({'slope':slope,'intercept':intercept})
flags=[];residual=[];residual_blocks=[]
for b,block in enumerate(q.reshape(8,32)):
    phase=(2-b)%4
    flags.extend((block[phase::4]&1).tolist())
    other=[int(v&1) for j,v in enumerate(block) if j%4!=phase]
    residual+=other;residual_blocks.append(other)
a=np.array(Image.open(ROOT/'research/sources/cryptoHALV.png'),float);c=(costs(a,1)+costs(a,2))/2
local=[]
for constraint in r['constrained_models']:
    state=np.array(constraint['states']);rows=[]
    for b in range(8):
        indices=np.arange(32*b,min(32*b+31,255))
        old=float(np.mean(c[indices,q[indices],q[indices+1]]));new=float(np.mean(c[indices,state[indices],state[indices+1]]))
        rows.append({'block_1based':b+1,'baseline_within_block_mse':old,'constrained_mse':new,
                     'ratio':new/old if old else None,'changed_nodes':int(np.sum(state[b*32:b*32+32]!=q[b*32:b*32+32]))})
    local.append({'model':constraint['model'],'blocks':rows})
out={'parity_result_sha256':hashlib.sha256((ROOT/'research/data/parity_phase_check.json').read_bytes()).hexdigest(),
     'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
     'dominant_phases':dominant.tolist(),'unique_maximum_in_every_block':True,'affine_models':models,
     'exact_conditional_phase_reference':{'draws':len(shifts),'affine_models_tested':16,'observed_mismatches':best,
                                          'as_good':int(np.sum(reference<=best)),'fraction':float(np.mean(reference<=best)),
                                          'limitation':'Exploratory conditional reference given observed phase counts; not a global p-value or proof of intended coding.'},
     'flag64_bits':flags,'flag64_hex':int(''.join(map(str,flags)),2).to_bytes(8,'big').hex(),
     'middle40_flags':flags[16:56],
     'middle40_runs':[[v,len(list(g))] for v,g in itertools.groupby(flags[16:56])],
     'residual192_bits':residual,'residual_ones_per_block':[sum(v) for v in residual_blocks],
     'edge_residual72_hex':int(''.join(map(str,residual_blocks[0]+residual_blocks[1]+residual_blocks[7])),2).to_bytes(9,'big').hex(),
     'note':'Off-phase bits are preserved, not labeled noise or discarded. Only first two and last blocks have nonzero off-phase bits.',
     'local_constraint_costs':local}
(ROOT/'research/data/phase_law_diagnostics.json').write_text(json.dumps(out,indent=2)+'\n')
print('Dominant phases',out['dominant_phases'],'conditional reference',out['exact_conditional_phase_reference'])
print('Residual ones per block',out['residual_ones_per_block'])
for model in local:print(model['model'],[(v['block_1based'],v['ratio'],v['changed_nodes']) for v in model['blocks']])
