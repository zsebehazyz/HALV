#!/usr/bin/env python3
"""Fixed, reproducible price-envelope check; does not fit image pixels."""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((ROOT / 'research/data/btc_usd_daily_2020_to_halving.csv').open()))
results = {}
for start in ('2020-01-01', '2020-05-11'):
    selected = [r for r in rows if start <= r['date'] <= '2024-04-19']
    prices = [float(r['price_usd']) for r in selected]
    blocks = [prices[i * len(prices) // 8:(i + 1) * len(prices) // 8] for i in range(8)]
    maxima = [max(b) for b in blocks]
    means = [sum(b) / len(b) for b in blocks]
    returns = [math.log(b / a) for a, b in zip(prices, prices[1:])]
    rms = []
    for i in range(8):
        b = returns[i * len(returns) // 8:(i + 1) * len(returns) // 8]
        rms.append(math.sqrt(sum(x*x for x in b) / len(b)))
    results[start] = {
        'end': selected[-1]['date'], 'daily_rows': len(prices),
        'first_price_usd': prices[0], 'last_price_usd': prices[-1],
        'block_maxima_usd': maxima, 'block_means_usd': means,
        'block_maxima_relative_to_first': [v / maxima[0] for v in maxima],
        'daily_log_return_rms_per_block': rms,
        'hypothetical_halving_envelope_relative_to_first': [2**(-i) for i in range(8)],
    }
output = {
    'method': 'Eight consecutive equal-count daily blocks; no tuning or image fitting.',
    'limitation': 'Tests only a direct chronological linear-scale price envelope. Image geometry is not measured. Does not rule out arbitrary transforms, reversals, returns, or encoded references.',
    'windows': results,
}
print(json.dumps(output, indent=2))
