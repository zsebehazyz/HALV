#!/usr/bin/env python3
"""Predeclared linked hypotheses C1..C5; see research/HYPOTHESES.md."""
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from PIL import Image
from bitcoin_oracle import ORDER,TARGET,addresses,sha256,selftest
from check_corners import orientations

ROOT=Path(__file__).resolve().parents[1]
FULL=(1<<256)-1

def integer(bits):
    return int(''.join(str(int(v)) for v in bits),2)

def rotate_blocks(q,shifts,sign):
    size=len(q)//len(shifts)
    return [int(v) for i,shift in enumerate(shifts)
            for v in np.roll(q[i*size:(i+1)*size],sign*shift)]

def generate_masks(a,spec):
    marker={};signature={}
    def add(target,value,label):
        for reverse in [False,True]:
            v=value
            if reverse:v=int(format(value,'0256b')[::-1],2)
            for inverse in [False,True]:
                x=v^FULL if inverse else v
                target.setdefault(x,label+f'/reverse={reverse}/complement={inverse}')
    for y in spec['marker']['row_starts']:
        for threshold in spec['marker']['thresholds_inclusive']:
            n=spec['marker']['rows'];column=spec['marker']['column'];repeat=spec['marker']['repeat']
            bits=(a[y:y+n,column]>=threshold).astype(int).tolist()
            add(marker,integer(bits*repeat),f'M/rows={y}:{y+n}/threshold>={threshold}/repeat={repeat}')
    for name,x,y in [('HALV',868,912),('ZDEN',868,872)]:
        cells=[]
        for i in range(4):
            pixels=a[y:y+18,x+16*i:x+16*i+14]>0
            cells.append(pixels.reshape(9,2,7,2).transpose(0,2,1,3).reshape(9,7,4))
        for sample in spec['signature']['samples']:
            gs=[c.any(2) if sample=='any' else c.all(2) for c in cells]
            for orient in range(8):
                arrays=[list(orientations(g))[orient][0] for g in gs]
                for reverse_glyphs in [False,True]:
                    seq=arrays[::-1] if reverse_glyphs else arrays
                    for padding in spec['signature']['padding_bits']:
                        for prefix in [False,True]:
                            bits=[]
                            for g in seq:
                                body=g.astype(int).flatten().tolist()
                                bits+=([padding]+body if prefix else body+[padding])
                            assert len(bits)==256
                            add(signature,integer(bits),f'S/{name}/{sample}/orientation={orient}/reverse_glyphs={reverse_glyphs}/pad={padding}/prefix={prefix}')
    return marker,signature

def main():
    input_names=['research/sources/cryptoHALV.png','research/data/pixel_measurements.json',
                 'research/data/marker_grid_check.json','research/data/corner_check.json',
                 'research/models/composite_v1.json','tools/check_composite_models.py']
    input_hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in input_names}
    p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    if input_hashes[input_names[0]]!=p['sha256']:raise ValueError('Image and reconstruction hashes differ')
    q=next(f['states'] for f in p['fits'] if f['start_x']==92 and f['step_px']==3
           and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1)
    a=np.array(Image.open(ROOT/input_names[0]).convert('L'))
    spec=json.loads((ROOT/'research/models/composite_v1.json').read_text())
    marker,signature=generate_masks(a,spec)
    corner=json.loads((ROOT/'research/data/corner_check.json').read_text())
    date=[int(c) for c in corner['dates']['cryptoHALV.png']['reading']]
    groups=json.loads((ROOT/'research/data/marker_grid_check.json').read_text())['conditional_morse']['groups']
    tree=[int('1'+''.join('1' if c=='-' else '0' for c in g),2) for g in groups]
    assert len(date)==8 and len(tree)==4 and len(q)==256
    verification=selftest()
    candidates={};family_keys=defaultdict(set);attempts=defaultdict(int)
    invalid=defaultdict(int)
    def add(value,family,label):
        raw=value.to_bytes(32,'big')
        for key,suffix in [(raw,'raw'),(sha256(raw),'sha256')]:
            attempts[family]+=1
            if not 0<int.from_bytes(key,'big')<ORDER:
                invalid[family]+=1;continue
            candidates.setdefault(key,{'model':family,'path':label+'/'+suffix})
            family_keys[family].add(key)
    for sm,sl in signature.items():
        for mm,ml in marker.items():add(sm^mm,'C3',sl+' XOR '+ml)
    for reverse in [False,True]:
        seq=q[::-1] if reverse else q
        versions=[('identity',seq)]
        for sign in [-1,1]:
            versions.append((f'date_rotation={sign}',rotate_blocks(seq,date,sign)))
            versions.append((f'morse_tree_rotation={sign}',rotate_blocks(seq,tree,sign)))
        for version,s in versions:
            for perm in itertools.permutations(range(4)):
                high=integer([(perm[v]>>1)&1 for v in s])
                low=integer([perm[v]&1 for v in s])
                for origin,masks in [('M',marker),('S',signature)]:
                    family=('C1' if origin=='M' else 'C2') if version=='identity' else 'C4' if version.startswith('date') else 'C5'
                    tag=f'W/reverse={reverse}/{version}/permutation='+''.join(map(str,perm))
                    for mask,label in masks.items():
                        selected=(high&mask)|(low&(FULL^mask))
                        for operation,value in [('select_high_or_low',selected),('xor_high',high^mask),('xor_low',low^mask)]:
                            add(value,family,tag+'/'+operation+'/'+label)
    print(json.dumps({'phase':'generated','marker_masks':len(marker),'signature_masks':len(signature),
                      'unique_candidates':len(candidates),'family_attempts':dict(attempts)}),flush=True)
    matches=[]
    for i,(key,label) in enumerate(candidates.items(),1):
        for fmt,address in addresses(key).items():
            if address==TARGET:matches.append({'key_hex':key.hex(),'format':fmt,**label})
        if i%10000==0:print(json.dumps({'phase':'checking','checked':i,'total':len(candidates)}),flush=True)
    result={'input_sha256':input_hashes,'oracle_selftest':verification,
            'wave_reconstruction':'x=92, clock=3px, unsigned four-state nominal fit; no uncertainty expansion',
            'date_digits':date,'morse_groups':groups,'morse_tree_indices':tree,
            'marker_masks':len(marker),'signature_masks':len(signature),
            'models':{c:{'attempts_including_duplicates':attempts[c],
                         'invalid_scalar_attempts':invalid[c],
                         'unique_valid_scalars':len(family_keys[c])} for c in sorted(attempts)},
            'global_unique_valid_scalars':len(candidates),'public_key_formats_per_scalar':2,
            'candidate_set_sha256':sha256(b''.join(sorted(candidates))).hex(),
            'matches':matches,
            'limitations':['Predeclared bounded models, not exhaustive compositions.',
                           'Marker as selector/XOR mask and glyph padding are hypotheses.',
                           'Date/Morse rotations are weak hypotheses, not decoded instructions.',
                           'Negative results do not exclude a part from instruction, normalization, or other joint roles.',
                           'No alternate waveform reconstruction, WIF decoder chain, or audio demodulation tested here.']}
    (ROOT/'research/data/composite_model_check.json').write_text(json.dumps(result,indent=2)+'\n')
    manifests={name:[{'mask_hex':m.to_bytes(32,'big').hex(),'source':label} for m,label in masks.items()]
               for name,masks in [('M',marker),('S',signature)]}
    (ROOT/'research/data/composite_masks.json').write_text(json.dumps(manifests,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
