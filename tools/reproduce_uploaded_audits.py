#!/usr/bin/env python3
"""C24: run only the four manually reviewed uploaded scripts in isolated scratch."""
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import numpy as np
from residual_channels import ROOT,nominal_states

def main():
    spec_path=ROOT/'research/models/upload_audit_v1.json';spec=json.loads(spec_path.read_text())
    q=nominal_states().flatten();results={};comparisons={}
    outputs={
      'HALV_kulso_belso_dimenzio_ellenorzes_20261101.py':('HALV_kulso_belso_dimenzio_20261101.json','reproduced_upload_dimensions.json'),
      'HALV_352bit_WIF7_audit_20261101.py':('HALV_352bit_WIF7_audit_20261101.json','reproduced_upload_wif7.json'),
      'HALV_TXID_harom_kimenet_celzott_audit_20261101.py':('HALV_TXID_harom_kimenet_celzott_audit_20261101.json','reproduced_upload_txid_outputs.json'),
      'HALV_TXID_128_szimbólum_egyezes_kontroll_20261101.py':('HALV_TXID_128_szimbólum_egyezes_kontroll_20261101.json','reproduced_upload_txid_control.json')}
    with tempfile.TemporaryDirectory(prefix='halv_reviewed_uploads_',dir='/tmp') as tmp:
        scratch=Path(tmp);shutil.copyfile(ROOT/'research/sources/cryptoHALV.png',scratch/'cryptoHALV (1).png')
        with (scratch/'HALV_256_minta_20261031.csv').open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['round_q']);w.writerows([[int(v)] for v in q])
        csv_sha=hashlib.sha256((scratch/'HALV_256_minta_20261031.csv').read_bytes()).hexdigest()
        for script in spec['reviewed_execution_allowlist']:
            source=ROOT/'research/sources'/('upload_'+script);shutil.copyfile(source,scratch/script)
            print('Running reviewed upload:',script,flush=True)
            run=subprocess.run([sys.executable,str(scratch/script)],cwd=scratch,capture_output=True,text=True,timeout=600)
            if run.returncode:raise RuntimeError(f'{script}: {run.stderr}')
            report_name,saved_name=outputs[script];produced=json.loads((scratch/report_name).read_text())
            (ROOT/'research/data'/saved_name).write_text(json.dumps(produced,indent=2,ensure_ascii=False)+'\n')
            original=ROOT/'research/sources'/('upload_'+report_name)
            if original.exists():
                claimed=json.loads(original.read_text());keys=sorted(set(claimed)|set(produced));differences={}
                for key in keys:
                    if key=='elapsed_seconds':continue
                    if claimed.get(key)!=produced.get(key):differences[key]={'claimed':claimed.get(key),'reproduced':produced.get(key)}
                comparisons[script]={'all_declared_fields_match_except_runtime':not differences,'differences':differences}
            else:
                observed=[r['observed_phase_affine_dimension'] for r in produced['blocks']]
                best=[r['best_affine_dimension_across_offsets'] for r in produced['blocks']]
                comparisons[script]={'reported_default_dimensions_match':observed==[6,6,4,4,3,4,3,5],
                    'reported_minimum_dimensions_match':best==[5,5,4,4,3,4,3,5]}
            results[script]={'saved_result':'research/data/'+saved_name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                             'stdout':run.stdout,'returncode':run.returncode}
            print('Saved',saved_name,'comparison:',comparisons[script],flush=True)
    blocks=q.reshape(8,32);h=blocks>>1;l=blocks&1;shifted=np.roll(l.reshape(8,8,4),1,axis=2).reshape(8,32)
    phase_scores=[]
    for b in range(8):
        cells=blocks[b].reshape(8,4);hh=cells>>1;ll=cells&1
        phase_scores.append([int(hh[:,p].sum()+sum(ll[:,j].sum() for j in range(4) if j!=(p-1)%4)) for p in range(4)])
    weights=2**np.arange(7,-1,-1);hv=weights@h;lv=weights@l;s=2*hv+lv
    decoded=''.join(f'{int("".join(map(str,row)),2):x}' for row in (h^shifted).reshape(64,4))
    files=['research/data/pixel_measurements.json','research/sources/cryptoHALV.png','research/models/upload_audit_v1.json',
           'research/sources/upload_batch_20261101_manifest.json','tools/reproduce_uploaded_audits.py','tools/residual_channels.py']
    out={'model':'C24','input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
         'generated_csv_sha256':csv_sha,'canonical_states_sha256':hashlib.sha256(q.astype(np.uint8).tobytes()).hexdigest(),
         'comparisons':comparisons,'executions':results,'hamming_phase_scores':phase_scores,
         'cellwise_H_xor_rotated_L_hex':decoded,'collision_count_per_block':(h&shifted).sum(1).tolist(),
         'weighted_H_hex':bytes(int(v) for v in hv).hex(),'weighted_L_hex':bytes(int(v) for v in lv).hex(),
         'weighted_sum_overflow_columns':np.flatnonzero(s>255).tolist(),'weighted_sum_overflow_count':int(sum(s>255)),
         'funding_data_status':'User-provided transcript; no independent raw transaction validation in this offline audit',
         'fixed_uploaded_CORE20_hex':'fdcbb96843ad8c6463dcc298b5672995448146f1','limitations':spec['limitations']}
    (ROOT/'research/data/upload_audit_check.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print('Finished C24; phase scores:',phase_scores,flush=True)

if __name__=='__main__':main()
