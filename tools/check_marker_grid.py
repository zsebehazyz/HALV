#!/usr/bin/env python3
"""Exhaustive intensity thresholds and a declared seven-bit regrouping family."""
import json
import hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from measure_image import runs
from bitcoin_oracle import ALPHABET

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'research/sources/cryptoHALV.png'
a=np.array(Image.open(path))
v=a[438:513,91]
plateaus=[]
for t in range(1,256):
    count=len(runs(v>=t,438))
    if plateaus and plateaus[-1]['count']==count:plateaus[-1]['end']=t
    else:plateaus.append({'start':t,'end':t,'count':count})
spans=runs(v>=32,438)
marks=['-' if n>=4 else '.' for lo,hi,n in spans]
gaps=[b[0]-a[1]-1 for a,b in zip(spans,spans[1:])]
groups=[marks[0]]
for gap,mark in zip(gaps,marks[1:]):
    if gap>=5:groups.append(mark)
    else:groups[-1]+=mark
decode=dict(zip('.- -... -.-. -.. . ..-. --. .... .. .--- -.- .-.. -- -. --- .--. --.- .-. ... - ..- ...- .-- -..- -.-- --..'.split(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
ix=np.flatnonzero(v>=3)
bits=(v[ix[0]:ix[-1]+1]>=3).astype(int).tolist()
raw_values=[int(''.join(map(str,bits[i:i+7])),2) for i in range(0,63,7)]
variants=[]
for phase in range(7):
    # Explicit cyclic phase test, not seven extra measured pixels.
    shifted=bits[phase:]+bits[:phase]
    for reverse in [False,True]:
        seq=shifted[::-1] if reverse else shifted
        for invert in [False,True]:
            seq2=[b^int(invert) for b in seq]
            for little in [False,True]:
                gs=[seq2[i:i+7] for i in range(0,63,7)]
                vals=[int(''.join(map(str,g[::-1] if little else g)),2) for g in gs]
                variants.append({'phase':phase,'reverse':reverse,'complement':invert,'little':little,
                                 'values':vals,'all_base58_ascii':all(chr(n) in ALPHABET for n in vals),
                                 'all_base58_zero_based_indices':all(n<58 for n in vals)})
out={'image_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
     'column':91,'roi_rows_inclusive':[438,512],'comparator':'>=',
     'threshold_plateaus':plateaus,
     'conditional_morse':{'threshold':32,'dash_min_height':4,'group_min_blank_gap':5,
                          'heights':[r[2] for r in spans],'blank_gaps':gaps,'groups':groups,
                          'reading':''.join(decode.get(g,'?') for g in groups),
                          'limitation':'Conditional on thresholds, not proof of Morse.'},
     'seven_bit':{'threshold':3,'rows_inclusive':[int(ix[0]+438),int(ix[-1]+438)],
                  'bit_count':len(bits),'values':raw_values,'variants':variants,
                  'variants_all_base58_ascii':sum(r['all_base58_ascii'] for r in variants),
                  'variants_all_base58_indices':sum(r['all_base58_zero_based_indices'] for r in variants)}}
(ROOT/'research/data/marker_grid_check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='seven_bit'},indent=2))
print({k:v for k,v in out['seven_bit'].items() if k!='variants'})
