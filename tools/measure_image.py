#!/usr/bin/env python3
"""Measure the mirrored PNG; fit explicit hypotheses, not a claimed decoding."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def runs(mask, origin):
    ix = np.flatnonzero(mask)
    return [[int(r[0]+origin), int(r[-1]+origin), len(r)]
            for r in np.split(ix, np.flatnonzero(np.diff(ix)>1)+1) if len(r)]

def fit(a, start, step, restricted=False, stroke_scale=1.0, alphabet=None):
    # Default reproduces the original four-nonnegative-state experiment.
    values = list(range(4)) if alphabet is None else list(alphabet)
    count = len(values)
    xs = np.arange(start, 858, step)
    scales = 128.0 / 2.0**np.minimum(np.arange(len(xs))*step//96, 7)
    yy = np.arange(85, 866)[:, None]
    offsets = np.arange(1, step)[None, :]
    costs = []
    for k in range(len(xs)-1):
        obs = a[85:866, xs[k]+np.arange(1, step)] / 255.0
        c = np.empty((count, count))
        for ui, u in enumerate(values):
            for vi, v in enumerate(values):
                if restricted and abs(u-v) != 1:
                    c[ui, vi] = np.inf
                    continue
                amp0, amp1 = u*scales[k], v*scales[k+1]
                slope = (amp1-amp0)/step
                amp = amp0 + slope*offsets
                d = np.minimum(np.abs(yy-(475-amp)), np.abs(yy-(475+amp))) / np.sqrt(1+slope*slope)
                # Explicit approximate stroke kernel, not an assertion about the author's renderer.
                pred = np.interp(d/stroke_scale, [0, 1, 2, 3], [1, 113/255, 20/255, 0])
                c[ui, vi] = np.mean((obs-pred)**2)
        costs.append(c)
    costs = np.array(costs)
    forward = np.zeros((len(xs), count))
    parent = np.zeros((len(xs), count), int)
    if alphabet is not None:
        forward[0, np.array(values)<0] = np.inf  # Fix only the global mirror orientation.
    for k, c in enumerate(costs):
        z = forward[k, :, None]+c
        parent[k+1] = np.argmin(z, axis=0)
        forward[k+1] = np.min(z, axis=0)
    states = np.zeros(len(xs), int)
    states[-1] = np.argmin(forward[-1])
    for k in range(len(xs)-1, 0, -1):
        states[k-1] = parent[k, states[k]]
    back = np.zeros_like(forward)
    for k in range(len(xs)-2, -1, -1):
        back[k] = np.min(costs[k]+back[k+1][None, :], axis=1)
    total = forward[-1].min()
    gaps = forward+back-total
    alt = np.sort(gaps, axis=1)[:, 1]
    return {
        'start_x': int(start), 'step_px': step, 'restrict_delta_to_plus_minus_one': restricted,
        'stroke_scale': stroke_scale,
        'nodes': len(xs), 'mean_segment_mse': float(total/len(costs)),
        'coordinates': xs.tolist(), 'scales': scales.tolist(), 'states': [values[i] for i in states],
        'second_state_cost_gaps': alt.tolist(),
        'limitation': 'Approximate straight-segment renderer; vertices omitted from loss; no uniqueness or key claim. Costs across different clocks are not directly comparable likelihoods.',
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--image', type=Path, default=ROOT/'research/sources/cryptoHALV.png')
    args = p.parse_args()
    image = Image.open(args.image)
    if image.size != (950, 950):
        raise ValueError('Fixed-coordinate experiment requires the 950x950 source mirror, not a resized copy.')
    a = np.array(image.convert('L'), dtype=float)
    output = {
        'sha256': hashlib.sha256(args.image.read_bytes()).hexdigest(),
        'dimensions': list(image.size), 'mode': image.mode,
        'metadata': image.info,
        'marker': {},
        'symmetry_mae_by_axis': {},
    }
    for axis in [474, 475, 476]:
        d = min(axis-85, 865-axis)
        output['symmetry_mae_by_axis'][str(axis)] = float(np.mean(np.abs(a[axis-d:axis, 95:859]-a[axis+1:axis+d+1, 95:859][::-1])))
    for threshold in [0, 1, 5, 10, 20, 40, 80, 120, 180]:
        output['marker'][str(threshold)] = runs(np.max(a[438:513, 90:93], axis=1)>threshold, 438)
    with (ROOT/'research/data/marker_pixels.csv').open('w') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['y', 'x90', 'x91', 'x92'])
        for y in range(438, 513): w.writerow([y]+a[y, 90:93].astype(int).tolist())
    fits = [fit(a, start, step, restricted)
            for start in [91, 92, 93] for step, restricted in [(3, False), (3, True), (6, False)]]
    fits.extend(fit(a, 92, 3, stroke_scale=w) for w in [0.85, 1.15])
    output['fits'] = fits
    (ROOT/'research/data/pixel_measurements.json').write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k != 'fits'}, indent=2))
    for f in fits:
        print({k:f[k] for k in ['start_x','step_px','restrict_delta_to_plus_minus_one','nodes','mean_segment_mse']})

if __name__ == '__main__':
    main()
