#!/usr/bin/env python3
"""C30: complete format gates and exact target checks for the C28-C29 chain."""
import gzip
import hashlib
import time
from collections import Counter,defaultdict
import numpy as np
from cryptography.hazmat.primitives.asymmetric import ec
from ordered_decode_common import *
from bitcoin_oracle import ORDER,TARGET,b58decode,addresses,selftest
from check_five_sample_wif import decode_wif,wif_selftest

BIT_REVERSE=bytes(int(f'{i:08b}'[::-1],2) for i in range(256))
BASE58=set('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz')
HEX=set(b'0123456789abcdefABCDEF')

def key_views(raw):
    for reverse_bytes in [False,True]:
        data=raw[::-1] if reverse_bytes else raw
        for reverse_byte_bits in [False,True]:
            yield (data.translate(BIT_REVERSE) if reverse_byte_bits else data),{'reverse_bytes':reverse_bytes,'reverse_bits_per_byte':reverse_byte_bits}

def packets(case):
    bits,r=bit_arrays(case);main=bytes.fromhex(case['main32_hex']);sidecar=bytes.fromhex(case['outer_residual12_hex'])
    yield 'main_then_sidecar',main+sidecar
    blockwise=bytearray();vv=nibble_values(bits);rr=nibble_values(r)
    for b in range(8):
        if b in [0,1,7]:blockwise.extend(int(16*a+c) for a,c in zip(vv[8*b:8*b+8],rr[8*b:8*b+8]))
        else:
            assert not np.any(r[8*b:8*b+8]);blockwise.extend(packed(bits[8*b:8*b+8]))
    assert len(blockwise)==44;yield 'blockwise_main_residual',bytes(blockwise)

def public_hashes(raw):
    point=ec.derive_private_key(int.from_bytes(raw,'big'),ec.SECP256K1()).public_key().public_numbers()
    x=point.x.to_bytes(32,'big');y=point.y.to_bytes(32,'big')
    return {name:hashlib.new('ripemd160',hashlib.sha256(pub).digest()).digest() for name,pub in [
        ('compressed',bytes([2+(point.y&1)])+x),('uncompressed',b'\x04'+x+y)]}

def main():
    settings=spec();cases=json.loads((ROOT/'research/data/ordered_control_cases.json').read_text())
    payloads=json.loads((ROOT/'research/data/ordered_arithmetic_payloads.json').read_text())
    tests={'address':selftest(),'wif':wif_selftest()}
    one=public_hashes((1).to_bytes(32,'big'))
    assert one['compressed'].hex()=='751e76e8199196d454941c45d1b3a323f1433bd6'
    assert one['uncompressed'].hex()=='91b24bf9f5288532960ac687abb035127b1d28a5'
    registry={};sets=defaultdict(set);invalid=Counter();emissions=Counter();wif_counts=Counter();wif_hist=Counter();valid_wifs=[];hex_counts=Counter()
    def add(raw,label,recipe,orient=True):
        variants=key_views(raw) if orient else [(raw,{})]
        for key,view in variants:
            emissions[label]+=1
            if not 0<int.from_bytes(key,'big')<ORDER:invalid[label]+=1;continue
            sets[label].add(key);registry.setdefault(key,{'stage':label,'recipe':recipe,'key_view':view})
    path=ROOT/'research/data/ordered_format_trials.jsonl.gz'
    with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as log:
        for case in cases:
            cid=case['case_id'];add(bytes.fromhex(case['main32_hex']),'C28_main',{'case_id':cid})
            bits,r=bit_arrays(case);v=nibble_values(bits);rv=nibble_values(r)
            for name,raw in [('main_high',bytes(int(x) for x in 16*v+rv)),('residual_high',bytes(int(x) for x in 16*rv+v))]:
                score=sum(byte in HEX for byte in raw);hex_counts['streams']+=1;hex_counts['max_hex_characters_in64']=max(hex_counts['max_hex_characters_in64'],score)
                row={'format':'ASCII64_hex','case_id':cid,'packing':name,'hex_characters':score}
                if score==64:
                    hex_counts['complete_hex_strings']+=1;add(bytes.fromhex(raw.decode('ascii')),'C30_ASCII_hex',row,False)
                log.write((json.dumps(row,separators=(',',':'))+'\n').encode())
            for layout_name,packet in packets(case):
                rawbits=np.array([(byte>>i)&1 for byte in packet for i in range(7,-1,-1)])
                for reverse_stream in [False,True]:
                    stream=rawbits[::-1] if reverse_stream else rawbits
                    for offset in [0,1,2]:
                        groups=stream[offset:offset+350].reshape(50,7)
                        for little in [False,True]:
                            ordered=groups[:,::-1] if little else groups;values=ordered@np.array([64,32,16,8,4,2,1])
                            text=''.join(chr(v) for v in values);score=sum(c in BASE58 for c in text);wif_hist[score]+=1;wif_counts['ASCII7_trials']+=1
                            row={'format':'ASCII7_WIF50','case_id':cid,'layout':layout_name,'reverse_stream':reverse_stream,
                                 'padding_offset':offset,'reverse_character_bits':little,'base58_characters':score}
                            if score==50:
                                wif_counts['complete_Base58_50']+=1;wif='5'+text;decoded,reason=decode_wif(wif)
                                row.update({'wif':wif,'wif_validation':reason})
                                if decoded:
                                    wif_counts['valid_Base58Check_WIF']+=1;valid_wifs.append(row)
                                    add(decoded['key'],'C30_WIF',row,False)
                            log.write((json.dumps(row,separators=(',',':'))+'\n').encode())
    for row in payloads:add(bytes.fromhex(row['payload32_hex']),'C29_'+row['family'],row)
    print('C30 formed',len(registry),'unique valid scalars; WIF gates',dict(wif_counts),flush=True)
    target=b58decode(TARGET)[1:21];matches=[];start=time.monotonic()
    for index,(raw,recipe) in enumerate(registry.items(),1):
        for fmt,value in public_hashes(raw).items():
            if value==target:
                certificate={'key_hex':raw.hex(),'public_key_format':fmt,'target':TARGET,'origin':recipe,'addresses':addresses(raw)}
                assert certificate['addresses'][fmt]==TARGET;matches.append(certificate);print('MATCH',json.dumps(certificate),flush=True)
        if index%10000==0:print('Checked',index,'of',len(registry),'elapsed',round(time.monotonic()-start,1),'s',flush=True)
    dump('ordered_key_candidates.json',[{'key_hex':key.hex(),'first_origin':origin} for key,origin in registry.items()])
    files=['research/models/ordered_decode_v1.json','research/data/ordered_control_check.json','research/data/ordered_control_cases.json',
           'research/data/ordered_arithmetic_check.json','research/data/ordered_arithmetic_payloads.json',
           'tools/check_ordered_formats.py','tools/ordered_decode_common.py','tools/bitcoin_oracle.py','tools/check_five_sample_wif.py']
    out={'model':'C30','input_sha256':hashes(files),'oracle_selftests':tests,'hash160_scalar1_both_formats_known_answers':True,
         'raw_candidate_groups':{name:{'emissions':emissions[name],'invalid_scalar_rejections':invalid[name],'unique_scalars':len(sets[name])} for name in emissions},
         'C29_group_labels_follow_first_payload_recipe':True,'unique_valid_scalars':len(registry),'public_key_formats':2,
         'candidate_set_sha256':hashlib.sha256(b''.join(sorted(registry))).hexdigest(),'hash_finalization_used':False,
         'wif_format_gate':{**dict(wif_counts),'best_Base58_characters_in50':max(wif_hist),'histogram':dict(sorted(wif_hist.items()))},
         'valid_wif_records':valid_wifs,'ascii64_hex_gate':dict(hex_counts),'matches':matches,
         'format_trials_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'elapsed_oracle_seconds':round(time.monotonic()-start,3),
         'limitations':settings['limitations']+[settings['C30']['scope']]}
    dump('ordered_format_check.json',out)
    print('Finished C30:',len(registry),'scalars,',len(matches),'target matches; WIF best',max(wif_hist),flush=True)

if __name__=='__main__':main()
