#!/usr/bin/env python3
"""C40: all-seed bare8SVX probes, exact Morse gates and synthetic controls."""
import csv
import hashlib
import itertools
import json
import math
import re
from collections import Counter
import numpy as np
from residual_channels import ROOT,nominal_states

CODES='.- -... -.-. -.. . ..-. --. .... .. .--- -.- .-.. -- -. --- .--. --.- .-. ... - ..- ...- .-- -..- -.-- --.. ----- .---- ..--- ...-- ....- ..... -.... --... ---.. ----.'.split()
ENCODE=dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',CODES));DECODE={v:k for k,v in ENCODE.items()}


def decode(indices,table):
    state=np.arange(256,dtype=int);out=np.empty((256,len(indices)),dtype=np.uint8)
    for i,index in enumerate(indices):
        state=np.clip(state+table[int(index)],0,255);out[:,i]=state
    return out


def strict_morse(mask):
    active=np.flatnonzero(mask)
    if not len(active):return []
    core=mask[active[0]:active[-1]+1];edges=np.r_[0,np.flatnonzero(core[1:]!=core[:-1])+1,len(core)]
    lengths=np.diff(edges);on=lengths[::2];gaps=lengths[1::2]
    if len(on)<8:return []
    found=[]
    for unit in range(1,9):
        if not np.all(np.isin(on,[unit,3*unit])) or not np.all(np.isin(gaps,[unit,3*unit,7*unit])):continue
        marks=['.' if n==unit else '-' for n in on];groups=[marks[0]];word_breaks=[]
        for gap,mark in zip(gaps,marks[1:]):
            if gap>=3*unit:
                if gap==7*unit:word_breaks.append(len(groups))
                groups.append(mark)
            else:groups[-1]+=mark
        if any(g not in DECODE for g in groups) or len(groups)<3:continue
        text=''.join((' ' if i in word_breaks else '')+DECODE[g] for i,g in enumerate(groups))
        found.append({'unit_samples':unit,'text':text,'letters':len(groups),'marks':len(on),
                      'groups':groups,'on_lengths':on.tolist(),'gap_lengths':gaps.tolist(),
                      'trimmed_exterior_silence':[int(active[0]),int(len(mask)-1-active[-1])]})
    return found


def calibration(table):
    levels=[]
    for ci,char in enumerate('SOS'):
        for mi,mark in enumerate(ENCODE[char]):
            levels.extend([149]*(1 if mark=='.' else 3))
            if mi<len(ENCODE[char])-1:levels.append(128)
        if ci<2:levels.extend([128]*3)
    levels=[128]+levels+[128];deltas=np.diff([128]+levels)
    indices=[table.index(int(d)) for d in deltas];decoded=decode(indices,table)[128]
    assert decoded.tolist()==levels
    assert any(r['text']=='SOS' and r['unit_samples']==1 for r in strict_morse(abs(decoded.astype(int)-128)>16))
    assert decode([0,15],table)[0].tolist()==[0,21]
    assert decode([15,9],table)[255].tolist()==[255,255]
    return {'known_SOS_codec_and_Morse_roundtrip':True,'saturation_vectors':2}


def search(q,table,keep_pcm=False):
    masks={};recipes=[];all_pcm=[];emissions=0
    for reverse in [False,True]:
        seq=q[::-1] if reverse else q
        for permutation in itertools.permutations(range(4)):
            dibits=np.array(permutation)[seq].reshape(64,4)
            raw=dibits@np.array([64,16,4,1])
            for order in ['low_first','high_first']:
                paired=np.c_[raw&15,raw>>4] if order=='low_first' else np.c_[raw>>4,raw&15]
                pcm=decode(paired.flatten(),table);rid=len(recipes)
                recipes.append({'reverse_q':reverse,'state_permutation':permutation,'nibble_order':order})
                if keep_pcm:all_pcm.append(pcm)
                for threshold in [0,8,16,32]:
                    activities=abs(pcm.astype(int)-128)>threshold
                    packed=np.packbits(activities,axis=1)
                    unique,first,counts=np.unique(packed,axis=0,return_index=True,return_counts=True)
                    for value,seed,count in zip(unique,first,counts):
                        key=value.tobytes();emissions+=int(count)
                        if key in masks:masks[key]['occurrences']+=int(count)
                        else:masks[key]={'recipe_id':rid,'seed':int(seed),'threshold':threshold,'occurrences':int(count)}
    messages=[]
    for key,witness in masks.items():
        mask=np.unpackbits(np.frombuffer(key,dtype=np.uint8))
        for found in strict_morse(mask):messages.append({**found,'activity_hex':key.hex(),'witness':witness})
    return {'recipes':recipes,'unique_activity_masks':len(masks),'activity_emissions':emissions,
            'messages':messages,'max_message_letters':max((r['letters'] for r in messages),default=0)},all_pcm


def main():
    spec=json.loads((ROOT/'research/models/fibonacci_audio_probe_v1.json').read_text())
    src=(ROOT/'research/sources/ffmpeg_8svx.c').read_text()
    table=[int(x) for x in re.search(r'\bfibonacci\[16\]\s*=\s*\{([^}]+)\}',src).group(1).split(',')]
    tests=calibration(table);q=nominal_states().flatten()
    result,pcms=search(q,table,True)
    pcm_array=np.array(pcms,dtype=np.uint8);assert pcm_array.shape==(96,256,128)
    np.savez_compressed(ROOT/'research/data/fibonacci_pcm128_all_seeds.npz',pcm=pcm_array)
    reference_id=next(i for i,r in enumerate(result['recipes']) if not r['reverse_q'] and r['state_permutation']==(0,1,2,3) and r['nibble_order']=='low_first')
    with (ROOT/'research/data/hypothetical_pcm128_identity_seed128.csv').open('w',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(['sample','unsigned_PCM','centered_PCM','status'])
        writer.writerows([i,int(v),int(v)-128,'hypothetical_decoder_output_not_measured_audio'] for i,v in enumerate(pcm_array[reference_id,128]))
    lookup={value:i for i,value in enumerate(table)}
    identity_indices=[lookup[int(d)] for d in np.diff(np.r_[0,q])]
    identity_pcm=decode(identity_indices,table);assert np.array_equal(identity_pcm[0],q)
    relative=identity_pcm.astype(int)-identity_pcm[:,0,None].astype(int)
    unique,inv=np.unique(relative,axis=0,return_inverse=True)
    groups=[np.flatnonzero(inv==i).tolist() for i in range(len(unique))]
    controls=[]
    if result['messages']:
        rng=np.random.default_rng(401101)
        for i in range(16):
            shuffled=np.concatenate([rng.permutation(b) for b in q.reshape(8,32)])
            ref,_=search(shuffled,table)
            controls.append({'draw':i,'qualified_messages':len(ref['messages']),'max_message_letters':ref['max_message_letters']})
        controls_status='16 same-family conditional q-shuffle controls executed'
    else:controls_status='Skipped per frozen condition: no qualified observed message'
    names=['research/models/fibonacci_audio_probe_v1.json','research/data/pixel_measurements.json',
           'research/sources/ffmpeg_8svx.c','tools/probe_fibonacci_audio.py','tools/residual_channels.py']
    out={'model':'C40','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in names},
         'calibration':tests,'compressed_code_streams':96,'initial_predictors_per_stream':256,
         'decoded_PCM_arrays':96*256,'samples_per_array':128,**result,
         'identity_delta_redecode':{'initial0_recovers_q':True,'DC_relative_classes':len(groups),'seeds_by_class':groups},
         'controls_status':controls_status,'controls':controls,
         'minimum_standard_Morse_samples_for51characters':201,'minimum_for64characters':253,
         'no_private_key_search':True,'limitations':spec['limitations']}
    (ROOT/'research/data/fibonacci_audio_probe_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'model':'C40','decoded_PCM_arrays':96*256,'unique_activity_masks':result['unique_activity_masks'],
                      'qualified_Morse_messages':len(result['messages']),'messages':result['messages'][:6],
                      'DC_relative_identity_classes':len(groups),'controls_status':controls_status},indent=2),flush=True)


if __name__=='__main__':main()
