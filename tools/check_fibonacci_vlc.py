#!/usr/bin/env python3
"""C44 standard variable-length Fibonacci codes; no padding or prefix deletion."""
import hashlib
import itertools
import json
from collections import Counter
import numpy as np
from residual_channels import ROOT, nominal_states, extract
from bitcoin_oracle import addresses, TARGET, b58decode, sha256, selftest


def encode(n):
    if n < 1:
        raise ValueError('positive integers only')
    weights = [1, 2]
    while weights[-1] <= n:
        weights.append(sum(weights[-2:]))
    weights = [w for w in weights if w <= n]
    bits = [0] * len(weights)
    for i in range(len(weights)-1, -1, -1):
        if weights[i] <= n:
            bits[i] = 1
            n -= weights[i]
    assert n == 0
    return ''.join(map(str, bits)) + '1'


def parse(bits):
    values, spans = [], []
    start = 0
    while True:
        end = bits.find('11', start)
        if end < 0:
            break
        word = bits[start:end+2]
        a, b, value = 1, 2, 0
        for bit in word[:-1]:
            value += (bit == '1') * a
            a, b = b, a+b
        assert encode(value) == word
        values.append(value)
        spans.append([start, end+2])
        start = end+2
    return values, spans, bits[start:]


def sources(q):
    for perm in itertools.permutations(range(4)):
        yield 'q_' + ''.join(map(str, perm)), ''.join(format(perm[int(x)], '02b') for x in q.flatten())
    for name, plane in [('H', q >> 1), ('L', q & 1)]:
        yield name, ''.join(map(str, plane.flatten().tolist()))
    for frame in ['absolute', 'phase_relative']:
        a, r = extract(q, frame)
        for name, array in [('A256', a), ('R256', r), ('R96', r.reshape(8,8,4)[[0,1,7]])]:
            yield frame+'_'+name, ''.join(map(str, array.flatten().tolist()))


def recipes(q):
    for name, bits in sources(q):
        for rev, inv in itertools.product([False, True], repeat=2):
            seq = bits[::-1] if rev else bits
            if inv:
                seq = seq.translate(str.maketrans('01', '10'))
            for framing in ['continuous', 'eight_equal_blocks']:
                width = len(seq) if framing == 'continuous' else len(seq)//8
                chunks = [seq[i:i+width] for i in range(0,len(seq),width)]
                parsed = [parse(chunk) for chunk in chunks]
                values = list(itertools.chain.from_iterable(p[0] for p in parsed))
                yield {'source': name, 'reverse_bits': rev, 'complement': inv, 'framing': framing,
                       'bit_length': len(seq), 'bits': seq, 'values': values,
                       'word_spans_per_chunk': [p[1] for p in parsed],
                       'unfinished_suffixes': [p[2] for p in parsed],
                       'complete': all(not p[2] for p in parsed)}


def summary(rows):
    complete = [r for r in rows if r['complete']]
    return {'recipes':len(rows), 'complete':len(complete),
            'complete_by_framing':dict(Counter(r['framing'] for r in complete)),
            'complete_byte_mappings':sum(all(0 <= v-shift <= 255 for v in r['values'])
                                         for r in complete for shift in [0,1]),
            'complete_32_integer_streams':sum(len(r['values'])==32 for r in complete)}


def candidates(row):
    out=[]
    if not row['complete']:
        return out
    for shift in [0,1]:
        values=[n-shift for n in row['values']]
        if not all(0<=n<=255 for n in values):
            continue
        data=bytes(values)
        keys=[]
        if len(data)==32:
            keys.append(('raw32',data))
        if len(data)==64 and all(c in b'0123456789abcdefABCDEF' for c in data):
            keys.append(('hex64',bytes.fromhex(data.decode('ascii'))))
        if len(data) in [51,52]:
            try:
                raw=b58decode(data.decode('ascii'))
                if len(raw) in [37,38] and raw[0]==128 and sha256(sha256(raw[:-4]))[:4]==raw[-4:] and (len(raw)==37 or raw[-5]==1):
                    keys.append(('WIF',raw[1:33]))
            except (ValueError, UnicodeError):
                pass
        for kind,key in keys:
            addrs=addresses(key)
            out.append({'shift':shift,'kind':kind,'valid_scalar':bool(addrs),
                        'target_match':TARGET in addrs.values(),'addresses':addrs})
    return out


def main():
    expected=['11','011','0011','1011','00011','10011','01011','000011','100011','010011']
    assert [encode(i) for i in range(1,11)]==expected
    for n in range(1,4097):
        assert parse(encode(n)) == ([n], [[0,len(encode(n))]], '')
    assert parse('1111')[0]==[1,1]
    assert parse('11000')[2]=='000'
    assert parse('101')[2]=='101'
    selftest()
    q=nominal_states()
    rows=list(recipes(q))
    for row in rows:
        row['candidates']=candidates(row)
    rng=np.random.default_rng(441101)
    controls=[]
    for draw in range(128):
        shuffled=np.array([rng.permutation(b) for b in q.reshape(8,32)]).reshape(64,4)
        controls.append({'draw':draw,**summary(list(recipes(shuffled)))})
    observed=summary(rows)
    names=['research/models/fibonacci_vlc_v1.json','research/data/pixel_measurements.json',
           'tools/check_fibonacci_vlc.py','tools/residual_channels.py','tools/bitcoin_oracle.py']
    out={'model':'C44','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in names},
         'calibration':{'known_codes':10,'integer_roundtrips':4096,'terminator_consumption':True,'unfinished_suffix_rejected':True},
         'summary':observed,'candidate_count':sum(len(r['candidates']) for r in rows),
         'target_matches':sum(c['target_match'] for r in rows for c in r['candidates']),
         'rows':rows,'controls':controls,
         'control_counts_ge_observed':{k:sum(c[k]>=observed[k] for c in controls)
                                     for k in ['complete','complete_byte_mappings','complete_32_integer_streams']},
         'limitations':json.loads((ROOT/names[0]).read_text())['limitations']}
    (ROOT/'research/data/fibonacci_vlc_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['rows','controls','input_sha256','limitations']},indent=2))

if __name__=='__main__':
    main()
