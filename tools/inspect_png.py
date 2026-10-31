#!/usr/bin/env python3
"""PNG signature/chunk CRC/trailing-byte check, not a complete stego analysis."""
import json
import struct
import zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
raw=(ROOT/'research/sources/cryptoHALV.png').read_bytes()
pos=8
chunks=[]
while pos<len(raw):
    n=struct.unpack('>I',raw[pos:pos+4])[0]
    typ=raw[pos+4:pos+8]
    dat=raw[pos+8:pos+8+n]
    crc=struct.unpack('>I',raw[pos+8+n:pos+12+n])[0]
    chunks.append({'type':typ.decode(),'length':n,'crc_ok':zlib.crc32(typ+dat)&0xffffffff==crc})
    pos+=12+n
    if typ==b'IEND': break
out={'signature_valid':raw[:8]==b'\x89PNG\r\n\x1a\n','chunks':chunks,'bytes_after_IEND':len(raw)-pos}
(ROOT/'research/data/png_structure.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
