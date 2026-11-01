#!/usr/bin/env python3
"""Visualize complete residual failures and exact source-free inverse control."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from residual_channels import ROOT


def main():
    data=json.loads((ROOT/'research/data/fibonacci_residual_roles_check.json').read_text())
    best=min(data['residual_roles'],key=lambda row:row['mismatch_count'])
    actual=np.array(list(map(int,best['actual_R']))).reshape(8,32)
    predicted=np.array(list(map(int,best['predicted_R']))).reshape(8,32)
    witness=next(row for row in data['coupled_rows'] if row['complete'] and row['frame']=='absolute' and row['transform']=='identity' and row['layout']=='R_then_A' and not row['reverse_bits'] and row['complement'])
    fig,axes=plt.subplots(4,1,figsize=(12,9),gridspec_kw={'height_ratios':[1,1,1,1.8]})
    for ax,array,title in zip(axes[:3],[actual,predicted,actual!=predicted],
            ['Teljes R a legkisebb hibájú próba olvasási koordinátáiban (29 egyes)',
             'Legkisebb hibájú határjóslat: fázisrelatív, toggle_after, végbit; keretezése befejezetlen',
             'Eltérés: 47/256 bit — ezt nem javítjuk cellánként']):
        ax.imshow(array,cmap='Greys',vmin=0,vmax=1,aspect='auto',interpolation='nearest')
        ax.set_title(title,fontsize=10);ax.set_yticks(range(8),range(1,9));ax.set_ylabel('Blokk');ax.set_xticks(range(0,32,4))
    axes[2].set_xlabel('A/R-bithely a 32 bites blokkon belül')
    axes[3].step(range(256),data['q'],where='mid',label='Mért q',linewidth=2,alpha=.5)
    axes[3].plot(range(256),witness['recovered_q'],'.',markersize=3,label='Csak Fibonacci-egészekből visszaállított q')
    for b in range(1,8):axes[3].axvline(32*b-.5,color='gray',alpha=.3)
    axes[3].set_title('Példa a 23 pontos inverzre: abszolút R→A, komplement; 256/256 egyezés',fontsize=10)
    axes[3].set_xlabel('Hullámminta');axes[3].set_yticks([0,1,2,3]);axes[3].legend(loc='upper right',fontsize=8)
    fig.suptitle('C45–C46: a visszaállíthatóság sikeres, a maradék szemantikája továbbra is nyitott',fontsize=12)
    fig.tight_layout();fig.savefig(ROOT/'research/data/fibonacci_residual_roles_audit.png',dpi=160);plt.close(fig)

if __name__=='__main__':main()
