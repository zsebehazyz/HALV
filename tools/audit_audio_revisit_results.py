#!/usr/bin/env python3
"""Independent CSV/codec/threshold/regression checks for C39-C41."""
import csv
import hashlib
import json
import re
from fractions import Fraction as F
import numpy as np
from PIL import Image
from residual_channels import ROOT,nominal_states


def split_marks(bits):
    indices=[i for i,v in enumerate(bits) if v];parts=[]
    for index in indices:
        if not parts or index!=parts[-1][-1]+1:parts.append([index])
        else:parts[-1].append(index)
    return [len(p) for p in parts],[b[0]-a[-1]-1 for a,b in zip(parts,parts[1:])]


def main():
    marker=json.loads((ROOT/'research/data/marker_pixel_revisit_check.json').read_text())
    audio=json.loads((ROOT/'research/data/fibonacci_audio_probe_check.json').read_text())
    price=json.loads((ROOT/'research/data/price_shape_revisit_check.json').read_text())
    inputs={}
    for doc in [marker,audio,price]:
        for path,value in doc['input_sha256'].items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==value,path
            inputs[path]=value
    column=np.array(Image.open(ROOT/'research/sources/cryptoHALV.png'))[:,91]
    rows=list(csv.DictReader((ROOT/'research/data/marker_x91_rows443_506.csv').open()))
    assert [int(r['intensity']) for r in rows]==column[443:507].tolist()
    targets={'XEX':('-..-.-..-',{3,4}),'NMRM':('-.--.-.--',{1,3,6})};counts={k:0 for k in targets}
    # Algebraic interval feasibility, independent of text decoding and cut enumeration.
    for threshold in range(1,256):
        for reverse in [False,True]:
            bits=(column[438:513]>=threshold).tolist()
            if reverse:bits=bits[::-1]
            heights,gaps=split_marks(bits)
            if len(heights)!=9:continue
            for name,(pattern,separators) in targets.items():
                lo_mark=max(h for h,c in zip(heights,pattern) if c=='.')+1
                hi_mark=min(h for h,c in zip(heights,pattern) if c=='-')
                lo_gap=max(g for i,g in enumerate(gaps) if i not in separators)+1
                hi_gap=min(g for i,g in enumerate(gaps) if i in separators)
                counts[name]+=max(0,hi_mark-lo_mark+1)*max(0,hi_gap-lo_gap+1)
    assert counts==marker['marker']['global_morse_target_recipe_counts']
    q=nominal_states().flatten();nodes=list(csv.DictReader((ROOT/'research/data/canonical_q256.csv').open()))
    assert [int(r['q']) for r in nodes]==q.tolist() and len(nodes)==256
    assert [int(r['x']) for r in nodes]==list(range(92,858,3))
    pixels=list(csv.DictReader((ROOT/'research/data/canonical_within_block_pixels.csv').open()))
    assert len(pixels)==752
    for row in pixels:
        b=int(row['block_1based'])-1;k=int(row['local_pixel']);j=min(k//3,30);t=k-3*j
        expected=3*int(q[32*b+j])+t*int(q[32*b+j+1]-q[32*b+j])
        assert int(row['amplitude_in_scale_over3'])==expected
    physical=list(csv.DictReader((ROOT/'research/data/canonical_physical_polyline_pixels.csv').open()))
    for row in physical:
        x=int(row['x']);i=min((x-92)//3,254);t=F(x-92-3*i,3)
        h0=int(q[i])*(128//2**(i//32));h1=int(q[i+1])*(128//2**((i+1)//32))
        assert F(row['exact_height_px'])==(1-t)*h0+t*h1
    src=(ROOT/'research/sources/ffmpeg_8svx.c').read_text()
    table=[int(x) for x in re.search(r'\bfibonacci\[16\]\s*=\s*\{([^}]+)\}',src).group(1).split(',')]
    packed=(ROOT/'research/data/canonical_fib_delta_low_first.bin').read_bytes()
    acc=0;restored=[]
    for byte in packed:
        for code in [byte&15,byte>>4]:acc+=table[code];restored.append(acc)
    assert restored==q.tolist()
    pcms=np.load(ROOT/'research/data/fibonacci_pcm128_all_seeds.npz')['pcm'];assert pcms.shape==(96,256,128)
    replayed=0
    for ri,recipe in enumerate(audio['recipes']):
        source=q[::-1] if recipe['reverse_q'] else q
        values=[recipe['state_permutation'][int(v)] for v in source]
        raw=[64*values[i]+16*values[i+1]+4*values[i+2]+values[i+3] for i in range(0,256,4)]
        indices=[]
        for byte in raw:indices.extend([byte&15,byte>>4] if recipe['nibble_order']=='low_first' else [byte>>4,byte&15])
        for seed in range(256):
            acc=seed;out=[]
            for code in indices:acc=max(0,min(255,acc+table[code]));out.append(acc)
            assert out==pcms[ri,seed].tolist();replayed+=1
    curves={}
    for row in csv.DictReader((ROOT/'research/data/price_shape_resampled256.csv').open()):
        curves.setdefault((row['start'],row['signal']),[]).append(float(row['value']))
    train=np.arange(64,192);test=np.r_[0:64,192:256]
    scales=128//2**(np.arange(256)//32);references=[]
    def independent_fit(row,shift):
        x=np.array(curves[(row['start'],row['signal'])]);x=x[::-1] if row['reverse'] else x;x=np.roll(x,shift)
        y=q if row['target']=='normalized_q' else q*scales
        design=np.c_[x,np.ones(256)];coef=np.linalg.lstsq(design[train],y[train],rcond=None)[0]
        pred=design@coef;mse=np.mean((pred[test]-y[test])**2);base=np.mean((y[train].mean()-y[test])**2)
        return 1-mse/base,coef
    for row in price['models']:
        score,coef=independent_fit(row,0)
        assert abs(score-row['heldout_skill'])<1e-10
        assert np.allclose(coef,[row['gain'],row['offset']],rtol=1e-9,atol=1e-9)
    for shift in range(1,256):
        best=max(independent_fit(row,shift)[0] for row in price['models'])
        assert abs(best-price['family_shift_references'][shift-1]['selected_best_heldout_skill'])<1e-9
        references.append(best)
    assert sum(v>=price['best_exploratory_model']['heldout_skill']-1e-12 for v in references)==price['shift_references_as_good']
    names=['research/data/marker_pixel_revisit_check.json','research/data/fibonacci_audio_probe_check.json',
           'research/data/price_shape_revisit_check.json','tools/audit_audio_revisit_results.py']
    out={'purpose':'C39-C41 independent archive and calculation audit',
         'verified_input_files':len(inputs),'Morse_recipe_counts_by_independent_inequalities':counts,
         'canonical_vertices':len(nodes),'within_block_model_pixels':len(pixels),'whole_polyline_pixels':len(physical),
         'independently_replayed_PCM_arrays':replayed,'independent_price_models':len(price['models']),
         'independent_price_family_shift_references':len(references),
         'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in names}}
    (ROOT/'research/data/audio_revisit_integrity.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
