#!/usr/bin/env python3
"""C19: exact audit of the proposed Bitcoin-reward staircase calibration."""
import hashlib
import json
import math
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    spec=json.loads((ROOT/'research/models/reward_staircase_v1.json').read_text())
    phase=json.loads((ROOT/'research/data/signature_phase_decode_check.json').read_text())
    heights=list(map(F,phase['heights_exact']));rewards=[F(50,2**i) for i in range(5)]
    residuals=[h-r for h,r in zip(heights,rewards)];mse=sum(v*v for v in residuals)/5
    assert mse==F(17,64)
    # For positive rational values, using the floor before integer bit_length gives floor(log2).
    logs=[(r.numerator//r.denominator).bit_length()-1 for r in rewards]
    assert logs==phase['floor_log2']
    scales=[F(128,2**b) for b in range(8)];factors=[r/s for r,s in zip(rewards,scales[2:7])]
    assert len(set(factors))==1 and factors[0]==F(25,16)
    profiles=json.loads((ROOT/'research/data/fractional_area_profiles.json').read_text());ranges=[]
    for profile in profiles:
        if profile['domain']!='physical_nodes':continue
        values=list(map(F,profile['values64_exact']))
        for factor in [F(25,16),F(16,25)]:
            maximum=max(values)*factor
            # Every pairing uses every nonnegative area once; a single area>=256
            # forces an overflow even with the smallest (floor) declared rounder.
            assert maximum.numerator//maximum.denominator>=256
            ranges.append({'profile':profile['label'],'factor':str(factor),'maximum_cell_exact':str(maximum),
                           'floor_maximum':maximum.numerator//maximum.denominator,
                           'direct_pair_byte_overflow_unavoidable':True})
    files=['research/data/signature_phase_decode_check.json','research/data/fractional_area_profiles.json',
           'research/models/reward_staircase_v1.json','tools/check_reward_staircase.py']
    out={'model':'C19','input_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
         'measured_heights_exact':[str(v) for v in heights],'reward_series_exact':[str(v) for v in rewards],
         'height_minus_reward_exact':[str(v) for v in residuals],'mean_squared_error_exact':str(mse),
         'rmse_pixels':math.sqrt(float(mse)),'max_abs_residual_pixels':float(max(map(abs,residuals))),
         'ideal_reward_floor_logs':logs,'ideal_reward_zero_phases':[e%4 for e in logs],
         'same_as_measured_signature_phase':True,'reward_to_middle_wave_scale_factor_exact':str(factors[0]),
         'scaled_all8_amplitude_values_exact':[str(s*factors[0]) for s in scales],
         'all8_extension_is_not_all_historical_rewards':True,
         'physical_area_range_only_checks':ranges,
         'interpretation':'Reward theme and phase identity coexist; the common scale does not yet normalize areas into bytes',
         'no_private_key_search':True,'limitations':spec['limitations']}
    (ROOT/'research/data/reward_staircase_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['input_sha256','physical_area_range_only_checks']},indent=2))

if __name__=='__main__':main()
