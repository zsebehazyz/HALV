# Zden's Crypto Puzzle Series (2015–2024)

## Overview
One of the most prolific and long-running series of creative Bitcoin puzzles by a single creator. Zden's format is deceptively simple — "Find the private key in this image" — but the encoding methods vary wildly between puzzles and range from beginner-accessible to years-long unsolved challenges.

## Creator
**Zden** (pseudonymous)
- Twitter: @Zd3N
- Website: http://crypto.haluska.sk/

## Years Active
**2015–2024** (ongoing; new puzzles still occasionally released)

## Type
Image-based algorithmic puzzles — each image contains a private key encoded using a custom technique that must be reverse-engineered. Methods include:
- Pixel color value arithmetic
- Geometric area calculations
- Animated GIF frame encoding
- LSB steganography
- Custom base-N encoding
- Font/glyph-based encoding

## Status
Most levels SOLVED; a select few remain unsolved or were relaunched after flaws were discovered.

## Full Puzzle Catalog

### Core Bitcoin Puzzle Levels
| Level | Solve Time | Prize | Status | Notes |
|-------|-----------|-------|--------|-------|
| Level 1 | 6 hours | BTC | Solved | Entry-level; beginner-accessible |
| Level 2 | 29 hours | BTC | Solved | — |
| Level 3 | 38 hours | BTC | Solved | — |
| Level 4 | 52 hours | BTC | Solved | Solution published on Steemit |
| Level 5 | 3+ years; relaunched 2021 | 0.005 BTC | Solved (relaunched version) | Original was buggy/incomplete; relaunch fixed |
| Level HALV | — | Unknown | Solved | Created for the 2024 Bitcoin Halving |
| Level SFX | 21 hours | Unknown | Solved | — |
| Level XM17 | 22 hours | Unknown | Solved | Animated GIF; key encoded in specific frames |

### Special / Themed Puzzles
| Puzzle | Solve Time | Prize | Notes |
|--------|-----------|-------|-------|
| 1BiTCoiN WHiTe PaPeR | 72 hours | 1 BTC + physical print | NFT + physical puzzle; generative art based on Satoshi's whitepaper |
| XIXOIO ETH Puzzle | 8 min (after hint) | 6 ETH | Unsolved for 1 year; hint released; solved in 8 minutes |
| HCPP17 Monero | 3 months | 13.37 XMR | Released at HCPP17 (Hackers Congress Paralelní Polis) conference in Prague |
| Litecoin SegWit | 2 weeks | ~210 LTC | Released around SegWit activation |
| Codex Protocol Puzzle | 20 days | Unknown | For Codex Protocol Ethereum project |
| Demobit 2018 Special | 51 days | BTC | Released at Demobit 2018 demoparty |
| Decred Janus | ~10 days | DCR | Seed phrase puzzle for Decred (DCR) cryptocurrency |
| Nethemba DefCon 24 | 5 days 3 hours | BTC | Premium Nethemba security bounty; released at DefCon 24 |

## Notable Level 5 Incident
Level 5 became one of the longest-standing unsolved puzzles in the series, but for an unfortunate reason — **the original puzzle had a flaw**. After 3+ years without a solve, Zden discovered the encoding was incomplete or broken, and **relaunched Level 5 in 2021** with a corrected version.

The relaunched Level 5 uses the rule:
> **Sum of two rectangles' areas = one byte of the private key**

HomelessPhD maintains a community-solving GitHub repo for this puzzle: https://github.com/HomelessPhD/Zden_LVL5

## Technical Encoding Examples

### Animated GIF (Level XM17)
Private key bytes are encoded in specific frames of an animated GIF — each frame contains pixel data that, when extracted at the right position, yields one byte of the key.

### Rectangle Area Method (Level 5 relaunch)
The image contains colored rectangles. For each pair:
- Calculate the **area of each rectangle** (width × height in pixels)
- The **sum of the pair's areas** corresponds to one byte value (0–255)
- All bytes assembled yield the private key

## Multi-Cryptocurrency Coverage
Zden doesn't limit himself to Bitcoin:
- Bitcoin (BTC)
- Ethereum (ETH)
- Litecoin (LTC)
- Monero (XMR)
- Decred (DCR)
- Various others

## Conference Circuit
Several puzzles were released at specific conferences:
- **HCPP17** — Hackers Congress Paralelní Polis, Prague (cypherpunk-focused annual conference)
- **DefCon 24** — Las Vegas hacker conference (Nethemba security firm puzzle)
- **Demobit 2018** — Bratislava demoscene party

## Links
- Main website: http://crypto.haluska.sk/
- privatekeys.pw Level 5: https://privatekeys.pw/puzzles/0.005-btc-lvl5-puzzle
- HomelessPhD Level 5 solver: https://github.com/HomelessPhD/Zden_LVL5
- 1BiTCoiN WHiTe PaPeR write-up: https://jtobcat.medium.com/solving-zdens-1bitcoin-white-paper-puzzle-6ffa4963e1a2

## Notes
Zden's puzzles span an impressive range of difficulty and technique. The consistent format ("find the key in the image") belies an enormous variety of underlying encoding approaches. The XIXOIO ETH puzzle is a fascinating case study — completely unsolved for one year, then solved in **8 minutes** once a single hint was released. This suggests the puzzle was technically valid but required one specific insight to unlock. The conference-released puzzles added a social/temporal dimension — being physically present at HCPP or DefCon gave you early access.
