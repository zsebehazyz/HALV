#!/usr/bin/env python3
"""R28 source/known-key verification; not a Codex artwork decoder or HALV search."""
import hashlib,json,re
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from Crypto.Hash import keccak
ROOT=Path(__file__).resolve().parents[1]


def keccak256(data):
    h=keccak.new(digest_bits=256);h.update(data);return h.digest()


def main():
    # Distinguish EthereumKeccak from the incompatible NISTSHA3 padding.
    assert keccak256(b'').hex()=='c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'
    catalog=(ROOT/'research/sources/webreview_catalog_codex-protocol.txt').read_text()
    secret=re.search(r'key: hex\("([a-f0-9]{64})"',catalog)[1]
    expected_address=re.search(r'address: "([^"]+)"',catalog)[1]
    expected_public=re.search(r'pubkey: uncompressed\(\s*"([a-f0-9]+)"',catalog)[1]
    public=ec.derive_private_key(int(secret,16),ec.SECP256K1()).public_key().public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint)
    assert public.hex()==expected_public
    address='0x'+keccak256(public[1:])[-20:].hex();assert address==expected_address
    access=json.loads((ROOT/'research/sources/codex_author_review_access.json').read_text())
    images=[]
    for row in access:
        if 'path' not in row:continue
        data=(ROOT/row['path']).read_bytes();digest=hashlib.sha256(data).hexdigest()
        assert digest==row['sha256'] and len(data)==row['bytes']
        assert digest in catalog and str(len(data)) in catalog
        images.append({'path':row['path'],'sha256':digest,'bytes':len(data),'catalog_matches':True})
    # Conditional mathematical fact only: not evidence of author edge numbering.
    pair=(0,1);residues=[]
    while True:
        residues.append(pair[0]);pair=(pair[1],sum(pair)%5)
        if pair==(0,1):break
        assert len(residues)<100
    assert len(residues)==20
    a,b=0,1
    for i in range(256):
        assert a%5==residues[i%20];a,b=b,a+b
    bitstring=''.join(f'{v:08b}' for v in bytes.fromhex(secret))
    diagnostics=[]
    for period in [20,40]:
        bad=[i for i in range(period,256) if bitstring[i]!=bitstring[i%period]]
        diagnostics.append({'candidate_bit_period':period,'first_mismatch_zero_based':bad[0] if bad else None,'mismatch_count':len(bad)})
    names=['research/sources/codex_author_review_access.json','research/sources/codex_author_review_search.json','research/sources/webreview_catalog_codex-protocol.txt','research/sources/webreview_codex_solution_note.txt','tools/verify_codex_author_evidence.py']
    out={'review':'R28','published_key_hex':secret,'public_key_matches_catalog':True,'derived_ethereum_address':address,'ethereum_address_matches_catalog':True,
         'known_key_check_not_artwork_decoder':True,'images':images,
         'author_article_available':any(r['id']=='article' and r.get('status')==200 for r in access),
         'exact_author_four_step_algorithm_verified':False,
         'conditional_fibonacci_mod5':{'seed_convention':[0,1],'residues':residues,'state_period':20,'checked_exact_big_integer_residues':256,'not_an_author_algorithm_claim':True},
         'published_key_period_diagnostic':diagnostics,
         'no_new_HALV_Fibonacci_search':True,
         'unverified_details':['actual graph and local edge ordering','initial vertex and directed edge','Fibonacci seeds and phase','absolute or relative edge index including return edge','move/read-bit order and edge-to-bit property','state updates and reset policy','output bit order'],
         'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in names}}
    (ROOT/'research/data/codex_author_evidence_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['images','input_sha256','published_key_hex']},indent=2))

if __name__=='__main__':main()
