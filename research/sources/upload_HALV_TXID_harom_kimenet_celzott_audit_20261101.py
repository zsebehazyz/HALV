#!/usr/bin/env python3
"""Reproducible, bounded exploratory audit of HALV financing TXID, output values,
Bitcoin output HASH160 fields and original 256 2-bit waveform samples.
Not evidence of a hidden derivation scheme unless a precise address match occurs.
Uses user-supplied funding transaction details; does not fetch on-chain data.
"""
from pathlib import Path
from collections import Counter
import csv, itertools, json, hashlib, time
import numpy as np
from PIL import Image
from cryptography.hazmat.primitives.asymmetric import ec

D=Path(__file__).resolve().parent
PNG=D/'cryptoHALV (1).png'
assert hashlib.sha256(PNG.read_bytes()).hexdigest()=='3a487ebaeb4801137f09159a2d533046936cd395f4e2f7d115ac554607790e95'
TXID='30946152b5f24ed975a26b28a46cb19d1ef2728159c5806544ffd0c2fb535205'
TX=bytes.fromhex(TXID)
B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
N=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
sha=lambda b:hashlib.sha256(b).digest()
h160=lambda b:hashlib.new('ripemd160',sha(b)).digest()
def decode(a):
    i=0
    for c in a:i=i*58+B58.index(c)
    b=i.to_bytes((i.bit_length()+7)//8,'big')
    b=b'\0'*(len(a)-len(a.lstrip('1')))+b
    assert len(b)==25 and sha(sha(b[:-4]))[:4]==b[-4:],a
    return b[0], b[1:21]
ADDR={
 'HALV_main':'1crypto24HCr178iMcKd5iUi5D4rsg1nK',
 'DotPuz_4040':'1DoTPuzbAuLZHU4TodFrnMvZXBxAoBBcNv',
 'P2SH_change':'391fj9nysMwBVN6mp2MTz6CTnqPSwdS5Fx',
 'funding_input':'3DsjYuh1UDZFB1M3HMmPfuTNyQpATRRXDD',
}
A={k:decode(v) for k,v in ADDR.items()}
assert A['HALV_main'][0]==A['DotPuz_4040'][0]==0
assert A['P2SH_change'][0]==5
Q=np.array([int(r['round_q']) for r in csv.DictReader((D/'HALV_256_minta_20261031.csv').open())],dtype=np.uint8).reshape(8,32)
assert Q.shape==(8,32) and Q.max()<=3
CORE=bytes.fromhex('FDCBB96843AD8C6463DCC298B5672995448146F1')
assert len(CORE)==20
im=np.asarray(Image.open(PNG).convert('L'))
mark=im[443:507,91]

def bits_byte(bb):
    assert len(bb)==256
    return bytes(int(''.join(map(str,bb[i:i+8])),2) for i in range(0,256,8))
def arrays(q):
    h=((q>>1)&1).astype(int);l=(q&1).astype(int)
    out={
      'H_8x32_vertical':bits_byte(h.T.flatten()),
      'L_8x32_vertical':bits_byte(l.T.flatten()),
      'H_12px_horizontal':bits_byte(h.flatten()),
      'L_12px_horizontal':bits_byte(l.flatten()),
      'full_two_bits_sha':sha(bytes([int(x) for x in q.flatten()])),
    }
    out['H_xor_L_vertical']=bytes(a^b for a,b in zip(out['H_8x32_vertical'],out['L_8x32_vertical']))
    out['H_plus_L_vertical']=bytes((a+b)&255 for a,b in zip(out['H_8x32_vertical'],out['L_8x32_vertical']))
    out['2H_plus_L_vertical']=bytes((2*a+b)&255 for a,b in zip(out['H_8x32_vertical'],out['L_8x32_vertical']))
    out['H_xor_L_horizontal']=bytes(a^b for a,b in zip(out['H_12px_horizontal'],out['L_12px_horizontal']))
    return out
wave=arrays(Q)
qn=Q.copy()
for b in range(8):
    phase=(3-b)%4
    qn[b]=np.roll(qn[b].reshape(8,4),-phase,axis=1).reshape(32)
wave.update({'normalized_'+k:v for k,v in arrays(qn).items()})
# Explicit 160+64+32 partition explored before, this time combining it with TXID.
for threshold in (1,128,177,216,217):
    arr=(mark>=threshold).astype(int)
    marker=bytes(int(''.join(map(str,arr[8*j:8*j+8])),2) for j in range(8))
    wave['core_marker_date_'+str(threshold)]=CORE+marker+bytes.fromhex('20042402')
# 160 bits from core plus deterministic 96 from exterior blocks, using selected bitplanes
outer=Q[[0,1,7]].flatten()
for plane in ('high','low'):
    one=((outer>>1)&1) if plane=='high' else (outer&1)
    out=bytes(int(''.join(map(str,one[8*j:8*j+8])),2) for j in range(12))
    wave['core_outer_'+plane]=CORE+out

amounts={'mini':4040,'prize':312500,'change':2240049,'fee':8484,'input':2565073}
assert amounts['mini']+amounts['prize']+amounts['change']+amounts['fee']==amounts['input']
# Seeds are readily motivated by the visible TXID or transaction fields; do not claim that
# many variants are proof of systematic completeness.
seeds={
 'txid_as_scalar':TX,
 'txid_reverse':TX[::-1],
 'sha256_txid_binary':sha(TX),
 'sha256_reverse_txid':sha(TX[::-1]),
 'sha256_sha256_txid_binary':sha(sha(TX)),
 'sha256_txid_text':sha(TXID.encode()),
 'sha256_txid_ascii_reverse':sha(TXID[::-1].encode()),
 'sha256_image_png':sha(PNG.read_bytes()),
 'sha256_image_plus_txid':sha(PNG.read_bytes()+TX),
 'sha256_txid_plus_image':sha(TX+PNG.read_bytes()),
 'sha256_core':sha(CORE),
 'sha256_txid_plus_core':sha(TX+CORE),
 'sha256_core_plus_txid':sha(CORE+TX),
 'sha256_date_plus_txid':sha(b'20042402'+TX),
 'sha256_txid_plus_date':sha(TX+b'20042402'),
 'sha256_name_DoTPuz_plus_txid':sha(b'DoTPuz'+TX),
}
for name,v in wave.items():
    if len(v)==32:
        seeds['wave_'+name]=v
        seeds['sha256_wave_'+name]=sha(v)
    else:seeds['sha256_wave_'+name]=sha(v)

# Address payloads are 20 bytes, and cannot be standalone 256-bit scalar. Use explicitly
# defined 32-byte composites or hashes, never silently pad as a purported decryption.
for label,(ver,payload) in A.items():
    seeds['sha256_address_payload_'+label]=sha(bytes([ver])+payload)
    seeds['sha256_address_text_'+label]=sha(ADDR[label].encode())
    seeds['sha256_txid_address_payload_'+label]=sha(TX+bytes([ver])+payload)
    seeds['sha256_address_payload_txid_'+label]=sha(bytes([ver])+payload+TX)
    seeds['txid_prefix12_address_payload_'+label]=TX[:12]+payload
    seeds['address_payload_txid_suffix12_'+label]=payload+TX[-12:]
for name,v in amounts.items():
    for width in (4,8):
        for endian in ('little','big'):
            salt=v.to_bytes(width,endian)
            seeds[f'sha256_txid_{name}_{width}_{endian}']=sha(TX+salt)
            seeds[f'sha256_{name}_{width}_{endian}_txid']=sha(salt+TX)
            seeds[f'sha256_core_{name}_{width}_{endian}_txid']=sha(CORE+salt+TX)
            seeds[f'sha256_txid_{name}_{width}_{endian}_core']=sha(TX+salt+CORE)
    seeds[f'sha256_txid_{name}_ascii']=sha(TX+str(v).encode())
    seeds[f'sha256_{name}_ascii_txid']=sha(str(v).encode()+TX)
for endian in ('little','big'):
    values=b''.join(amounts[k].to_bytes(8,endian) for k in ['mini','prize','change'])
    seeds[f'sha256_3outputs_{endian}']=sha(values)
    seeds[f'sha256_txid_3outputs_{endian}']=sha(TX+values)
    seeds[f'sha256_3outputs_txid_{endian}']=sha(values+TX)
    seeds[f'sha256_core_3outputs_{endian}']=sha(CORE+values)
    for name,w in wave.items():
        seeds[f'sha256_wave_{name}_3outputs_{endian}']=sha(w+values)

# Only add outputs for exact, reproducible candidate formulae.
allcand={}
def add(label,v):
    if len(v)==32:
        allcand.setdefault(v,[]).append(label)
for name,v in seeds.items():
    add(name,v)
    add(name+'|reversebytes',v[::-1])
    add(name+'|shasingle',sha(v))
    add(name+'|sha-double',sha(sha(v)))
    add(name+'|half32_rotate',v[16:]+v[:16])

# Compound masked candidate stream: TXID is a 256-bit salt; PNG-derived 32-byte strings
# are potential ciphertexts. Natural reversible operations are XOR / +/- with mod N.
for name,w in wave.items():
    if len(w)!=32:continue
    for txlabel, t in [('txid_raw',TX),('txid_reverse',TX[::-1]),('txid_sha',sha(TX)),('txid_double_sha',sha(sha(TX)))]:
        for wlab, ww in [('direct',w),('reverse',w[::-1])]:
            lhs=int.from_bytes(ww,'big');rhs=int.from_bytes(t,'big')
            prefix=f'{name}|{wlab}|{txlabel}'
            add(prefix+'|xor',bytes(a^b for a,b in zip(ww,t)))
            add(prefix+'|plus_mod_curve',((lhs+rhs)%N).to_bytes(32,'big'))
            add(prefix+'|minus_mod_curve',((lhs-rhs)%N).to_bytes(32,'big'))
            add(prefix+'|reversed_minus_mod_curve',((rhs-lhs)%N).to_bytes(32,'big'))
            add(prefix+'|sha_concat',sha(ww+t))
            add(prefix+'|sha_reverse_concat',sha(t+ww))

# Direct cryptographic hashes of distinct ordered output addresses and binary amounts.
for ordering in itertools.permutations(['DotPuz_4040','HALV_main','P2SH_change']):
    for encode in ('payload','base58text','value_and_payload'):
        inp=b''
        for label in ordering:
            if encode=='payload': inp+=bytes([A[label][0]])+A[label][1]
            elif encode=='base58text':inp+=ADDR[label].encode()+b'|'
            else:
                k={'DotPuz_4040':'mini','HALV_main':'prize','P2SH_change':'change'}[label]
                inp+=amounts[k].to_bytes(8,'little')+bytes([A[label][0]])+A[label][1]
        add('sha256_outputs_'+encode+'_'.join(ordering),sha(inp))
        add('sha256_txid_outputs_'+encode+'_'.join(ordering),sha(TX+inp))


def check_scalar(k):
    val=int.from_bytes(k,'big')
    if not 0<val<N:return None
    p=ec.derive_private_key(val,ec.SECP256K1()).public_key().public_numbers()
    x=p.x.to_bytes(32,'big'); y=p.y.to_bytes(32,'big')
    scripts=[]
    for kind, pub in [('compressed',bytes([2+(p.y&1)])+x),('uncompressed',b'\x04'+x+y)]:
        ph=h160(pub)
        for name in ('HALV_main','DotPuz_4040'):
            if ph==A[name][1]:return {'target':name,'method':kind}
        # These are a subset of possible P2SH scripts. Arbitrary scripts cannot be
        # reconstructed from a private key or a P2SH HASH160 alone.
        forms={
          'P2SH_P2WPKH':b'\x00\x14'+ph,
          'P2SH_P2PK':bytes([len(pub)])+pub+b'\xac',
          'P2SH_P2PKH':b'\x76\xa9\x14'+ph+b'\x88\xac',
          'P2SH_1of1_multisig':b'\x51'+bytes([len(pub)])+pub+b'\x51\xae',
        }
        for sk, script in forms.items():
            if h160(script)==A['P2SH_change'][1]:return {'target':'P2SH_change','method':sk+'/'+kind}
    return None

if __name__=='__main__':
    # self-test the P2PKH address algorithm with private key 1.
    selftest_pub=ec.derive_private_key(1,ec.SECP256K1()).public_key().public_numbers()
    selftest=h160(bytes([2+(selftest_pub.y&1)])+selftest_pub.x.to_bytes(32,'big')).hex()
    assert selftest=='751e76e8199196d454941c45d1b3a323f1433bd6'
    t0=time.monotonic(); hits=[]
    for idx,(val,labels) in enumerate(allcand.items(),1):
        found=check_scalar(val)
        if found:
            data={'private_key_hex':val.hex(),'descriptions':labels,'match':found}
            hits.append(data)
            print('MATCH',json.dumps(data,ensure_ascii=False),flush=True)
        if idx%5000==0:print('Progress:',idx,'of',len(allcand),'elapsed_s',round(time.monotonic()-t0,1),flush=True)
    core_sha=sha(CORE)
    # No misinterpretation of HASH160 targets as raw private keys.
    target_hash_proximities={k:sum((x^y).bit_count() for x,y in zip(CORE, payload)) for k,(ver,payload) in A.items()}
    out={
      'funding_txid':TXID,
      'input_satoshis':amounts['input'],
      'outputs_satoshis':{k:amounts[k] for k in ('mini','prize','change')},
      'fee_satoshis':amounts['fee'],
      'output_sum_correct':True,
      'decoded_addresses':{k:{'type':'P2PKH' if v[0]==0 else 'P2SH', 'hash160':v[1].hex()} for k,v in A.items()},
      'middle_codec_160bit':CORE.hex(),
      'original_png_sha256':sha(PNG.read_bytes()).hex(),
      'txid_sha256':sha(TX).hex(),
      'txid_as_32byte_key':TX.hex(),
      'wave_sources_32byte_count':sum(len(x)==32 for x in wave.values()),
      'seed_variants':len(seeds),
      'unique_32byte_candidates':len(allcand),
      'checked_against':['HALV P2PKH both pubkey serializations','DoTPuz P2PKH both pubkey serializations','391fj9nys P2SH-P2WPKH / P2PK / P2PKH / 1of1 multisig, both serializations'],
      'exact_hits':hits,
      'middle_160bit_vs_address_hash_bit_differences':target_hash_proximities,
      'elapsed_seconds':round(time.monotonic()-t0,2),
      'scope_warnings':['Not all mathematically imaginable permutations, only reproducibly specified transforms','P2SH may use arbitrary redeem script: impossible to derive full script universe from single key','Funding input/output data were taken from user-provided explorer transcript; raw transaction not downloaded for independent verification','TXID as direct seed of key corresponding to an output in that same transaction would require a self-referential construction; TXID can still serve as an encoding mask if image was prepared later']
    }
    filename=D/'HALV_TXID_harom_kimenet_celzott_audit_20261101.json'
    filename.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:out[k] for k in ['unique_32byte_candidates','exact_hits','elapsed_seconds','middle_160bit_vs_address_hash_bit_differences']},ensure_ascii=False))
    print('Report',filename)
