#!/usr/bin/env python3
"""C47 finite image-directed A/R joins and key-to-whole-wave gates."""
import hashlib,itertools,json
import numpy as np
from residual_channels import ROOT,nominal_states,extract,restore
from bitcoin_oracle import addresses,TARGET,selftest

JOINS=list(itertools.combinations(range(8),4))

def bitrows(values):
    return (np.array(values,dtype=np.uint16)[:,None]>>np.arange(7,-1,-1))&1

def controls(swap,rotation):
    marker=np.array(json.loads((ROOT/'research/data/timing_lattice_check.json').read_text())['marker']['bits'])
    date=np.array(list(map(int,json.loads((ROOT/'research/data/corner_check.json').read_text())['dates']['cryptoHALV.png']['reading'])))
    z=(3-np.arange(8))%4;r=(z-1)%4
    sw={'none':np.zeros(8,int),'BD':marker,'inverse_BD':1-marker}[swap]
    rot={'none':np.zeros(8,int),'z':z,'r':r,'date':date%8}[rotation]
    return np.repeat(sw,8),np.repeat(rot,8),np.repeat(date,8)

def mix(a,r,positions):
    out=np.empty((64,8),int);out[:,positions]=a
    out[:,[p for p in range(8) if p not in positions]]=r
    return out@2**np.arange(7,-1,-1)

def inverse(values,positions,sw,rot,date,operation,complement):
    v=np.array(values,dtype=np.int64)
    if complement:v^=255
    if operation=='add':v=(v-date)%256
    elif operation=='subtract':v=(v+date)%256
    v=((v>>rot)|(v<<(8-rot)))&255
    b=bitrows(v);a=b[:,positions].copy();r=b[:,[p for p in range(8) if p not in positions]].copy()
    a[sw==1],r[sw==1]=r[sw==1].copy(),a[sw==1].copy()
    return a,r

def forward(a,r,positions,sw,rot,date,operation,complement):
    a=a.copy();r=r.copy();a[sw==1],r[sw==1]=r[sw==1].copy(),a[sw==1].copy()
    v=mix(a,r,positions);v=((v<<rot)|(v>>(8-rot)))&255
    if operation=='add':v=(v+date)%256
    elif operation=='subtract':v=(v-date)%256
    if complement:v^=255
    return v

def main():
    selftest();q=nominal_states();rows=[];outputs=[];hits=[]
    alphabets={'upper':np.array(list(b'0123456789ABCDEF')),'lower':np.array(list(b'0123456789abcdef'))}
    # Byte-join positive control independent of measuredq.
    for positions in JOINS:
        for value in range(256):
            b=bitrows([value])[0];a=np.tile(b[list(positions)],(64,1));r=np.tile(b[[p for p in range(8) if p not in positions]],(64,1))
            assert np.all(mix(a,r,positions)==value)
    for frame in ['absolute','phase_relative']:
        a,r=extract(q,frame)
        for positions,swap,rotation,operation,complement in itertools.product(JOINS,['none','BD','inverse_BD'],['none','z','r','date'],['none','add','subtract'],[False,True]):
            sw,rot,date=controls(swap,rotation)
            v=forward(a,r,positions,sw,rot,date,operation,complement)
            aa,rr=inverse(v,positions,sw,rot,date,operation,complement)
            assert np.array_equal(restore(aa,rr,frame),q)
            row={'id':len(rows),'frame':frame,'A_positions':list(positions),'swap':swap,'rotation':rotation,'operation':operation,'complement':complement,'roundtrip256q':True,'alphabets':{}}
            for name,alphabet in alphabets.items():
                accepted=np.isin(v,alphabet);options=np.zeros((64,16),bool);compatible=[]
                for char in alphabet:
                    ca,cr=inverse(np.full(64,char),positions,sw,rot,date,operation,complement)
                    same=np.all(ca==a,axis=1);rv=cr@np.array([8,4,2,1]);options[np.flatnonzero(same),rv[same]]=True
                counts=options.sum(1);actual=r@np.array([8,4,2,1])
                membership=options[np.arange(64),actual]
                assert np.array_equal(membership,accepted)
                row['alphabets'][name]={'valid_cells':int(accepted.sum()),'invalid_cells':np.flatnonzero(~accepted).tolist(),
                    'no_R_solution_cells':np.flatnonzero(counts==0).tolist(),'unique_R_solution_cells':int(np.sum(counts==1)),
                    'ambiguous_R_solution_cells':int(np.sum(counts>1)),'all_actual_R_compatible':bool(np.all(membership))}
                if np.all(accepted):
                    for reverse in [False,True]:
                        raw=bytes(v.tolist());text=raw[::-1] if reverse else raw;key=bytes.fromhex(text.decode())
                        regenerated=key.hex().upper().encode() if name=='upper' else key.hex().encode()
                        if reverse:regenerated=regenerated[::-1]
                        ca,cr=inverse(list(regenerated),positions,sw,rot,date,operation,complement)
                        assert np.array_equal(restore(ca,cr,frame),q)
                        addrs=addresses(key);hits.append({'recipe':len(rows),'alphabet':name,'reverse':reverse,'key_hex':key.hex(),'addresses':addrs,'match':TARGET in addrs.values()})
            rows.append(row);outputs.append(v.astype(np.uint8))
    np.savez_compressed(ROOT/'research/data/image_directed_join_outputs.npz',values=np.array(outputs))
    names=['research/models/image_directed_join_v1.json','research/data/pixel_measurements.json','research/data/timing_lattice_check.json','research/data/corner_check.json','research/sources/webreview_xixoio_solver.png','tools/check_image_directed_join.py','tools/residual_channels.py','tools/bitcoin_oracle.py']
    best=max(s['valid_cells'] for row in rows for s in row['alphabets'].values())
    witnesses=[{'id':row['id'],'alphabet':name,**s} for row in rows for name,s in row['alphabets'].items() if s['valid_cells']==best]
    out={'model':'C47','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in names},'recipes':len(rows),'join_calibration_cases':70*256,'full_roundtrips':len(rows),'best_valid_hex_cells_out_of64':best,'best_witnesses':witnesses,'key_candidates':hits,'target_matches':sum(h['match'] for h in hits),'rows':rows}
    (ROOT/'research/data/image_directed_join_check.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['rows','input_sha256','best_witnesses']},indent=2))

if __name__=='__main__':main()
