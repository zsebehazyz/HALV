#!/usr/bin/env python3
"""Check whether 128 hypothetical 4-state HALV waveform symbols expose funding
TXID's 128 dibits better than random 256-bit identifiers. Exploratory test.
Selection of waveform decoders is finite/predeclared; report null-simulation
that performs the same broad search, to avoid spurious significance.
"""
import csv, itertools, hashlib, json
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
Q=np.array([int(r['round_q']) for r in csv.DictReader((D/'HALV_256_minta_20261031.csv').open())],dtype=np.uint8)
assert len(Q)==256
TX=bytes.fromhex('30946152b5f24ed975a26b28a46cb19d1ef2728159c5806544ffd0c2fb535205')
perm=np.array(list(itertools.permutations(range(4))),dtype=np.int8)
r=np.arange(4)
spec={
 'pair_first':Q[::2],
 'pair_second':Q[1::2],
 'pair_min':np.minimum(Q[::2],Q[1::2]),
 'pair_max':np.maximum(Q[::2],Q[1::2]),
 'pair_xor':Q[::2]^Q[1::2],
 'pair_sum_mod4':(Q[::2]+Q[1::2])%4,
 'pair_diff_mod4':(Q[::2]-Q[1::2])%4,
}
def dibits(tx):
 return np.array([(x>>s)&3 for x in tx for s in (6,4,2,0)],dtype=np.uint8)
def best(t):
 result=(-1,None)
 for tx_orientation,t0 in [('tx_be',t),('tx_be_reverse_symbols',t[::-1])]:
  for k,q0 in spec.items():
   for direction,q in [('forward',q0),('reverse',q0[::-1])]:
    for shift in range(128):
     tt=np.roll(t0,shift)
     h=np.bincount(q*4+tt,minlength=16).reshape(4,4)
     # perm maps old symbols q=0..3 onto the txid dibit 0..3
     scores=np.sum(h[r[None,:],perm],axis=1)
     idx=int(np.argmax(scores));score=int(scores[idx])
     if score>result[0]:result=(score,(k,direction,tx_orientation,shift,perm[idx].tolist()))
 return result

if __name__=='__main__':
 observed=best(dibits(TX))
 # Pseudo-random independent 256-bit identifiers instead of altering the waveform.
 # Apply EXACT same model selection to each sample, so all multiple comparisons are included.
 null=[]
 for j in range(400):
  random_tx=hashlib.sha256(TX+j.to_bytes(4,'little')+b'HALV-NULL-V1').digest()
  null.append(best(dibits(random_tx))[0])
 hist={str(i):null.count(i) for i in sorted(set(null))}
 report={
   'observed_max_correct_128':observed[0],
   'observed_best_parameters':observed[1],
   'random_trials':len(null),
   'random_min':min(null),'random_median':float(np.median(null)),'random_max':max(null),
   'random_count_at_least_observed':sum(x>=observed[0] for x in null),
   'empirical_p_with_plus_one':(1+sum(x>=observed[0] for x in null))/(1+len(null)),
   'random_histogram':hist,
   'tested':f'{len(spec)} waveform pairing schemes x both directions x both txid orientations x 128 shifts x 24 bijective state mappings',
   'warning':'This can only reject a direct substituted/shifted-dibit encoding; XOR with a truly unknown secret would show no correlation.'
 }
 (D/'HALV_TXID_128_szimbólum_egyezes_kontroll_20261101.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
 print(json.dumps({k:report[k] for k in report if k!='random_histogram'},ensure_ascii=False,indent=2))
