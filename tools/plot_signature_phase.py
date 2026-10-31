#!/usr/bin/env python3
"""Display the measured staircase relation and all eight zero-phase counts."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def main():
    d=json.loads((ROOT/'research/data/signature_phase_decode_check.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    heights=list(map(float,d['heights_exact']));exps=d['floor_log2'];x=np.arange(1,6)
    axes[0].plot(x,heights,'ko-',label='measured heights from reference929.5')
    axes[0].plot(x,2.**np.array(exps),color='steelblue',marker='o',label='lower power-of-two boundary')
    axes[0].plot(x,2.**(np.array(exps)+1),color='gray',ls='--',label='upper boundary (excluded)')
    axes[0].set_yscale('log',base=2)
    for i,(h,e,p) in enumerate(zip(heights,exps,d['zero_phase_middle'])):
        axes[0].annotate(f'h={h:g}; e={e}; phase={p}',(i+1,h),xytext=(0,9),textcoords='offset points',ha='center',fontsize=8)
    axes[0].set(title='floor(log2(height)) mod4 gives zero phase',xlabel='visible stair index',ylabel='height (pixel)',xticks=x)
    axes[0].legend(fontsize=7,loc='lower left')
    rows=d['block_phase_predictions'];counts=np.array([r['zero_counts_by_phase'] for r in rows])
    im=axes[1].imshow(counts,cmap='Blues',vmin=0,vmax=8,aspect='auto')
    for b in range(8):
        for p in range(4):axes[1].text(p,b,str(counts[b,p]),ha='center',va='center',color='white' if counts[b,p]>=5 else 'black')
        axes[1].plot(rows[b]['predicted_zero_phase'],b,'s',ms=30,mfc='none',mec='darkorange',mew=2)
    axes[1].set(title='Zeros in eight cells at each phase; orange=prediction',xlabel='local sample position mod4',ylabel='wave block (1-based)',
                xticks=range(4),yticks=range(8),yticklabels=range(1,9))
    axes[1].text(.02,-.16,'Block1 has a tie. Middle40 cells: exact3H+1L roundtrip.',transform=axes[1].transAxes,fontsize=8)
    fig.colorbar(im,ax=axes[1],label='number of zero states /8')
    fig.suptitle('C18: measured relation; approximately halving heights also explain descending exponents')
    fig.savefig(ROOT/'research/data/signature_phase_audit.png',dpi=160);plt.close(fig)
    print('Saved signature_phase_audit.png')

if __name__=='__main__':main()
