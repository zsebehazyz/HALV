#!/usr/bin/env python3
"""Plot exact zero-area consequences in the normalized aligned differences."""
import json
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/halv-matplotlib')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from residual_channels import ROOT


def main():
    data=json.loads((ROOT/'research/data/stateful_bridge_integrity.json').read_text())
    fig,axes=plt.subplots(1,3,figsize=(12,3.5),sharey=True)
    for ax,row in zip(axes,data['nontrivial_zero_area_cells']):
        x=np.arange(5)*3;y=np.array(row['five_difference_nodes'])/2
        ax.plot(x,y,'o-',color='#222222')
        ax.fill_between(x,y,0,where=y>=0,interpolate=True,color='#ef9b46',alpha=.6)
        ax.fill_between(x,y,0,where=y<=0,interpolate=True,color='#4984bf',alpha=.6)
        ax.axhline(0,color='gray',linewidth=.7)
        a,b=row['blocks_1based'];ax.set_title(f'{a}–{b}. blokk, cella {row["cell_zero_based"]} (0-alapú)')
        ax.set_xticks(x);ax.set_xlabel('Cellán belüli hely (3 px / minta)')
        ax.text(.5,.9,'Előjeles területváltozás: pontosan 0',transform=ax.transAxes,ha='center',fontsize=8,
                bbox={'facecolor':'white','alpha':.85,'edgecolor':'none'})
    axes[0].set_ylabel('Igazított eltérés: (cél − forrás) / 2')
    fig.suptitle('Eltérő minták is adhatnak azonos cellaterületet')
    fig.text(.5,.015,'Levezetett geometriai azonosság, normalizált fáziskoordinátákban; nem új PNG-mérés.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.06,1,.95));fig.savefig(ROOT/'research/data/stateful_area_cancellations.png',dpi=160);plt.close(fig)


if __name__=='__main__':main()
