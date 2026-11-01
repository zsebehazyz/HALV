#!/usr/bin/env python3
"""Independent overlap/conflict audit for the C37-C38 snapshot."""
import hashlib
import json
from residual_channels import ROOT,nominal_states


def conflicts_at(q,starts):
    seen={};conflicts=0
    for b in [2,3,4,5]:
        for k,value in enumerate(q[b]):
            key=(b%2,starts[b]+k);value=int(value)
            if key in seen and seen[key]!=value:conflicts+=1
            else:seen[key]=value
    return conflicts


def main():
    a=json.loads((ROOT/'research/data/sliding_window_generator_check.json').read_text())
    b=json.loads((ROOT/'research/data/two_plane_window_check.json').read_text())
    verified={}
    for result in [a,b]:
        for name,digest in result['input_sha256'].items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
            verified[name]=digest
    q=nominal_states().reshape(8,32)
    for row in a['all_trials']:
        n=conflicts_at(q,row['starts']);assert n==row['training_conflicts'] and n>0
    for row in b['all_plane_trials']:
        plane=q>>1 if row['plane']=='high' else q&1
        n=conflicts_at(plane,row['starts']);assert n==row['training_conflicts'] and n>0
    for d in a['linear_overlap_diagnostics']:
        i,j=[v-1 for v in d['blocks_1based']];exact=[]
        for row in d['all_displacements']:
            offset=row['displacement_target_start']
            pairs=[(int(q[i,k]),int(q[j,k-offset])) for k in range(32) if 0<=k-offset<32]
            assert len(pairs)==row['overlap_samples']
            assert sum(x==y for x,y in pairs)==row['exact_samples']
            if all(x==y for x,y in pairs):exact.append(len(pairs))
        assert max(exact,default=0)==d['longest_exact_whole_overlap']
    out={'purpose':'Independent exact-window and binary-plane audit, not a key search',
         'verified_input_files':len(verified),'full_state_trials_verified':len(a['all_trials']),
         'binary_plane_trials_verified':len(b['all_plane_trials']),
         'whole_boundary_overlap_lengths':[d['longest_exact_whole_overlap'] for d in a['linear_overlap_diagnostics']],
         'new_template_successes':0,
         'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                         ['research/data/sliding_window_generator_check.json','research/data/two_plane_window_check.json','tools/audit_window_generators.py']}}
    (ROOT/'research/data/window_generators_integrity.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
