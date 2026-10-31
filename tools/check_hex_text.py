#!/usr/bin/env python3
"""Check whether the 512 reconstructed bits are 64 ASCII hexadecimal digits."""
import itertools
import json
from pathlib import Path
from bitcoin_oracle import TARGET,addresses

ROOT=Path(__file__).resolve().parents[1]
p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
q=next(f['states'] for f in p['fits'] if f['start_x']==92 and f['step_px']==3
       and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1)
results=[];matches=[]
for reverse in [False,True]:
    for perm in itertools.permutations(range(4)):
        s=q[::-1] if reverse else q
        v=[perm[x] for x in s]
        raw=bytes(sum(v[i+j]<<(6-2*j) for j in range(4)) for i in range(0,256,4))
        score=sum(c in b'0123456789abcdefABCDEF' for c in raw)
        results.append({'reverse':reverse,'permutation':list(perm),'hex_characters':score})
        if score==64:
            key=bytes.fromhex(raw.decode('ascii'))
            if TARGET in addresses(key).values():matches.append({'reverse':reverse,'permutation':perm,'key_hex':key.hex()})
out={'image_sha256':p['sha256'],'hypotheses':len(results),'required_hex_characters':64,
     'best_hex_character_count':max(r['hex_characters'] for r in results),
     'valid_hex_strings':sum(r['hex_characters']==64 for r in results),'matches':matches,'results':results}
(ROOT/'research/data/hex_text_check.json').write_text(json.dumps(out,indent=2)+'\n')
print({k:v for k,v in out.items() if k!='results'})
