#!/usr/bin/env python3
"""C6: exact binary-overlay relations between the 63-bit marker and glyphs."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
FULL=(1<<63)-1

def integer(a):return int(''.join(str(int(v)) for v in a.flat),2)

def main():
    path=ROOT/'research/sources/cryptoHALV.png'
    a=np.array(Image.open(path).convert('L'))
    targets={t:integer(a[444:507,91]>=t) for t in [1,3,24,108,178]}
    exact=[];best={};attempts=0
    for sample in ['any','all']:
        glyphs=[]
        names=[]
        for text,x,y in [('HALV',868,912),('ZDEN',868,872)]:
            for i,char in enumerate(text):
                pixels=a[y:y+18,x+16*i:x+16*i+14]>0
                c=pixels.reshape(9,2,7,2).transpose(0,2,1,3).reshape(9,7,4)
                glyphs.append(c.any(2) if sample=='any' else c.all(2));names.append(text+'/'+char)
        for flip_y in [False,True]:
            for flip_x in [False,True]:
                values=[]
                for g in glyphs:
                    b=g[::-1] if flip_y else g
                    if flip_x:b=b[:,::-1]
                    values.append(integer(b))
                for subset in range(1,256):
                    selected=[v for i,v in enumerate(values) if subset>>i&1]
                    reduced={}
                    for op in ['xor','or','and']:
                        v=FULL if op=='and' else 0
                        for w in selected:
                            v=(v^w) if op=='xor' else (v|w) if op=='or' else (v&w)
                        reduced[op]=v
                    for op,value in reduced.items():
                        for invert in [False,True]:
                            v=value^FULL if invert else value
                            for threshold,target in targets.items():
                                attempts+=1;distance=(v^target).bit_count()
                                family=op+'/threshold='+str(threshold)
                                record={'operation':op,'threshold':threshold,'sample':sample,
                                        'flip_y':flip_y,'flip_x':flip_x,'complement':invert,
                                        'glyphs':[n for i,n in enumerate(names) if subset>>i&1],
                                        'hamming_distance':distance}
                                if family not in best or distance<best[family]['hamming_distance']:best[family]=record
                                if distance==0:exact.append(record)
    out={'image_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'marker_rows_inclusive':[444,506],'marker_length':63,'glyph_shape':[9,7],
         'constant_baselines':{str(t):{'all_zero_distance':v.bit_count(),'all_one_distance':(v^FULL).bit_count()} for t,v in targets.items()},
         'attempts_including_duplicates':attempts,'exact_relations':exact,
         'best_diagnostic_only':best,
         'limitation':'No exact relation means only this global binary-overlay family failed. Nearest patterns are diagnostics, not decoded messages or key candidates.'}
    (ROOT/'research/data/marker_glyph_relation.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'attempts':attempts,'exact_relations':len(exact),
                      'minimum_hamming_distance':min(r['hamming_distance'] for r in best.values())}))

if __name__=='__main__':main()
