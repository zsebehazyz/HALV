#!/usr/bin/env python3
"""C48 exact collision certificates, no fitted lookup or private-key search."""
import hashlib,json
from collections import defaultdict
from residual_channels import ROOT,nominal_states,extract,nibble_values


def main():
    results=[];q=nominal_states()
    for frame in ['absolute','phase_relative']:
        a,r=extract(q,frame);av=nibble_values(a);rv=nibble_values(r)
        for clock in ['block_only','cell_parity','cell_mod4']:
            groups=defaultdict(list)
            for i in range(64):
                key=(i//8,int(av[i]))+(() if clock=='block_only' else (i%(2 if clock=='cell_parity' else 4),))
                groups[key].append(i)
            conflicts=[]
            for key,indices in groups.items():
                values={int(rv[i]) for i in indices}
                if len(values)>1:
                    first=next((x,y) for x in indices for y in indices if rv[x]!=rv[y])
                    conflicts.append({'key':key,'cells':indices,'R_values':[int(rv[i]) for i in indices],
                                      'certificate':{'i':first[0],'j':first[1],'A':int(av[first[0]]),'R_i':int(rv[first[0]]),'R_j':int(rv[first[1]])}})
            results.append({'frame':frame,'clock':clock,'conflicting_groups':len(conflicts),'conflicts':conflicts,
                            'scope':'R=f(A,block,counter_modulus); block id grants MORE information than any fixed blockwise marker/date/phase cue. Conflict disproves this deterministic pointwise family only.'})
    names=['research/data/pixel_measurements.json','tools/residual_channels.py','tools/check_residual_local_collisions.py']
    out={'model':'C48','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in names},'rows':results,
         'no_fitted_parameters':True,'no_key_search':True,
         'limitations':'Does not excludeR carrying independent data, neighbor-dependent rules, unobserved state or redefined payload after nonlinear joining; absence of a collision does not validate a generator.'}
    (ROOT/'research/data/residual_local_collisions.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps([{'frame':r['frame'],'clock':r['clock'],'conflicts':r['conflicting_groups']} for r in results],indent=2))

if __name__=='__main__':main()
