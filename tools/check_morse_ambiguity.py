#!/usr/bin/env python3
"""Demonstrate ambiguity without pretending to measure the attached image."""
import json

MORSE = dict(zip(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
    '.- -... -.-. -.. . ..-. --. .... .. .--- -.- .-.. -- -. --- .--. --.- .-. ... - ..- ...- .-- -..- -.-- --.. ----- .---- ..--- ...-- ....- ..... -.... --... ---.. ----.'.split()
))
DECODE = {v: k for k, v in MORSE.items()}

def partitions(pattern):
    if not pattern:
        return ['']
    return [DECODE[pattern[:n]] + suffix
            for n in range(1, min(5, len(pattern)) + 1)
            if pattern[:n] in DECODE
            for suffix in partitions(pattern[n:])]

results = []
for text in ('XEX', 'NMRM'):
    groups = [MORSE[c] for c in text]
    pattern = ''.join(groups)
    alternatives = partitions(pattern)
    results.append({'claimed_reading': text, 'grouped': ' '.join(groups),
                    'pattern': pattern, 'marks': len(pattern),
                    'possible_alphanumeric_readings_without_gaps': len(alternatives),
                    'shortest_readings': sorted(alternatives, key=lambda s: (len(s), s))[:12]})
print(json.dumps({'note': 'Patterns come from user-supplied prior notes, not new pixel measurements. Counts allow A-Z/0-9 and arbitrary letter boundaries.',
                  'results': results}, indent=2))
