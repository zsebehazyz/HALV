"""Shared, reversible definitions of the two four-bit HALV channels."""
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def nominal_states():
    p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    f=next(f for f in p['fits'] if f['start_x']==92 and f['step_px']==3
           and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1)
    return np.array(f['states'],dtype=int).reshape(64,4)

def positions(block,frame):
    z=(3-block)%4;r=(z-1)%4
    if frame=='absolute':hp=[i for i in range(4) if i!=z];lp=[i for i in range(4) if i!=r]
    elif frame=='phase_relative':hp=[r,(r+2)%4,(r+3)%4];lp=[z,(z+1)%4,(z+2)%4]
    else:raise ValueError(frame)
    return z,r,hp,lp

def extract(states,frame):
    a=[];res=[]
    for i,cell in enumerate(states):
        z,r,hp,lp=positions(i//8,frame)
        a.append([int(cell[p]>>1) for p in hp]+[int(cell[r]&1)])
        res.append([int(cell[z]>>1)]+[int(cell[p]&1) for p in lp])
    return np.array(a),np.array(res)

def restore(a,res,frame):
    states=[]
    for i,(av,rv) in enumerate(zip(a,res)):
        z,r,hp,lp=positions(i//8,frame);h=[0]*4;l=[0]*4
        for p,bit in zip(hp,av[:3]):h[p]=int(bit)
        l[r]=int(av[3]);h[z]=int(rv[0])
        for p,bit in zip(lp,rv[1:]):l[p]=int(bit)
        states.append([2*x+y for x,y in zip(h,l)])
    return np.array(states)

def nibble_values(bits):return bits@np.array([8,4,2,1])
def packed(bits):
    v=nibble_values(bits);return bytes(int(16*x+y) for x,y in zip(v[::2],v[1::2]))

def edge_residual(res):return packed(res.reshape(8,8,4)[[0,1,7]].reshape(24,4))
