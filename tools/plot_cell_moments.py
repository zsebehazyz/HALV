#!/usr/bin/env python3
"""Illustrate C43 exact area/firstmoment collision, not a decoded key."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/halv-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/halv-cache')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from residual_channels import ROOT


def main():
    xs=np.arange(5)*3
    fig,axes=plt.subplots(1,2,figsize=(9,3.6),sharex=True,sharey=True)
    for ax,values,label,second in zip(axes,[[0,0,2,0,0],[0,1,0,1,0]],['A','B'],['25/6','31/6']):
        height=np.array(values)/2;ax.plot(xs,height,'o-',color='#236a9d');ax.fill_between(xs,height,alpha=.2,color='#236a9d')
        ax.set_title(f'{label}: q='+','.join(map(str,values)))
        ax.text(.5,.88,f'J₀=1, J₁=2, J₂={second}',transform=ax.transAxes,ha='center')
        ax.set_xticks(xs);ax.set_xlabel('Helyi vízszintes koordináta (px)');ax.grid(alpha=.15)
    axes[0].set_ylabel('Normalizált sugár q/2');axes[0].set_ylim(0,1.25)
    fig.suptitle('Azonos terület és első momentum mellett is eltérhet a cella')
    fig.text(.5,.01,'Közös jobb végpont: 0. A J-momentumok u=x/3 koordinátában értendők; nem kulcsadatok.',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.06,1,.94));fig.savefig(ROOT/'research/data/cell_moment_collision.png',dpi=160);plt.close(fig)


if __name__=='__main__':main()
