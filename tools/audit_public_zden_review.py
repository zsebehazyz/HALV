#!/usr/bin/env python3
"""Audit collected public-source bytes and historical Bitcoin key claims.

This verifies archived claims, not unseen forum coverage or HALV solution.
"""
import hashlib
import json
import re
from pathlib import Path
from bitcoin_oracle import addresses, b58decode, sha256, selftest

ROOT=Path(__file__).resolve().parents[1]
MANIFEST='research/sources/public_web_review_20261101.json'


def main():
    records=json.loads((ROOT/MANIFEST).read_text())
    ids=[r['id'] for r in records];assert len(set(ids))==len(ids)
    verified=[]
    for record in records:
        if 'path' not in record:continue
        path=(ROOT/record['path']).resolve();assert path.is_relative_to(ROOT)
        data=path.read_bytes()
        assert len(data)==record['bytes']
        assert hashlib.sha256(data).hexdigest()==record['sha256'],record['id']
        verified.append(record['id'])
    selftest();keys=[]
    for name in ['level-1','level-2','level-3','level-5','1bitcoin-white-paper']:
        source=(ROOT/('research/sources/webreview_catalog_'+name+'.txt')).read_text()
        expected=re.search(r'address:\s*"([^"]+)"',source)[1]
        match=re.search(r'key:\s*hex\("([0-9a-f]+)"\)',source)
        assert match,name
        key=bytes.fromhex(match[1]);actual=addresses(key)
        assert expected==actual['uncompressed'],name
        wif=re.search(r'\.wif\(\s*"([1-9A-HJ-NP-Za-km-z]+)"',source)
        if wif:
            raw=b58decode(wif[1]);assert raw[0]==128 and raw[1:-4]==key
            assert sha256(sha256(raw[:-4]))[:4]==raw[-4:]
        keys.append({'level':name,'uncompressed_address':expected,'published_key_derives_address':True,
                     'WIF_checked':bool(wif),'scope':'published vector check, not artwork decoding'})
    # Human transcription of the printed32byte line on the inspected Level3 solver diagram.
    diagram_hex='6008c37d0aa226dbbe611be64106964bca6cbba7098fe4602a932c590e14b074'
    assert addresses(bytes.fromhex(diagram_hex))['uncompressed']==keys[2]['uncompressed_address']
    out={'review':'R26-public-source-review','network_requests_recorded':len(records),
         'saved_source_files_hash_verified':len(verified),
         'successes':sum(r.get('status')==200 for r in records),
         'failed_or_blocked':sum('error' in r for r in records),
         'commit_pinned_exact_response_matches':sum(r.get('pinned_bytes_match',False) for r in records),
         'catalog_digest_matching_solver_images':sum(r.get('matches_catalog_digest',False) for r in records),
         'historical_vectors':keys,'level3_printed_diagram_vector_verified':True,
         'coverage_limit':'Public GitHub only; author site, search engines and forums blocked by current egress policy. No private group access.',
         'not_a_HALV_solution':True,
         'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [MANIFEST,'tools/audit_public_zden_review.py','tools/bitcoin_oracle.py']}}
    (ROOT/'research/data/public_zden_review_integrity.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
