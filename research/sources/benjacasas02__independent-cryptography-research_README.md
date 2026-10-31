# Benjamin — Independent Cryptography Research

> **Cryptanalysis · Applied Mathematics · Reverse Engineering · Computational Experiments**

I'm a computer science student from **Chile** working independently on cryptography and hard technical problems.

What began as curiosity about cryptographic puzzles gradually became an obsession with understanding them properly.

Instead of guessing answers, I started building the infrastructure I wished existed:

* solvers;
* mathematical models;
* reproducible experiments;
* verification tools;
* forensic pipelines;
* hypothesis ledgers;
* and systems for recording not only what works — but what fails.

Today I use difficult public cryptographic challenges as **experimental laboratories for research**.

My operating loop is simple:

```text
hypothesis
    ↓
formalization
    ↓
small discriminating experiment
    ↓
evidence
    ↓
adjudication
    ↓
next decision
```

I am interested less in producing a plausible answer than in producing an answer that **survives verification**.

---

## Selected Research

<table>
<tr>
<td width="33%" valign="top">

### 🔐 Paradigm Kryptos

**Experimental cryptanalysis at scale**

My largest research project.

I built a scientific framework for investigating cipher families, representations, symmetries, nuisance parameters, identifiability and search reachability.

**Focus**

* cipher-family identification
* representation discovery
* exact inference
* mathematical quotients
* controlled synthetic experiments
* search-space reduction
* independent verification
* negative-result preservation

[Explore Paradigm Kryptos →](research/paradigm-kryptos/README.md)

</td>

<td width="33%" valign="top">

### 🧭 Glimmer

**Multimodal cryptographic treasure hunt**

A web-based Bitcoin puzzle combining navigation, textual clues, metadata, classical puzzle mechanisms and mnemonic reconstruction.

I independently reconstructed substantial portions of its structure and progressed through branches beyond much of the surviving public documentation.

**Focus**

* route reconstruction
* lock analysis
* asset forensics
* EXIF investigation
* BIP39 structure
* web archaeology
* decoy discrimination
* constraint propagation

[Explore Glimmer →](research/glimmer/README.md)

</td>

<td width="33%" valign="top">

### 🧩 Zden

Reverse-engineering a halving-scaled visual signal

Zden’s HALV puzzle encodes a Bitcoin private-key candidate in the geometry of a rasterized waveform.

The computational oracle is inexpensive and exact: derive the P2PKH address from a candidate scalar and compare it with the prize address. The difficult part is reconstructing the signal generator that produced the image without using the target address to guide the measurement.

Focus

forensic image analysis
quantized waveform reconstruction
multiscale signal geometry
sampling-clock discrimination
target-blind model selection
exact Bitcoin address validation
hypothesis elimination without visual overfitting


[Explore Zden →](research/zden/README.md)

</td>
</tr>
</table>

---

# Paradigm Kryptos

Paradigm Kryptos changed the way I approach cryptanalysis.

The obvious way to attack an unknown cipher is to keep trying transformations until something resembles language.

I wanted something better.

So I began treating every proposed mechanism as a scientific hypothesis.

A typical branch looks like:

```text
candidate cipher family
        ↓
identify symmetries / gauges / aliases
        ↓
derive an inference method
        ↓
validate implementation on known controls
        ↓
measure identifiability on synthetic data
        ↓
measure specificity against competing families
        ↓
freeze decision criteria
        ↓
only then inspect the target
```

This produced an increasingly large research infrastructure including:

* an append-only scientific ledger;
* exact and approximate inference engines;
* cryptanalytic experiment harnesses;
* representation-search machinery;
* symmetry and quotient analysis;
* computational performance audits;
* synthetic positive and negative controls;
* independent verification tools.

One of the most important lessons has been learning to distinguish claims that sound similar but are mathematically different:

```text
parameter recovery
        ≠
family identification

synthetic success
        ≠
target relevance

round-trip correctness
        ≠
correct cryptanalytic model

search failure
        ≠
model falsification
```

That distinction now guides almost everything I build.

[View technical research →](research/paradigm-kryptos/)

---

# Glimmer

Glimmer required a completely different research style.

Instead of one clean cryptographic object, the puzzle combines:

```text
web navigation
+ visual clues
+ hidden routes
+ metadata
+ text
+ classical puzzle mechanisms
+ Bitcoin
+ mnemonic reconstruction
```

I approached it as a **multimodal inference problem**.

My work has included:

* reconstructing the route graph;
* following and validating multiple branches;
* analyzing hidden locks;
* extracting and interpreting asset metadata;
* separating deliberate decoys from structural clues;
* reconstructing constraints on mnemonic material;
* analyzing ordering ambiguities;
* comparing public community progress against independently recovered structure.

Some active target-relevant findings remain private because the puzzle is still competitive.

Where useful, private hypotheses can be cryptographically committed before disclosure to establish provenance without publishing the underlying content.

[View Glimmer research →](research/glimmer/)

---

# Zden — Level HALV

Zden’s Level HALV was published on 2024-04-20, the day of Bitcoin’s fourth halving.

The prize address is:

1crypto24HCr178iMcKd5iUi5D4rsg1nK

It is a funded, unspent legacy P2PKH address. Because it has never spent an output, its public key is not exposed. A proposed solution can therefore be validated only by treating it as a secp256k1 private scalar, deriving the corresponding compressed and uncompressed Bitcoin addresses, and requiring an exact match.

The reward of 312,500 satoshis mirrors the fourth-halving block subsidy of 3.125 BTC at a scale of 1:1000.

What the image actually contains

Forensic analysis of the official cryptoHALV.png rules out the usual hidden-data channels:

no appended payload after IEND
no meaningful bit-plane steganography
no hidden color or alpha channel
no independent FFT watermark
no usable metadata payload

The waveform itself is the data-bearing object.

Its geometry establishes a precise multiscale structure:

the signal occupies exactly 768 horizontal pixels
its measured span is x = 91…858
a marked vertical feature at x = 90…92 identifies the origin
the signal divides into eight blocks of 96 pixels
the scale halves from one block to the next
the block scales are:
128, 64, 32, 16, 8, 4, 2, 1

Within block (b), the measured amplitude levels follow:

[
A=q\cdot 2^{7-b},\qquad q\in{1,2,3}
]

The observed maximum slopes in the high-resolution blocks agree with:

[
\text{slope}=\frac{2^{7-b}}{3}
]

This establishes a physical lattice of three pixels and connects the waveform directly to repeated halving.

The real ambiguity: lattice versus symbol clock

A three-pixel lattice does not necessarily mean that every three pixels encode one symbol. At least two compact models remain:

Model	Clock	Symbols	Information
Binary-step model	3 px	256 directions	(256\times1=256) bits
Quaternary-state model	6 px	128 states	(128\times2=256) bits

In the binary model, each three-pixel step would encode an upward or downward transition.

In the quaternary model, every six pixels would encode one state:

[
q\in{0,1,2,3}
]

with the centerline supplying state zero and the visible amplitudes supplying states one through three.

Both models fit the 768-pixel span, and both can produce the measured maximum slope. A change of two amplitude units over six pixels has the same slope as a change of one unit over three pixels:

[
\frac{2s}{6}=\frac{s}{3}
]

Therefore, the slope proves the raster lattice but does not by itself determine the symbol rate.

The binary-step interpretation also faces a parity constraint. If every transition is exactly (+1) or (-1), then:

[
q_{n+m}-q_n\equiv m\pmod 2
]

A measured transition from (q=2) to (q=1) across two three-pixel intervals violates this invariant. Rounded rendering cannot repair an inconsistency in the underlying discrete path.

This makes the six-pixel quaternary model the strongest current hypothesis, although it still requires pixel-level reconstruction.

What has already been eliminated

More than 33,000 unique candidates have been tested from:

apex shape and amplitude channels
59-, 64-, 67- and 69-lobe segmentations
direct nibble interpretations
differential and accumulated encodings
half-key expansions
interval and run-length transducers
block and halving metadata
hashes, reversals, complements and byte-order variants

None derives the target address.

These negatives strongly constrain apex-only interpretations, but they do not test a complete reconstruction of 128 regularly sampled quaternary states. The missing information may lie between the visible extrema rather than in an additional external “half” of the key.

Current resolution strategy

The next discriminating experiment is to reconstruct the image as the output of a small family of signal generators:

Extract the medial centerline rather than the outside stroke boundary.
Compare a three-pixel binary clock with a six-pixel quaternary clock.
Render each candidate using a limited set of global smoothing models:
straight polyline
rounded joins
quadratic midpoint interpolation
Catmull–Rom interpolation with one global tension
one-pass corner cutting
Fit the global geometry on the first high-resolution blocks.
Predict the remaining blocks without retuning.
Reject any model requiring per-lobe corrections.
Recover the discrete state sequence using dynamic programming.
Only after reconstruction, test the resulting 256 bits against the Bitcoin oracle.

If the quaternary model produces 128 states, the primary decoding space is small:

24 bijections between four states and two-bit symbols
forward and reverse traversal
bit order within each pair
byte order
compressed and uncompressed public-key derivation

A solution is accepted only if the resulting scalar derives exactly to:

1crypto24HCr178iMcKd5iUi5D4rsg1nK

No visual plausibility, partial prefix, printable output or statistical score is treated as evidence.

Why this puzzle matters

HALV is not primarily a password search or a conventional steganography problem.

It is a digital signal reverse-engineering problem disguised as a simple image:

rasterized curve
→ recover scale and clock
→ infer discrete states
→ decode 256 bits
→ derive Bitcoin address

The central methodological lesson is that a visible sampling grid and a symbol clock are not the same thing. The correct solution must explain the complete pixel geometry before it is allowed to use the target address.

That turns the puzzle from uncontrolled interpretation into a falsifiable model-selection problem.

[View Zden research →](research/zden/)

---

# Selected Results

I maintain a separate index of results that I consider worth inspecting independently.

It includes:

* solved controls;
* exact mathematical reductions;
* successful reconstruction work;
* failed experiments with preserved criteria;
* computational hardstops;
* unresolved hypotheses with unusually high information value.

[**View Selected Results →**](selected-results/README.md)

---

# Research Philosophy

I try to follow several rules.

### 1. Preserve failure

If an experiment fails its frozen criterion, I do not rescue it afterward by changing the metric.

```text
FAILED means FAILED.
```

A better idea becomes a **new experiment**.

---

### 2. Separate evidence levels

I use labels such as:

| Status          | Meaning                                                             |
| --------------- | ------------------------------------------------------------------- |
| **PROVEN**      | Established directly by reproducible or independent evidence        |
| **SUPPORTED**   | Strong evidence exists, but meaningful alternatives remain          |
| **OPEN**        | Live hypothesis awaiting adjudication                               |
| **FAILED**      | Failed its frozen experimental criterion                            |
| **PARKED**      | Potentially viable but blocked by information, algorithm or compute |
| **UNKNOWN**     | Evidence is insufficient                                            |
| **SPECULATIVE** | Interesting idea without substantial supporting evidence            |

---

### 3. Reduce before searching

Before brute force, I look for:

* symmetries;
* invariants;
* quotient spaces;
* aliases;
* gauges;
* factorizations;
* short generators;
* algebraic structure;
* information bottlenecks.

The most useful computation is often the computation you can prove you no longer need to perform.

---

### 4. Prefer discriminating experiments

A good experiment should change what I believe.

I prefer a cheap test that kills half the hypothesis space over an expensive search that merely produces another candidate.

---

### 5. Distinguish the blocker

When progress stops, I try to identify whether the limitation is:

```text
INFORMATION
REPRESENTATION
ALGORITHM
IMPLEMENTATION
COMPUTE
```

Optimizing the wrong layer usually wastes more time than the original problem.

---

# Reproducibility

Whenever possible, research artifacts include:

```text
hypothesis
assumptions
implementation
controls
frozen decision rule
raw result
interpretation
final status
```

I also preserve negative results because they prevent future work from unknowingly repeating already-adjudicated branches.

Active competitive research may be withheld temporarily.

For those cases, I can publish SHA-256 commitments such as:

```text
2026-XX-XX
project: active-hypothesis-007
sha256: <commitment>
```

and reveal the corresponding document later.

[View commitments →](commitments/README.md)

---

# What I'm Interested In

My current interests include:

```text
cryptanalysis
applied mathematics
computational experimentation
algorithms
search-space reduction
finite algebra
combinatorics
reverse engineering
steganography
blockchain forensics
scientific software
AI-assisted research
```

More generally, I like problems where the correct representation is unclear and where progress requires building new tools rather than applying a known recipe.

---

# Why I Do This

None of this began as coursework.

I kept following these problems because I genuinely could not stop thinking about them.

Over time, cryptography began occupying more and more of the time I previously spent on conventional coursework.

But the obsession produced something tangible.

I built software.

I ran experiments.

I learned mathematics because the problems required it.

I discovered mistakes in my own methods.

I rebuilt them.

And I became increasingly interested in one question:

> **How far could I take this if I had real runway to pursue it?**

So far, almost all of this work has been done independently from Chile, with limited resources.

I want to find out what happens when that constraint changes.

---

# Independent Research Sponsorship

I'm currently looking for a small number of people interested in supporting independent technical research.

I'm **not** asking anyone to bet that I will solve a particular puzzle.

The funded product is the research:

* software;
* experiments;
* mathematical analysis;
* technical reports;
* tooling;
* reproducible artifacts;
* useful negative results.

Funding would primarily buy the resource that matters most:

## uninterrupted research time.

It would also support compute, tooling, archival access and infrastructure.

A relatively small amount of funding can create a disproportionate amount of research runway for me in Chile.

### Current objective

**Fund my first dedicated independent research cycle.**

During that cycle I intend to publish:

* regular research notes;
* reproducible experiments;
* new software and tooling where appropriate;
* experimental failures as well as successes;
* a final technical summary of what changed.

No guarantee of a puzzle solution.

No manufactured breakthroughs.

Just serious work and an auditable record of what the evidence supports.

[**Sponsor Research →**](sponsorship/README.md)

---

# Explore

**→ [Selected Results](selected-results/README.md)**
**→ [Paradigm Kryptos](research/paradigm-kryptos/README.md)**
**→ [Glimmer](research/glimmer/README.md)**
**→ [Zden](research/zden/README.md)**
**→ [Methodology](methodology/README.md)**
**→ [Research Sponsorship](sponsorship/README.md)**

---

# Contact

**Benjamin Casas Del Valle**
Chile 🇨🇱

GitHub: `https://github.com/benjacasas02`
Email: `benja.casas02@gmail.com`


If you're a researcher, hacker, builder, funder, or simply someone who likes betting early on unusual technical people, I'd be happy to hear from you.

---

<sub>
Public cryptographic challenges discussed in this repository are treated as research objects. Active prize-relevant information may be withheld where disclosure would compromise an ongoing public competition.
</sub>
