#!/usr/bin/env python3
"""Verify C31-C34 source fingerprints, exhaustive logs and exact area identity."""
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path
from residual_channels import ROOT


def main():
    state=json.loads((ROOT/'research/data/stateful_bridge_check.json').read_text())
    nonlinear=json.loads((ROOT/'research/data/nonlinear_context_check.json').read_text())
    verified={};counts=Counter();maximal=0;hist=Counter()
    for result in [state,nonlinear]:
        for path,expected in result['input_sha256'].items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
            verified[path]=expected
        p=ROOT/result['trial_log']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==result['trial_log_sha256']
        with gzip.open(p,'rt') as stream:
            for line in stream:
                row=json.loads(line);model=row.get('model','C34');counts[model]+=1
                if model=='C31':
                    assert row['status']=='training_inconsistent'
                    if row['input_memory']==row['output_memory']==4:maximal+=1
                elif model in ['C32','C33']:assert not row['training_exact']
                elif row['training_exact']:hist[(row['known_cells'],row['correct_cells'])]+=1
    for model in ['C31','C32','C33']:assert counts[model]==state['counts'][model+'_configurations']
    assert counts['C34']==nonlinear['counts']['configurations']
    assert sum(hist.values())==nonlinear['counts']['training_exact']
    expected=Counter({(v['known_cells'],v['correct_cells']):v['configurations'] for v in nonlinear['heldout_coverage_histogram']})
    assert hist==expected
    cancelled=[];area_checks=0
    for pair in state['geometric_consequences']:
        dq=[b-a for a,b in zip(pair['source_samples'],pair['aligned_target_samples'])]
        h=dq+[dq[-1]]
        direct=[]
        for cell in range(8):
            # Four separate trapezoids of3px width atq/2 height: denominator4.
            numerator=sum(3*(h[i]+h[i+1]) for i in range(4*cell,4*cell+4))
            direct.append(numerator);area_checks+=1
            if numerator==0 and any(h[4*cell:4*cell+5]):
                cancelled.append({'blocks_1based':pair['blocks_1based'],'cell_zero_based':cell,
                                  'five_difference_nodes':h[4*cell:4*cell+5]})
        assert direct==pair['signed_area_change_quarter_numerators']
        assert sum(direct)==sum(3*(h[i]+h[i+1]) for i in range(32))
    assert maximal==4608
    out={'purpose':'Integrity and mathematical consequence audit, not new key search',
         'verified_input_files':len(verified),'trial_records':dict(counts),
         'C31_maximal_feature_spaces_inconsistent':maximal,
         'C31_nested_lower_memories_also_inconsistent':True,
         'C34_training_exact':sum(hist.values()),'C34_max_known_heldout_cells':max(k for k,c in hist),
         'C34_max_correct_heldout_cells':max(c for k,c in hist),
         'exact_area_cells_checked':area_checks,'nontrivial_zero_area_cells':cancelled,
         'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                         ['research/data/stateful_bridge_check.json','research/data/nonlinear_context_check.json','tools/audit_stateful_bridge.py']}}
    (ROOT/'research/data/stateful_bridge_integrity.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
