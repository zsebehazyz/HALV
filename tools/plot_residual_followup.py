#!/usr/bin/env python3
"""C21-C23 evidence: heldout image sensitivity and exact geometric corrections."""
import json
from fractions import Fraction
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def main():
    d=json.loads((ROOT/'research/data/residual_physics_check.json').read_text())
    fig,axes=plt.subplots(1,3,figsize=(14,4.5),layout='constrained')
    colors={1:'steelblue',2:'darkorange',8:'seagreen'}
    for block,color in colors.items():
        for offset,style in [(1,'-o'),(2,'--s')]:
            xx=[];yy=[]
            for run in d['pixel_runs']:
                if run['roi']!='wave_only_tail' or run['fit_offset']!=offset:continue
                constraint=next(r for r in run['constraints'] if r['constraint']=='full_R_zero_everywhere')
                row=constraint['blocks'][block-1];xx.append(run['width']);yy.append(row['ratio_to_free'])
            axes[0].plot(xx,yy,style,color=color,label=f'block{block}, train column+{offset}')
    axes[0].set(title='Heldout image error when R is forced to0',xlabel='fixed stroke width scale',ylabel='constrained/free MSE ratio')
    axes[0].legend(fontsize=7)
    tail=[]
    for roi in ['legacy','wave_only_tail']:
        run=next(r for r in d['pixel_runs'] if r['width']==1 and r['fit_offset']==1 and r['roi']==roi)
        row=next(r for r in run['constraints'] if r['constraint']=='full_R_zero_everywhere')['blocks'][7]
        tail.append(row['ratio_to_free'])
    axes[1].bar(['legacy ROI\nincludes signature','wave-only ROI'],tail,color=['gray','seagreen'])
    for i,v in enumerate(tail):axes[1].text(i,v+.05,f'{v:.3f}x',ha='center')
    axes[1].set(title='Tail: background changed the percentage',ylabel='constrained/free heldout MSE ratio',ylim=(0,max(tail)+.8))
    area=next(r for r in d['exact_area_corrections'] if r['domain']=='normalized')
    values=np.array([float(Fraction(v)) for v in area['radius_area_corrections_exact']])
    axes[2].bar(range(64),values,color='darkorange')
    for x in [7.5,15.5,23.5,31.5,39.5,47.5,55.5]:axes[2].axvline(x,color='gray',lw=.4)
    axes[2].set(title='Exact R area contribution:22 cells, total48',xlabel='12px cell index',ylabel='normalized q/2 radius area')
    fig.suptitle('Residual retained by the pixels; tested predictor families did not identify its generator')
    fig.savefig(ROOT/'research/data/residual_followup_audit.png',dpi=160);plt.close(fig)
    print('Saved residual_followup_audit.png')

if __name__=='__main__':main()
