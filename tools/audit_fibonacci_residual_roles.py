#!/usr/bin/env python3
"""Independent C45 masks and C46 inverse, with no measured sidechannel input."""
import hashlib
import json
from collections import Counter
from residual_channels import ROOT
from audit_fibonacci_vlc import independent


def fib_encode(n):
    weights=[1,2]
    while weights[-1]<=n:weights.append(weights[-1]+weights[-2])
    index=len(weights)-2;chosen=set()
    for i in range(index,-1,-1):
        if n>=weights[i]:chosen.add(i);n-=weights[i]
    assert n==0
    return ''.join('1' if i in chosen else '0' for i in range(index+1))+'1'


def undo(values,row):
    seq=''.join(fib_encode(v) for v in values)
    if row['complement']:seq=''.join(str(1-int(b)) for b in seq)
    if row['reverse_bits']:seq=seq[::-1]
    assert len(seq)==512
    layout=row['layout']
    if layout=='A_then_R':aa,rr=seq[:256],seq[256:]
    elif layout=='R_then_A':rr,aa=seq[:256],seq[256:]
    elif layout=='cellwise':
        aa=''.join(seq[i:i+4] for i in range(0,512,8))
        rr=''.join(seq[i+4:i+8] for i in range(0,512,8))
    elif layout=='bitwise':aa,rr=seq[::2],seq[1::2]
    a=[int(aa[i:i+4],2) for i in range(0,256,4)]
    r=[int(rr[i:i+4],2) for i in range(0,256,4)]
    running=0;previous=0;recovered=[]
    for av,rv in zip(a,r):
        kind=row['transform']
        if kind=='xor_R':av^=rv
        elif kind=='running_xor_R':running^=rv;av^=running
        elif kind=='rotate_R':
            for _ in range(rv%4):av=(av>>1)|((av&1)<<3)
        elif kind=='difference_A':av=(previous+av)%16;previous=av
        recovered.append(av)
    a=[[int(c) for c in format(v,'04b')] for v in recovered]
    r=[[int(c) for c in format(v,'04b')] for v in r]
    q=[]
    for cell,(ab,rb) in enumerate(zip(a,r)):
        z=(3-cell//8)%4;odd=(z-1)%4
        hp=([p for p in range(4) if p!=z] if row['frame']=='absolute' else [odd,(odd+2)%4,(odd+3)%4])
        lp=([p for p in range(4) if p!=odd] if row['frame']=='absolute' else [z,(z+1)%4,(z+2)%4])
        h=[0]*4;l=[0]*4;h[z]=rb[0];l[odd]=ab[3]
        for p,bit in zip(hp,ab[:3]):h[p]=bit
        for p,bit in zip(lp,rb[1:]):l[p]=bit
        q.extend(2*x+y for x,y in zip(h,l))
    return q,''.join(str(b) for row in r for b in row)


def channels(q,frame):
    a=[];r=[]
    for cell in range(64):
        values=q[4*cell:4*cell+4];z=(3-cell//8)%4;odd=(z-1)%4
        hp=[i for i in range(4) if i!=z] if frame=='absolute' else [odd,(odd+2)%4,(odd+3)%4]
        lp=[i for i in range(4) if i!=odd] if frame=='absolute' else [z,(z+1)%4,(z+2)%4]
        a.extend([values[i]//2 for i in hp]+[values[odd]%2])
        r.extend([values[z]//2]+[values[i]%2 for i in lp])
    return ''.join(map(str,a)),''.join(map(str,r))


def main():
    data=json.loads((ROOT/'research/data/fibonacci_residual_roles_check.json').read_text())
    for name,digest in data['input_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    assert hashlib.sha256(bytes(data['q'])).hexdigest()==data['q_sha256']
    inverse_count=0;complete_by_transform=Counter()
    for row in data['coupled_rows']:
        values,spans,tail=independent(row['bits'])
        assert values==row['values'] and spans==row['word_spans'] and tail==row['unfinished_suffix']
        assert row['complete']==(tail=='')
        if row['complete']:
            q,r=undo(values,row)
            assert q==data['q']==row['recovered_q']
            assert r==row['recovered_R']==channels(q,row['frame'])[1]
            assert hashlib.sha256(bytes(q)).hexdigest()==row['recovered_q_sha256']
            assert hashlib.sha256(r.encode()).hexdigest()==row['recovered_R_sha256']
            assert not any(all(0<=v-s<=255 for v in values) for s in [0,1])
            boundaries=([32*i for i in range(1,16) if i!=8] if row['layout'] in ['A_then_R','R_then_A'] else [64*i for i in range(1,8)])
            crossing=[{'span':[lo,hi],'boundaries':[b for b in boundaries if lo<b<hi]} for lo,hi in spans if any(lo<b<hi for b in boundaries)]
            assert crossing==row['cross_block_words']
            inverse_count+=1;complete_by_transform[row['transform']]+=1
        else:assert not row['roundtrip_verified']
    for row in data['residual_roles']:
        a,r=channels(data['q'],row['frame'])
        if row['reverse_bits']:a,r=a[::-1],r[::-1]
        state=0;seq=[]
        for av,rv in zip(a,r):
            if row['mode']=='toggle_before':state^=int(rv)
            seq.append(str(int(av)^state))
            if row['mode']=='toggle_after':state^=int(rv)
        seq=''.join(seq)
        if row['complement_stream']:seq=''.join(str(1-int(b)) for b in seq)
        vals,spans,tail=independent(seq);mask=[int(row['complement_mask'])]*256
        for lo,hi in spans:
            locations=([lo] if row['mask']=='start' else [hi-1] if row['mask']=='end' else [hi-2,hi-1])
            for pos in locations:mask[pos]^=1
        predicted=''.join(map(str,mask));mismatch=[i for i,(x,y) in enumerate(zip(predicted,r)) if x!=y]
        assert predicted==row['predicted_R'] and r==row['actual_R']
        assert mismatch==row['mismatch_positions'] and len(mismatch)==row['mismatch_count']
        assert bool(not mismatch and not tail)==row['joint_gate']
    assert inverse_count==data['roundtrips_verified']
    assert dict(complete_by_transform)==data['coupled_summary']['complete_by_transform']
    out={'models':['C45','C46'],'independently_audited_boundary_recipes':len(data['residual_roles']),
         'independently_parsed_joint_recipes':len(data['coupled_rows']),
         'full256sample_and256residual_bit_inverse_paths':inverse_count,
         'no_original_q_or_R_passed_to_inverse_function':True,
         'no_tail_used_for_incomplete_inverse':True,
         'all_input_hashes_verified':True,
         'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                        ['research/data/fibonacci_residual_roles_check.json','tools/audit_fibonacci_residual_roles.py','tools/audit_fibonacci_vlc.py']}}
    (ROOT/'research/data/fibonacci_residual_roles_integrity.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
