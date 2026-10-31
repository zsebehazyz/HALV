#!/usr/bin/env python3
"""C18: staircase zero phase, lossless middle nibbles and layered direct keys."""
import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from bitcoin_oracle import ORDER,TARGET,addresses,selftest

ROOT=Path(__file__).resolve().parents[1]

def main():
    spec=json.loads((ROOT/'research/models/signature_phase_decode_v1.json').read_text())
    stairs=json.loads((ROOT/'research/data/signature_staircase_geometry.json').read_text())['horizontals']
    p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    fit=next(f for f in p['fits'] if f['start_x']==92 and f['step_px']==3
             and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1)
    blocks=np.array(fit['states']).reshape(8,32);reference=F(1859,2)
    heights=[reference-F(str(s['center_y'])) for s in stairs]
    assert len(heights)==5 and all(h.denominator==1 for h in heights)
    exponents=[h.numerator.bit_length()-1 for h in heights];zero_phase=[e%4 for e in exponents]
    middle=list(range(2,7));edge=[0,1,7];baseline_lo=max(F(str(s['center_y']))+2**e for s,e in zip(stairs,exponents))
    baseline_hi=min(F(str(s['center_y']))+2**(e+1) for s,e in zip(stairs,exponents))
    # Extend the single descending exponent law, rather than fitting block-specific phases.
    assert exponents==list(range(exponents[0],exponents[0]-5,-1))
    all_exponents=[exponents[0]+2-b for b in range(8)]
    all_zero_phase=[e%4 for e in all_exponents];odd_phase=[(z-1)%4 for z in all_zero_phase]
    zero_counts=[[int(sum(blocks[b,r::4]==0)) for r in range(4)] for b in range(8)]
    phases=[]
    for b in range(8):
        counts=zero_counts[b];z=all_zero_phase[b]
        phases.append({'block_1based':b+1,'predicted_zero_phase':z,'zero_counts_by_phase':counts,
                       'predicted_zero_count_out_of8':counts[z],
                       'is_maximum':counts[z]==max(counts),'is_unique_maximum':counts.count(max(counts))==1,
                       'predicted_odd_phase':odd_phase[b]})
        assert counts[z]==max(counts)
    assert all_zero_phase[2:7]==zero_phase
    assert [int(float(fit['scales'][32*b])).bit_length()-1 for b in range(8)]==all_exponents
    cell_bits={};reconstructed_states={};canonical_hex={}
    for b in middle:
        z=all_zero_phase[b];r=odd_phase[b];high_positions=[i for i in range(4) if i!=z]
        bits=[];restored=[]
        for cell in blocks[b].reshape(8,4):
            assert cell[z]==0 and all(v%2==0 for i,v in enumerate(cell) if i!=r)
            code=[int(cell[i]>>1) for i in high_positions]+[int(cell[r]%2)];bits.append(code)
            inverse=[0]*4
            for i,bit in zip(high_positions,code[:3]):inverse[i]=2*bit
            inverse[r]+=code[3];assert inverse==cell.tolist();restored.extend(inverse)
        cell_bits[b]=bits;reconstructed_states[str(b+1)]=restored
        canonical_hex[str(b+1)]=''.join(f'{int("".join(map(str,code)),2):x}' for code in bits)
    # Preserve all remaining information, without assuming it is a private key.
    # Middle blocks:4bytes each; edge blocks:8bytes of raw2-bit states each.
    full_parts=[];full_roundtrip=[]
    for b in range(8):
        if b in middle:
            part=bytes.fromhex(canonical_hex[str(b+1)])
            z=all_zero_phase[b];r=odd_phase[b];high_positions=[i for i in range(4) if i!=z]
            for character in part.hex():
                nibble=int(character,16);code=[(nibble>>i)&1 for i in [3,2,1,0]];cell=[0]*4
                for i,bit in zip(high_positions,code[:3]):cell[i]=2*bit
                cell[r]+=code[3];full_roundtrip.extend(cell)
        else:
            rawbits=''.join(f'{int(v):02b}' for v in blocks[b]);part=int(rawbits,2).to_bytes(8,'big')
            recovered=f'{int.from_bytes(part,"big"):064b}'
            full_roundtrip.extend(int(recovered[i:i+2],2) for i in range(0,64,2))
        full_parts.append(part)
    layered44=b''.join(full_parts);assert len(layered44)==44
    assert full_roundtrip==blocks.flatten().tolist()
    (ROOT/'research/data/layered_lossless44.bin').write_bytes(layered44)
    candidates={};recipes=[];attempts=Counter();unique_groups={};side_channels=[]
    bd=list(map(int,spec['bd']))
    for edge_rule in spec['edge_selection_rules']:
        selected={};residual=[]
        for b in edge:
            choose_high=(bd[b]==1 if edge_rule=='BD_1_high_0_low' else bd[b]==0
                         if edge_rule=='BD_1_low_0_high' else edge_rule=='all_high_control')
            selected[b]=[int(v>>1 if choose_high else v%2) for v in blocks[b]]
            residual.extend(int(v%2 if choose_high else v>>1) for v in blocks[b])
        side_channels.append({'edge_rule':edge_rule,'unselected_edge96_bits_hex':f'{int("".join(map(str,residual)),2):024x}'})
        for perm in itertools.permutations(range(4)):
            for cells in spec['cell_order']:
                payload=dict(selected)
                for b in middle:
                    codes=cell_bits[b] if cells=='forward' else cell_bits[b][::-1]
                    payload[b]=[code[i] for code in codes for i in perm]
                for direction in spec['bit_direction']:
                    pieces=[payload[b] if direction=='forward' else payload[b][::-1] for b in range(8)]
                    for order in spec['block_order']:
                        ordered=pieces if order=='original' else pieces[::-1]
                        bits=[v for part in ordered for v in part];assert len(bits)==256
                        key=int(''.join(map(str,bits)),2).to_bytes(32,'big');attempts[edge_rule]+=1
                        recipe={'edge_rule':edge_rule,'middle_bit_permutation':perm,'cell_order':cells,'bit_direction':direction,'block_order':order}
                        if not 0<int.from_bytes(key,'big')<ORDER:continue
                        candidates.setdefault(key,recipe);unique_groups.setdefault(edge_rule,set()).add(key)
                        recipes.append({**recipe,'key_hex':key.hex()})
    oracle=selftest();matches=[]
    for key,recipe in candidates.items():
        for fmt,address in addresses(key).items():
            if address==TARGET:matches.append({'recipe':recipe,'format':fmt,'key_hex':key.hex()})
    files=['research/sources/cryptoHALV.png','research/data/pixel_measurements.json','research/data/signature_staircase_geometry.json',
           'research/models/signature_phase_decode_v1.json','tools/check_signature_phase_decode.py','tools/bitcoin_oracle.py']
    out={'model':'C18','input_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
         'reference_y':str(reference),'heights_exact':[str(h) for h in heights],'floor_log2':exponents,
         'zero_phase_middle':zero_phase,'odd_phase_middle':odd_phase[2:7],
         'baseline_interval_same_floor_logs':{'lower_inclusive':str(baseline_lo),'upper_exclusive':str(baseline_hi)},
         'floor_logs_also_equal_wave_amplitude_scale_exponents_in_middle':True,'block_phase_predictions':phases,
         'lossless_middle_states_checked':160,'lossless_middle_cells_checked':40,
         'full_lossless_representation':{'bytes':44,'state_roundtrip_count':256,'hex':layered44.hex(),
              'sha256':hashlib.sha256(layered44).hexdigest(),'file':'research/data/layered_lossless44.bin',
              'block_bytes':[8,8,4,4,4,4,4,8],'not_a_private_key':True},
         'canonical_middle32bit_blocks_hex':canonical_hex,'reconstructed_middle_states':reconstructed_states,
         'middle_four_bit_symbol_counts':dict(Counter(int(''.join(map(str,code)),2) for codes in cell_bits.values() for code in codes)),
         'edge_residual_channels':side_channels,'attempts_including_duplicates':sum(attempts.values()),
         'unique_valid_scalars':len(candidates),'groups':{g:{'attempts':attempts[g],'unique_valid_scalars':len(unique_groups.get(g,()))} for g in attempts},
         'candidate_set_sha256':hashlib.sha256(b''.join(sorted(candidates))).hexdigest(),'public_key_formats':2,
         'hash_finalization_used':False,'oracle_selftest':oracle,'matches':matches,'limitations':spec['limitations']}
    (ROOT/'research/data/signature_phase_decode_check.json').write_text(json.dumps(out,indent=2)+'\n')
    (ROOT/'research/data/signature_phase_decode_recipes.json').write_text(json.dumps(recipes,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['model','heights_exact','zero_phase_middle','odd_phase_middle',
          'baseline_interval_same_floor_logs','lossless_middle_states_checked','full_lossless_representation',
          'attempts_including_duplicates','unique_valid_scalars','matches']},indent=2))

if __name__=='__main__':main()
