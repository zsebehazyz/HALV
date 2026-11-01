#!/usr/bin/env python3
"""Audits a NEW falsifiable idea, not a solved key: 352 hypothesized bits
might be 50 7-bit ASCII WIF characters plus two padding bits; the leading '5'
would have been omitted as in Zden's SFX and whitepaper puzzles.
Source: recorded 256 HALV 4-level samples, SHA-gated original PNG.
"""
import csv, hashlib, itertools, json, collections
from pathlib import Path
D=Path(__file__).resolve().parent
f=D/'cryptoHALV (1).png'
sha=hashlib.sha256(f.read_bytes()).hexdigest()
assert sha=='3a487ebaeb4801137f09159a2d533046936cd395f4e2f7d115ac554607790e95'
rows=list(csv.DictReader((D/'HALV_256_minta_20261031.csv').open()))
q=[[int(rows[b*32+i]['round_q']) for i in range(32)] for b in range(8)]
phase={2:1,3:0,4:3,5:2,6:1}
alphabet='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
charsets=set(alphabet)
models=0
best=[]
perfect=0
scores=collections.Counter()
for perm in itertools.permutations(range(4)):
 for outer_bit_order in ['hi-lo','lo-hi']:
  for cell_reverse in [False,True]:
   for block_reverse in [False,True]:
    for bit_reverse in [False,True]:
     bits=[]
     for b in (range(7,-1,-1) if block_reverse else range(8)):
      z=q[b]
      if b not in phase:
       for v in (z[::-1] if cell_reverse else z):
        bits.extend([(v>>1)&1,v&1] if outer_bit_order=='hi-lo' else [v&1,(v>>1)&1])
      else:
       groups=[z[4*g:4*g+4] for g in range(8)]
       if cell_reverse:groups=groups[::-1]
       p=phase[b]
       for cell in groups:
        nib=[(cell[j]>>1)&1 for j in range(4) if j!=p]+[cell[(p-1)%4]&1]
        bits.extend([nib[j] for j in perm])
     assert len(bits)==352
     if bit_reverse:bits=bits[::-1]
     for offset in range(3):
      for reverse_7bit in [False,True]:
       for inverse in [False,True]:
        chars=[]
        for start in range(offset,offset+350,7):
         grp=bits[start:start+7]
         if reverse_7bit:grp=grp[::-1]
         number=0
         for x in grp:number=number*2+(x^inverse)
         chars.append(chr(number))
        nbase=sum(c in charsets for c in chars)
        nprint=sum(32<=ord(c)<127 for c in chars)
        scores[nbase]+=1
        models+=1
        if nbase==50: perfect+=1
        obj={'base58_count':nbase,'ascii_printable_count':nprint,'text':''.join(c if 32<=ord(c)<127 else '.' for c in chars),
             'mapping':perm,'outer_bit_order':outer_bit_order,'cell_reverse':cell_reverse,
             'block_reverse':block_reverse,'full_bit_reverse':bit_reverse,
             'seven_bit_reverse':reverse_7bit,'inverse':inverse,'offset':offset}
        best.append(obj)
best.sort(key=lambda x:(x['base58_count'],x['ascii_printable_count']), reverse=True)
result={'source_sha256':sha,'model':'352 bits from 3 outer (2-bit) plus 5 middle (4-bit) block sets, search 7-bit ASCII WIF without leading 5',
 'models_tested':models,'perfect_base58_strings':perfect,'highest_base58_chars_in_50':best[0]['base58_count'],
 'highest_printable':max(x['ascii_printable_count'] for x in best), 'top5':best[:5],
 'scoring_histogram':{str(k):v for k,v in sorted(scores.items())},
 'caveat':'The 352-bit representation and 3+1 encoding are speculative, this only tests simple shared reading conventions.'}
(D/'HALV_352bit_WIF7_audit_20261101.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ('scoring_histogram',)},ensure_ascii=False,indent=2))
