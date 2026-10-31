#!/usr/bin/env python3
"""Empirical three-channel factorization with all residual bits preserved."""
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/halv-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/halv-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
q=np.array(next(f['states'] for f in p['fits'] if f['start_x']==92 and f['step_px']==3 and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1)).reshape(8,32)
d=json.loads((ROOT/'research/data/phase_law_diagnostics.json').read_text())
fig,axes=plt.subplots(2,2,figsize=(14,8),layout='constrained')
for ax,values,title in [
    (axes[0,0],q>>1,'High bit: 256 bits'),
    (axes[0,1],q&1,'Low bit: dominant phase 2,1,0,3 repeated'),
    (axes[1,0],np.array(d['flag64_bits']).reshape(8,8),'64 bits at predicted carrier phase'),
    (axes[1,1],np.array(d['residual192_bits']).reshape(8,24),'All 192 off-phase bits retained (26 ones)')]:
    ax.imshow(values,cmap='gray',vmin=0,vmax=1,aspect='auto',interpolation='nearest')
    ax.set(title=title,yticks=range(8),yticklabels=range(1,9),ylabel='Block')
for b in range(8):
    axes[0,1].scatter(np.arange((2-b)%4,32,4),np.full(8,b),c='red',marker='|',s=45)
for ax in axes[0]:
    for x in np.arange(3.5,32,4):ax.axvline(x,color='blue',alpha=.3)
fig.suptitle('Nominal fitted-state channel structure; no private-key decoding established')
fig.savefig(ROOT/'research/data/phase_channels.png',dpi=160)
print('Wrote phase_channels.png')
