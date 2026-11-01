#!/usr/bin/env python3
"""Index saved evidence so future sessions can retrieve and verify prior work."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    if (ROOT/'research/MASTER_OVERVIEW.md').exists():
        from build_master_document import main as build_master_document
        build_master_document()
    files=[]
    for directory,role in [('research/data','executed_result_or_artifact'),
                           ('research/sources','source_or_reference'),
                           ('research/models','model_specification'),
                           ('tools','reproduction_tool')]:
        for path in sorted((ROOT/directory).glob('*')):
            if path.is_file():
                files.append({'path':str(path.relative_to(ROOT)),'role':role,
                              'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    for name in ['README.md','AGENTS.md','research/HYPOTHESES.md','research/LOG.md',
                 'research/MASTER_OVERVIEW.md','research/HALV_TELJES_KUTATAS.md']:
        p=ROOT/name
        if not p.exists():continue
        files.append({'path':name,'role':'research_map_or_log','bytes':p.stat().st_size,
                      'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    for p in sorted((ROOT/'research').glob('REPORT_*.md')):
        files.append({'path':str(p.relative_to(ROOT)),'role':'research_report','bytes':p.stat().st_size,
                      'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    summaries=[]
    for filename,field,unit in [
        ('level5_geometry_verification.json','geometry_reference_matches','historical Level5 geometry matches; positive control, not HALV'),
        ('candidate_check.json','valid_scalars_checked','valid private scalars'),
        ('five_sample_wif_check.json','target_matches','target matches; hypotheses are in families'),
        ('corner_check.json','unique_corner_candidates','valid private scalars'),
        ('composite_model_check.json','global_unique_valid_scalars','valid private scalars'),
        ('bd_halving_check.json','unique_valid_scalars','valid private scalars'),
        ('halving_pairs_check.json','unique_valid_scalars','valid private scalars'),
        ('pair64_check.json','unique_valid_scalars','valid private scalars'),
        ('bd_pair64_check.json','unique_valid_scalars','valid private scalars'),
        ('phase_decode_check.json','unique_valid_scalars','valid private scalars'),
        ('fractional_area_check.json','unique_valid_scalars','valid private scalars'),
        ('signature_phase_decode_check.json','unique_valid_scalars','valid private scalars'),
        ('uniform_phase_layers_check.json','unique_valid_scalars','valid private scalars'),
        ('residual_predictors_check.json','unique_valid_scalars','valid private scalars; includes the96 C20 controls'),
        ('ordered_format_check.json','unique_valid_scalars','valid private scalars in C28-C30 only; both public key formats'),
        ('marker_glyph_relation.json','attempts_including_duplicates','structural comparisons, not private keys')]:
        p=ROOT/'research/data'/filename
        if p.exists():
            data=json.loads(p.read_text())
            match_count=data['target_matches'] if 'target_matches' in data else len(data.get('matches',data.get('exact_relations',[])))
            summary={'result':str(p.relative_to(ROOT)),'count_field':field,'count':data[field],'unit':unit}
            if 'expected_address_match' in data:summary['historical_control_address_match']=data['expected_address_match']
            else:summary['target_or_exact_matches']=match_count
            summaries.append(summary)
    structural=[]
    p=ROOT/'research/data/upload_audit_check.json'
    if p.exists():
        d=json.loads(p.read_text());comparison=d['comparisons']
        matches=all(v.get('all_declared_fields_match_except_runtime',
                    v.get('reported_default_dimensions_match',False) and v.get('reported_minimum_dimensions_match',False))
                    for v in comparison.values())
        structural.append({'result':str(p.relative_to(ROOT)),'kind':'reviewed_upload_reproduction',
                           'reviewed_programs':len(d['executions']),'declared_comparisons_match':matches,
                           'not_new_private_key_search':True})
    p=ROOT/'research/data/lag2_halving_check.json'
    if p.exists():
        d=json.loads(p.read_text());middle=d['forecast_models'][2]
        structural.append({'result':str(p.relative_to(ROOT)),'kind':'posthoc_forecast_reconstruction',
                           'window_scores':d['window_scores'],'forecast_matches_out_of32':middle['forecast_matches_out_of32'],
                           'low_bit_errors':middle['low_bit_errors'],'high_bit_errors':middle['high_bit_errors'],
                           'not_global_discovery_probability':True})
    p=ROOT/'research/data/lag2_residual_bridge_check.json'
    if p.exists():
        d=json.loads(p.read_text());structural.append({'result':str(p.relative_to(ROOT)),
            'kind':'residual_transition_relationship','coordinate_configurations':d['coordinate_configurations'],
            'exact_training_fit_counts':d['exact_training_fit_counts'],'heldout_successes':len(d['full_heldout_successes']),
            'not_private_key_search':True})
    p=ROOT/'research/data/historical_level2_control.json'
    if p.exists():
        d=json.loads(p.read_text());structural.append({'result':str(p.relative_to(ROOT)),
            'kind':'historical_positive_control','puzzle':'Zden Level2',
            'neighbor_constraints_passed':d['neighbor_constraints_passed'],
            'neighbor_constraints_total':d['neighbor_constraints_total'],
            'valid_wif_readings':sum(v['validation']=='valid' for v in d['candidate_readings']),
            'historical_target_match':d['historical_target_match'],'not_HALV_key_search':True})
    p=ROOT/'research/data/ordered_control_check.json'
    if p.exists():
        d=json.loads(p.read_text());structural.append({'result':str(p.relative_to(ROOT)),
            'kind':'invertible_control_family','cases':d['cases'],
            'states_recovered_in_every_case':d['states_recovered_in_every_case'],
            'exact_neighbor_relations':len(d['exact_neighbor_relations']),
            'roundtrip_is_not_decoder_evidence':True})
    p=ROOT/'research/data/ordered_arithmetic_check.json'
    if p.exists():
        d=json.loads(p.read_text());structural.append({'result':str(p.relative_to(ROOT)),
            'kind':'coupled_arithmetic_and_geometry','recipes_including_duplicates':d['attempts_including_duplicates'],
            'unique_payloads32':d['unique_formed_payloads32'],'groups':d['groups'],
            'payloads_are_not_independent_key_tests':True})
    p=ROOT/'research/data/stateful_bridge_check.json'
    if p.exists():
        d=json.loads(p.read_text());structural.append({'result':str(p.relative_to(ROOT)),
            'kind':'causal_residual_transition_bridge','configuration_counts':d['counts'],
            'C31_exact_training_fits':len(d['C31_exact_training_fits']),
            'C32_exact_training_fits':len(d['C32_exact_training_fits']),
            'C33_exact_training_fits':len(d['C33_exact_training_fits']),
            'not_private_key_search':True})
    p=ROOT/'research/data/nonlinear_context_check.json'
    if p.exists():
        d=json.loads(p.read_text());structural.append({'result':str(p.relative_to(ROOT)),
            'kind':'nonlinear_causal_context_coverage','configuration_counts':d['counts'],
            'full_heldout_successes':len(d['strong_successes']),
            'max_known_heldout_cells':max(v['known_cells'] for v in d['heldout_coverage_histogram']),
            'max_correct_heldout_cells':max(v['correct_cells'] for v in d['heldout_coverage_histogram']),
            'not_private_key_search':True})
    p=ROOT/'research/data/halving_invariants_check.json'
    if p.exists():
        d=json.loads(p.read_text());structural.append({'result':str(p.relative_to(ROOT)),
            'kind':'exact_dyadic_and_permutation_invariants','quantizer_identity_checks':d['exact_quantizer_identity_checks'],
            'all8_histograms_distinct':d['all8_histograms_distinct'],
            'all_block_pair_bounds':len(d['all_block_pair_bounds']),'not_private_key_search':True})
    p=ROOT/'research/data/phase_ascii_generator_check.json'
    if p.exists():
        d=json.loads(p.read_text());structural.append({'result':str(p.relative_to(ROOT)),
            'kind':'full512bit_phase_ASCII_flag_gate','format_trials':d['all_trials'],
            'complete_hex_readings':len(d['complete_hex_readings']),'scalars_passing_format_gate':d['unique_valid_scalars'],
            'target_matches':len(d['matches']),'full512bit_flag_roundtrips':d['full512bit_flag_roundtrips']})
    out={'purpose':'Persistent evidence index; read together with HYPOTHESES.md and LOG.md.',
         'counting_rule':'Do not sum per-run unique candidates as global uniques; overlap across runs has not been measured. Structural comparisons, WIF strings, hypotheses and private scalars are separate units.',
         'result_summaries':summaries,'structural_summaries':structural,'files':files}
    (ROOT/'research/RUN_INDEX.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Indexed',len(files),'saved evidence files.')

if __name__=='__main__':main()
