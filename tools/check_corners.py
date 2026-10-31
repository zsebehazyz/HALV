#!/usr/bin/env python3
"""Measured corner comparisons and a bounded, explicit bitmap-to-key family."""
import csv
import hashlib
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/halv-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/halv-cache')
import numpy as np
from PIL import Image
from bitcoin_oracle import ORDER,TARGET,addresses,sha256,selftest

ROOT=Path(__file__).resolve().parents[1]

def spans(mask,origin=0):
    ix=np.flatnonzero(mask)
    return [[int(r[0]+origin),int(r[-1]+origin),len(r)]
            for r in np.split(ix,np.flatnonzero(np.diff(ix)>1)+1) if len(r)]

def orientations(a):
    for transpose in [False,True]:
        for flip_y in [False,True]:
            for flip_x in [False,True]:
                b=a.T if transpose else a
                if flip_y:b=b[::-1]
                if flip_x:b=b[:,::-1]
                yield b,f'transpose={transpose}/flip_y={flip_y}/flip_x={flip_x}'

def main():
    images={name:np.array(Image.open(ROOT/'research/sources'/name).convert('L'))
            for name in ['cryptoHALV.png','crypto5.png','crypto5fix.png']}
    a=images['cryptoHALV.png'];old=images['crypto5fix.png']
    hashes={name:hashlib.sha256((ROOT/'research/sources'/name).read_bytes()).hexdigest() for name in images}
    comparisons={}
    for name,(x0,y0,x1,y1) in {
        'header':(788,806,916,830),'U_Z_ZDEN':(868,832,932,890),
        'left_stems_and_staircase':(788,830,868,930),'level_label':(868,890,932,930)
    }.items():
        comparisons[name]={'roi':[x0,y0,x1,y1],
            'different_pixels_vs_level5fix':int(np.count_nonzero(a[y0:y1,x0:x1]!=old[y0:y1,x0:x1])),
            'level5_original_vs_fix_differences':int(np.count_nonzero(images['crypto5.png'][y0:y1,x0:x1]!=old[y0:y1,x0:x1]))}
    digit_patterns={
        '0':['010','101','101','101','010'], '1':['010','110','010','010','111'],
        '2':['110','001','010','100','111'], '4':['101','101','111','001','001'],
        '8':['010','101','010','101','010'], '9':['010','101','011','001','010']}
    lookup={''.join(v):k for k,v in digit_patterns.items()}
    dates={}
    for name,im in images.items():
        gs=[''.join('1' if p else '0' for p in im[925:930,20+4*i:23+4*i].flat) for i in range(8)]
        dates[name]={'glyph_bitstrings':gs,'reading':''.join(lookup.get(g,'?') for g in gs)}
    candidates={}
    def add(key,label):
        if len(key)==32 and 0<int.from_bytes(key,'big')<ORDER:candidates.setdefault(key,label)
    # Four 7x9 glyphs contain 252 sampled bits. Treat 4 missing bits as a bounded hypothesis.
    glyph_stats={}
    for text,x0,y0 in [('HALV',868,912),('ZDEN',868,872)]:
        glyphs=[]
        for i in range(4):
            pixels=a[y0:y0+18,x0+16*i:x0+16*i+14]>0
            cells=pixels.reshape(9,2,7,2).transpose(0,2,1,3).reshape(9,7,4)
            glyphs.append(cells)
        glyph_stats[text]={'shape_per_glyph':[9,7],
            'nonuniform_2x2_cells':sum(int(np.count_nonzero(g.any(2)!=g.all(2))) for g in glyphs)}
        for sample in ['top_left','any','all','majority']:
            gs=[g[:,:,0] if sample=='top_left' else g.any(2) if sample=='any' else g.all(2) if sample=='all' else g.sum(2)>=2 for g in glyphs]
            # Also pad each 63-bit glyph separately to 64 bits (four 8-byte fields).
            for orient_index in range(8):
                oriented=[list(orientations(g))[orient_index] for g in gs]
                for reverse_glyphs in [False,True]:
                    values=oriented[::-1] if reverse_glyphs else oriented
                    for inverse in [False,True]:
                        words=[int(''.join(str(int(b)^int(inverse)) for b in g.flat),2) for g,_ in values]
                        for extra in range(16):
                            for end in ['prefix','suffix']:
                                padded=[((extra>>i&1)<<63)|v if end=='prefix' else (v<<1)|(extra>>i&1) for i,v in enumerate(words)]
                                key=b''.join(v.to_bytes(8,'big') for v in padded)
                                add(key,f'{text}/{sample}/per_glyph/{values[0][1]}/reverse_glyphs={reverse_glyphs}/complement={inverse}/{end}={extra}')
            for layout,bitmap in [('glyph_serial',np.vstack(gs)),('row_interleaved',np.hstack(gs))]:
                for b,orientation in orientations(bitmap):
                    bits=b.astype(int).flatten().tolist()
                    for inverse in [False,True]:
                        value=int(''.join(str(v^int(inverse)) for v in bits),2)
                        for extra in range(16):
                            for end,n in [('prefix',(extra<<252)|value),('suffix',(value<<4)|extra)]:
                                add(n.to_bytes(32,'big'),f'{text}/{sample}/{layout}/{orientation}/complement={inverse}/{end}={extra}')
    # Explicit canonical binary raster encodings, no arbitrary windows or pixel selection.
    for name,bitmap in {
        'date':a[925:930,20:51]>0,
        'signature':a[806:930,788:932]>0,
        'signature_xor_level5':a[806:930,788:932]!=old[806:930,788:932],
        'staircase':a[830:930,788:868]>0,
    }.items():
        for b,orientation in orientations(bitmap):
            for bitorder in ['big','little']:
                raw=np.packbits(b,bitorder=bitorder).tobytes()
                label=f'{name}/{orientation}/packbits={bitorder}'
                add(sha256(raw),label+'/sha256');add(sha256(sha256(raw)),label+'/double_sha256')
    for text in ['20042402','20042024','20240420']:
        for label,raw in [('ascii',text.encode()),('bcd',bytes.fromhex(text)),('decimal',int(text).to_bytes(4,'big'))]:
            add(sha256(raw),f'date/{text}/{label}/sha256')
            add(sha256(sha256(raw)),f'date/{text}/{label}/double_sha256')
    verification=selftest()
    lvl5=addresses(bytes.fromhex('f4bfad68198549d3e5612fa3b1cabad14679c634359e2f5efdd804ddce8a9f51'))
    if lvl5['uncompressed']!='1cryptoGeCRiTzVgxBQcKFFjSVydN1GW7':raise RuntimeError('Level5 reference failed')
    matches=[]
    for key,label in candidates.items():
        for fmt,address in addresses(key).items():
            if address==TARGET:matches.append({'label':label,'format':fmt,'key_hex':key.hex()})
    lobe_counts=[]
    for t in range(1,256):
        n=len(spans(a[475,91:859]<t,91))
        if lobe_counts and lobe_counts[-1]['count']==n:lobe_counts[-1]['end']=t
        else:lobe_counts.append({'start':t,'end':t,'count':n})
    lobes=[]
    for i,(left,right,width) in enumerate(spans(a[475,91:859]<1,91)):
        y,x=np.where(a[85:476,left:right+1]>100)
        peak_y=int(y.min()+85) if len(y) else 475
        lobes.append({'index':i,'left':left,'right':right,'width':width,'peak_y_threshold100':peak_y,
                      'block_by_midpoint':max(0,min(7,int((((left+right)/2)-92)//96)))})
    with (ROOT/'research/data/lobes_centerline_t1.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(lobes[0]),lineterminator='\n');w.writeheader();w.writerows(lobes)
    out={'image_hashes':hashes,'corner_unique_intensities':np.unique(a[806:930,788:932]).tolist(),
         'comparisons':comparisons,'dates':dates,'glyph_sampling':glyph_stats,
         'lobe_definition':'Dark runs at y=475 in x=91..858, intensity <1; includes open first run, excludes unresolved small tail lobes. Not a topology certificate.',
         'lobe_threshold_plateaus':lobe_counts,
         'lobe_counts_per_96px_block_by_midpoint':[sum(l['block_by_midpoint']==b for l in lobes) for b in range(8)],
         'oracle_selftest':verification,'level5_reference_addresses':lvl5,
         'unique_corner_candidates':len(candidates),'formats_per_candidate':2,'matches':matches,
         'candidate_set_sha256':sha256(b''.join(sorted(candidates))).hex(),
         'limitation':'Negative for the explicit 252-bit glyph/padding and canonical bitmap/date hash families only. No claim that signature is irrelevant; no unique eight-separator rule found.'}
    (ROOT/'research/data/corner_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,2,figsize=(14,10),layout='constrained')
    for ax,im,title in [(axes[0,0],a[800:935,780:935],'HALV signature'),
                        (axes[0,1],old[800:935,780:935],'Level 5 signature (mirror)'),
                        (axes[1,0],a[925:930,20:51],'HALV date: 20042402'),
                        (axes[1,1],a[800:935,780:935]!=old[800:935,780:935],'HALV XOR Level 5; white means changed')]:
        ax.imshow(im,cmap='gray',interpolation='nearest',aspect='auto');ax.set_title(title)
    fig.savefig(ROOT/'research/data/corner_comparison.png',dpi=160)

if __name__=='__main__':main()
