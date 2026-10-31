#!/usr/bin/env python3
"""Allow the hidden mirrored trace to cross the axis between sample nodes."""
import json
import hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from measure_image import fit

ROOT=Path(__file__).resolve().parents[1]
a=np.array(Image.open(ROOT/'research/sources/cryptoHALV.png'),dtype=float)
results=[]
for step,start in [(3,92),(6,92),(6,95)]:
    for alphabet in [list(range(-3,4)),[-3,-1,1,3]]:
        f=fit(a,start,step,alphabet=alphabet)
        f['state_alphabet']=alphabet
        f['limitation']+=' Signed-state ties can be unobservable across zero-valued nodes. No unique sign reconstruction is claimed.'
        results.append(f)
        print({'step':step,'start':start,'alphabet':alphabet,'nodes':f['nodes'],'mse':f['mean_segment_mse']},flush=True)
reference=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
nominal=next(f for f in reference['fits'] if f['start_x']==92 and f['step_px']==3
             and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1)
image_hash=hashlib.sha256((ROOT/'research/sources/cryptoHALV.png').read_bytes()).hexdigest()
if image_hash!=reference['sha256']:
    raise ValueError('Stored baseline belongs to a different image')
out={'fits':results,'image_sha256':image_hash,
     'signed_three_px_abs_differs_from_nominal':sum(abs(a)!=b for a,b in zip(results[0]['states'],nominal['states']))}
(ROOT/'research/data/signed_model_check.json').write_text(json.dumps(out,indent=2)+'\n')
