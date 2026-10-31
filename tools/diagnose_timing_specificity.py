#!/usr/bin/env python3
"""Distinguish a low reference timing loss from specifically Morse evidence."""
import hashlib
import json
from pathlib import Path
import numpy as np
from check_timing_lattice import activities,runs

ROOT=Path(__file__).resolve().parents[1]
p=json.loads((ROOT/'research/data/pixel_measurements.json').read_text())
q=np.array(next(f['states'] for f in p['fits'] if f['start_x']==92 and f['step_px']==3
               and not f['restrict_delta_to_plus_minus_one'] and f['stroke_scale']==1))
r=json.loads((ROOT/'research/data/timing_lattice_check.json').read_text())
records=[]
for model in r['best_observed_models']:
    index=r['activity_rule_order'].index(model['rule'])
    states,lengths=runs(activities(q)[index]);states=states[1:-1]^model['inverted'];lengths=lengths[1:-1]
    units=3*lengths/model['unit_px'];assignments={};losses={}
    for grammar in ['morse_137','symmetric_13_without_word_gap']:
        errors=[]
        for label,mask,allowed in [('marks',states,[1,3]),('gaps',~states,[1,3,7] if grammar=='morse_137' else [1,3])]:
            distances=(units[mask,None]-np.array(allowed)[None,:])**2
            choice=np.argmin(distances,axis=1)
            errors.extend(distances[np.arange(len(choice)),choice].tolist())
            if grammar=='morse_137':
                assignments[label]={str(n):int(np.sum(np.array(allowed)[choice]==n)) for n in allowed}
        losses[grammar]=float(np.mean(errors))
    records.append({'model':model,'nearest_duration_assignments':assignments,'losses':losses,
                    'grammars_identical_on_observed':bool(np.isclose(*losses.values())),
                    'rms_error_in_units':float(np.sqrt(losses['morse_137']))})
out={'timing_result_sha256':hashlib.sha256((ROOT/'research/data/timing_lattice_check.json').read_bytes()).hexdigest(),
     'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'best_model_diagnostics':records,
     'interpretation':'Low surrogate reference fractions identify regularity relative to the specified controls. The best observed model uses no seven-unit word gaps and is unchanged by a non-word-gap 1/3 grammar; it does not identify Morse uniquely.',
     'not_a_new_key_search':True}
(ROOT/'research/data/timing_specificity.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
