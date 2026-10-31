#!/usr/bin/env python3
"""Bounded, explicit transforms of the fitted 256-state model. Not a full search."""
import itertools
import json
from pathlib import Path
from bitcoin_oracle import TARGET, ORDER, addresses, sha256, selftest

ROOT = Path(__file__).resolve().parents[1]

def pack(bits):
    return int(''.join(map(str, bits)), 2).to_bytes(len(bits)//8, 'big')

def main():
    verification = selftest()
    measurement = json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
    # Only a predeclared family: x=92, spacing=3, straight, four-state fits.
    fits = [f for f in measurement['fits'] if f['start_x']==92 and f['step_px']==3
            and not f['restrict_delta_to_plus_minus_one']]
    candidates = {}
    def add(key, label):
        if len(key) == 32:
            candidates.setdefault(key, label)
    def variants(key, label):
        for b, suffix in [(key, 'identity'), (key[::-1], 'byte_reverse'),
                          (bytes(x^255 for x in key), 'complement')]:
            add(b, label+'/'+suffix)
    for f in fits:
        q = f['states']
        base = 'stroke='+str(f['stroke_scale'])
        for rev in [False, True]:
            s = q[::-1] if rev else q
            tag = base+'/reverse='+str(rev)
            # All 14 nonconstant boolean projections of four states.
            for mask in range(1, 15):
                variants(pack([(mask>>v)&1 for v in s]), tag+'/projection='+str(mask))
            # Four declared initial states; test differences rather than amplitudes.
            for initial in range(4):
                diffs = [b-a for a,b in zip([initial]+s[:-1], s)]
                # Every nonconstant partition of the observed -3..+3 difference alphabet.
                for mask in range(1, 127):
                    variants(pack([(mask>>(d+3))&1 for d in diffs]),
                             tag+'/difference/initial='+str(initial)+'/projection='+str(mask))
            # All bijections of states to two bits: 512 fitted bits -> bounded halvings.
            for perm in itertools.permutations(range(4)):
                bits = [bit for v in s for bit in ((perm[v]>>1)&1, perm[v]&1)]
                raw = pack(bits)
                label = tag+'/permutation='+''.join(map(str, perm))
                for name, key in [('first', raw[:32]), ('second', raw[32:]),
                                  ('even_bytes', raw[::2]), ('odd_bytes', raw[1::2]),
                                  ('xor_halves', bytes(a^b for a,b in zip(raw[:32],raw[32:]))),
                                  ('sha256', sha256(raw)), ('double_sha256', sha256(sha256(raw)))]:
                    variants(key, label+'/'+name)
            # Literal reconstructed samples, binary and ASCII, with explicit hashes.
            for name, raw in [('bytes', bytes(s)), ('ascii', ''.join(map(str, s)).encode())]:
                variants(sha256(raw), tag+'/'+name+'/sha256')
                variants(sha256(sha256(raw)), tag+'/'+name+'/double_sha256')
            # Differences -> standard 8SVX table indices (lossless within this model).
            table = [-34,-21,-13,-8,-5,-3,-2,-1,0,1,2,3,5,8,13,21]
            delta = [b-a for a,b in zip([0]+s[:-1], s)]
            nibbles = [table.index(d) for d in delta]
            for swap in [False, True]:
                raw = bytes((b<<4)|a if swap else (a<<4)|b for a,b in zip(nibbles[::2],nibbles[1::2]))
                label = tag+'/fib_delta_indices/swap='+str(swap)
                variants(sha256(raw), label+'/sha256')
                for k in range(4): variants(raw[k*32:(k+1)*32], label+'/quarter='+str(k))
    matches = []
    valid = 0
    for key, label in candidates.items():
        if not 0 < int.from_bytes(key, 'big') < ORDER:
            continue
        valid += 1
        for fmt, address in addresses(key).items():
            if address == TARGET:
                matches.append({'transform':label, 'format':fmt, 'key_hex':key.hex()})
    reference = fits[0]['states']
    stability = [{'stroke_scale':f['stroke_scale'],
                  'different_indices':[i for i,(a,b) in enumerate(zip(reference,f['states'])) if a!=b]}
                 for f in fits]
    result = {'selftest': verification, 'image_sha256':measurement['sha256'],
              'fits_tested':len(fits), 'state_stability_relative_to_stroke_1':stability,
              'unique_32byte_candidates':len(candidates), 'valid_scalars_checked':valid,
              'public_key_formats_per_valid_scalar':2, 'matches':matches,
              'candidate_set_sha256':sha256(b''.join(sorted(candidates))).hex(),
              'limitation':'A negative applies only to these reconstructions and declared transforms. No uncertainty expansion, full waveform decoder, or exhaustive key search.'}
    (ROOT/'research/data/candidate_check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
