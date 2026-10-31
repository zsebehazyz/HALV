#!/usr/bin/env python3
"""Explicit five-sample Base58 families; reject range errors, never reduce modulo 58."""
import itertools
import json
from collections import Counter
from pathlib import Path
from bitcoin_oracle import ALPHABET, ORDER, TARGET, addresses, b58decode, b58encode, sha256, selftest

ROOT=Path(__file__).resolve().parents[1]

def decode_wif(text):
    if len(text) not in (51,52): return None,'length'
    try: raw=b58decode(text)
    except ValueError: return None,'alphabet'
    if len(raw) not in (37,38): return None,'decoded_length'
    payload, checksum=raw[:-4],raw[-4:]
    if sha256(sha256(payload))[:4]!=checksum: return None,'checksum'
    if payload[0]!=0x80: return None,'version'
    compressed=len(payload)==34
    if compressed and payload[-1]!=1: return None,'compression_marker'
    key=payload[1:33]
    if not 0<int.from_bytes(key,'big')<ORDER: return None,'scalar_range'
    return {'key':key,'compressed':compressed},'valid'

def encode_payload(payload):
    return b58encode(payload+sha256(sha256(payload))[:4])

def wif_selftest():
    tests=0
    one=(1).to_bytes(32,'big')
    for text,compressed in [
        ('5HpHagT65TZzG1PH3CSu63k8DbpvD8s5ip4nEB3kEsreAnchuDf',False),
        ('KwDiBf89QgGbjEhKnhXJuH7LrciVrZi3qYjgd9M7rFU73sVHnoWn',True)]:
        result,reason=decode_wif(text)
        if reason!='valid' or result!={'key':one,'compressed':compressed}:
            raise RuntimeError('Known scalar-1 WIF failed')
        tests+=1
        damaged=text[:-1]+('1' if text[-1]!='1' else '2')
        if decode_wif(damaged)[1]!='checksum': raise RuntimeError('Checksum mutation accepted')
        tests+=1
    for payload in [b'\x81'+one,b'\x80'+one+b'\x02',b'\x80'+bytes(32),b'\x80'+ORDER.to_bytes(32,'big')]:
        if decode_wif(encode_payload(payload))[0] is not None:
            raise RuntimeError('Invalid WIF payload accepted')
        tests+=1
    if decode_wif('0'*51)[1]!='alphabet': raise RuntimeError('Invalid alphabet accepted')
    tests+=1
    return {'cases_passed':tests,'known_vectors':'scalar 1, uncompressed and compressed',
            'negative_cases':'mutated checksum, version, compression marker, scalar zero/order, forbidden alphabet'}

def main():
    verification={'address_oracle':selftest(),'wif_decoder':wif_selftest()}
    data=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    f=next(f for f in data['fits'] if f['start_x']==92 and f['step_px']==3
           and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1)
    q=f['states']
    families={name:{'hypotheses':0,'rejections':Counter(),'minimum_out_of_range_groups':51,
                    'unique_in_range_strings':set(),'prefix_5_count':0}
              for name in ['five_base4_digits','five_binary_digits']}
    accepted=[]
    evidence=[]
    def examine(values,name,label):
        stats=families[name];stats['hypotheses']+=1
        bad=sum(not 0<=v<58 for v in values)
        stats['minimum_out_of_range_groups']=min(stats['minimum_out_of_range_groups'],bad)
        evidence.append((name,label,values))
        if bad:
            stats['rejections']['digit_out_of_range']+=1;return
        text=''.join(ALPHABET[v] for v in values)
        stats['unique_in_range_strings'].add(text)
        if text[0]=='5': stats['prefix_5_count']+=1
        result,reason=decode_wif(text)
        stats['rejections'][reason]+=1
        if result:
            aa=addresses(result['key'])
            accepted.append({'family':name,'label':label,'wif':text,
                             'addresses':aa,'matches_target':TARGET in aa.values()})
    for reverse in [False,True]:
        seq=q[::-1] if reverse else q
        for offset in [0,1]:
            groups=[seq[offset+5*i:offset+5*i+5] for i in range(51)]
            for little in [False,True]:
                ordered=[g[::-1] if little else g for g in groups]
                base=f'reverse={reverse}/offset={offset}/little={little}'
                for perm in itertools.permutations(range(4)):
                    values=[]
                    for g in ordered:
                        value=0
                        for state in g:value=4*value+perm[state]
                        values.append(value)
                    for index_base in [0,1]:
                        examine([v-index_base for v in values],'five_base4_digits',
                                base+'/perm='+''.join(map(str,perm))+'/index_base='+str(index_base))
                for mask in range(1,15):
                    values=[]
                    for g in ordered:
                        value=0
                        for state in g:value=2*value+((mask>>state)&1)
                        values.append(value)
                    examine(values,'five_binary_digits',base+'/mask='+str(mask))
    for stats in families.values():
        stats['unique_in_range_strings']=len(stats['unique_in_range_strings'])
        stats['rejections']=dict(stats['rejections'])
    # A nonzero run of fitted states is not assumed to be the same as a visual lobe.
    run_count=sum(v!=0 and (i==0 or q[i-1]==0) for i,v in enumerate(q))
    result={'image_sha256':data['sha256'],'selftests':verification,
            'samples':len(q),'groups':51,'samples_per_group':5,'unused_samples':1,
            'assumptions':'Contiguous noncyclic groups; discard first or last sample; both directions and within-group endianness. Four-state bijections or nonconstant boolean projections only. No modulo, clipping, offsets beyond explicit 0/1 indexing, substitution cipher, or error repair.',
            'families':families,'valid_wifs':accepted,
            'target_matches':sum(r['matches_target'] for r in accepted),
            'hypothesis_set_sha256':sha256(json.dumps(evidence,separators=(',',':')).encode()).hex(),
            'nonzero_runs_in_fitted_states':run_count,
            'limitation':'A negative excludes only this explicit mapping family on this reconstruction, not all WIF encodings or alternate sample reconstructions.'}
    (ROOT/'research/data/five_sample_wif_check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
