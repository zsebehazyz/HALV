#!/usr/bin/env python3
"""C36: reversible full512-bit phase/ASCII flag hypotheses with strict gates."""
import gzip
import hashlib
import itertools
import json
from collections import Counter
import numpy as np
from residual_channels import ROOT,nominal_states
from bitcoin_oracle import ORDER,TARGET,addresses,selftest

HEX=set('0123456789abcdefABCDEF')


def flag_decode(words,position,use_flag,complement):
    flag=words[:,position];data=np.delete(words,position,axis=1)
    result=data^(flag[:,None] if use_flag else 0)^complement
    restored=result^(flag[:,None] if use_flag else 0)^complement
    restored=np.insert(restored,position,flag,axis=1)
    assert np.array_equal(restored,words)
    values=result@np.array([64,32,16,8,4,2,1])
    return ''.join(chr(int(v)) for v in values),flag


def calibrate():
    text=f'{1:064x}';data=np.array([[(ord(c)>>k)&1 for k in range(6,-1,-1)] for c in text])
    flags=np.arange(64)%2;count=0
    for position,use_flag,complement in itertools.product(range(8),[False,True],[0,1]):
        encoded=data^(flags[:,None] if use_flag else 0)^complement
        words=np.insert(encoded,position,flags,axis=1)
        recovered,_=flag_decode(words,position,use_flag,complement)
        assert recovered==text;count+=1
    return {'synthetic64hex_flag_roundtrips':count,'oracle':selftest()}


def main():
    spec=json.loads((ROOT/'research/models/phase_ascii_generator_v1.json').read_text());tests=calibrate()
    q=nominal_states().reshape(8,32);views=[];scales=128//2**np.arange(8)
    for name in spec['phase_views']:
        x=q.copy()
        for b in range(8):
            phase=(2-b)%4
            if name=='signature_phase_inside_each_quad':x[b]=np.roll(x[b].reshape(8,4),-phase,axis=1).flatten()
            elif name=='signature_phase_whole_block':x[b]=np.roll(x[b],-phase)
            elif name=='C25_equivalent_phase_whole_block':x[b]=np.roll(x[b],-int((2*scales[b])//3-5*b))
        restored=x.copy()
        for b in range(8):
            phase=(2-b)%4
            if name=='signature_phase_inside_each_quad':restored[b]=np.roll(restored[b].reshape(8,4),phase,axis=1).flatten()
            elif name=='signature_phase_whole_block':restored[b]=np.roll(restored[b],phase)
            elif name=='C25_equivalent_phase_whole_block':restored[b]=np.roll(restored[b],int((2*scales[b])//3-5*b))
        assert np.array_equal(restored,q)
        views.append((name,x.flatten()))
    counts=Counter();hist=Counter();complete=[];keys={};best=None;roundtrips=0
    path=ROOT/'research/data/phase_ascii_generator_trials.jsonl.gz'
    with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as stream:
        def check(text,recipe,flags=None):
            nonlocal best
            score=sum(c in HEX for c in text);hist[score]+=1;counts[recipe['format']]+=1
            row={**recipe,'hex_characters_out_of64':score}
            if best is None or score>best['hex_characters_out_of64']:best=row.copy()
            if score==64:
                raw=bytes.fromhex(text);row['text']=text
                if flags is not None:row['preserved_flags_hex']=np.packbits(flags).tobytes().hex()
                complete.append(row.copy())
                if 0<int.from_bytes(raw,'big')<ORDER:keys.setdefault(raw,row.copy())
            stream.write((json.dumps(row,separators=(',',':'))+'\n').encode())
        for name,original in views:
            for reverse in [False,True]:
                seq=original[::-1] if reverse else original
                for permutation in itertools.permutations(range(4)):
                    p=np.array(permutation);symbols=p[seq].reshape(64,4)
                    inv=np.argsort(p)
                    for layout in spec['byte_layouts']:
                        if layout=='interleaved_2bits_per_sample':
                            words=np.stack([symbols>>1,symbols&1],axis=2).reshape(64,8)
                            back=2*words[:,::2]+words[:,1::2]
                        else:
                            words=np.c_[symbols>>1,symbols&1];back=2*words[:,:4]+words[:,4:]
                        assert np.array_equal(inv[back].flatten(),seq)
                        base={'phase_view':name,'reverse_samples':reverse,'state_permutation':permutation,'byte_layout':layout}
                        raw=(words@np.array([128,64,32,16,8,4,2,1])).tolist()
                        check(''.join(chr(v) for v in raw),{**base,'format':'direct8bit_ASCII_hex'})
                        for position,use_flag,complement in itertools.product(range(8),[False,True],[0,1]):
                            text,flags=flag_decode(words,position,use_flag,complement);roundtrips+=1
                            check(text,{**base,'format':'ASCII7_plus_flag','flag_position':position,
                                        'xor_flag':use_flag,'complement':complement},flags)
    matches=[]
    for key,recipe in keys.items():
        for fmt,address in addresses(key).items():
            if address==TARGET:matches.append({'key_hex':key.hex(),'format':fmt,'recipe':recipe})
    files=['research/models/phase_ascii_generator_v1.json','research/data/pixel_measurements.json',
           'research/data/lag2_halving_check.json','tools/check_phase_ascii_generator.py','tools/residual_channels.py','tools/bitcoin_oracle.py']
    out={'model':'C36','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
         'calibration':tests,'format_trials':dict(counts),'all_trials':sum(counts.values()),
         'full512bit_flag_roundtrips':roundtrips,'phase_views_inverted_exactly':len(views),'histogram':dict(sorted(hist.items())),
         'best_diagnostic_not_near_solution':best,'complete_hex_readings':complete,'unique_valid_scalars':len(keys),
         'public_key_formats':2,'matches':matches,'trial_log':str(path.relative_to(ROOT)),
         'trial_log_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'limitations':spec['limitations']}
    (ROOT/'research/data/phase_ascii_generator_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['model','format_trials','all_trials','full512bit_flag_roundtrips',
                                       'best_diagnostic_not_near_solution','unique_valid_scalars','matches']},indent=2))


if __name__=='__main__':main()
