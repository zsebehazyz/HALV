#!/usr/bin/env python3
"""Show historical Level2 footer pixels beside the independently decoded address."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from residual_channels import ROOT

def main():
    result=json.loads((ROOT/'research/data/historical_level2_control.json').read_text())
    a=np.array(Image.open(ROOT/'research/sources/history_level2_crypto2__crypto2.png'))
    fig,axes=plt.subplots(2,1,figsize=(13,3.5),layout='constrained')
    axes[0].imshow(a[670:686,365:590],cmap='gray',interpolation='nearest',aspect='auto')
    axes[0].set_title('Original Level2 address pixels (nearest-neighbor display)');axes[0].axis('off')
    valid=next(v for v in result['candidate_readings'] if v['validation']=='valid')
    axes[1].text(.02,.7,'Decoded uncompressed address: '+valid['historical_addresses']['uncompressed'],fontfamily='monospace',fontsize=14)
    axes[1].text(.02,.3,'51 sectors; 306/306 neighbor complement constraints; one of two WIF readings passes checksum',fontsize=12)
    axes[1].axis('off');fig.savefig(ROOT/'research/data/historical_level2_audit.png',dpi=160);plt.close(fig)
    print('Saved historical_level2_audit.png')

if __name__=='__main__':main()
