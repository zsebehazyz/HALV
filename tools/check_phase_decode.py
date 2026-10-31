#!/usr/bin/env python3
"""C13: phase/flag channels plus preserved 64-to-32 and codec-to-pair branches."""
import hashlib
import itertools
import json
import re
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from bitcoin_oracle import ORDER,TARGET,addresses,sha256,selftest

ROOT=Path(__file__).resolve().parents[1]

def views(q):
    yield 'identity',q.copy(),False
    for scope in ['all','middle']:
        for operator in ['quad','block']:
            x=q.reshape(8,32).copy()
            for b in range(8):
                if scope=='middle' and b not in range(2,7):continue
                phase=(2-b)%4
                x[b]=np.roll(x[b],-phase) if operator=='block' else np.roll(x[b].reshape(8,4),-phase,axis=1).flatten()
            yield f'{scope}_{operator}',x.flatten(),scope

def channels(q,scope):
    blocks=q.reshape(8,32);flags=[]
    for b,row in enumerate(blocks):
        aligned=scope=='all' or scope=='middle' and b in range(2,7)
        phase=0 if aligned else (2-b)%4
        flags.extend((row[phase::4]&1).tolist())
    groups=q.reshape(64,4)
    return (groups>>1)@np.array([8,4,2,1]),(groups&1)@np.array([8,4,2,1]),np.array(flags)

def delta_decode(deltas,initials):
    state=np.array(initials,dtype=int);result=np.empty((len(state),len(deltas)),dtype=int)
    for i,delta in enumerate(deltas):
        state=np.clip(state+delta,0,255);result[:,i]=state
    return result

def main():
    p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    q=np.array(next(f['states'] for f in p['fits'] if f['start_x']==92 and f['step_px']==3 and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1))
    audit=json.loads((ROOT/'research/data/parity_phase_check.json').read_text())
    tail=np.array(next(r['states'] for r in audit['constrained_models'] if r['model']=='predicted_middle_and_last'))
    ff=(ROOT/'research/sources/ffmpeg_8svx.c').read_text()
    tables={name:np.array([int(x) for x in re.search(r'\b'+name+r'\[16\]\s*=\s*\{([^}]+)\}',ff).group(1).split(',')]) for name in ['fibonacci','exponential']}
    packed=bytes([0x98,0xf0]);low_first=[n for b in packed for n in [b&15,b>>4]]
    assert delta_decode(tables['fibonacci'][low_first],[128]).tolist()==[[128,129,95,116]]
    assert delta_decode(tables['fibonacci'][[0,15]],[0]).tolist()==[[0,21]]
    assert delta_decode(tables['fibonacci'][[15,9]],[255]).tolist()==[[255,255]]
    verification=selftest();candidates={};attempts=Counter();rejected=Counter();sets=defaultdict(set)
    def add(values,branch,label):
        attempts[branch]+=1
        if len(values)!=32 or np.any(values<0) or np.any(values>255):rejected[branch]+=1;return
        raw=bytes(int(v) for v in values)
        for reverse in [False,True]:
            key=raw[::-1] if reverse else raw
            if not 0<int.from_bytes(key,'big')<ORDER:rejected[branch]+=1;continue
            sets[branch].add(key);candidates.setdefault(key,{'branch':branch,'recipe':label+f'/byte_reverse={reverse}'})
    pair_orders={
        'adjacent':lambda v:(v[::2],v[1::2]),'global_halves':lambda v:(v[:32],v[32:]),
        'block_halves':lambda v:(v.reshape(8,8)[:,:4].flatten(),v.reshape(8,8)[:,4:].flatten()),
        'transpose_adjacent':lambda v:(v.reshape(8,8).T.flatten()[::2],v.reshape(8,8).T.flatten()[1::2])}
    sum_rules={
        'direct':lambda a,b:a+b,'half_floor':lambda a,b:(a+b)//2,'half_ceil':lambda a,b:(a+b+1)//2,
        'half_ties_even':lambda a,b:np.rint((a+b)/2).astype(int),
        'half_each_floor':lambda a,b:a//2+b//2,'half_each_ceil':lambda a,b:(a+1)//2+(b+1)//2,
        'byte_wrap_control':lambda a,b:(a+b)%256}
    nibble_rules={
        'high_only':lambda n,m,f:n,'xor_low':lambda n,m,f:n^m,'add_low':lambda n,m,f:(n+m)%16,
        'subtract_low':lambda n,m,f:(n-m)%16,'complement_flag':lambda n,m,f:n^(15*f),
        'flip_msb_flag':lambda n,m,f:n^(8*f),'flip_lsb_flag':lambda n,m,f:n^f,
        'rotate_left_flag':lambda n,m,f:np.where(f,((n<<1)&15)|(n>>3),n)}
    for source,original in [('nominal',q),('predicted_last_phase',tail)]:
        for view,x,scope in views(original):
            prefix=source+'/'+view
            n,m,f=channels(x,scope)
            for reverse in [False,True]:
                nn,mm,flags=(n[::-1],m[::-1],f[::-1]) if reverse else (n,m,f)
                for bitreverse in [False,True]:
                    lookup=np.array([int(format(i,'04b')[::-1],2) for i in range(16)])
                    h=lookup[nn] if bitreverse else nn;l=lookup[mm] if bitreverse else mm
                    for name,fn in nibble_rules.items():
                        digits=fn(h,l,flags);raw=(16*digits[::2]+digits[1::2])
                        add(raw,'nibble',prefix+f'/reverse={reverse}/nibble_bit_reverse={bitreverse}/'+name)
                # These are hypotheses for the compressed nibble stream, not an actual IFF file.
                for table_name,table in tables.items():
                    for index_rule,indices in [('plain',nn),('xor8_flag',nn^(8*flags)),('xor15_flag',nn^(15*flags))]:
                        for swap in [False,True]:
                            idx=indices.reshape(32,2)[:,::-1].flatten() if swap else indices
                            decoded=delta_decode(table[idx],np.arange(256))
                            for initial,values in enumerate(decoded):
                                for normalizer in ['direct','half_each_floor']:
                                    out=sum_rules[normalizer](values[::2],values[1::2])
                                    add(out,'codec_pair64',prefix+f'/reverse={reverse}/{table_name}/{index_rule}/swap={swap}/seed={initial}/{normalizer}')
                seq=x[::-1] if reverse else x
                for perm in itertools.permutations(range(4)):
                    digits=np.array([perm[v] for v in seq]).reshape(64,4)
                    for quad_reverse in [False,True]:
                        values=(digits[:,::-1] if quad_reverse else digits)@np.array([64,16,4,1])
                        for order,pair in pair_orders.items():
                            a,b=pair(values)
                            for name,fn in sum_rules.items():
                                add(fn(a,b),'pair64',prefix+f'/reverse={reverse}/perm={perm}/quad_reverse={quad_reverse}/{order}/{name}')
    print('Generated',len(candidates),'distinct scalars',dict(attempts),flush=True)
    matches=[]
    for i,(key,label) in enumerate(candidates.items(),1):
        for fmt,address in addresses(key).items():
            if address==TARGET:matches.append({**label,'format':fmt,'key_hex':key.hex()})
        if i%10000==0:print('Checked',i,'of',len(candidates),flush=True)
    files=['research/sources/cryptoHALV.png','research/sources/ffmpeg_8svx.c','research/data/pixel_measurements.json',
           'research/data/parity_phase_check.json','research/models/phase_decode_v1.json','tools/check_phase_decode.py']
    out={'model':'C13','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
         'branches':{b:{'attempts':attempts[b],'invalid_or_range_rejections':rejected[b],'unique_scalars':len(sets[b])} for b in attempts},
         'unique_valid_scalars':len(candidates),'public_key_formats':2,'hash_finalization_used':False,
         'candidate_set_sha256':sha256(b''.join(sorted(candidates))).hex(),'matches':matches,
         'oracle_selftest':verification,'codec_known_answer_tests':3,
         'limitations':json.loads((ROOT/'research/models/phase_decode_v1.json').read_text())['limitations']}
    (ROOT/'research/data/phase_decode_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
