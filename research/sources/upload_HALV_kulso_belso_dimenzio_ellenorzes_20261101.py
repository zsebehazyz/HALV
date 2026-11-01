"""HALV: independent GF(2) cell-affine-dimension check, no private-key guesses."""
import csv, hashlib, json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent
IMAGE = ROOT / 'cryptoHALV (1).png'
CSV = ROOT / 'HALV_256_minta_20261031.csv'
EXPECTED_SHA = '3a487ebaeb4801137f09159a2d533046936cd395f4e2f7d115ac554607790e95'
assert hashlib.sha256(IMAGE.read_bytes()).hexdigest() == EXPECTED_SHA
with CSV.open(newline='', encoding='utf-8') as f:
    q = np.asarray([int(row['round_q']) for row in csv.DictReader(f)], dtype=np.uint8)
assert q.size == 256 and np.all(q <= 3)
q = q.reshape(8, 32)

def gf2_rank(vals):
    pivots = {}
    for v in vals:
        x = int(v)
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    return len(pivots)

def cell_words(block):
    words = []
    for cell in block.reshape(8,4):
        value = 0
        for v in cell:
            value = (value << 2) | int(v)
        words.append(value)
    return words

result = []
for b in range(8):
    phases = []
    for start in range(4):
        cells = cell_words(np.roll(q[b], -start))
        phases.append({'start_offset_samples': start,
                       'linear_rank': gf2_rank(cells),
                       'affine_dimension': gf2_rank([v ^ cells[0] for v in cells]),
                       'distinct_cell_patterns': len(set(cells))})
    result.append({'block': b + 1,
                   'observed_phase_affine_dimension': phases[0]['affine_dimension'],
                   'best_affine_dimension_across_offsets': min(p['affine_dimension'] for p in phases),
                   'phase_checks': phases})
output = {'image_sha256': EXPECTED_SHA, 'num_samples': 256, 'cell_width_samples': 4,
          'method': 'Eight 8-bit cell patterns per block. Binary affine dimension over GF(2), after all four within-block cyclic start offsets. For a shared 4-bit affine-embedded code, affine dimension cannot exceed 4 and is invariant under fixed invertible bit permutations, XOR masks, or GF(2)-linear invertible transforms. Cell offsets are circular *within* each block; this does not test arbitrary variable-length symbols.',
          'blocks': result}
out = ROOT / 'HALV_kulso_belso_dimenzio_20261101.json'
out.write_text(json.dumps(output, indent=2, ensure_ascii=False),encoding='utf-8')
for row in result:
    print('block', row['block'], 'default dimension', row['observed_phase_affine_dimension'],
          'min dimension', row['best_affine_dimension_across_offsets'])
print('saved:',out)
