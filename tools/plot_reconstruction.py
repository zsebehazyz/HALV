#!/usr/bin/env python3
"""Plot measured pixels and the explicit nominal reconstruction."""
import csv
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/halv-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME', '/tmp/halv-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
p = json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
f = next(f for f in p['fits'] if f['start_x']==92 and f['step_px']==3
         and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1)
x, q, scale = map(np.array, [f['coordinates'],f['states'],f['scales']])
with (ROOT/'research/data/reconstructed_states.csv').open('w') as out:
    w=csv.writer(out,lineterminator='\n');w.writerow(['index','x','scale_px','state','alternative_state_cost_gap'])
    w.writerows(zip(range(len(x)),x,scale,q,f['second_state_cost_gaps']))
a=np.array(Image.open(ROOT/'research/sources/cryptoHALV.png'))
fig, axes=plt.subplots(2,1,figsize=(13,7),layout='constrained')
ax=axes[0]
ax.imshow(a,cmap='gray',vmin=0,vmax=255,interpolation='nearest',aspect='auto')
ax.plot(x,475-q*scale,color='tab:orange',linewidth=.7,label='Fitted mirrored straight polyline')
ax.plot(x,475+q*scale,color='tab:orange',linewidth=.7)
ax.set(xlim=(90,188),ylim=(865,85),title='First block: actual mirror pixels and nominal fit (aspect ratio adjusted)',xlabel='Image x (pixels)',ylabel='Image y (pixels)')
ax.legend(loc='upper right',fontsize=8)
axes[1].plot(range(256),q,'.-',markersize=3,linewidth=.6)
axes[1].set(title='256 fitted states after removing the assumed block halving',xlabel='State index',ylabel='State q',yticks=[0,1,2,3])
for b in range(1,8):axes[1].axvline(b*32-.5,color='gray',alpha=.3)
fig.suptitle('HALV reconstruction hypothesis — not a decoded private key')
fig.savefig(ROOT/'research/data/reconstruction.png',dpi=160)
print('Wrote research/data/reconstruction.png and reconstructed_states.csv')
