#!/usr/bin/env python3
"""Generate independent reference vectors using reedsolo==1.7.0, not puzzle data."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--reference-path',type=Path);args=ap.parse_args()
    if args.reference_path:sys.path.insert(0,str(args.reference_path))
    import reedsolo
    version=importlib.metadata.version('reedsolo');assert version=='1.7.0'
    vectors=[]
    for prim,generator in [(0x11d,2),(0x11b,3)]:
        for fcr in [0,1]:
            codec=reedsolo.RSCodec(12,prim=prim,generator=generator,fcr=fcr)
            for raw in [bytes(range(32)),bytes((7*i+11)%256 for i in range(32))]:
                encoded=bytes(codec.encode(raw));assert encoded[:32]==raw and len(encoded)==44
                vectors.append({'field_polynomial':prim,'generator':generator,'first_root':fcr,
                                'data_hex':raw.hex(),'parity_hex':encoded[-12:].hex()})
    root=Path(__file__).resolve().parents[1]
    out={'reference_package':'reedsolo','version':version,'package_source':'https://pypi.org/project/reedsolo/1.7.0/',
         'module_sha256':hashlib.sha256(Path(reedsolo.__file__).read_bytes()).hexdigest(),
         'generation_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'vectors':vectors,
         'purpose':'Independent implementation known answers; messages are fixed synthetic data, not HALV'}
    (root/'research/sources/rs_reference_vectors.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Saved',len(vectors),'independent RS reference vectors.')

if __name__=='__main__':main()
