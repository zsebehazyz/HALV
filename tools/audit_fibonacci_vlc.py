#!/usr/bin/env python3
"""C44 independent regex framing and Fibonacci-weight audit."""
import hashlib
import itertools
import json
import re
from collections import Counter
from residual_channels import ROOT
from check_fibonacci_vlc import parse


def independent(bits):
    values=[];spans=[];cursor=0
    while (match:=re.compile(r'(?:0|10)*11').match(bits,cursor)) is not None:
        payload=match.group()[:-1]
        weights=[1,2]
        for _ in range(max(0,len(payload)-2)):
            weights.append(weights[-1]+weights[-2])
        values.append(sum(w for w,b in zip(weights,payload) if b=='1'))
        spans.append([cursor,match.end()]);cursor=match.end()
    return values,spans,bits[cursor:]


def main():
    data=json.loads((ROOT/'research/data/fibonacci_vlc_check.json').read_text())
    for name,digest in data['input_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    count=0
    for width in range(13):
        for bits in itertools.product('01',repeat=width):
            bits=''.join(bits)
            assert independent(bits)==parse(bits)
            count+=1
    complete=Counter();byte_mappings=0
    for row in data['rows']:
        bits=row['bits'];width=len(bits) if row['framing']=='continuous' else len(bits)//8
        values=[];tails=[];spans=[]
        for start in range(0,len(bits),width):
            v,s,t=independent(bits[start:start+width]);values.extend(v);spans.append(s);tails.append(t)
        assert values==row['values'] and tails==row['unfinished_suffixes'] and spans==row['word_spans_per_chunk']
        assert row['complete']==all(not t for t in tails)
        if row['complete']:
            complete[row['framing']]+=1
            byte_mappings+=sum(all(0<=v-shift<=255 for v in values) for shift in [0,1])
    assert dict(complete)==data['summary']['complete_by_framing']
    assert byte_mappings==data['summary']['complete_byte_mappings']==0
    out={'model':'C44','exhaustive_binary_strings_through12bits':count,
         'independently_decoded_recipes':len(data['rows']),
         'complete_by_framing':dict(complete),'complete_byte_mappings':byte_mappings,
         'all_input_hashes_verified':True,
         'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                        ['research/data/fibonacci_vlc_check.json','tools/audit_fibonacci_vlc.py']}}
    (ROOT/'research/data/fibonacci_vlc_integrity.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
