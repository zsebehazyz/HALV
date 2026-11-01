#!/usr/bin/env python3
"""Independent quadrature and full-vector least-squares replay of C42 winners."""
import hashlib
import json
import math
import numpy as np
from PIL import Image
from scipy.integrate import quad
from scipy.special import ndtr
from residual_channels import ROOT


def independently_render_mask(pattern,recipe,ys):
    groups={'NMRM':[(3,1),(3,3),(1,3,1),(3,3)],'XEX':[(3,1,1,3),(1,),(3,1,1,3)]}
    intervals=[];t=0
    if pattern=='regular4':intervals=[(4*i,4*i+3) for i in range(4)]
    else:
        for ci,group in enumerate(groups[pattern]):
            for mi,width in enumerate(group):
                intervals.append((t,t+width));t+=width
                if mi<len(group)-1:t+=1
            if ci<len(groups[pattern])-1:t+=3
    origin=recipe['origin_y'];unit=recipe['unit_pixels'];sigma=recipe['vertical_sigma'];values=[]
    for y in ys:
        value=0.
        for first,last in intervals:
            a=origin+unit*first;b=origin+unit*last
            if sigma==0:value+=max(0,min(y+.5,b)-max(y-.5,a))
            else:
                value+=quad(lambda t:ndtr((y+.5-t)/sigma)-ndtr((y-.5-t)/sigma),a,b,
                            epsabs=1e-10,epsrel=1e-10,limit=100)[0]
        values.append(value)
    return np.clip(values,0,1)


def main():
    result=json.loads((ROOT/'research/data/marker_raster_check.json').read_text())
    for name,digest in result['input_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    stored=np.load(ROOT/'research/data/marker_raster_predictions.npz')
    observed=np.array(Image.open(ROOT/'research/sources/cryptoHALV.png'),float)[438:513,90:93]
    assert np.array_equal(observed,stored['observed']);ys=stored['rows'];train=ys<=474;held=~train
    positive=train&(observed[:,1]>=3);design=np.c_[observed[positive,1],np.ones(positive.sum())]
    coefficient=np.linalg.lstsq(design,observed[positive][:,[0,2]].mean(1),rcond=None)[0];c,d=coefficient
    assert np.allclose(coefficient,[result['transverse_profile_training_only']['slope_c'],result['transverse_profile_training_only']['intercept_d']])
    palette=[0,23,47,75,107,141,178,216];index=0;records=[];search=np.load(ROOT/'research/data/marker_raster_search.npz')
    for entry in result['results']:
        for variant in entry['variants']:
            recipe=variant['training_selected_recipe'];m=independently_render_mask(entry['pattern'],recipe,ys)
            if recipe['carrier_period'] is None:r=np.ones(len(ys))
            else:
                r=np.array([palette[int(math.floor(8*(((y-438)/recipe['carrier_period']+recipe['carrier_phase'])%1)))]/216 for y in ys])
            linear=np.c_[c*m*r,m*r,c*m*r];additive=np.c_[d*m*(r>0),np.zeros(len(m)),d*m*(r>0)]
            gain=float(np.sum(linear[train]*(observed-additive)[train])/np.sum(linear[train]**2));gain=float(np.clip(gain,0,255))
            pred=gain*linear+additive
            assert abs(gain-recipe['gain'])<1e-6
            assert np.max(abs(pred-stored['predictions'][index]))<1e-5
            for label,mask in [('training',train),('heldout',held)]:
                error=pred[mask]-observed[mask];metrics=variant[label]
                assert abs(float(np.mean(error**2))-metrics['mse'])<1e-5
                assert abs(float(np.max(abs(error)))-metrics['max_abs_error'])<1e-5
                assert int(np.sum(abs(error)>1))==metrics['intensity_errors_gt1']
            grid=search[entry['pattern']+'_'+variant['carrier_kind']]
            assert abs(float(grid[:,4].min())-variant['coarse_training_winner']['training_sse'])<1e-8
            records.append({'pattern':entry['pattern'],'carrier':variant['carrier_kind'],
                            'training_MSE':variant['training']['mse'],'heldout_MSE':variant['heldout']['mse'],
                            'heldout_errors_gt1':variant['heldout']['intensity_errors_gt1']})
            index+=1
    assert index==6 and not result['patterns_passing_pixel_gate'] and result['clock_propagated_to_wave'] is False
    assert result['global_primary_selected_by_training']=='regular4'
    out={'purpose':'Independent C42 quadrature/least-squares audit, not a new hypothesis search',
         'independently_replayed_variants':index,'pixel_values_per_variant':int(observed.size),
         'global_training_selected_reference':'regular4','passing_pixel_gate':0,'variants':records,
         'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [
             'research/data/marker_raster_check.json','research/data/marker_raster_predictions.npz',
             'research/data/marker_raster_search.npz','tools/audit_marker_raster.py']}}
    (ROOT/'research/data/marker_raster_integrity.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
