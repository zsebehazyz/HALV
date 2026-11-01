#!/usr/bin/env python3
"""Scientific C42 figure: full marker ROI and train-selected forward predictions."""
import json
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/halv-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/halv-cache')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from residual_channels import ROOT


def main():
    results=json.loads((ROOT/'research/data/marker_raster_check.json').read_text())
    data=np.load(ROOT/'research/data/marker_raster_predictions.npz');obs=data['observed'];ys=data['rows']
    fig,axes=plt.subplots(4,1,figsize=(12,11),sharex=True,gridspec_kw={'height_ratios':[.6,1,1,1]})
    axes[0].imshow(obs.T,origin='lower',aspect='auto',cmap='gray',vmin=0,vmax=255,
                   extent=(437.5,512.5,89.5,92.5));axes[0].set_yticks([90,91,92]);axes[0].set_ylabel('PNG x')
    axes[0].set_title('C42: három oszlop; illesztés y438–474, ellenőrzés y475–512')
    for i,entry in enumerate(results['results']):
        selected=entry['primary_selected_by_training'];which=0 if selected['carrier_kind']=='flat' else 1
        pred=data['predictions'][2*i+which];ax=axes[i+1]
        ax.plot(ys,obs[:,1],'.-',color='black',lw=.8,label='Mért közép')
        ax.plot(ys,pred[:,1],color='#dc7b18',lw=1.2,label='Jósolt közép')
        ax.plot(ys,obs[:,[0,2]].mean(1),'.',color='#777777',label='Mért szélek átlaga')
        ax.plot(ys,pred[:,0],color='#287bb5',lw=1,label='Jósolt szélek')
        ax.axvspan(474.5,512.5,color='#c93c54',alpha=.08);ax.set_ylim(-5,260)
        ax.set_title(f'{entry["pattern"]}: tanító MSE {selected["training"]["mse"]:.2f}, ellenőrző MSE {selected["heldout"]["mse"]:.2f}; nem teljesíti a ±1 kaput',fontsize=10)
        ax.set_ylabel('Fényesség');ax.grid(alpha=.15)
    for ax in axes:ax.axvline(474.5,color='#a82542',ls='--',lw=.8)
    axes[1].legend(loc='upper left',ncol=4,fontsize=8)
    axes[-1].set_xlabel('Eredeti PNG pixelsora (y)')
    fig.tight_layout();fig.savefig(ROOT/'research/data/marker_raster_comparison.png',dpi=160);plt.close(fig)


if __name__=='__main__':main()
