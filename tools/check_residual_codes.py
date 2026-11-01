#!/usr/bin/env python3
"""C22: exact12byte predictions, with independently checked coding primitives."""
import hashlib
import itertools
import json
import zlib
import numpy as np
from residual_channels import ROOT,nominal_states,extract,edge_residual,packed

def gf_mul(a,b,prim):
    value=0
    while b:
        if b&1:value^=a
        b>>=1;a<<=1
        if a&256:a^=prim
    return value

def gf_pow(a,n,prim):
    v=1
    for _ in range(n):v=gf_mul(v,a,prim)
    return v

def rs_parity(data,prim,generator,first_root,nsym=12):
    polynomial=[1]
    for root in range(first_root,first_root+nsym):
        factor=gf_pow(generator,root,prim);product=[0]*(len(polynomial)+1)
        for i,v in enumerate(polynomial):product[i]^=v;product[i+1]^=gf_mul(v,factor,prim)
        polynomial=product
    out=list(data)+[0]*nsym
    for i in range(len(data)):
        coefficient=out[i]
        if coefficient:
            for j in range(1,len(polynomial)):out[i+j]^=gf_mul(polynomial[j],coefficient,prim)
    return bytes(out[-nsym:])

def crc(data,poly,reflected=False,xorout=0xffffffff):
    value=0xffffffff
    for byte in data:
        if reflected:
            value^=byte
            for _ in range(8):value=(value>>1)^poly if value&1 else value>>1
        else:
            value^=byte<<24
            for _ in range(8):value=((value<<1)^poly)&0xffffffff if value&0x80000000 else (value<<1)&0xffffffff
    return value^xorout

CHECKS={'CRC32_IEEE':lambda d:zlib.crc32(d),
        'CRC32_CASTAGNOLI':lambda d:crc(d,0x82f63b78,True),
        'CRC32_BZIP2':lambda d:crc(d,0x04c11db7),
        'CRC32_MPEG2':lambda d:crc(d,0x04c11db7,xorout=0),
        'ADLER32':lambda d:zlib.adler32(d)}

def views(bits):
    result={};nblocks=len(bits)//8
    for perm in itertools.permutations(range(4)):
        for cells_reverse,bits_reverse,blocks_reverse in itertools.product([False,True],repeat=3):
            parts=[]
            for b in range(nblocks):
                cells=bits[8*b:8*b+8];cells=cells[::-1] if cells_reverse else cells
                bb=cells[:,perm].flatten();parts.append(bb[::-1] if bits_reverse else bb)
            stream=np.concatenate(parts[::-1] if blocks_reverse else parts)
            raw=int(''.join(map(str,stream)),2).to_bytes(len(stream)//8,'big')
            result.setdefault(raw,{'permutation':perm,'reverse_cells':cells_reverse,'reverse_word_bits':bits_reverse,'reverse_blocks':blocks_reverse})
    return result

def berlekamp_massey(seq):
    n=len(seq);c=[1]+[0]*n;b=[1]+[0]*n;length=0;shift=1
    for k in range(n):
        discrepancy=seq[k]
        for i in range(1,length+1):discrepancy^=c[i]&seq[k-i]
        if not discrepancy:shift+=1;continue
        previous=c.copy()
        for j in range(n+1-shift):c[j+shift]^=b[j]
        if 2*length<=k:length=k+1-length;b=previous;shift=1
        else:shift+=1
    return c[:length+1]

def recurrence_predict(prefix,polynomial,count):
    result=list(prefix)
    for _ in range(count):
        value=0
        for i in range(1,len(polynomial)):value^=polynomial[i]&result[-i]
        result.append(value)
    return result[-count:]

def selftest():
    reference=json.loads((ROOT/'research/sources/rs_reference_vectors.json').read_text())
    for row in reference['vectors']:
        actual=rs_parity(bytes.fromhex(row['data_hex']),row['field_polynomial'],row['generator'],row['first_root'])
        assert actual.hex()==row['parity_hex']
    expected=[0xcbf43926,0xe3069283,0xfc891918,0x0376e6e7,0x091e01de]
    for (name,fn),value in zip(CHECKS.items(),expected):assert fn(b'123456789')==value,name
    sequence=[1,0,0]
    for i in range(3,56):sequence.append(sequence[i-1]^sequence[i-3])
    poly=berlekamp_massey(sequence[:28]);assert poly==[1,1,0,1]
    assert recurrence_predict(sequence[:28],poly,28)==sequence[28:]
    assert berlekamp_massey([0]*32)==[1]
    return {'independent_rs_vectors':len(reference['vectors']),'standard_checksum_vectors':5,'binary_recurrence_tests':2}

def main():
    spec=json.loads((ROOT/'research/models/residual_codes_v1.json').read_text());validation=selftest();states=nominal_states()
    results={}
    for frame in spec['frames']:
        a,res=extract(states,frame);av=views(a);edge=res.reshape(8,8,4)[[0,1,7]].reshape(24,4);rv=views(edge)
        rs_matches=[];checksum_matches=[];rs_predictions=[];checksum_predictions=[]
        for raw,view in av.items():
            for prim,generator in spec['reed_solomon']['field_variants']:
                for fcr in spec['reed_solomon']['first_roots']:
                    parity=rs_parity(raw,prim,generator,fcr);rs_predictions.append(parity)
                    if parity in rv:rs_matches.append({'primary_view':view,'residual_view':rv[parity],'prim':prim,'generator':generator,'first_root':fcr})
            words=[raw[i:i+4] for i in range(0,32,4)]
            banks={'edge_words':[words[i] for i in [0,1,7]],'halves_and_whole':[raw[:16],raw[16:],raw],
                   'edge_middle_whole':[b''.join(words[i] for i in [0,1,7]),b''.join(words[2:7]),raw]}
            for algorithm,fn in CHECKS.items():
                for name,parts in banks.items():
                    values=[fn(part) for part in parts]
                    for order in ['big','little']:
                        parity=b''.join(v.to_bytes(4,order) for v in values);checksum_predictions.append(parity)
                        if parity in rv:checksum_matches.append({'primary_view':view,'residual_view':rv[parity],'algorithm':algorithm,'bank':name,'word_byte_order':order})
        residual=edge_residual(res);fib=[];binary=[]
        for order in ['big','little']:
            fields=[int.from_bytes(residual[i:i+4],order) for i in range(0,12,4)]
            for target_index in [2,7]:
                first,second=fields[:2]
                for _ in range(2,target_index+1):first,second=second,(first+second)&0xffffffff
                fib.append({'word_byte_order':order,'predicted_index':target_index,'training_fields':fields[:2],
                            'actual_third_field':fields[2],'predicted_field':second,'exact':second==fields[2]})
        for reverse_bytes in [False,True]:
            data=residual[::-1] if reverse_bytes else residual
            for reverse_bits in [False,True]:
                bits=[(v>>i)&1 for v in data for i in (range(8) if reverse_bits else range(7,-1,-1))]
                poly=berlekamp_massey(bits[:64]);prediction=recurrence_predict(bits[:64],poly,32)
                binary.append({'reverse_bytes':reverse_bytes,'lsb_first':reverse_bits,'degree':len(poly)-1,'is_short_degree_le16':len(poly)<=17,
                               'polynomial':poly,'heldout32_bits_correct':sum(a==b for a,b in zip(prediction,bits[64:])),
                               'heldout32_exact':prediction==bits[64:],'predicted32_bit_string':''.join(map(str,prediction))})
        results[frame]={'primary_views':len(av),'residual_views':len(rv),
            'rs':{'predictions':len(rs_predictions),'full_packet_comparisons':len(rs_predictions)*len(rv),'matches':rs_matches,
                  'prediction_set_sha256':hashlib.sha256(b''.join(sorted(set(rs_predictions)))).hexdigest()},
            'checksum_banks':{'predictions':len(checksum_predictions),'full_packet_comparisons':len(checksum_predictions)*len(rv),'matches':checksum_matches,
                  'prediction_set_sha256':hashlib.sha256(b''.join(sorted(set(checksum_predictions)))).hexdigest()},
            'fibonacci_word_predictions':fib,'binary_fibonacci_predictions':binary}
    files=['research/data/pixel_measurements.json','research/models/residual_codes_v1.json','research/sources/rs_reference_vectors.json',
           'tools/residual_channels.py','tools/check_residual_codes.py']
    out={'model':'C22','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
         'primitive_validation':validation,'frames':results,'no_private_key_search':True,'limitations':spec['limitations']}
    (ROOT/'research/data/residual_codes_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'model':'C22','primitive_validation':validation,'frames':{k:{'views':[v['primary_views'],v['residual_views']],
          'rs_comparisons':v['rs']['full_packet_comparisons'],'rs_matches':len(v['rs']['matches']),
          'checksum_comparisons':v['checksum_banks']['full_packet_comparisons'],'checksum_matches':len(v['checksum_banks']['matches']),
          'fibonacci_matches':sum(r['exact'] for r in v['fibonacci_word_predictions']),
          'binary_degrees':[r['degree'] for r in v['binary_fibonacci_predictions']],
          'binary_exact_matches':sum(r['heldout32_exact'] for r in v['binary_fibonacci_predictions'])} for k,v in results.items()}},indent=2))

if __name__=='__main__':main()
