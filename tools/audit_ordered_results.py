#!/usr/bin/env python3
"""Audit archived C28-C30 counts, source hashes and candidate provenance.

Archive the large generated candidate JSON losslessly; no new key search.
Run after all three check_ordered_* programs.
"""
import gzip
import hashlib
import json
from collections import Counter
import numpy as np
from ordered_decode_common import *
from check_ordered_formats import public_hashes, key_views
from bitcoin_oracle import addresses, b58decode, ORDER, TARGET


def main():
    files = ['ordered_control_check.json', 'ordered_arithmetic_check.json',
             'ordered_format_check.json']
    checks = [json.loads((ROOT/'research/data'/name).read_text()) for name in files]
    verified = {}
    for result in checks:
        for name, expected in result['input_sha256'].items():
            actual = hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
            assert actual == expected, name
            verified[name] = actual
    c28, c29, c30 = checks
    cases = json.loads((ROOT/'research/data/ordered_control_cases.json').read_text())
    mask = marker()
    for case in cases:
        bits, r = bit_arrays(case)
        recipe = case['recipe']; frame = recipe['frame']
        a = unlayout(bits, frame)
        if recipe['kind'] != 'identity':
            sel = recipe['residual_selector']
            u = (r.sum(1)%2 if sel == 'parity_R' else np.any(r,axis=1).astype(int)
                 if sel == 'nonzero_R' else np.zeros(64,int) if sel == 'none'
                 else r[:,int(sel[1])])
            u = u ^ recipe['global_polarity']
            if recipe['marker_polarity']: u = u ^ np.repeat(mask,8)
            shifted, flag = flag_inverse(a,u)
            original = np.empty_like(shifted)
            original[neighbor_permutation(recipe['neighbor'],mask)] = shifted
            a = np.c_[original,flag]
        assert np.array_equal(restore(a,r,'absolute' if frame == 'zero_position' else frame), nominal_states())
    recipes_path = ROOT/c29['recipe_log']
    assert hashlib.sha256(recipes_path.read_bytes()).hexdigest() == c29['recipe_log_sha256']
    with gzip.open(recipes_path,'rt') as stream: recipes = [json.loads(line) for line in stream]
    assert len(recipes) == c29['attempts_including_duplicates']
    formed = {r['payload32_hex'] for r in recipes if r['status'] == 'formed'}
    assert len(formed) == c29['unique_formed_payloads32']
    physical = Counter((r['domain'],r['status']) for r in recipes if 'domain' in r)
    trial_path = ROOT/'research/data/ordered_format_trials.jsonl.gz'
    assert hashlib.sha256(trial_path.read_bytes()).hexdigest() == c30['format_trials_sha256']
    with gzip.open(trial_path,'rt') as stream: trials = [json.loads(line) for line in stream]
    counts = Counter(row['format'] for row in trials)
    assert counts['ASCII7_WIF50'] == c30['wif_format_gate']['ASCII7_trials']
    hist = Counter(row['base58_characters'] for row in trials if row['format'] == 'ASCII7_WIF50')
    assert hist == Counter({int(k):v for k,v in c30['wif_format_gate']['histogram'].items()})
    assert counts['ASCII64_hex'] == c30['ascii64_hex_gate']['streams']
    original = ROOT/'research/data/ordered_key_candidates.json'
    archive = original.with_suffix('.json.gz')
    if original.exists():
        raw = original.read_bytes()
        with gzip.GzipFile(filename=str(archive),mode='wb',mtime=0) as stream: stream.write(raw)
        assert gzip.decompress(archive.read_bytes()) == raw
        original.unlink()  # Only the regenerated large JSON; bytes preserved above.
    else: raw = gzip.decompress(archive.read_bytes())
    candidates = json.loads(raw)
    keys = {bytes.fromhex(row['key_hex']) for row in candidates}
    assert len(keys) == len(candidates) == c30['unique_valid_scalars']
    assert all(len(k) == 32 and 0 < int.from_bytes(k,'big') < ORDER for k in keys)
    assert hashlib.sha256(b''.join(sorted(keys))).hexdigest() == c30['candidate_set_sha256']
    expected = {view for data in formed for view,_ in key_views(bytes.fromhex(data))}
    expected.update(view for row in cases for view,_ in key_views(bytes.fromhex(row['main32_hex'])))
    assert expected == keys
    # Small cross-check of point serialization with the pre-existing address path.
    ordered = sorted(keys); sample = [ordered[i*(len(ordered)-1)//15] for i in range(16)]
    for key in sample:
        for fmt, address in addresses(key).items():
            assert b58decode(address)[1:21] == public_hashes(key)[fmt]
            assert address != TARGET
    result = {'purpose':'Archive/integrity audit, not a new key search',
              'verified_input_files':len(verified),'roundtrip_cases':len(cases),
              'states_per_roundtrip':256,'arithmetic_log_records':len(recipes),
              'geometry_records_by_domain_and_status':[
                  {'domain':domain,'status':status,'count':count}
                  for (domain,status),count in sorted(physical.items())],
              'format_log_records':dict(counts),'exact_candidate_union_verified':True,
              'candidate_count':len(keys),'public_key_serialization_crosschecks':len(sample)*2,
              'candidate_archive':str(archive.relative_to(ROOT)),
              'candidate_archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
              'candidate_uncompressed_sha256':hashlib.sha256(raw).hexdigest(),
              'audit_tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    dump('ordered_integrity_audit.json', result)
    print(json.dumps(result,indent=2))


if __name__ == '__main__': main()
