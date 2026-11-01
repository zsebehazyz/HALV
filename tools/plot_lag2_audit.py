#!/usr/bin/env python3
"""Reproduce the supplied alignments and show prediction/control limitations."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from residual_channels import ROOT,nominal_states

def main():
    q=nominal_states().reshape(8,32);r=json.loads((ROOT/'research/data/lag2_halving_check.json').read_text())
    fig,axes=plt.subplots(3,1,figsize=(13,7),layout='constrained')
    for ax,b,shift in zip(axes,[2,3,4],[26,18,14]):
        aligned=np.roll(q[b+2],shift);im=ax.imshow(np.vstack([q[b],aligned]),cmap='viridis',vmin=0,vmax=3,aspect='auto',interpolation='nearest')
        for x in np.flatnonzero(q[b]!=aligned):
            for y in range(2):ax.add_patch(Rectangle((x-.49,y-.49),.98,.98,fill=False,ec='orangered',lw=1.5))
        ax.set(title=f'Blocks{b+1}-{b+3}: {int(sum(q[b]==aligned))}/32 matches; right shift{shift}',
               yticks=[0,1],yticklabels=[f'block{b+1}',f'block{b+3}, shifted'],xticks=range(0,32,2),xlabel='sample index')
    fig.colorbar(im,ax=axes,label='normalized state0..3',shrink=.7)
    fig.suptitle('C25: independently reproduced lag2 block alignments')
    fig.savefig(ROOT/'research/data/lag2_pair_alignment.png',dpi=160);plt.close(fig)
    model=r['forecast_models'][2];pred=np.array(model['predicted_target_samples']);actual=np.array(model['actual_target_samples'])
    fig=plt.figure(figsize=(13,7),layout='constrained');grid=fig.add_gridspec(2,2,height_ratios=[1,1.15])
    ax=fig.add_subplot(grid[0,:]);ax.imshow(np.vstack([pred,actual]),cmap='viridis',vmin=0,vmax=3,aspect='auto',interpolation='nearest')
    for x in np.flatnonzero(pred!=actual):
        for y in range(2):ax.add_patch(Rectangle((x-.49,y-.49),.98,.98,fill=False,ec='red',lw=1.8))
    ax.set(title='a=10 fitted on the first two pairs predicts block7:25/32; seven high-bit errors',
           yticks=[0,1],yticklabels=['predicted block7','actual block7'],xticks=range(0,32,2),xlabel='sample index')
    ax=fig.add_subplot(grid[1,0]);positions=np.arange(0,32,4)
    ax.plot(range(8),pred[positions]&1,'o-',lw=3,label='prediction')
    ax.plot(range(8),actual[positions]&1,'x--',ms=10,label='actual')
    ax.set(title='All8 variable low-bit slots match (3 ones)',xlabel='allowed slot index',ylabel='low bit',yticks=[0,1],xticks=range(8));ax.legend()
    ax=fig.add_subplot(grid[1,1]);data=np.load(ROOT/'research/data/lag2_control_scores.npz')
    for size,color in [(4,'steelblue'),(8,'darkorange')]:
        values=data[f'chunk{size}_max_forecast'];record=r['controls'][str(size)]['max_forecast']
        ax.hist(values,bins=np.arange(10,33)-.5,density=True,histtype='step',lw=2,color=color,
                label=f'chunk{size}, tail={record["plus_one_fraction"]:.4f}')
    ax.axvline(25,color='black',ls='--',label='observed25')
    ax.set(title='Controls: maximum heldout score over4 windows',xlabel='heldout target matches /32',ylabel='fraction per score');ax.legend(fontsize=8)
    fig.suptitle('Forecast reconstruction, not an independent prospective discovery; a=10 remains unexplained')
    fig.savefig(ROOT/'research/data/lag2_prediction_audit.png',dpi=160);plt.close(fig)
    print('Saved lag2_pair_alignment.png and lag2_prediction_audit.png')

if __name__=='__main__':main()
