#!/usr/bin/env python3
"""Forensic plots for C15/C16; use already saved results and fixed model choices."""
import json
from fractions import Fraction
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from check_boundary33 import distance_field,render

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    f=next(f for f in p['fits'] if f['start_x']==92 and f['step_px']==3
           and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1)
    xs=np.array(f['coordinates']);ys=np.array(f['states'])*np.array(f['scales'])
    a=np.array(Image.open(ROOT/'research/sources/cryptoHALV.png'),float)/255
    result=json.loads((ROOT/'research/data/boundary33_check.json').read_text())
    width=result['chosen_global_width'];boundary=result['boundaries'][1]
    best=next(r for r in boundary['width_models'] if r['width']==width)['best_independent_by_training']
    columns=list(range(278,291));continuous=render(distance_field(xs,ys,columns),width)
    height=best['endpoint']*f['scales'][63]
    extra=[((284,height),(284,ys[64]))] if best['join']=='vertical_connector' else []
    independent=render(distance_field(xs,ys,columns,extra,(63,height)),width)
    fig,ax=plt.subplots(2,2,figsize=(11,8),layout='constrained')
    ax[0,0].imshow(a[330:421,278:291],cmap='gray',vmin=0,vmax=1,extent=[277.5,290.5,420.5,329.5],aspect='auto')
    ax[0,0].plot(xs[62:67],475-ys[62:67],color='lime',lw=1,label='shared endpoint')
    ax[0,0].plot([281,284,284,287],[475-ys[63],475-height,475-ys[64],475-ys[65]],color='orange',lw=1,ls='--',label='best integer endpoint')
    ax[0,0].axvline(284,color='cyan',lw=.6);ax[0,0].set_title('Original pixels: informative block boundary')
    ax[0,0].set(xlabel='x (pixel)',ylabel='y (pixel)',xlim=(277.5,290.5),ylim=(420.5,329.5));ax[0,0].legend(fontsize=8)
    yy=np.arange(330,421);col=columns.index(284)
    ax[0,1].plot(yy,a[330:421,284],color='black',label='observed')
    ax[0,1].plot(yy,continuous[330-85:421-85,col],label='shared endpoint')
    ax[0,1].plot(yy,independent[330-85:421-85,col],ls='--',label='best integer endpoint')
    ax[0,1].set(title='Held-out column x=284 (upper curve)',xlabel='y (pixel)',ylabel='brightness /255');ax[0,1].legend(fontsize=8)
    tailcols=list(range(853,863));base=render(distance_field(xs,ys,tailcols),width)
    ext=render(distance_field(xs,ys,tailcols,[((857,ys[-1]),(860,0))]),width)
    ax[1,0].plot(tailcols,a[475,tailcols],'ko-',label='observed')
    ax[1,0].plot(tailcols,base[475-85],label='ends at857')
    ax[1,0].plot(tailcols,ext[475-85],ls='--',label='extended to860, endpoint0')
    ax[1,0].set(title='Terminal centerline (wave-only ROI)',xlabel='x (pixel)',ylabel='brightness /255');ax[1,0].legend(fontsize=8)
    widths=[r['width'] for r in boundary['width_models']]
    ax[1,1].semilogy(widths,[r['continuous']['validation_mse'] for r in boundary['width_models']],'o-',label='shared endpoint')
    ax[1,1].semilogy(widths,[r['best_independent_by_training']['validation_mse'] for r in boundary['width_models']],'o-',label='integer endpoint')
    ax[1,1].set(title='Boundary result across fixed stroke widths',xlabel='stroke scale',ylabel='held-out pixel MSE');ax[1,1].legend(fontsize=8)
    fig.suptitle('C15: approximate raster comparison; no proof of logical sample indexing')
    fig.savefig(ROOT/'research/data/boundary33_audit.png',dpi=160);plt.close(fig)

    profiles=json.loads((ROOT/'research/data/fractional_area_profiles.json').read_text())
    fig,ax=plt.subplots(2,1,figsize=(12,6),layout='constrained')
    for i,domain in enumerate(['normalized_nodes','physical_nodes']):
        chosen={p['channel']:np.array([float(Fraction(v)) for v in p['values64_exact']])
                for p in profiles if p['domain']==domain and p['anchor']==92 and p['extent']=='radius'}
        h=chosen['high_bit_only_control'];corrected=chosen['half_q_corrected']
        ax[i].plot(range(64),h,label='area from H only',color='steelblue')
        ax[i].plot(range(64),corrected,label='area from H + L/2',color='darkorange')
        ax[i].fill_between(range(64),h,corrected,color='orange',alpha=.3,label='exact L/2 contribution')
        for x in range(8,64,8):ax[i].axvline(x-.5,color='gray',lw=.5)
        ax[i].set(title=f'{domain}, anchor92, radius area',xlabel='12px cell index',ylabel='area in declared domain')
        ax[i].legend(fontsize=8)
    fig.suptitle('C16: fractions retained before rounding; physical scale not yet identified for key bytes')
    fig.savefig(ROOT/'research/data/fractional_area_audit.png',dpi=160);plt.close(fig)
    print('Saved boundary33_audit.png and fractional_area_audit.png')

if __name__=='__main__':main()
