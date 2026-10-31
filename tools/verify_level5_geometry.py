#!/usr/bin/env python3
"""Positive control: independently measure Level 5, apply two geometric hints, sum pairs."""
import csv
import hashlib
import json
import re
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects
from bitcoin_oracle import addresses

ROOT=Path(__file__).resolve().parents[1]

def main():
    image=ROOT/'research/sources/crypto5fix.png'
    a=np.array(Image.open(image).convert('L'));labels,_=label(a[30:900,120:785]>0)
    rectangles=[];lines=[]
    for y,x in find_objects(labels):
        patch=a[y.start+30:y.stop+30,x.start+120:x.stop+120];h,w=patch.shape
        bbox={'x':x.start+120,'y':y.start+30,'W':w,'H':h}
        if np.all(patch>0):lines.append(bbox);continue
        left=int(np.flatnonzero(patch[h//2]==0)[0]);right=int(np.flatnonzero(patch[h//2,::-1]==0)[0])
        top=int(np.flatnonzero(patch[:,w//2]==0)[0]);bottom=int(np.flatnonzero(patch[::-1,w//2]==0)[0])
        assert left==right and top==bottom
        rectangles.append({**bbox,'left':left,'top':top,'O':w*h,'I':int(np.count_nonzero(patch==0)),
                           'S':int(np.count_nonzero(patch>0)),'center_y':y.start+30+h/2})
    assert len(rectangles)==64 and len(lines)==2
    rectangles.sort(key=lambda r:r['center_y'])
    rectangles=[r for i in range(0,64,8) for r in sorted(rectangles[i:i+8],key=lambda r:r['x'])]
    reference=list(csv.DictReader(line for line in (ROOT/'research/sources/level5_data__rectangle-measurements.csv').open() if not line.startswith('#')))
    matches=sum(all(r[k]==int(ref[k]) for k in ['W','H','O','I','S']) for r,ref in zip(rectangles,reference))
    assert matches==64
    corrections=[]
    for i,r in enumerate(rectangles):
        # A hint is centered under its rectangle, separated by exactly four blank rows.
        hints=[ln for ln in lines if ln['H']==1 and ln['y']==r['y']+r['H']+4
               and abs((ln['x']+(ln['W']-1)/2)-(r['x']+(r['W']-1)/2))<=1]
        assert len(hints)<=1
        r['index']=i+1;r['true_width']=hints[0]['W'] if hints else r['W']
        if hints:corrections.append({'index':i+1,'outer_width':r['W'],'true_width':r['true_width'],'hint_line':hints[0]})
        numerator=(10*r['true_width']+r['left']-1)*(10*r['H']+r['top']-1)
        r['transformed_area']=numerator/4096;r['rounded_area']=(numerator+2048)//4096
        r['rounding_residual']=abs(r['transformed_area']-r['rounded_area'])
    areas=[r['rounded_area'] for r in rectangles]
    sums=[areas[i]+areas[i+1] for i in range(0,64,2)]
    assert all(0<=v<=255 for v in sums)
    key=bytes(sums)
    readme=(ROOT/'research/sources/level5_README.md').read_text()
    known=re.search(r'```\s*\n([0-9a-f]{64})\n```',readme).group(1)
    aa=addresses(key);expected='1cryptoGeCRiTzVgxBQcKFFjSVydN1GW7'
    assert key.hex()==known and aa['uncompressed']==expected
    with (ROOT/'research/data/level5_remeasured_rectangles.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rectangles[0]),lineterminator='\n');w.writeheader();w.writerows(rectangles)
    files=['research/sources/crypto5fix.png','research/sources/level5_README.md',
           'research/sources/level5_data__rectangle-measurements.csv','tools/verify_level5_geometry.py']
    out={'input_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in files},
         'rectangles_measured':64,'geometry_reference_matches':matches,'hint_lines':lines,'width_corrections':corrections,
         'formula':'round((10*true_width + left - 1)*(10*height + top - 1)/4096)',
         'rounded_areas':areas,'pair_sums':sums,'max_rounding_residual':max(r['rounding_residual'] for r in rectangles),
         'published_solved_key_hex':key.hex(),'published_key_match':key.hex()==known,
         'addresses':aa,'expected_address':expected,'expected_address_match':aa['uncompressed']==expected,
         'note':'Known solved historical puzzle benchmark; not a HALV private key or new solution.'}
    (ROOT/'research/data/level5_geometry_verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
