#!/usr/bin/env python3
"""C42: train-only calibrated three-column forward raster comparisons."""
import hashlib
import itertools
import json
import numpy as np
from PIL import Image
from scipy.special import ndtr
from residual_channels import ROOT

ROWS=np.arange(438,513,dtype=float)
TRAIN=ROWS<=474
TEST=~TRAIN
PALETTE=np.array([0,23,47,75,107,141,178,216],float)/216
CODES={'N':'-.','M':'--','R':'.-.','X':'-..-','E':'.'}


def intervals(pattern):
    if pattern=='regular4':return np.array([[4*i,4*i+3] for i in range(4)],float)
    out=[];t=0.
    for ci,char in enumerate(pattern):
        for mi,mark in enumerate(CODES[char]):
            width=1 if mark=='.' else 3;out.append([t,t+width]);t+=width
            if mi<len(CODES[char])-1:t+=1
        if ci<len(pattern)-1:t+=3
    return np.array(out)


def gaussian_integral(t,sigma):
    z=t/sigma
    return t*ndtr(z)+sigma*np.exp(-z*z/2)/np.sqrt(2*np.pi)


def masks(pattern,origins,units,sigma):
    out=np.zeros((len(origins),len(ROWS)),float)
    for first,last in intervals(pattern):
        a=origins[:,None]+units[:,None]*first;b=origins[:,None]+units[:,None]*last
        lo=ROWS[None,:]-.5;hi=ROWS[None,:]+.5
        if sigma==0:out+=np.maximum(0,np.minimum(hi,b)-np.maximum(lo,a))
        else:
            out+=gaussian_integral(hi-a,sigma)-gaussian_integral(lo-a,sigma)
            out-=gaussian_integral(hi-b,sigma)-gaussian_integral(lo-b,sigma)
    return np.clip(out,0,1)


def carrier(period,phase):
    if period is None:return np.ones(len(ROWS))
    index=np.floor(8*np.mod((ROWS-438)/period+phase,1)).astype(int)
    return PALETTE[index]


def transverse(observed):
    selected=TRAIN&(observed[:,1]>=3)
    design=np.c_[observed[selected,1],np.ones(selected.sum())]
    c,d=np.linalg.lstsq(design,observed[selected][:,[0,2]].mean(1),rcond=None)[0]
    assert c>0 and d>=0
    return float(c),float(d)


def score_matrix(mask,carriers,observed,c,d):
    """All geometry/carrier scores, exactly the same3-column training objective."""
    m=mask[:,TRAIN];r=carriers[:,TRAIN];active=(r>0).astype(float)
    y=observed[TRAIN];m2=m*m
    numerator=m@(r*(y[:,1]+c*(y[:,0]+y[:,2]))).T-2*c*d*(m2@(r*active).T)
    denominator=(1+2*c*c)*(m2@(r*r).T)
    gain=np.clip(np.divide(numerator,denominator,out=np.zeros_like(numerator),where=denominator>1e-12),0,255)
    constant=float(np.sum(y*y))-2*d*(m@(active*(y[:,0]+y[:,2])).T)+2*d*d*(m2@active.T)
    sse=np.maximum(0,constant-2*gain*numerator+gain*gain*denominator)
    return sse,gain


def render(mask,ramp,gain,c,d):
    center=gain*mask*ramp;side=c*center+d*mask*(ramp>0)
    return np.c_[side,center,side]


def measure(pred,obs,selection):
    errors=pred[selection]-obs[selection];foreground=np.any(obs[selection]>0,axis=1)
    return {'pixels':int(errors.size),'mse':float(np.mean(errors**2)),
            'foreground_mse':float(np.mean(errors[foreground]**2)) if foreground.any() else None,
            'max_abs_error':float(np.max(abs(errors))),'intensity_errors_gt1':int(np.sum(abs(errors)>1))}


def small_grid(center,radius,step,bounds):
    v=np.round(center+np.arange(-int(round(radius/step)),int(round(radius/step))+1)*step,10)
    return np.unique(v[(v>=bounds[0]-1e-9)&(v<=bounds[1]+1e-9)])


def evaluate(pattern,origins,units,sigmas,carrier_recipes,observed,c,d,archive):
    oo,uu=np.meshgrid(origins,units,indexing='ij');oo=oo.flatten();uu=uu.flatten()
    ramps=np.array([carrier(p,ph) for p,ph in carrier_recipes]);best=None;trials=0
    for sigma in sigmas:
        mm=masks(pattern,oo,uu,float(sigma));scores,gains=score_matrix(mm,ramps,observed,c,d)
        j,k=np.unravel_index(int(np.argmin(scores)),scores.shape);trials+=scores.size
        candidate={'origin_y':float(oo[j]),'unit_pixels':float(uu[j]),'vertical_sigma':float(sigma),
                   'carrier_period':carrier_recipes[k][0],'carrier_phase':carrier_recipes[k][1],
                   'gain':float(gains[j,k]),'training_sse':float(scores[j,k])}
        if best is None or candidate['training_sse']<best['training_sse']:best=candidate
        if archive is not None:
            ck=scores.argmin(1);archive.append(np.c_[oo,uu,np.full(len(oo),sigma),ck,scores[np.arange(len(oo)),ck],gains[np.arange(len(oo)),ck]])
    return best,trials


def candidate_prediction(pattern,recipe,c,d):
    m=masks(pattern,np.array([recipe['origin_y']]),np.array([recipe['unit_pixels']]),recipe['vertical_sigma'])[0]
    r=carrier(recipe['carrier_period'],recipe['carrier_phase'])
    return render(m,r,recipe['gain'],c,d)


def calibrate():
    m=masks('regular4',np.array([443.5]),np.array([1.]),0)[0]
    assert m[np.where(ROWS==444)[0][0]]==1 and m[np.where(ROWS==443)[0][0]]==0
    assert abs(float(m.sum())-12)<1e-12
    smoothed=masks('regular4',np.array([443.5]),np.array([1.]),.5)[0]
    assert abs(float(smoothed.sum())-12)<1e-9
    brightness=np.array([0,0,23,47,75,107,141,178,216]+[75]*66,float)
    side=.4*brightness+3*(brightness>0);synthetic=np.c_[side,brightness,side]
    c,d=transverse(synthetic);assert np.allclose([c,d],[.4,3],atol=1e-12)
    origin=443.5;unit=2.;sigma=0.;r=carrier(7.,.25)
    mm=masks('NMRM',np.array([origin]),np.array([unit]),sigma)
    truth=render(mm[0],r,216.,c,d);score,gain=score_matrix(mm,r[None,:],truth,c,d)
    assert abs(gain[0,0]-216)<1e-9 and score[0,0]<1e-7
    # Independent full-vector least-squares gain, with the fixed additive side term.
    coeff=np.c_[c*mm[0]*r,mm[0]*r,c*mm[0]*r]
    additive=np.c_[d*mm[0]*(r>0),np.zeros(len(ROWS)),d*mm[0]*(r>0)]
    direct=float(np.sum(coeff[TRAIN]*(truth-additive)[TRAIN])/np.sum(coeff[TRAIN]**2))
    assert abs(direct-gain[0,0])<1e-9
    known,checks=evaluate('NMRM',np.array([443.25,443.5,443.75]),np.array([1.975,2.,2.025]),
                          [0.,.25],[(None,0.),(7.,.25),(7.,.1875)],truth,c,d,None)
    predicted=candidate_prediction('NMRM',known,c,d)
    assert np.max(abs(predicted[TEST]-truth[TEST]))<1e-6
    return {'pixel_box_known_answer':True,'Gaussian_area_conservation':True,
            'transverse_profile_recovered':True,'synthetic_raster_gain_and_SSE':True,
            'analytic_gain_direct_vector_check':True,'synthetic_train_selected_heldout_exact':True,
            'synthetic_search_candidates':checks}


def main():
    spec=json.loads((ROOT/'research/models/marker_raster_v1.json').read_text());tests=calibrate()
    observed=np.array(Image.open(ROOT/'research/sources/cryptoHALV.png'),float)[438:513,90:93]
    c,d=transverse(observed);grid=spec['coarse_grid'];results=[];archives={};prediction_arrays=[]
    origins=np.arange(439.5,446.5+.001,.25);units=np.round(np.arange(1,5+.001,.025),10)
    for pattern in ['NMRM','XEX','regular4']:
        variants=[]
        for kind in ['flat','palette']:
            carriers=[(None,0.)] if kind=='flat' else [(float(p),float(ph)) for p in np.arange(6.5,7.75+.001,.125) for ph in np.arange(16)/16]
            archive=[];coarse,count=evaluate(pattern,origins,units,grid['vertical_sigma'],carriers,observed,c,d,archive)
            archives[pattern+'_'+kind]=np.vstack(archive)
            ro=small_grid(coarse['origin_y'],.25,.05,(439.5,446.5));ru=small_grid(coarse['unit_pixels'],.025,.005,(1,5))
            rs=small_grid(coarse['vertical_sigma'],.125,.025,(0,1))
            if kind=='flat':fine_carriers=[(None,0.)]
            else:
                periods=small_grid(coarse['carrier_period'],.125,.025,(6.5,7.75))
                phases=np.unique(np.round(np.mod(coarse['carrier_phase']+np.arange(-4,5)/64,1),10))
                fine_carriers=[(float(p),float(ph)) for p in periods for ph in phases]
            refined,n=evaluate(pattern,ro,ru,rs,fine_carriers,observed,c,d,None)
            selected=refined if refined['training_sse']<coarse['training_sse'] else coarse
            pred=candidate_prediction(pattern,selected,c,d)
            train=measure(pred,observed,TRAIN);held=measure(pred,observed,TEST)
            assert abs(train['mse']*int(TRAIN.sum())*3-selected['training_sse'])<1e-5
            record={'pattern':pattern,'carrier_kind':kind,'coarse_trials':count,'refinement_trials':n,
                    'coarse_training_winner':coarse,'training_selected_recipe':selected,
                    'training':train,'heldout':held,'all_heldout_within1':held['intensity_errors_gt1']==0}
            variants.append(record);prediction_arrays.append(pred)
        primary=min(variants,key=lambda r:r['training']['mse'])
        results.append({'pattern':pattern,'variants':variants,'primary_selected_by_training':primary})
        print(pattern,'train',round(primary['training']['mse'],3),'heldout',round(primary['heldout']['mse'],3),
              'heldout max',round(primary['heldout']['max_abs_error'],3),'gate',primary['all_heldout_within1'],flush=True)
    np.savez_compressed(ROOT/'research/data/marker_raster_search.npz',**archives)
    np.savez_compressed(ROOT/'research/data/marker_raster_predictions.npz',observed=observed,
                        predictions=np.array(prediction_arrays),rows=ROWS.astype(int))
    names=['research/models/marker_raster_v1.json','research/sources/cryptoHALV.png','tools/check_marker_raster.py']
    gates=[r['pattern'] for r in results if r['primary_selected_by_training']['all_heldout_within1']]
    out={'model':'C42','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in names},
         'calibration':tests,'transverse_profile_training_only':{'slope_c':c,'intercept_d':d},
         'train_rows':[438,474],'heldout_rows':[475,512],'results':results,'patterns_passing_pixel_gate':gates,
         'global_primary_selected_by_training':min(results,key=lambda r:r['primary_selected_by_training']['training']['mse'])['pattern'],
         'clock_propagated_to_wave':False,'full_q_and_R_preserved':True,'geometric_branch_retained':True,
         'no_private_key_search':True,'limitations':spec['limitations']}
    (ROOT/'research/data/marker_raster_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Passing gate:',gates,flush=True)


if __name__=='__main__':main()
