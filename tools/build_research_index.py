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
        ('marker_glyph_relation.json','attempts_including_duplicates','structural comparisons, not private keys')]:
        p=ROOT/'research/data'/filename
        if p.exists():
            data=json.loads(p.read_text())
            match_count=data['target_matches'] if 'target_matches' in data else len(data.get('matches',data.get('exact_relations',[])))
            summary={'result':str(p.relative_to(ROOT)),'count_field':field,'count':data[field],'unit':unit}
            if 'expected_address_match' in data:summary['historical_control_address_match']=data['expected_address_match']
            else:summary['target_or_exact_matches']=match_count
            summaries.append(summary)
    out={'purpose':'Persistent evidence index; read together with HYPOTHESES.md and LOG.md.',
         'counting_rule':'Do not sum per-run unique candidates as global uniques; overlap across runs has not been measured. Structural comparisons, WIF strings, hypotheses and private scalars are separate units.',
         'result_summaries':summaries,'files':files}
    (ROOT/'research/RUN_INDEX.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Indexed',len(files),'saved evidence files.')

if __name__=='__main__':main()
