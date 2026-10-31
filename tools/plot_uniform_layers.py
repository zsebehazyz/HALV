#!/usr/bin/env python3
"""Plot all64 primary/residual cells, keeping every exceptional bit visible."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def main():
    d=json.loads((ROOT/'research/data/uniform_phase_layers_check.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(11,5),layout='constrained')
    for ax,field,title,cmap in zip(axes,['primary_nibble','residual_nibble'],
            ['Primary4 bits: same extraction in every cell','Residual4 bits:44 zero cells,20 nonzero cells'],['Blues','Oranges']):
        values=np.array([r[field] for r in d['cell_rows']]).reshape(8,8)
        im=ax.imshow(values,cmap=cmap,vmin=0,vmax=15)
        for b in range(8):
            for c in range(8):ax.text(c,b,f'{values[b,c]:x}',ha='center',va='center',color='white' if values[b,c]>=9 else 'black')
        ax.set(title=title,xlabel='cell index within block',ylabel='wave block (1-based)',
               xticks=range(8),yticks=range(8),yticklabels=range(1,9))
        fig.colorbar(im,ax=ax,label='nibble value')
    for row in d['exception_rows']:
        for c in row['cell_indices_nonzero']:
            axes[1].plot(c,row['block_1based']-1,'s',ms=27,mfc='none',mec='crimson',mew=1.7)
    fig.suptitle('C20: uniform lossless split; red boxes mark the12 nonzero zero-phase samples')
    fig.savefig(ROOT/'research/data/uniform_phase_layers.png',dpi=160);plt.close(fig)
    print('Saved uniform_phase_layers.png')

if __name__=='__main__':main()
