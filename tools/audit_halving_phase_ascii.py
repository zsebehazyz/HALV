#!/usr/bin/env python3
"""Verify C35-C36 archives and the declared deterministic conclusions."""
import gzip
import hashlib
import json
from collections import Counter
from residual_channels import ROOT,nominal_states


def main():
    c35=json.loads((ROOT/'research/data/halving_invariants_check.json').read_text())
    c36=json.loads((ROOT/'research/data/phase_ascii_generator_check.json').read_text())
    verified={}
    for data in [c35,c36]:
        for path,expected in data['input_sha256'].items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
            verified[path]=expected
    hist=c35['histograms_by_block'];assert len({tuple(h) for h in hist})==8
    q=nominal_states().reshape(8,32)
    for pair in c35['all_block_pair_bounds']:
        b,c=[v-1 for v in pair['blocks_1based']]
        assert pair['maximum_matches_under_any_permutation']==sum(min(x,y) for x,y in zip(hist[b],hist[c]))
        assert pair['minimum_changed_samples']>0
        assert sorted(pair['optimal_source_index_permutation'])==list(range(32))
        witness=pair['optimal_source_index_permutation']
        assert sum(int(q[b,i])==int(value) for i,value in zip(witness,q[c]))==pair['maximum_matches_under_any_permutation']
    selected=c35['lag2_pairs'][4]
    assert selected['blocks_1based']==[5,7] and selected['high_bit_errors']==7 and selected['low_bit_errors']==0
    assert selected['absolute_height_differences_px']==[4]*7
    path=ROOT/c36['trial_log'];assert hashlib.sha256(path.read_bytes()).hexdigest()==c36['trial_log_sha256']
    counts=Counter();scores=Counter()
    with gzip.open(path,'rt') as stream:
        for line in stream:
            row=json.loads(line);counts[row['format']]+=1;scores[row['hex_characters_out_of64']]+=1
    assert dict(counts)==c36['format_trials'] and sum(counts.values())==c36['all_trials']
    assert scores==Counter({int(k):v for k,v in c36['histogram'].items()})
    assert max(scores)==29 and scores[64]==0 and not c36['complete_hex_readings']
    out={'purpose':'C35-C36 integrity and conclusion audit, not a new key search',
         'verified_input_files':len(verified),'all_block_pair_bounds':len(c35['all_block_pair_bounds']),
         'target_pair_7_height_differences_px':[4]*7,'all_format_trial_records':sum(counts.values()),
         'complete_hex_readings':0,'unique_valid_scalars':c36['unique_valid_scalars'],
         'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                         ['research/data/halving_invariants_check.json','research/data/phase_ascii_generator_check.json','tools/audit_halving_phase_ascii.py']}}
    (ROOT/'research/data/halving_phase_ascii_integrity.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
