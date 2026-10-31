#!/usr/bin/env python3
"""Visual evidence for the verified control and the tested HALV 64-cell hypothesis."""
import csv
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/halv-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/halv-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
control=json.loads((ROOT/'research/data/level5_geometry_verification.json').read_text())
rects=list(csv.DictReader((ROOT/'research/data/level5_remeasured_rectangles.csv').open()))
cells=list(csv.DictReader((ROOT/'research/data/halv_64_cells.csv').open()))
p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
q=np.array(next(f['states'] for f in p['fits'] if f['start_x']==92 and f['step_px']==3
               and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1))
fig,axes=plt.subplots(2,2,figsize=(14,10),layout='constrained')
ax=axes[0,0];ax.imshow(np.array(Image.open(ROOT/'research/sources/crypto5fix.png')),cmap='gray')
for c in control['width_corrections']:
    r=rects[c['index']-1];x,y,w,h=[int(r[k]) for k in ['x','y','W','H']]
    ax.add_patch(Rectangle((x-3,y-3),w+6,h+12,fill=False,edgecolor='red',linewidth=1.5))
    ax.annotate(f"#{c['index']}: W {c['outer_width']} -> {c['true_width']}",(x,y),xytext=(525,y-15),color='red',fontsize=9,arrowprops={'arrowstyle':'->','color':'red'})
ax.set(title='Level 5: two hint lines correct two widths',xlim=(520,730),ylim=(760,470))
ax=axes[0,1];ax.plot(92+3*np.arange(32),q[:32],'.-')
for i in range(9):ax.axvline(91+12*i,color='gray',alpha=.4)
for i in range(8):ax.text(97+12*i,3.35,str(cells[i]['base4_identity']),ha='center',fontsize=9)
ax.set(title='HALV: first eight 12px cells; identity base4 values',xlabel='Image x',ylabel='Normalized fitted q',ylim=(-.2,3.6),xlim=(90,188))
for ax,matrix,title in [
    (axes[1,0],np.array(control['rounded_areas']).reshape(8,8),'Level 5: 64 verified normalized areas'),
    (axes[1,1],np.array([int(r['base4_identity']) for r in cells]).reshape(8,8),'HALV: 64 hypothesized base4 values; not a solution')]:
    ax.imshow(matrix,cmap='Blues',vmin=0,vmax=255)
    for (i,j),v in np.ndenumerate(matrix):ax.text(j,i,str(v),ha='center',va='center',fontsize=8,color='white' if v>155 else 'black')
    for j in [1.5,3.5,5.5]:ax.axvline(j,color='orange',linewidth=1.5)
    ax.set(title=title,xlabel='Cell column; orange lines separate adjacent pairs',ylabel='Row / halving block')
fig.savefig(ROOT/'research/data/pair64_control_comparison.png',dpi=160)
print('Wrote pair64_control_comparison.png')
