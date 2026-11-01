#!/usr/bin/env python3
"""C39: exact marker data, globally thresholded Morse and rational exports."""
import csv
import hashlib
import json
import re
from collections import Counter
from fractions import Fraction as F
import numpy as np
from PIL import Image
from residual_channels import ROOT,nominal_states

CODES='.- -... -.-. -.. . ..-. --. .... .. .--- -.- .-.. -- -. --- .--. --.- .-. ... - ..- ...- .-- -..- -.-- --..'.split()
DECODE=dict(zip(CODES,'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))


def spans(mask):
    edges=np.r_[0,np.flatnonzero(mask[1:]!=mask[:-1])+1,len(mask)]
    return [(int(a),int(b-1),int(b-a)) for a,b in zip(edges[:-1],edges[1:]) if mask[a]]


def write_csv(name,headers,rows):
    p=ROOT/'research/data'/name
    with p.open('w',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(headers);writer.writerows(rows)


def main():
    spec=json.loads((ROOT/'research/models/marker_pixel_revisit_v1.json').read_text())
    image=np.array(Image.open(ROOT/'research/sources/cryptoHALV.png'),dtype=int)
    column=image[:,91];v=column[443:507];ramp=np.array(spec['claimed_ramp'])
    strong=v>=3;errors=np.min(abs(v[strong,None]-ramp),axis=1)
    carrier=[]
    for phase in range(7):
        predicted=ramp[(np.arange(443,507)-phase)%7]
        residual=abs(v-predicted)
        carrier.append({'phase_y_mod7':phase,'strong_points_fitting_tolerance1':int(np.sum((residual<=1)&strong)),
                        'strong_points':int(strong.sum()),'strong_L1_residual':int(residual[strong].sum())})
    masks=[]
    for threshold in [1,3,32,178]:
        bits=(v>=threshold).astype(int)
        masks.append({'threshold':threshold,'bits':''.join(map(str,bits)),
                      'hex':np.packbits(bits).tobytes().hex(),'ones':int(bits.sum())})
    rawrows=[[y,int(column[y]),int(vv>=3),int(ramp[np.argmin(abs(ramp-vv))]) if vv>=3 else '']
             for y,vv in zip(range(443,507),v)]
    write_csv('marker_x91_rows443_506.csv',['y','intensity','mask_ge3','nearest_claimed_ramp'],rawrows)
    matches={'XEX':[],'NMRM':[]};nine_thresholds=[];exact_timing=[]
    for threshold in range(1,256):
        rawmask=column[438:513]>=threshold
        for reverse in [False,True]:
            mask=rawmask[::-1] if reverse else rawmask;ss=spans(mask)
            if len(ss)!=9:continue
            if not reverse:nine_thresholds.append(threshold)
            heights=[s[2] for s in ss];gaps=[b[0]-a[1]-1 for a,b in zip(ss,ss[1:])]
            for unit in [F(heights[0]),F(heights[0],3)]:
                if all(F(h) in [unit,3*unit] for h in heights) and all(F(g) in [unit,3*unit,7*unit] for g in gaps):
                    exact_timing.append({'brightness_threshold':threshold,'reverse':reverse,'unit_pixels':str(unit),
                                         'heights':heights,'gaps':gaps})
            for dash_cut in range(1,max(heights)+2):
                marks=['-' if h>=dash_cut else '.' for h in heights]
                for gap_cut in range(1,max(gaps)+2):
                    groups=[marks[0]]
                    for gap,mark in zip(gaps,marks[1:]):
                        if gap>=gap_cut:groups.append(mark)
                        else:groups[-1]+=mark
                    text=''.join(DECODE.get(g,'?') for g in groups)
                    if text in matches:
                        matches[text].append({'brightness_threshold':threshold,'reverse':reverse,
                                              'dash_min_height':dash_cut,'letter_gap_min':gap_cut,
                                              'heights':heights,'gaps':gaps,'groups':groups})
    states=nominal_states().flatten();q=states.reshape(8,32);scales=128//2**np.arange(8)
    source=(ROOT/'research/sources/ffmpeg_8svx.c').read_text()
    table=[int(x) for x in re.search(r'\bfibonacci\[16\]\s*=\s*\{([^}]+)\}',source).group(1).split(',')]
    lookup={value:i for i,value in enumerate(table)}
    global_delta=np.diff(np.r_[0,states]);indices=[lookup[int(d)] for d in global_delta]
    assert all((idx&1)==(int(d)&1) for idx,d in zip(indices,global_delta))
    packed=bytes(a|(b<<4) for a,b in zip(indices[::2],indices[1::2]))
    (ROOT/'research/data/canonical_fib_delta_low_first.bin').write_bytes(packed)
    txt=['HALV nominal256 vertices; measured model, not decoded audio or a solved key.',
         'x=92+3*i; block scale=128/2**floor(i/32); mirror center y=475.',
         'Eight lines of32 q values; do not confuse256 vertices with128 packed delta bytes.']
    txt += [','.join(map(str,row)) for row in q]
    (ROOT/'research/data/canonical_q256.txt').write_text('\n'.join(txt)+'\n')
    node_rows=[]
    for i,value in enumerate(states):
        b=i//32;d='' if i%32==0 else int(value-states[i-1])
        node_rows.append([i,b+1,i%32,92+3*i,int(value),int(scales[b]),int(value*scales[b]),d,
                          '' if d=='' else lookup[d],int(global_delta[i]),indices[i]])
    write_csv('canonical_q256.csv',['index','block_1based','local_index','x','q','scale_px','height_px',
                                    'delta_within_block','fib_index_within_block','delta_global_init0','fib_index_global'],node_rows)
    block_pixels=[];vertex_deltas=[];pixel_deltas=[]
    for b,row in enumerate(q):
        values=[]
        for j in range(31):values.extend([int(3*row[j]+t*(row[j+1]-row[j])) for t in range(3)])
        values.append(int(3*row[-1]));ds=np.diff(values)
        assert np.array_equal(ds,np.repeat(np.diff(row),3))
        vertex_deltas.extend(map(int,np.diff(row)));pixel_deltas.extend(map(int,ds))
        for k,value in enumerate(values):
            delta='' if k==0 else int(ds[k-1])
            block_pixels.append([b+1,k,92+96*b+k,value,delta,'' if delta=='' else lookup[delta]])
    write_csv('canonical_within_block_pixels.csv',['block_1based','local_pixel','x','amplitude_in_scale_over3',
                                                 'pixel_delta','fib_index_if_delta'],block_pixels)
    whole=[];heights=[F(int(value*scales[i//32])) for i,value in enumerate(states)]
    for x in range(92,858):
        i=min((x-92)//3,254);t=F(x-(92+3*i),3)
        h=(1-t)*heights[i]+t*heights[i+1]
        whole.append([x,str(h),i,int(i//32==(i+1)//32),int((x-92)%3==0)])
    write_csv('canonical_physical_polyline_pixels.csv',['x','exact_height_px','left_vertex_index','same_scale_interval','is_vertex'],whole)
    # Exact index encode/decode identity at initial0; no clamping required.
    acc=0;decoded=[]
    for index in indices:acc+=table[index];decoded.append(acc)
    assert decoded==states.tolist()
    out={'model':'C39','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [
         'research/models/marker_pixel_revisit_v1.json','research/sources/cryptoHALV.png','research/data/pixel_measurements.json',
         'research/sources/ffmpeg_8svx.c','tools/audit_marker_pixel_revisit.py','tools/residual_channels.py']},
         'marker':{'raw_intensities':v.tolist(),'strong_points':int(strong.sum()),
                   'near_claimed_ramp_tolerance1':int(sum(errors<=1)),'fixed7row_carrier_fits':carrier,
                   'nine_component_thresholds':nine_thresholds,'masks':masks,
                   'exact_standard_Morse_timing_recipes':exact_timing,
                   'global_morse_target_recipe_counts':{k:len(v) for k,v in matches.items()},
                   'global_morse_target_recipes':matches},
         'wave':{'vertices':256,'packed_delta_bytes':len(packed),'within_block_vertex_deltas':len(vertex_deltas),
                 'within_block_pixels':len(block_pixels),'within_block_pixel_deltas':len(pixel_deltas),
                 'whole_polyline_pixels':len(whole),'triplication_identity':True,
                 'vertex_delta_histogram':dict(sorted(Counter(vertex_deltas).items())),
                 'pixel_delta_histogram':dict(sorted(Counter(pixel_deltas).items())),
                 'fib_delta_LSB_is_parity_difference':True,'encode_decode_identity':True},
         'limitations':spec['limitations']}
    (ROOT/'research/data/marker_pixel_revisit_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'marker':{k:v for k,v in out['marker'].items() if k not in ['global_morse_target_recipes','raw_intensities']},
                      'wave':out['wave']},indent=2))


if __name__=='__main__':main()
