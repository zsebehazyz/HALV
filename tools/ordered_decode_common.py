"""Shared finite primitives for the ordered C28-C30 experiment."""
import hashlib
import json
from pathlib import Path
import numpy as np
from residual_channels import ROOT,nominal_states,extract,restore,positions,nibble_values,packed,edge_residual

def spec():return json.loads((ROOT/'research/models/ordered_decode_v1.json').read_text())
def marker():return np.array(json.loads((ROOT/'research/data/timing_lattice_check.json').read_text())['marker']['bits'])
def hashes(names):return {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names}
def dump(name,value):(ROOT/'research/data'/name).write_text(json.dumps(value,indent=2)+'\n')

def flag_decode(data,flag):return np.c_[data^flag[:,None],1-flag]
def flag_inverse(decoded,control):
    g=1-decoded[:,-1];return decoded[:,:-1]^g[:,None],g^control

def layout(bits,frame):
    if frame!='zero_position':return bits.copy()
    result=np.empty_like(bits)
    for i,row in enumerate(bits):
        z,_,hp,_=positions(i//8,'absolute');result[i,hp]=row[:3];result[i,z]=row[3]
    return result

def unlayout(bits,frame):
    if frame!='zero_position':return bits.copy()
    result=np.empty_like(bits)
    for i,row in enumerate(bits):
        z,_,hp,_=positions(i//8,'absolute');result[i,:3]=row[hp];result[i,3]=row[z]
    return result

def bit_arrays(case):
    raw=bytes.fromhex(case['main32_hex']);a=np.array([[(v>>s)&1 for s in range(7,-1,-1)] for v in raw]).reshape(64,4)
    rv=[int(c,16) for c in case['full_residual64_nibbles_hex']]
    r=np.array([[(v>>s)&1 for s in [3,2,1,0]] for v in rv])
    return a,r

def neighbor_permutation(name,mask):
    result=np.arange(64)
    for i in range(64):
        b,c=divmod(i,8)
        if name=='previous_global':result[i]=(i-1)%64
        elif name=='next_global':result[i]=(i+1)%64
        elif name!='current':
            step=-1 if name=='previous_in_block' else 1
            if name in ['marker_direction','inverse_marker_direction']:
                step=1 if mask[b] else -1
                if name=='inverse_marker_direction':step=-step
            result[i]=8*b+(c+step)%8
    assert len(np.unique(result))==64
    return result

def complement_diagnostic(data):
    result={}
    for name,offset in [('adjacent_cells',1),('adjacent_blocks',8),('lag2_blocks',16)]:
        indices=np.arange(offset,64-offset);match=(data[indices-offset]^data[indices+offset])==1
        middle=(indices>=16)&(indices<56)
        result[name]={'passed':int(match.sum()),'total':int(match.size),
                      'middle_passed':int(match[middle].sum()),'middle_total':int(match[middle].size)}
    return result
