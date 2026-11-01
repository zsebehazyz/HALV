#!/usr/bin/env python3
"""C27: reproduce the archived Level2 sampler and neighbor/flag decoder."""
import hashlib
import json
import math
import numpy as np
from PIL import Image
from residual_channels import ROOT
from check_five_sample_wif import decode_wif,wif_selftest
from bitcoin_oracle import addresses,selftest

def main():
    spec=json.loads((ROOT/'research/models/historical_level2_control_v1.json').read_text())
    name='research/sources/history_level2_crypto2__crypto2.png';im=np.array(Image.open(ROOT/name).convert('RGB'))
    step=2*math.pi/(51*2);rows=[];samples=[]
    def sample(angle,radius,window):
        x=474+int(math.sin(angle)*radius);y=474-int(math.cos(angle)*radius)
        avg=im[y-window:y+window+1,x-window:x+window+1].sum(axis=(0,1))//((2*window+1)**2)
        bit=int(np.all(avg>=250));samples.append({'x':x,'y':y,'window':window,'bit':bit});return bit
    for sector in range(51):
        angle=step*(1+2*sector);raw=[]
        for ring in range(-3,4):
            if ring==0:raw.append(sample(angle,360,10))
            else:
                raw.append(sample(angle-step/2.4,360-ring*32,1))
                raw.append(sample(angle+step/2.4,360-ring*32,1))
        rows.append(raw)
    layers=[[] for _ in range(7)]
    for raw in rows:
        for ring,(a,b) in enumerate([(0,1),(2,3),(4,5),(6,6),(7,8),(9,10),(11,12)]):layers[ring].extend([raw[a],raw[b]])
    decoded=[];checks=[];flags=[]
    for i in range(51):
        left=(i-1)%51;right=(i+1)%51;bits=[]
        for ring in range(7):
            if ring==3:bits.append(layers[3][2*i]);continue
            a=layers[ring][2*left+1];b=layers[ring][2*right]
            checks.append({'sector':i,'ring':ring,'left_bit':a,'right_bit':b,'complementary':a+b==1})
            bits.append(b)
        flag=bits[3];flags.append(flag)
        if flag:bits=[v^1 for v in bits]
        else:bits[3]=1
        decoded.append(chr(int(''.join(map(str,bits)),2)))
    assert all(row['complementary'] for row in checks)
    text=''.join(decoded);index=text.index('5');candidates=[text[index:]+text[:index],(text[index+1:]+text[:index+1])[::-1]]
    verified=[]
    for candidate in candidates:
        result,reason=decode_wif(candidate)
        row={'wif':candidate,'validation':reason}
        if result:row.update({'historical_public_key_compressed':result['compressed'],'historical_addresses':addresses(result['key']),
                              'historical_key_hex':result['key'].hex()})
        verified.append(row)
    assert sum(row['validation']=='valid' for row in verified)==1
    # Manually transcribed from the original image footer; see the audit crop.
    historical_target='1cryptoTuax4qeedzVC35eYf4c16v4reJ'
    valid=next(row for row in verified if row['validation']=='valid')
    assert valid['historical_addresses']['uncompressed']==historical_target
    files=[name,'research/sources/history_level2_crypto2__README.rst','research/sources/history_level2_crypto2__crypto2.go',
           'research/sources/history_level2_crypto2__d.rb','research/sources/history_level2_provenance.json',
           'research/models/historical_level2_control_v1.json','tools/verify_historical_level2.py',
           'tools/check_five_sample_wif.py','tools/bitcoin_oracle.py']
    out={'model':'C27','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
         'image_shape':list(im.shape),'raw_sectors':rows,'samples':samples,'neighbor_checks':checks,
         'neighbor_constraints_passed':sum(v['complementary'] for v in checks),'neighbor_constraints_total':len(checks),
         'flag_bits':flags,'decoded_ascii7_before_rotation':text,'candidate_readings':verified,
         'oracle_selftests':{'address':selftest(),'wif':wif_selftest()},
         'historical_target_address':historical_target,'historical_target_match':True,
         'target_address_match_status':'Footer manually transcribed and visually compared using the archived original; decoded uncompressed address equals it. Not automated OCR. No relation to HALV target implied',
         'no_halv_key_search':True,'limitations':spec['limitations']}
    (ROOT/'research/data/historical_level2_control.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Historical control:',len(rows),'sectors;',len(checks),'complementary constraints passed')
    for row in verified:print(row)

if __name__=='__main__':main()
