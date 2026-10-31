#!/usr/bin/env python3
"""Offline P2PKH candidate checking. No wallet/network/transaction operations."""
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

TARGET = '1crypto24HCr178iMcKd5iUi5D4rsg1nK'
ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def sha256(b):
    return hashlib.sha256(b).digest()

def b58encode(b):
    n = int.from_bytes(b, 'big')
    out = ''
    while n:
        n, r = divmod(n, 58)
        out = ALPHABET[r]+out
    return '1'*(len(b)-len(b.lstrip(b'\0')))+out

def b58decode(s):
    n = 0
    for c in s:
        n = n*58+ALPHABET.index(c)
    return b'\0'*(len(s)-len(s.lstrip('1')))+n.to_bytes((n.bit_length()+7)//8, 'big')

def addresses(key):
    scalar = int.from_bytes(key, 'big')
    if len(key) != 32 or not 0 < scalar < ORDER:
        return {}
    pub = ec.derive_private_key(scalar, ec.SECP256K1()).public_key()
    result = {}
    for name, fmt in [('compressed', serialization.PublicFormat.CompressedPoint),
                      ('uncompressed', serialization.PublicFormat.UncompressedPoint)]:
        point = pub.public_bytes(serialization.Encoding.X962, fmt)
        payload = b'\0'+hashlib.new('ripemd160', sha256(point)).digest()
        result[name] = b58encode(payload+sha256(sha256(payload))[:4])
    return result

def selftest():
    expected = {'compressed': '1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH',
                'uncompressed': '1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm'}
    if addresses((1).to_bytes(32, 'big')) != expected:
        raise RuntimeError('Private scalar 1 known-answer test failed')
    raw = b58decode(TARGET)
    if len(raw) != 25 or raw[0] != 0 or sha256(sha256(raw[:-4]))[:4] != raw[-4:]:
        raise RuntimeError('Target Base58Check failed')
    if addresses(bytes(32)) or addresses(ORDER.to_bytes(32, 'big')):
        raise RuntimeError('Scalar range validation failed')
    return {'scalar_1_both_formats': 'passed', 'target_base58check': 'passed',
            'invalid_scalars': 'passed', 'target_hash160': raw[1:-4].hex()}

if __name__ == '__main__':
    import json
    print(json.dumps(selftest(), indent=2))
