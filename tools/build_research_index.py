#!/usr/bin/env python3
"""Index saved evidence so future sessions can retrieve and verify prior work."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    files=[]
    for directory,role in [('research/data','executed_result_or_artifact'),
                           ('research/sources','source_or_reference'),
                           ('research/models','model_specification'),
                           ('tools','reproduction_tool')]:
        for path in sorted((ROOT/directory).glob('*')):
            if path.is_file():
                files.append({'path':str(path.relative_to(ROOT)),'role':role,
                              'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    for name in ['README.md','AGENTS.md','research/HYPOTHESES.md','research/LOG.md']:
        p=ROOT/name
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
    out={'purpose':'Persistent evidence index; read together with HYPOTHESES.md and LOG.md.',
         'counting_rule':'Do not sum per-run unique candidates as global uniques; overlap across runs has not been measured. Structural comparisons, WIF strings, hypotheses and private scalars are separate units.',
         'result_summaries':summaries,'structural_summaries':structural,'files':files}
    (ROOT/'research/RUN_INDEX.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Indexed',len(files),'saved evidence files.')

if __name__=='__main__':main()
