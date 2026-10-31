#!/usr/bin/env python3
"""C14: test parity/checksum roles for the measured 64-bit phase-position field."""
import hashlib
import json
from pathlib import Path
import numpy as np
from check_phase_decode import views,channels

ROOT=Path(__file__).resolve().parents[1]
FULL=(1<<64)-1
CRC={
    'ECMA182':(0x42F0E1EBA9EA3693,0,0,False,0x6C40DF5F0B497347),
    'WE':(0x42F0E1EBA9EA3693,FULL,FULL,False,0x62EC59E3F1A4F00A),
    'XZ':(0xC96C5795D7870F42,FULL,FULL,True,0x995DC9BBDF1939FA),
    'GO_ISO':(0xD800000000000000,FULL,FULL,True,0xB90956C775A41001)}

def crc64(data,params):
    poly,initial,xorout,reflected,_=params;state=initial
    for byte in data:
        state^=byte if reflected else byte<<56
        for _ in range(8):
            state=((state>>1)^poly if state&1 else state>>1) if reflected else (((state<<1)&FULL)^poly if state&(1<<63) else (state<<1)&FULL)
    return state^xorout

def main():
    for params in CRC.values():assert crc64(b'123456789',params)==params[-1]
    p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    q=np.array(next(f['states'] for f in p['fits'] if f['start_x']==92 and f['step_px']==3 and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1))
    audit=json.loads((ROOT/'research/data/parity_phase_check.json').read_text())
    tail=np.array(next(r['states'] for r in audit['constrained_models'] if r['model']=='predicted_middle_and_last'))
    parity_matches=[];crc_matches=[];parity_attempts=0;crc_comparisons=0;nearest=[]
    for source,original in [('nominal',q),('predicted_last_phase',tail)]:
        for view,x,scope in views(original):
            n,_,flags=channels(x,scope)
            for selection,label in [(np.arange(64),'all64'),(np.arange(16,56),'middle40')]:
                best=65
                for mask in range(16):
                    for intercept in [0,1]:
                        prediction=np.array([(int(v)&mask).bit_count()%2^intercept for v in n])
                        errors=int(np.sum(prediction[selection]!=flags[selection]));best=min(best,errors);parity_attempts+=1
                        if errors==0:parity_matches.append({'source':source,'view':view,'selection':label,'mask':mask,'intercept':intercept})
                nearest.append({'source':source,'view':view,'selection':label,'best_affine_parity_errors':best})
            f=int(''.join(map(str,flags.tolist())),2);flag_values=set()
            for value in [f,int(format(f,'064b')[::-1],2),int.from_bytes(f.to_bytes(8,'big')[::-1],'big')]:
                flag_values.add(value);flag_values.add(value^FULL)
            raw=bytes(int(v) for v in (16*n[::2]+n[1::2]))
            for encoding,payload in [('bytes',raw),('hex_ascii_lower',raw.hex().encode()),('hex_ascii_upper',raw.hex().upper().encode())]:
                for reverse in [False,True]:
                    data=payload[::-1] if reverse else payload
                    for name,params in CRC.items():
                        crc_comparisons+=len(flag_values)
                        value=crc64(data,params)
                        if value in flag_values:crc_matches.append({'source':source,'view':view,'encoding':encoding,'reverse_payload':reverse,'crc':name,'value_hex':format(value,'016x')})
    files=['research/data/pixel_measurements.json','research/data/parity_phase_check.json','tools/check_phase_decode.py','tools/check_phase_field_consistency.py']
    out={'model':'C14','input_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
         'crc_standard_check_vectors_passed':4,'affine_parity_attempts':parity_attempts,'exact_affine_parity_matches':parity_matches,
         'crc_comparisons_including_duplicates':crc_comparisons,'exact_crc_matches':crc_matches,
         'nearest_diagnostics':nearest,'no_private_key_search':True,
         'limitation':'Only the declared affine four-bit parity and four named CRC64 variants are tested. No generic checksum, cipher or metadata role is ruled out. Nearest patterns are not treated as decoded data.'}
    (ROOT/'research/data/phase_field_consistency.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Affine parity exact matches',len(parity_matches),'CRC64 exact matches',len(crc_matches))

if __name__=='__main__':main()
