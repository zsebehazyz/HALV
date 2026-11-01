#!/usr/bin/env python3
"""C41: train-only affine price-shape fits and full-family shift references."""
import csv
import hashlib
import json
import numpy as np
from residual_channels import ROOT,nominal_states

TRAIN=np.arange(64,192)
TEST=np.r_[0:64,192:256]


def affine(x,y):
    xx=x[TRAIN];yy=y[TRAIN];den=np.sum((xx-xx.mean())**2)
    gain=float(np.sum((xx-xx.mean())*(yy-yy.mean()))/den) if den else 0.
    offset=float(yy.mean()-gain*xx.mean());pred=gain*x+offset
    mse=float(np.mean((pred[TEST]-y[TEST])**2));baseline=float(np.mean((yy.mean()-y[TEST])**2))
    corr=float(np.corrcoef(pred[TEST],y[TEST])[0,1]) if np.std(pred[TEST])>1e-12 else None
    return {'gain':gain,'offset':offset,'heldout_mse':mse,'constant_training_mean_mse':baseline,
            'heldout_skill':1-mse/baseline if baseline else None,'heldout_prediction_correlation':corr},pred


def calibration():
    x=np.linspace(0,1,256);y=2*x+3;result,pred=affine(x,y)
    assert np.allclose(pred,y) and abs(result['heldout_skill']-1)<1e-12
    result,_=affine(np.ones(256),y);assert result['gain']==0 and abs(result['heldout_skill'])<1e-12
    return {'known_affine_heldout':True,'constant_input_control':True}


def main():
    spec=json.loads((ROOT/'research/models/price_shape_revisit_v1.json').read_text());tests=calibration()
    rows=list(csv.DictReader((ROOT/'research/data/btc_usd_daily_2020_to_halving.csv').open()))
    curves=[];export=[]
    for start in spec['starts']:
        selected=[r for r in rows if start<=r['date']<='2024-04-19']
        price=np.array([float(r['price_usd']) for r in selected]);log=np.log(price)
        for name,raw in [('price',price),('log_price',log),('absolute_daily_log_return',abs(np.diff(log)))]:
            x=np.interp(np.linspace(0,len(raw)-1,256),np.arange(len(raw)),raw)
            curves.append(({'start':start,'end':selected[-1]['date'],'signal':name,'native_values':len(raw)},x))
            export.extend([start,name,i,float(value)] for i,value in enumerate(x))
    with (ROOT/'research/data/price_shape_resampled256.csv').open('w',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(['start','signal','index','value']);writer.writerows(export)
    q=nominal_states().flatten();scales=128//2**(np.arange(256)//32)
    targets=[('normalized_q',q),('physical_height_q_times_scale',q*scales)]
    def family(shift):
        records=[]
        for recipe,source in curves:
            for reverse in [False,True]:
                x=np.roll(source[::-1] if reverse else source,shift)
                for label,target in targets:
                    result,pred=affine(x,target)
                    records.append({**recipe,'reverse':reverse,'target':label,**result})
        return records
    observed=family(0);assert len(observed)==24
    best=max(observed,key=lambda r:r['heldout_skill']);references=[]
    for shift in range(1,256):
        records=family(shift);references.append({'cyclic_shift':shift,'selected_best_heldout_skill':max(r['heldout_skill'] for r in records)})
    count=sum(r['selected_best_heldout_skill']>=best['heldout_skill']-1e-12 for r in references)
    assert family(0)==observed
    names=['research/models/price_shape_revisit_v1.json','research/data/btc_usd_daily_2020_to_halving.csv',
           'research/sources/coinmetrics.json','research/data/pixel_measurements.json',
           'tools/check_price_shape_revisit.py','tools/residual_channels.py']
    out={'model':'C41','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in names},
         'calibration':tests,'model_count':len(observed),'models':observed,
         'best_exploratory_model':best,'family_shift_references':references,
         'shift_references_as_good':count,'shift_reference_fraction_including_identity':(1+count)/256,
         'reference_is_not_global_p_value':True,'no_private_key_search':True,'limitations':spec['limitations']}
    (ROOT/'research/data/price_shape_revisit_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'model':'C41','best_exploratory_model':best,'shift_references_as_good_out_of255':count,
                      'conditional_reference_fraction':(1+count)/256},indent=2))


if __name__=='__main__':main()
