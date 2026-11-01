#!/usr/bin/env python3
"""Independent integer inverse and canonical-hex audit for C47."""
import hashlib,json
import numpy as np
from residual_channels import ROOT,nominal_states


def invert_byte(value,row,cell,marker,date):
    b=cell//8;kind=row['rotation'];z=(3-b)%4
    turn={'none':0,'z':z,'r':(z-1)%4,'date':date[b]%8}[kind]
    if row['complement']:value=255-value
    if row['operation']=='add':value=(value-date[b])%256
    elif row['operation']=='subtract':value=(value+date[b])%256
    for _ in range(turn):value=(value>>1)|((value&1)<<7)
    positions=set(row['A_positions'])
    a=[(value>>(7-i))&1 for i in range(8) if i in positions]
    r=[(value>>(7-i))&1 for i in range(8) if i not in positions]
    swap=(marker[b] if row['swap']=='BD' else 1-marker[b] if row['swap']=='inverse_BD' else 0)
    if swap:a,r=r,a
    return a,r


def restore_cell(a,r,frame,cell):
    z=(3-cell//8)%4;odd=(z-1)%4
    hp=[i for i in range(4) if i!=z] if frame=='absolute' else [odd,(odd+2)%4,(odd+3)%4]
    lp=[i for i in range(4) if i!=odd] if frame=='absolute' else [z,(z+1)%4,(z+2)%4]
    h=[0]*4;l=[0]*4;h[z]=r[0];l[odd]=a[3]
    for i,bit in zip(hp,a[:3]):h[i]=bit
    for i,bit in zip(lp,r[1:]):l[i]=bit
    return [2*x+y for x,y in zip(h,l)]


def main():
    d=json.loads((ROOT/'research/data/image_directed_join_check.json').read_text())
    for name,digest in d['input_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    values=np.load(ROOT/'research/data/image_directed_join_outputs.npz')['values']
    assert values.shape==(10080,64)
    marker=json.loads((ROOT/'research/data/timing_lattice_check.json').read_text())['marker']['bits']
    date=list(map(int,json.loads((ROOT/'research/data/corner_check.json').read_text())['dates']['cryptoHALV.png']['reading']))
    q=nominal_states().tolist();best=0
    for row,output in zip(d['rows'],values):
        for cell,value in enumerate(output):
            a,r=invert_byte(int(value),row,cell,marker,date)
            assert restore_cell(a,r,row['frame'],cell)==q[cell]
        for name,alphabet in [('upper',b'0123456789ABCDEF'),('lower',b'0123456789abcdef')]:
            valid=[int(v) in alphabet for v in output]
            record=row['alphabets'][name]
            assert sum(valid)==record['valid_cells']
            assert [i for i,v in enumerate(valid) if not v]==record['invalid_cells']
            best=max(best,sum(valid))
    # Re-evaluate algebraic R prediction for the archived diagnostic winner only.
    for witness in d['best_witnesses']:
        row=d['rows'][witness['id']];name=witness['alphabet'];alphabet=b'0123456789ABCDEF' if name=='upper' else b'0123456789abcdef'
        unique=ambiguous=0;empty=[]
        for cell,value in enumerate(values[row['id']]):
            actual_a,actual_r=invert_byte(int(value),row,cell,marker,date);options=set()
            for char in alphabet:
                a,r=invert_byte(char,row,cell,marker,date)
                if a==actual_a:options.add(tuple(r))
            if not options:empty.append(cell)
            unique+=len(options)==1;ambiguous+=len(options)>1
        assert empty==witness['no_R_solution_cells']
        assert unique==witness['unique_R_solution_cells'] and ambiguous==witness['ambiguous_R_solution_cells']
    assert best==d['best_valid_hex_cells_out_of64'] and not d['key_candidates']
    from audit_fibonacci_residual_roles import channels
    collision=json.loads((ROOT/'research/data/residual_local_collisions.json').read_text())
    collision_checks=[]
    for row in collision['rows']:
        ab,rb=channels(sum(q,[]),row['frame'])
        av=[int(ab[i:i+4],2) for i in range(0,256,4)]
        rv=[int(rb[i:i+4],2) for i in range(0,256,4)]
        groups={}
        for i in range(64):
            key=(i//8,av[i])
            if row['clock']!='block_only':key+=(i%(2 if row['clock']=='cell_parity' else 4),)
            groups.setdefault(key,set()).add(rv[i])
        assert sum(len(v)>1 for v in groups.values())==row['conflicting_groups']
        for conflict in row['conflicts']:
            cert=conflict['certificate'];i,j=cert['i'],cert['j']
            assert av[i]==av[j]==cert['A'] and rv[i]==cert['R_i'] and rv[j]==cert['R_j'] and rv[i]!=rv[j]
        collision_checks.append(row['conflicting_groups'])
    out={'model':'C47','independent_full256sample_inverses':len(values),'independent_hex_cell_checks':len(values)*64*2,
         'diagnostic_R_solution_enumerations_independently_audited':len(d['best_witnesses']),
         'best_valid_hex_cells_out_of64':best,'key_candidates':0,'C48_independent_conflicting_group_counts':collision_checks,
         'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['research/data/image_directed_join_check.json','research/data/image_directed_join_outputs.npz','tools/audit_image_directed_join.py','research/data/residual_local_collisions.json','tools/audit_fibonacci_residual_roles.py']}}
    (ROOT/'research/data/image_directed_join_integrity.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
