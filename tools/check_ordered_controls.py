#!/usr/bin/env python3
"""C28: historically calibrated, invertible controls and neighbor reconstruction."""
import json
import numpy as np
from ordered_decode_common import *

def historical_control():
    old=json.loads((ROOT/'research/data/historical_level2_control.json').read_text());layers=[[] for _ in range(7)]
    for row in old['raw_sectors']:
        for j,(p,q) in enumerate([(0,1),(2,3),(4,5),(6,6),(7,8),(9,10),(11,12)]):layers[j].extend([row[p],row[q]])
    data=[];flags=[]
    for i in range(51):
        data.append([layers[j][2*((i+1)%51)] for j in [0,1,2,4,5,6]]);flags.append(layers[3][2*i])
    decoded=flag_decode(np.array(data),np.array(flags));text=[]
    for row in decoded:
        bits=np.r_[row[:3],row[6],row[3:6]];text.append(chr(int(''.join(map(str,bits)),2)))
    assert ''.join(text)==old['decoded_ascii7_before_rotation']
    return {'historical_level2_characters_reproduced':51,'historical_target_already_verified':old['historical_target_match']}

def main():
    settings=spec();states=nominal_states();mask=marker();control=historical_control();cases=[]
    stair=json.loads((ROOT/'research/data/signature_phase_decode_check.json').read_text())
    assert [positions(b,'absolute')[0] for b in range(8)]==[r['predicted_zero_phase'] for r in stair['block_phase_predictions']]
    for frame in settings['C28']['frames']:
        base_frame='absolute' if frame=='zero_position' else frame
        a,r=extract(states,base_frame);local=a[:,3];block_mask=np.repeat(mask,8)
        selectors={'none':np.zeros(64,int),'parity_R':r.sum(1)%2,'nonzero_R':np.any(r,axis=1).astype(int)}
        selectors.update({f'R{i}':r[:,i] for i in range(4)})
        for kind in ['identity','controlled']:
            configurations=[('none',False,0,'current')] if kind=='identity' else [
                (sel,marked,polarity,neighbor) for sel in settings['C28']['residual_controls'] for marked in [False,True]
                for polarity in [0,1] for neighbor in settings['C28']['neighbors']]
            for selector,marked,polarity,neighbor in configurations:
                perm=neighbor_permutation(neighbor,mask);u=selectors[selector]^(block_mask if marked else 0)^polarity
                decoded=a.copy() if kind=='identity' else flag_decode(a[perm,:3],local^u)
                if kind=='identity':back=a.copy()
                else:
                    shifted,f=flag_inverse(decoded,u);d=np.empty_like(shifted);d[perm]=shifted;back=np.c_[d,f]
                assert np.array_equal(restore(back,r,base_frame),states)
                view=layout(decoded,frame);assert np.array_equal(unlayout(view,frame),decoded)
                case={'case_id':len(cases),'recipe':{'frame':frame,'kind':kind,'residual_selector':selector,
                      'marker_polarity':marked,'global_polarity':polarity,'neighbor':neighbor},
                      'main32_hex':packed(view).hex(),'outer_residual12_hex':edge_residual(r).hex(),
                      'full_residual64_nibbles_hex':''.join(f'{v:x}' for v in nibble_values(r)),
                      'roundtrip_states_checked':256,'complement_diagnostic':complement_diagnostic(decoded[:,:3])}
                cases.append(case)
    dump('ordered_control_cases.json',cases)
    exact=[];best={}
    for name in ['adjacent_cells','adjacent_blocks','lag2_blocks']:
        scores=[row['complement_diagnostic'][name] for row in cases]
        index=max(range(len(cases)),key=lambda i:scores[i]['passed']/scores[i]['total'])
        best[name]={'case_id':index,**scores[index]}
        exact.extend({'case_id':i,'relation':name} for i,s in enumerate(scores) if s['passed']==s['total'])
    files=['research/models/ordered_decode_v1.json','research/data/pixel_measurements.json',
           'research/data/timing_lattice_check.json','research/data/signature_phase_decode_check.json',
           'research/data/historical_level2_control.json','tools/ordered_decode_common.py','tools/check_ordered_controls.py','tools/residual_channels.py']
    out={'model':'C28','input_sha256':hashes(files),'historical_calibration':control,'cases':len(cases),
         'control_cases':sum(c['recipe']['kind']=='identity' for c in cases),'states_recovered_in_every_case':256,
         'exact_neighbor_relations':exact,'best_neighbor_diagnostics_no_significance_claim':best,
         'full_original_input_preserved':True,'marker_bits':mask.tolist(),'limitations':settings['limitations']}
    dump('ordered_control_check.json',out);print(json.dumps(out,indent=2))

if __name__=='__main__':main()
