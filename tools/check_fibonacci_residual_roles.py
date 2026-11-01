#!/usr/bin/env python3
"""C45/C46 full residual roles and source-free Fibonacci inverse reconstruction."""
import hashlib
import itertools
import json
from collections import Counter
import numpy as np
from residual_channels import ROOT, nominal_states, extract, restore, nibble_values
from check_fibonacci_vlc import parse, encode, candidates

FRAMES=['absolute','phase_relative']
TRANSFORMS=['identity','xor_R','running_xor_R','rotate_R','difference_A']
LAYOUTS=['A_then_R','R_then_A','cellwise','bitwise']


def bits(array):
    return ''.join(map(str,np.asarray(array).flatten().tolist()))


def nibbles(values):
    return np.array([[(int(v)>>k)&1 for k in [3,2,1,0]] for v in values])


def transform(a,r,kind,inverse=False):
    av=nibble_values(a);rv=nibble_values(r)
    if kind=='identity':return a.copy(),r.copy()
    if kind=='xor_R':av=av^rv
    elif kind=='running_xor_R':av=av^np.bitwise_xor.accumulate(rv)
    elif kind=='difference_A':
        av=(np.cumsum(av)%16) if inverse else ((av-np.r_[0,av[:-1]])%16)
    elif kind=='rotate_R':
        shifts=rv%4
        if inverse:shifts=(-shifts)%4
        av=((av<<shifts)|(av>>(4-shifts)))&15
    else:raise ValueError(kind)
    return nibbles(av),r.copy()


def layout(a,r,kind):
    if kind=='A_then_R':return bits(a)+bits(r)
    if kind=='R_then_A':return bits(r)+bits(a)
    if kind=='cellwise':return bits(np.concatenate([a,r],axis=1))
    if kind=='bitwise':return bits(np.stack([a.flatten(),r.flatten()],axis=1))
    raise ValueError(kind)


def unlayout(seq,kind):
    data=np.array(list(map(int,seq)))
    assert len(data)==512
    if kind=='A_then_R':return data[:256].reshape(64,4),data[256:].reshape(64,4)
    if kind=='R_then_A':return data[256:].reshape(64,4),data[:256].reshape(64,4)
    if kind=='cellwise':
        data=data.reshape(64,8);return data[:,:4],data[:,4:]
    if kind=='bitwise':
        data=data.reshape(256,2);return data[:,0].reshape(64,4),data[:,1].reshape(64,4)
    raise ValueError(kind)


def orient(seq,reverse,complement,inverse=False):
    if reverse:seq=seq[::-1]
    if complement:seq=seq.translate(str.maketrans('01','10'))
    return seq


def reconstruct(values,frame,kind,order,reverse,complement):
    # No measured q/R or unfinished tail is passed into this function.
    seq=''.join(encode(int(v)) for v in values)
    seq=orient(seq,reverse,complement)
    ta,r=unlayout(seq,order)
    a,r=transform(ta,r,kind,inverse=True)
    return restore(a,r,frame),a,r


def boundary_masks(seq):
    values,spans,tail=parse(seq)
    masks={name:np.zeros(len(seq),dtype=int) for name in ['start','end','delimiter_pair']}
    for lo,hi in spans:
        masks['start'][lo]=1;masks['end'][hi-1]=1;masks['delimiter_pair'][hi-2:hi]=1
    return values,spans,tail,masks


def roles(q):
    rows=[]
    for frame in FRAMES:
        a,r=extract(q,frame);original=bits(a);rs=bits(r)
        for reverse,complement in itertools.product([False,True],repeat=2):
            aa=original[::-1] if reverse else original
            rr=rs[::-1] if reverse else rs
            for mode in ['direct','toggle_before','toggle_after']:
                state=0;seq=[]
                for abit,rbit in zip(aa,rr):
                    if mode=='toggle_before':state^=int(rbit)
                    seq.append(str(int(abit)^state))
                    if mode=='toggle_after':state^=int(rbit)
                seq=''.join(seq)
                if complement:seq=seq.translate(str.maketrans('01','10'))
                values,spans,tail,masks=boundary_masks(seq)
                for maskname,mask in masks.items():
                    for invert_mask in [False,True]:
                        predicted=mask^(int(invert_mask));actual=np.array(list(map(int,rr)))
                        mismatch=np.flatnonzero(predicted!=actual).tolist()
                        rows.append({'frame':frame,'reverse_bits':reverse,'complement_stream':complement,
                                     'mode':mode,'mask':maskname,'complement_mask':invert_mask,
                                     'word_count':len(values),'unfinished_suffix':tail,'complete':not tail,
                                     'predicted_R':bits(predicted),'actual_R':rr,'mismatch_positions':mismatch,
                                     'mismatch_count':len(mismatch),'true_positive':int(np.sum((predicted==1)&(actual==1))),
                                     'false_positive':int(np.sum((predicted==1)&(actual==0))),
                                     'false_negative':int(np.sum((predicted==0)&(actual==1))),
                                     'exact_R':not mismatch,'joint_gate':not mismatch and not tail})
    return rows


def coupled(q,record=True):
    rows=[]
    for frame in FRAMES:
        a,r=extract(q,frame)
        for kind,order,reverse,complement in itertools.product(TRANSFORMS,LAYOUTS,[False,True],[False,True]):
            ta,tr=transform(a,r,kind);seq=orient(layout(ta,tr,order),reverse,complement)
            values,spans,tail=parse(seq)
            row={'frame':frame,'transform':kind,'layout':order,'reverse_bits':reverse,'complement':complement,
                 'complete':not tail,'word_count':len(values),'max_value':max(values,default=0)}
            if record:
                row.update(bits=seq,values=values,word_spans=spans,unfinished_suffix=tail,
                           roundtrip_verified=False,candidates=[])
                if not tail:
                    recovered,ra,rr=reconstruct(values,frame,kind,order,reverse,complement)
                    assert np.array_equal(recovered,q) and np.array_equal(ra,a) and np.array_equal(rr,r)
                    row.update(roundtrip_verified=True,recovered_q=recovered.flatten().tolist(),
                               recovered_R=bits(rr),recovered_q_sha256=hashlib.sha256(bytes(recovered.flatten().tolist())).hexdigest(),
                               recovered_R_sha256=hashlib.sha256(bits(rr).encode()).hexdigest())
                    row['candidates']=candidates({'complete':True,'values':values})
                    # Physical block boundaries map through the chosen channel layout.
                    boundaries=([32*i for i in range(1,16) if i!=8] if order in ['A_then_R','R_then_A']
                                else [64*i for i in range(1,8)])
                    row['cross_channel_join_words']=([list(span) for span in spans if span[0]<256<span[1]]
                                                     if order in ['A_then_R','R_then_A'] else [])
                    row['cross_block_words']=[{'span':[lo,hi],'boundaries':[b for b in boundaries if lo<b<hi]}
                                               for lo,hi in spans if any(lo<b<hi for b in boundaries)]
            rows.append(row)
    return rows


def stats(rows):
    done=[r for r in rows if r['complete']]
    return {'recipes':len(rows),'complete':len(done),
            'complete_by_transform':dict(Counter(r['transform'] for r in done)),
            'complete_by_layout':dict(Counter(r['layout'] for r in done)),
            'byte_mappings':sum(all(0<=v-shift<=255 for v in r.get('values',[])) for r in done for shift in [0,1])
                            if all('values' in r for r in done) else None}


def calibrate():
    rng=np.random.default_rng(450046)
    count=0
    for frame in FRAMES:
        for block in range(8):
            q=np.zeros((64,4),dtype=int)
            for cell in itertools.product(range(4),repeat=4):
                q[block*8]=cell
                a,r=extract(q,frame);assert np.array_equal(restore(a,r,frame),q);count+=1
    # All transforms/layouts inverted on arbitrary data (not just measured q).
    for frame,kind,order in itertools.product(FRAMES,TRANSFORMS,LAYOUTS):
        q=rng.integers(0,4,(64,4));a,r=extract(q,frame)
        ta,tr=transform(a,r,kind);seq=layout(ta,tr,order)
        aa,rr=unlayout(seq,order);aa,rr=transform(aa,rr,kind,True)
        assert np.array_equal(restore(aa,rr,frame),q)
    # Synthetic complete512bit Fibonacci message:128x2 and64x1 =>384+128bits.
    values=[2]*128+[1]*64;seq=''.join(encode(v) for v in values);assert len(seq)==512
    synthetic=0
    for frame,kind,order,reverse,complement in itertools.product(FRAMES,TRANSFORMS,LAYOUTS,[False,True],[False,True]):
        q,a,r=reconstruct(values,frame,kind,order,reverse,complement)
        ta,tr=transform(a,r,kind)
        assert orient(layout(ta,tr,order),reverse,complement)==seq
        assert parse(seq)[0]==values
        synthetic+=1
    return {'cell_state_frame_block_roundtrips':count,'random_full_transform_layout_roundtrips':40,
            'synthetic_complete_Fibonacci_full_inverse_paths':synthetic}


def main():
    calibration=calibrate();q=nominal_states();role_rows=roles(q);rows=coupled(q)
    rng=np.random.default_rng(461101);controls=[]
    for draw in range(64):
        shuffled=np.array([rng.permutation(b) for b in q.reshape(8,32)]).reshape(64,4)
        controls.append({'draw':draw,**stats(coupled(shuffled,record=False))})
    names=['research/models/fibonacci_residual_roles_v1.json','research/data/pixel_measurements.json',
           'tools/check_fibonacci_residual_roles.py','tools/check_fibonacci_vlc.py','tools/residual_channels.py','tools/bitcoin_oracle.py']
    out={'models':['C45','C46'],'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in names},
         'calibration':calibration,'q':q.flatten().tolist(),'q_sha256':hashlib.sha256(bytes(q.flatten().tolist())).hexdigest(),
         'residual_role_summary':{'recipes':len(role_rows),'exact_R':sum(r['exact_R'] for r in role_rows),
                                  'joint_gate':sum(r['joint_gate'] for r in role_rows),
                                  'minimum_R_bit_errors':min(r['mismatch_count'] for r in role_rows)},
         'coupled_summary':stats(rows),'roundtrips_verified':sum(r['roundtrip_verified'] for r in rows),
         'candidate_count':sum(len(r['candidates']) for r in rows),
         'target_matches':sum(c['target_match'] for r in rows for c in r['candidates']),
         'residual_roles':role_rows,'coupled_rows':rows,'controls':controls,
         'controls_complete_ge_observed':sum(c['complete']>=stats(rows)['complete'] for c in controls)}
    (ROOT/'research/data/fibonacci_residual_roles_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['input_sha256','q','residual_roles','coupled_rows','controls']},indent=2))

if __name__=='__main__':main()
