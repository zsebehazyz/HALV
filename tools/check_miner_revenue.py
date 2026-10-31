#!/usr/bin/env python3
"""Check direct chronological daily miner-revenue envelope; no screenshot fit."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((ROOT/'research/data/miner_revenue_daily.csv').open()))
out = {'formula': '(IssTotNtv + FeeTotNtv) * PriceUSD',
       'limitation': 'Approximate daily USD conversion. User screenshot units and aggregation are unknown; this is not image-to-image alignment.',
       'windows': {}}
for start in ['2020-01-01', '2020-05-11']:
    selected = [r for r in rows if start <= r['time'][:10] <= '2024-04-19']
    values = [(float(r['IssTotNtv'])+float(r['FeeTotNtv']))*float(r['PriceUSD']) for r in selected]
    maxima = [max(values[i*len(values)//8:(i+1)*len(values)//8]) for i in range(8)]
    out['windows'][start] = {'days':len(values), 'block_maxima_usd':maxima,
                            'block_maxima_relative_to_first':[v/maxima[0] for v in maxima]}
print(json.dumps(out,indent=2))
