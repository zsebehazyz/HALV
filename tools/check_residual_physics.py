#!/usr/bin/env python3
"""C23: wave-only pixel prediction, exact geometry and conditional delta tests."""
import hashlib
import json
import re
from collections import defaultdict
from fractions import Fraction as F
import numpy as np
from PIL import Image
from residual_channels import ROOT,nominal_states,extract,restore,nibble_values,edge_residual
from analyze_parity_phase import solve
from check_fractional_area import integrate

def image_costs(image,offset,width,crop_tail):
    out=np.empty((255,4,4));scales=128/2.**(np.arange(256)//32)
    for i in range(255):
        x=92+3*i+offset;lo,hi=(450,501) if crop_tail and x>=764 else (85,866)
        yy=np.arange(lo,hi);obs=image[lo:hi,x]/255
        for u in range(4):
            for v in range(4):
                start=u*scales[i];slope=(v*scales[i+1]-start)/3;amplitude=start+slope*offset
                d=np.minimum(abs(yy-(475-amplitude)),abs(yy-(475+amplitude)))/np.sqrt(1+slope*slope)
                pred=np.interp(d/width,[0,1,2,3],[1,113/255,20/255,0]);out[i,u,v]=np.mean((obs-pred)**2)
    return out

def allowed(blocks):
    mask=np.ones((256,4),bool)
    for b in blocks:
        z=(3-b)%4;r=(z-1)%4
        for j in range(32):
            if j%4==z:mask[32*b+j,1:]=False
            elif j%4!=r:mask[32*b+j,[1,3]]=False
    return mask

def main():
    spec=json.loads((ROOT/'research/models/residual_physics_v1.json').read_text())
    states=nominal_states();q=states.flatten();image=np.array(Image.open(ROOT/'research/sources/cryptoHALV.png'),float)
    within=(np.arange(255)+1)%32!=0;index=np.flatnonzero(within)
    conditions={'free':[],'full_R_zero_in_block1':[0],'full_R_zero_in_block2':[1],
                'full_R_zero_in_block8':[7],'full_R_zero_everywhere':list(range(8))}
    pixel_runs=[]
    for width in [.85,1,1.15]:
        for cropped in [False,True]:
            c1=image_costs(image,1,width,cropped);c2=image_costs(image,2,width,cropped)
            for train,test,offset in [(c1,c2,1),(c2,c1,2)]:
                training=train.copy();training[~within]=0
                free,_=solve(training);free_errors=test[index,free[:-1][index],free[1:][index]]
                if width==1:assert np.array_equal(free,q)
                rows=[]
                for name,restricted_blocks in conditions.items():
                    fitted,_=solve(training,allowed(restricted_blocks));errors=test[index,fitted[:-1][index],fitted[1:][index]]
                    byblock=[]
                    for b in range(8):
                        pick=(index//32)==b;baseline=float(np.mean(free_errors[pick]));mse=float(np.mean(errors[pick]))
                        byblock.append({'block_1based':b+1,'free_validation_mse':baseline,'constrained_validation_mse':mse,
                            'ratio_to_free':mse/baseline if baseline else None,'difference':mse-baseline,
                            'changed_nodes_from_free':np.flatnonzero(fitted[32*b:32*b+32]!=free[32*b:32*b+32]).tolist()})
                    rows.append({'constraint':name,'states':fitted.tolist(),'blocks':byblock})
                _,free_res=extract(free.reshape(64,4),'phase_relative')
                pixel_runs.append({'width':width,'roi':'wave_only_tail' if cropped else 'legacy',
                    'fit_offset':offset,'validation_offset':3-offset,'columns_in_each_set':248,
                    'free_state_changes_from_nominal':np.flatnonzero(free!=q).tolist(),
                    'free_residual_phase_relative_hex':edge_residual(free_res).hex(),'constraints':rows})
    a,res=extract(states,'phase_relative');base=restore(a,np.zeros_like(res),'phase_relative').flatten()
    difference=q-base;assert np.all(difference>=0)
    corrections=[]
    for domain in ['normalized','physical']:
        scale=[F(1) if domain=='normalized' else F(128,2**(i//32)) for i in range(256)]
        full=[F(v,2)*s for v,s in zip(q,scale)];baseline=[F(v,2)*s for v,s in zip(base,scale)]
        extra=[F(v,2)*s for v,s in zip(difference,scale)]
        fields=[]
        for values in [full,baseline,extra]:fields.append([integrate(values,92+12*i,92+12*(i+1)) for i in range(64)])
        assert all(x==y+z for x,y,z in zip(*fields))
        corrections.append({'domain':domain,'cells_with_nonzero_correction':sum(v!=0 for v in fields[2]),
                            'radius_area_corrections_exact':[str(v) for v in fields[2]],
                            'correction_sum_exact':str(sum(fields[2]))})
    ff=(ROOT/'research/sources/ffmpeg_8svx.c').read_text()
    tables={name:[int(x) for x in re.search(r'\b'+name+r'\[16\]\s*=\s*\{([^}]+)\}',ff).group(1).split(',')]
            for name in ['fibonacci','exponential']}
    audio={}
    for frame in ['absolute','phase_relative']:
        aa,rr=extract(states,frame);values=nibble_values(aa);codes=nibble_values(rr);groups=defaultdict(list)
        for i in range(1,64):
            if 0<values[i]<15:groups[int(codes[i])].append({'cell':i,'previous':int(values[i-1]),'current':int(values[i]),'delta':int(values[i]-values[i-1])})
        conflicts={str(code):rows for code,rows in groups.items() if len({r['delta'] for r in rows})>1}
        tests=[]
        for name,table in tables.items():
            for xor in [0,8]:
                for clip in [15,255]:
                    predicted=np.clip(values[:-1]+np.array([table[int(c)^xor] for c in codes[1:]]),0,clip)
                    tests.append({'table':name,'index_xor':xor,'clip_max':clip,'samples':63,
                                  'exact_one_step_samples':int(sum(predicted==values[1:])),
                                  'all_exact':bool(np.array_equal(predicted,values[1:]))})
        audio[frame]={'fixed_delta_lookup_interior_conflicts':conflicts,'standard_table_tests':tests}
    files=['research/sources/cryptoHALV.png','research/data/pixel_measurements.json','research/sources/ffmpeg_8svx.c',
           'research/models/residual_physics_v1.json','tools/residual_channels.py','tools/check_residual_physics.py',
           'tools/analyze_parity_phase.py','tools/check_fractional_area.py']
    out={'model':'C23','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
         'pixel_runs':pixel_runs,'geometric_half_state_correction_counts':{'half_unit_nodes':int(sum(difference==1)),
                       'whole_unit_nodes':int(sum(difference==2))},
         'exact_area_corrections':corrections,'audio':audio,'no_private_key_search':True,'limitations':spec['limitations']}
    (ROOT/'research/data/residual_physics_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print('C23: area corrections',[(v['domain'],v['cells_with_nonzero_correction'],v['correction_sum_exact']) for v in corrections])
    for run in pixel_runs:
        if run['width']!=1 or run['fit_offset']!=1:continue
        print(run['roi'])
        all_zero=next(r for r in run['constraints'] if r['constraint']=='full_R_zero_everywhere')
        for row in all_zero['blocks']:
            if row['block_1based'] in [1,2,8]:print(row)
    print('Direct delta lookup contradiction groups:',{k:list(v['fixed_delta_lookup_interior_conflicts']) for k,v in audio.items()})

if __name__=='__main__':main()
