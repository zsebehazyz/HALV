#!/usr/bin/env python3
"""C7: measured marker lattice, codec compatibility, and controlled timing proxies."""
import hashlib
import itertools
import json
import math
import os
import re
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/halv-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/halv-cache')
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]

def activities(q):
    d=np.r_[False,q[1:]!=q[:-1]]
    reset=d.copy();reset[::32]=False
    return [q>0,q>=2,q==3,d,reset]

def runs(a):
    borders=np.r_[0,np.flatnonzero(a[1:]!=a[:-1])+1,len(a)]
    return a[borders[:-1]],np.diff(borders)

def timing_scores(q,units):
    scores=[];legal=[]
    for a in activities(q):
        states,lengths=runs(a)
        legal.append({'marks_legal':int(np.sum(np.isin(lengths[states],[1,3]))),'marks':int(states.sum()),
                      'gaps_legal':int(np.sum(np.isin(lengths[~states],[1,3,7]))),'gaps':int((~states).sum())})
        # Boundary runs may be truncated by the image frame.
        states=states[1:-1];durations=3*lengths[1:-1]
        for inverse in [False,True]:
            on=states^inverse
            for unit in units:
                u=durations/unit
                residual=np.where(on,np.minimum((u-1)**2,(u-3)**2),
                                  np.minimum.reduce([(u-1)**2,(u-3)**2,(u-7)**2]))
                scores.append(float(np.mean(residual)) if len(residual) else math.inf)
    return np.array(scores),legal

def euler_surrogate(block,rng):
    adjacency=[[] for _ in range(4)]
    for a,b in zip(block[:-1],block[1:]):adjacency[int(a)].append(int(b))
    for edges in adjacency:rng.shuffle(edges)
    stack=[int(block[0])];trail=[]
    while stack:
        if adjacency[stack[-1]]:stack.append(adjacency[stack[-1]].pop())
        else:trail.append(stack.pop())
    result=np.array(trail[::-1],dtype=int)
    assert len(result)==len(block) and result[0]==block[0] and result[-1]==block[-1]
    assert np.array_equal(np.bincount(result,minlength=4),np.bincount(block,minlength=4))
    assert np.array_equal(np.bincount(4*result[:-1]+result[1:],minlength=16),
                          np.bincount(4*block[:-1]+block[1:],minlength=16))
    return result

def main():
    spec=json.loads((ROOT/'research/models/timing_lattice_v1.json').read_text())
    image=ROOT/'research/sources/cryptoHALV.png';a=np.array(Image.open(image),dtype=int);column=a[:,91]
    peaks=[y for y in range(438,513) if column[y]>=178 and column[y]>column[y-1] and column[y]>=column[y+1]]
    center=(peaks[0]+peaks[-1])/2
    distances=sorted(set(abs(y-center) for y in peaks));unit=distances[0]
    clock=math.gcd(*(b-a for a,b in zip(peaks,peaks[1:])))
    slots=list(range(peaks[0],peaks[-1]+1,clock))
    occupied=[int(y in peaks) for y in slots];byte=int(''.join(map(str,occupied)),2)
    lattice_counts={}
    for n in [8,9]:
        positions=list(range(peaks[0],peaks[0]+n*clock,clock));examples=[]
        for choice in itertools.combinations(positions,6):
            pair_sum=choice[0]+choice[-1]
            if any(choice[i]+choice[-1-i]!=pair_sum for i in range(3)):continue
            d=sorted(set(abs(2*y-pair_sum) for y in choice))
            if len(d)==3 and d[1]==3*d[0] and d[2]==7*d[0]:examples.append(list(choice))
        lattice_counts[str(n)]={'six_active_subsets':math.comb(n,6),'exact_137_symmetric_subsets':examples,
                               'warning':'Descriptive enumeration, not a p-value; grid/window/threshold selected from observed image.'}
    p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    q=np.array(next(f['states'] for f in p['fits'] if f['start_x']==92 and f['step_px']==3
                   and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1),dtype=int)
    ff=(ROOT/'research/sources/ffmpeg_8svx.c').read_text()
    tables={name:[int(x) for x in re.search(r'\b'+name+r'\[16\]\s*=\s*\{([^}]+)\}',ff).group(1).split(',')] for name in ['fibonacci','exponential']}
    deltas=np.concatenate([np.diff(b) for b in q.reshape(8,32)])
    codec={name:{'representable':int(np.sum(np.isin(deltas,table))),'total':len(deltas)} for name,table in tables.items()}
    models=[{'rule':rule,'inverted':inverse,'unit_px':u} for rule in spec['activity_rules'] for inverse in [False,True] for u in spec['timing_units_px']]
    observed,legacy=timing_scores(q,spec['timing_units_px'])
    assert len(observed)==len(models)==30
    controls={};matrices={};rng=np.random.default_rng(spec['seed'])
    for family in ['value_shuffle','transition_preserving_euler']:
        score_matrix=[];seen=set()
        for i in range(spec['surrogates_per_family']):
            blocks=[rng.permutation(b) if family=='value_shuffle' else euler_surrogate(b,rng) for b in q.reshape(8,32)]
            surrogate=np.concatenate(blocks);seen.add(surrogate.tobytes())
            scores,_=timing_scores(surrogate,spec['timing_units_px']);score_matrix.append(scores)
        matrix=np.array(score_matrix);matrices[family]=matrix;best=matrix.min(1)
        controls[family]={'draws':len(matrix),'distinct_sequences':len(seen),
            'modelwise_reference_fractions':((1+np.sum(matrix<=observed[None,:]+1e-12,axis=0))/(len(matrix)+1)).tolist(),
            'selected_best_reference_fraction':float((1+np.sum(best<=observed.min()+1e-12))/(len(matrix)+1)),
            'mean_best_score':float(best.mean()),'best_score_quantiles':np.quantile(best,[0,.025,.5,.975,1]).tolist()}
        print(family,controls[family]['selected_best_reference_fraction'],flush=True)
    np.savez_compressed(ROOT/'research/data/timing_surrogate_scores.npz',observed=observed,**matrices)
    files=['research/sources/cryptoHALV.png','research/sources/ffmpeg_8svx.c','research/data/pixel_measurements.json',
           'research/models/timing_lattice_v1.json','tools/check_timing_lattice.py']
    out={'model':'C7','input_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
         'marker':{'peaks':peaks,'peak_intensities':[int(column[y]) for y in peaks],
                   'center':center,'unique_distances':distances,'distance_ratios':[d/unit for d in distances],
                   'gaps':np.diff(peaks).tolist(),'lattice_step':clock,'slots':slots,'bits':occupied,
                   'byte_hex':format(byte,'02X'),'weak_extra_peak':{'y':506,'intensity':int(column[506])},
                   'lattice_subset_enumerations':lattice_counts},
         'codec_tables':tables,'within_block_delta_compatibility':codec,
         'activity_rule_order':spec['activity_rules'],'legacy_one_sample_unit_counts_including_boundaries':legacy,
         'models':models,'observed_losses':observed.tolist(),
         'best_observed_models':[models[i] for i in np.flatnonzero(np.isclose(observed,observed.min()))],
         'controls':controls,'limitations':spec['limitations'],
         'no_audio_or_private_key_decoded':True}
    (ROOT/'research/data/timing_lattice_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Best observed',float(observed.min()),out['best_observed_models'])
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(4,1,figsize=(13,12),layout='constrained')
    ys=np.arange(438,513);axes[0].plot(ys,column[ys],'.-');axes[0].scatter(peaks,column[peaks],label='Six strong peaks')
    axes[0].axvline(center,color='gray');axes[0].set(title='Actual marker column x=91; six strong peaks and the weaker y=506 peak',xlabel='Image y',ylabel='Intensity');axes[0].legend()
    axes[1].plot(np.arange(256)*3,q,'.-',linewidth=.6);axes[1].set(title='Nominal waveform states after assumed block normalization',xlabel='Relative x (pixels)',ylabel='q')
    axes[2].step(np.arange(256)*3,activities(q)[3],where='post');axes[2].set(title='Global change indicator; not decoded audio',xlabel='Relative x (pixels)')
    for name,matrix in matrices.items():axes[3].hist(matrix.min(1),bins=35,alpha=.5,label=name)
    axes[3].axvline(observed.min(),color='red',label='Observed minimum over 30 models');axes[3].set(title='Same model selection applied to every reference sequence',xlabel='Minimum timing loss',ylabel='Count');axes[3].legend()
    fig.savefig(ROOT/'research/data/timing_lattice_controls.png',dpi=150)

if __name__=='__main__':main()
