#!/usr/bin/env python3
"""C20: preserve every state with one4+4 bit rule for all64 cells."""
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
import numpy as np
from bitcoin_oracle import ORDER,TARGET,addresses,selftest

ROOT=Path(__file__).resolve().parents[1]

def bits4(v):return [(v>>i)&1 for i in [3,2,1,0]]
def value4(bits):return sum(v<<(3-i) for i,v in enumerate(bits))
def pack(codes):return bytes.fromhex(''.join(f'{value4(code):x}' for code in codes))

def main():
    spec=json.loads((ROOT/'research/models/uniform_phase_layers_v1.json').read_text())
    p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    fit=next(f for f in p['fits'] if f['start_x']==92 and f['step_px']==3
             and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1)
    blocks=np.array(fit['states']).reshape(8,32);primary=[];residual=[];cell_rows=[];exception_rows=[]
    restored=[];morse_map={'.':'E','-':'T','.-':'A','...':'S'}
    for b,block in enumerate(blocks):
        z=(3-b)%4;r=(z-1)%4;hp=[i for i in range(4) if i!=z];lp=[i for i in range(4) if i!=r]
        chosen=[]
        for j,cell in enumerate(block.reshape(8,4)):
            high=[int(v>>1) for v in cell];low=[int(v%2) for v in cell]
            a=[high[i] for i in hp]+[low[r]];c=[high[z]]+[low[i] for i in lp]
            primary.append(a);residual.append(c);chosen.append(int(cell[z]))
            hh=[0]*4;ll=[0]*4
            for i,bit in zip(hp,a[:3]):hh[i]=bit
            ll[r]=a[3];hh[z]=c[0]
            for i,bit in zip(lp,c[1:]):ll[i]=bit
            inverse=[2*h+l for h,l in zip(hh,ll)]
            assert inverse==cell.tolist();restored.extend(inverse)
            cell_rows.append({'block_1based':b+1,'cell':j,'primary_nibble':value4(a),'residual_nibble':value4(c),
                              'full3plus1_condition_holds':not any(c)})
        if any(chosen):
            code=''.join({0:' ',1:'.',2:'-',3:'?'}[v] for v in chosen);tokens=code.split()
            exception_rows.append({'block_1based':b+1,'zero_phase':z,'values8':chosen,
                'cell_indices_nonzero':[i for i,v in enumerate(chosen) if v],
                'mask8':''.join(str(int(v!=0)) for v in chosen),'morse_tokens':tokens,
                'direct_morse':''.join(morse_map.get(t,'?') for t in tokens)})
    assert restored==blocks.flatten().tolist()
    primary_bytes=pack(primary);residual_bytes=pack(residual)
    edge_residual=pack([residual[8*b+j] for b in [0,1,7] for j in range(8)])
    uniform44=primary_bytes+edge_residual;assert len(uniform44)==44
    # Decode the actual serialized44 bytes, with fixed middle residual0.
    actual_primary=[bits4(int(c,16)) for c in uniform44[:32].hex()]
    edge_codes=[bits4(int(c,16)) for c in uniform44[32:].hex()]
    actual_residual=[[0]*4 for _ in range(64)]
    for k,b in enumerate([0,1,7]):actual_residual[8*b:8*b+8]=edge_codes[8*k:8*k+8]
    assert actual_primary==primary and actual_residual==residual
    files_to_write={'uniform_primary32.bin':primary_bytes,'uniform_edge_residual12.bin':edge_residual,'uniform_lossless44.bin':uniform44}
    for name,data in files_to_write.items():(ROOT/'research/data'/name).write_bytes(data)
    laws=[]
    for slope in range(4):
        for intercept in range(4):
            count=sum(int(sum(blocks[b,(slope*b+intercept)%4::4]==0)) for b in range(8))
            laws.append({'slope':slope,'intercept':intercept,'zeros_out_of64':count})
    laws.sort(key=lambda x:x['zeros_out_of64'],reverse=True)
    draws=spec['surrogate_draws'];rng=np.random.default_rng(spec['rng_seed'])
    hist=[]
    for block in blocks:
        masks=rng.permuted(np.tile(block==0,(draws,1)),axis=1)
        hist.append(masks.reshape(draws,8,4).sum(1))
    scores=np.array([sum(hist[b][:,(a*b+c)%4] for b in range(8)) for a in range(4) for c in range(4)])
    top=np.sort(scores,axis=0)[-2:];maxima=top[-1];gaps=top[-1]-top[-2]
    observed= laws[0]['zeros_out_of64'];gap=observed-laws[1]['zeros_out_of64']
    np.savez_compressed(ROOT/'research/data/uniform_affine_surrogates.npz',maxima=maxima,top_two_gaps=gaps)
    candidates={};attempts=0
    for perm in itertools.permutations(range(4)):
        for reverse_cells,reverse_bits,reverse_blocks in itertools.product([False,True],repeat=3):
            parts=[]
            for b in range(8):
                cells=primary[8*b:8*b+8];cells=cells[::-1] if reverse_cells else cells
                bits=[code[i] for code in cells for i in perm];parts.append(bits[::-1] if reverse_bits else bits)
            parts=parts[::-1] if reverse_blocks else parts;allbits=[v for part in parts for v in part]
            key=int(''.join(map(str,allbits)),2).to_bytes(32,'big');attempts+=1
            if 0<int.from_bytes(key,'big')<ORDER:
                candidates.setdefault(key,{'permutation':perm,'reverse_cells':reverse_cells,'reverse_bits':reverse_bits,'reverse_blocks':reverse_blocks})
    oracle=selftest();matches=[]
    for key,recipe in candidates.items():
        for fmt,address in addresses(key).items():
            if address==TARGET:matches.append({'recipe':recipe,'format':fmt,'key_hex':key.hex()})
    qzero=[int(blocks[b,j]) for b in range(8) for j in range((3-b)%4,32,4)]
    bd='10111101';exception_mask='11000001'
    files=['research/data/pixel_measurements.json','research/data/signature_phase_decode_check.json',
           'research/models/uniform_phase_layers_v1.json','tools/check_uniform_phase_layers.py','tools/bitcoin_oracle.py']
    out={'model':'C20','input_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
         'state_roundtrip_count':256,'regular_cells':sum(not any(c) for c in residual),
         'nonregular_cells':sum(any(c) for c in residual),'cell_rows':cell_rows,
         'zero_phase_values_count':dict(Counter(qzero)),'exception_rows':exception_rows,
         'residual_bit_ones':sum(map(sum,residual)),
         'low_bit_ones_at_other_nonphase_nonzero_slots':sum(int(blocks[b,j]%2) for b in range(8) for j in range(32) if j%4 not in [(3-b)%4,(2-b)%4]),
         'primary32_hex':primary_bytes.hex(),'residual64_nibbles_hex':residual_bytes.hex(),'edge_residual12_hex':edge_residual.hex(),
         'binary_sha256':{name:hashlib.sha256(data).hexdigest() for name,data in files_to_write.items()},
         'affine_phase_laws':laws,'observed_best_gap':gap,
         'affine_control':{'draws':draws,'seed':spec['rng_seed'],'max_as_good':int(sum(maxima>=observed)),
                           'gap_as_good':int(sum(gaps>=gap)),'joint_as_good':int(sum((maxima>=observed)&(gaps>=gap))),
                           'nonzero_estimate_rule':'A zero count is not zero probability; use(count+1)/(draws+1) and report scope'},
         'bd_exception_mask':{'bd':bd,'exception_mask':exception_mask,'matching_positions':sum(a==b for a,b in zip(bd,exception_mask))},
         'attempts_including_duplicates':attempts,'unique_valid_scalars':len(candidates),'public_key_formats':2,
         'candidate_set_sha256':hashlib.sha256(b''.join(sorted(candidates))).hexdigest(),
         'oracle_selftest':oracle,'hash_finalization_used':False,'matches':matches,'limitations':spec['limitations']}
    (ROOT/'research/data/uniform_phase_layers_check.json').write_text(json.dumps(out,indent=2)+'\n')
    (ROOT/'research/data/uniform_phase_layers_recipes.json').write_text(json.dumps([{'key_hex':k.hex(),**v} for k,v in candidates.items()],indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['model','state_roundtrip_count','regular_cells','nonregular_cells','exception_rows',
           'residual_bit_ones','low_bit_ones_at_other_nonphase_nonzero_slots','primary32_hex','edge_residual12_hex',
           'observed_best_gap','affine_control','unique_valid_scalars','matches']},indent=2))

if __name__=='__main__':main()
