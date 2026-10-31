#!/usr/bin/env python3
"""C15: finite-segment geometry at amplitude block boundaries and final endpoint."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]

def distance_field(xs,ys,xcols,extra_segments=(),replace_segment=None):
    yy,xx=np.meshgrid(np.arange(85,866),np.array(xcols),indexing='ij')
    best=np.full(xx.shape,np.inf,dtype=float)
    segments=[((xs[i],ys[i]),(xs[i+1],ys[i+1])) for i in range(len(xs)-1)]
    if replace_segment is not None:
        index,end_y=replace_segment;segments[index]=(segments[index][0],(xs[index+1],end_y))
    segments+=list(extra_segments)
    for (x0,y0),(x1,y1) in segments:
        if min(x0,x1)>max(xcols)+4 or max(x0,x1)<min(xcols)-4:continue
        for mirror in [1,-1]:
            a=475+mirror*y0;b=475+mirror*y1;dx=x1-x0;dy=b-a
            denom=dx*dx+dy*dy
            t=np.clip(((xx-x0)*dx+(yy-a)*dy)/denom,0,1) if denom else np.zeros_like(xx)
            d=np.sqrt((xx-(x0+t*dx))**2+(yy-(a+t*dy))**2)
            best=np.minimum(best,d)
    return best

def render(d,width):return np.interp(d/width,[0,1,2,3],[1,113/255,20/255,0])

def main():
    p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    f=next(f for f in p['fits'] if f['start_x']==92 and f['step_px']==3 and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1)
    q=np.array(f['states']);xs=np.array(f['coordinates']);scales=np.array(f['scales']);ys=q*scales
    a=np.array(Image.open(ROOT/'research/sources/cryptoHALV.png'),float)/255
    spec=json.loads((ROOT/'research/models/boundary33_v1.json').read_text())
    calibration=[]
    for width in spec['width_scales']:
        losses={'train':[],'validation':[]}
        for i in range(8,256,16):
            columns=list(range(int(xs[i])-2,int(xs[i])+3))
            d=distance_field(xs,ys,columns);loss=float(np.mean((render(d,width)-a[85:866,columns])**2))
            losses['train' if i<128 else 'validation'].append(loss)
        calibration.append({'width':width,'training_patch_mse':float(np.mean(losses['train'])),
                            'validation_patch_mse':float(np.mean(losses['validation']))})
    chosen=min(calibration,key=lambda r:r['training_patch_mse'])['width']
    boundaries=[]
    for b in range(1,8):
        i=32*b;x=int(xs[i]);columns=[x-2,x-1,x,x+1,x+2];obs=a[85:866,columns]
        train=[0,1,3,4];test=2;baseline_d=distance_field(xs,ys,columns);rows=[]
        for width in spec['width_scales']:
            pred=render(baseline_d,width)
            baseline={'training_mse':float(np.mean((pred[:,train]-obs[:,train])**2)),
                      'validation_mse':float(np.mean((pred[:,test]-obs[:,test])**2))}
            candidates=[]
            for endpoint in range(4):
                height=endpoint*scales[i-1]
                for join in spec['join_models']:
                    extra=[((x,height),(x,ys[i]))] if join=='vertical_connector' else []
                    d=distance_field(xs,ys,columns,extra,replace_segment=(i-1,height));pred=render(d,width)
                    candidates.append({'endpoint':endpoint,'join':join,
                        'training_mse':float(np.mean((pred[:,train]-obs[:,train])**2)),
                        'validation_mse':float(np.mean((pred[:,test]-obs[:,test])**2))})
            best=min(candidates,key=lambda r:r['training_mse'])
            rows.append({'width':width,'continuous':baseline,'best_independent_by_training':best,'candidates':candidates})
        boundaries.append({'next_block_1based':b+1,'x':x,'shared_endpoint_in_previous_units':float(ys[i]/scales[i-1]),'width_models':rows})
    # Tight wave-only ROI: the signature also occupies these x columns lower down.
    columns=[859,860];terminal_slice=slice(468-85,483-85);obs=a[468:483,columns];terminal=[]
    for width in spec['width_scales']:
        base=render(distance_field(xs,ys,columns),width)[terminal_slice]
        for endpoint in range(4):
            pred=render(distance_field(xs,ys,columns,[((857,ys[-1]),(860,endpoint*scales[-1]))]),width)[terminal_slice]
            terminal.append({'width':width,'endpoint':endpoint,'baseline_mse':float(np.mean((base-obs)**2)),
                             'extended_mse':float(np.mean((pred-obs)**2))})
    files=['research/sources/cryptoHALV.png','research/data/pixel_measurements.json','research/models/boundary33_v1.json','tools/check_boundary33.py']
    out={'model':'C15','input_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in files},
         'node_span':{'first':int(xs[0]),'last':int(xs[-1]),'distance':int(xs[-1]-xs[0]),'vertices':len(xs),'intervals':len(xs)-1},
         'calibration':calibration,'chosen_global_width':chosen,'boundaries':boundaries,'terminal':terminal,
         'terminal_roi_y_inclusive':[468,482],
         'terminal_observed_columns':{str(x):a[468:483,x].tolist() for x in columns},
         'terminal_observed_max':float(obs.max()),'no_private_key_search':True,'limitations':spec['limitations']}
    (ROOT/'research/data/boundary33_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Calibration',calibration,'chosen',chosen)
    for b in boundaries:
        r=next(r for r in b['width_models'] if r['width']==chosen)
        print('Boundary',b['x'],'shared',b['shared_endpoint_in_previous_units'],'continuous',r['continuous'],'independent',r['best_independent_by_training'])
    print('Terminal',[r for r in terminal if r['width']==chosen])

if __name__=='__main__':main()
