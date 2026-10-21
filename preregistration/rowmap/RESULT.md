# RESULT: ROW-MAP rule test (PRE-REG-ROWMAP)

- Pre-registration `PRE_REG_ROWMAP.md`, sha256 `9f7a440ddbb427783a525e976f898b602cd95471654e9f681ded8ee50d1a0a45`. Frozen on the box (read-only) and copied to the Mac at 2026-10-20T11:31:36Z; Mac copy passes `shasum -c`. Run started 11:36:22Z; first ranking (S-R3, real data) 11:37:14Z; first trial ranking (d0 controls) 11:37:14Z; decoy strata 11:37:17Z to 11:37:28Z (`run_rowmap.log`). Nothing ran on trials before the freeze. VERIFIED.
- Deviations: one, in a sanity-check implementation, no effect on any decision (`DEVIATIONS_ROWMAP.md`).
- Child VCF sha256 before and after: `bec64c68...42175`, unchanged. Current CSV `TRACK1_SUBMISSION_FINAL_PROPOSED.csv` unchanged (a6527da7). No network call. VERIFIED.
- Scorer: the organisers' `evaluation.py` (git blob 2aed4922..., Space commit 60e1c30e), imported unmodified; every trial row set was written as a template-format CSV and parsed with `load_submission`, then scored with `score_proband`. VERIFIED.
- Sources: `trials_rowmap.tsv` (sha256 ad17340b...), `summary_rowmap.json` (3c220c8a...), `sanity_rowmap.json` (b9553a3b...), `real_rows.tsv` (6648e755...), code `run_rowmap.py` (b1ad4bb2...), `analyze_rowmap.py` (a619d9d8...), `propose_csv.py` (e8064820...). AlphaMissense hg38 sha256 0516cfd7...

## 1. Gates (all pass, VERIFIED)

| check | result |
|---|---|
| S-R1 base trials regenerate from `pools.tsv` with seeds 101, 102, 103, 501, 502 | A, A-BUB, E all equal |
| S-R2 d0 controls reproduce the spike-in v4 hit rank and gene | 700/700 |
| S-R3 real top 10 = CSV genes; R0 x C1 rows = current CSV; key = row 1 gives 100 / F-max 1.0 | pass, 10/10 rows |
| S-R4 input hashes, scorer blob | pass |
| S-R5 rules agree on the causal row where the causal gene has 1 call or 2 het calls (d0) | 0 mismatches |
| Decoys that became candidate calls of the causal gene | A-CH 1.000, A-HOM 1.000, E-CH 0.995, E-HOM 1.000, A-BUB 1.000 |
| d0 consistency: A-d0 R0 x C1 mean points 73.83, the spike-in RESULT value (73.8) | equal |

Decoy pools after the frozen extraction and consequence steps (SET18 genes sampled in the trials): PCNT 1819, BUB1B 1501, CEP57 620, CENPF 598, ESCO2 196, TRIM37 196, SLF2 160, MAD1L1 128, SMC5 124, TRIP13 82, CENATAC 73, CDC20 58; RNU4ATAC 0 (non-coding) and ZRSR2 (chrX) give no decoy trials.

## 2. Primary result: PRIM = A-CH-dec + E-CH-dec, N = 779 trials, 201 genes (VERIFIED)

Mean rank points (95% stratified gene-cluster bootstrap interval, 10,000 resamples, seed 1):

| rule | C1 | C2 | C3 | F-max C1 / C3 | P(row 1 exact) | causal row exact |
|---|---|---|---|---|---|---|
| R0 draft | 49.10 [44.80, 53.39] | 49.10 | 53.11 [50.78, 55.60] | 0.525 / 0.761 | 0.095 [0.076, 0.117] | 0.108 |
| P1 filter | 77.09 [68.28, 85.19] | 77.09 | 78.88 [71.32, 85.95] | 0.817 / 0.880 | 0.610 [0.575, 0.644] | 0.716 |
| P2 top-2 sort | 79.30 [71.87, 86.28] | 79.30 | 80.07 [73.12, 86.66] | 0.847 / 0.896 | 0.626 [0.592, 0.660] | 0.775 |
| P3 weaker allele | 79.30 | 79.30 | 80.07 | 0.847 / 0.896 | 0.626 | 0.775 |
| P4 MVA1 template | 78.66 [71.58, 85.50] | 78.66 | 79.43 [72.83, 85.82] | 0.841 / 0.893 | 0.614 | 0.763 |
| P5 ClinVar anchor | 79.62 [72.21, 86.54] | 79.62 | **80.20 [73.26, 86.77]** | 0.851 / 0.897 | 0.626 [0.592, 0.660] | 0.775 |

Row-1 exactness and causal-row exactness do not depend on the construction (C2 and C3 insert rows below the lead pair). Jeffreys intervals are trial-level.

Points distribution, R0 x C1: 100 x74, 50 x541, 25 x152, 0 x12. P5 x C3: 100 x488, 50 x258, 25 x31, 0 x2.

## 3. Decision (pre-registered rule applied as written)

| rule | winner | Delta vs R0 x C1 | gate interval (1 - 0.05/17) | A-CH-dec / E-CH-dec | verdict |
|---|---|---|---|---|---|
| D-RM-1 | **P5 x C3** | **+31.10** (95% [26.54, 35.47]; wins/losses 573/28) | [24.26, 37.72] | +30.08 / +32.09 | **adopt P5 x C3** (margin, gate and per-stratum condition all met) |
| D-RM-2 (C1 only, not binding) | P5 x C1 | +30.52 [25.70, 35.09] | [23.32, 37.52] | +28.91 / +32.09 | adopt P5 x C1 |

Falsifier cross-checks for the winner (flag if Delta <= -2.0): A-hid-dec +17.56, A-HOM-dec +74.71, E-HOM-dec +92.75. No flag. H-RM-1 supported.

Near-tie, stated plainly (POST HOC, same bootstrap, not part of the decision): the winner beats P2 x C3 and P3 x C3 by only +0.13 points [0.03, 0.26], and P1 x C3 by +1.32 [-1.36, 3.77]. P5 differs from P2 only in genes holding a ClinVar P/LP call. The C3 contribution is +0.58 [0.00, 1.37] in PRIM but -3.20 [-5.57, -1.01] in A-hid-dec (novel causals), where alternate pairs for a background gene above the causal push the causal row down. Almost all of the gain comes from replacing R0, not from the choice among P2, P3, P5 or from C3.

## 4. Secondary strata (mean rank points, VERIFIED)

| stratum | N (genes) | R0 x C1 | R0 x C2 | P1 x C1 | P2 x C1 | P4 x C1 | P5 x C1 | P5 x C3 |
|---|---|---|---|---|---|---|---|---|
| A-CH-dec | 384 (12) | 43.03 | 43.03 | 71.42 | 71.68 | 70.38 | 71.94 | 73.11 |
| E-CH-dec | 395 (189) | 55.00 | 55.00 | 82.59 | 86.71 | 86.71 | 87.09 | 87.09 |
| A-HOM-dec | 174 (12) | **0.00** | 46.98 | **0.00** | 74.71 | 73.56 | 74.71 | 74.71 |
| E-HOM-dec | 200 (96) | **0.50** | 46.62 | **0.50** | 93.25 | 92.25 | 93.25 | 93.25 |
| A-BUB-dec | 200 (1) | 50.25 | 50.25 | 99.50 | 96.25 | 79.50 | 96.25 | 96.25 |
| A-hid-dec | 558 (12) | 14.87 | 17.46 | 25.87 | 35.62 | 35.12 | 35.62 | 32.42 |
| A-d0 | 300 (14) | 73.83 | 73.83 | 73.83 | 73.83 | 73.83 | 73.83 | 73.83 |
| E-d0 | 300 (278) | 89.75 | 90.08 | 90.25 | 90.75 | 90.75 | 90.75 | 90.75 |
| A-BUB-d0 | 100 (1) | 100 | 100 | 100 | 100 | 100 | 100 | 100 |

Single-gene and 12-gene strata have degenerate or wide cluster intervals; full intervals are in `summary_rowmap.json`.

## 5. Why R0 fails (POST HOC diagnostic, `mech_check.py`; not a pre-registered result)

Causal-row exactness in PRIM, C1, by consequence class of the two causal alleles (T truncating, S splice_region, M missense, I inframe) and of the decoys:

| causal | decoys | N | R0 | P1 | P2 = P3 = P5 | P4 |
|---|---|---|---|---|---|---|
| T+T | M | 161 | 0.00 | 0.99 | 0.99 | 0.98 |
| T+T | M+M | 156 | 0.00 | 0.99 | 0.99 | 0.96 |
| S+T | M | 65 | 0.00 | 0.98 | 0.78 | 0.77 |
| S+T | M+M | 62 | 0.00 | 0.98 | 0.69 | 0.68 |
| M+T | M | 54 | 0.44 | 0.44 | 0.78 | 0.78 |
| M+T | M+M | 53 | 0.25 | 0.25 | 0.64 | 0.64 |
| M+M | M / M+M | 20 / 19 | 0.35 / 0.16 | 0.35 / 0.16 | 0.50 / 0.42 | 0.50 / 0.42 |

With more than two calls, R0 always takes one LoF-type call plus the lowest-position missense, so any missense decoy displaces a second truncating or splice causal allele (0/444 such trials). R0 also has no homozygous provision: a homozygous causal plus one het decoy becomes a wrong pair (A-HOM-dec 0 points). P1 drops homozygous calls when a het exists (0 points there). P1 beats the score rules on splice + truncating causals because the fixed s = 0.5 for splice_region (Section 5 of the pre-registration) ranks a splice causal below a decoy missense with AlphaMissense > 0.5; score rules win on missense-containing causals.

## 6. Hypotheses and predictions

| item | outcome |
|---|---|
| H-RM-1 | supported (D-RM-1 adopts P5 x C3, Delta +31.1) |
| H-RM-2 | supported: causal row exact 0.775 (P2, P3, P5) vs 0.716 (P1) vs 0.108 (R0) |
| H-RM-3 | supported: C3 >= C1 in PRIM for every rule; C2 = C1 exactly in PRIM rank points for every rule |
| H-RM-4 | supported: R0 x C1 and P1 0 / 0.5 points in HOM-dec; P2 and P5 74.7 / 93.3 |
| H-RM-5 | supported: row 1 is the BUB1B pair in 18 of 18 combinations (VERIFIED) |
| P-a, P-b (real rows) | held (Section 7) |
| P-c | held: winner is a score rule with C3 |
| P-d | held: R0 x C2 recovers 47.0 / 46.6 points in HOM-dec |
| P-e | held: P4 79.5 < P3 96.25 in A-BUB-dec |
| P-f | held for score rules (C3 costs 3.2 points in A-hid-dec); for R0, C2 gained 2.6 there instead of costing |

## 7. Real data (VERIFIED)

- BUB1B interval: 14 calls; only the two submitted calls lie in a protein-coding exon; every other call is at least 905 bp from one. The "third het" is intronic and is not a candidate in our pipeline, so every rule sees exactly two BUB1B calls.
- Row 1 (BUB1B pair) is unchanged under all 18 combinations.
- P5 x C3 (adopted) changes rows 4 and 5 only. Row 4 POU6F2: frameshift + missense becomes the two frameshift calls. Row 5 EIF4EBP1: the frameshift is kept, and the missense becomes the one with the highest AlphaMissense value instead of the lowest-position one. Neither gene has a ClinVar P/LP call, so P5 falls back to P2 there. C3 inserts nothing on the real data (BUB1B has only two coding hets), so P5 x C3 rows = P5 x C1 rows = P2 x C1 rows.
- Other combinations: P1 changes row 4 only; P2, P3, P4 change rows 4 and 5 (same rows as P5); any C2 inserts the two BUB1B halves at rows 2 and 3, moves LZTR1 to row 4 and drops AGAP3 and FOXO6.
- Proposed CSV (box only, D-RM-3): `TRACK1_SUBMISSION_ROWMAP_PROPOSED.csv`, sha256 a349d642fb4597ea2ebe1b032cf40e3ea2b962e80860e7cc9538164944d78e4f. Identical to the current CSV except the variants and notes of rows 4 and 5. EPCR vector unchanged and strictly decreasing; all 15 variants are in the supplied VCF with exact REF/ALT; `evaluation.py` with key = row 1 gives 100 points and F-max 1.0, the same as the current CSV. Changing rows 4 and 5 cannot change the automated score if the BUB1B pair is the key.

## 8. What changes in the methods if adopted

- ROW-MAP text: replace the draft rule with P5: "Anchor = a candidate call with a ClinVar P/LP assertion (truncating first, then higher per-variant score, then lower position); a homozygous anchor is a single row; otherwise the partner is the best other heterozygous candidate by the same key. With no P/LP call, take a homozygous call alone if present, else the two best heterozygous calls by that key. Per-variant score: 1.0 nonsense/frameshift, AlphaMissense for missense, 0.5 otherwise."
- C3: alternate pairs {a, c}, {b, c} below the lead pair when its gene has three or more heterozygous candidate calls. It inserts nothing on the real data. EPCR for an inserted row would be the positional value of the frozen vector, an ordinal label rather than the spike-in rank-slot probability.
- Measured basis: "chosen by a pre-registered spike-in with 1 to 2 decoy hets (PRE-REG-ROWMAP, sha256 9f7a440d...)".

## 9. Limits and open items

- Decoys are public ClinVar non-P/LP alleles, almost all missense (Section 5 table), not the child's own passenger calls. Truncating decoys are rare in this pool, which favours truncating-first rules (P1, P2, P5). Causals are ClinVar P/LP, enriched for high AlphaMissense, which favours score rules. The P5 vs P2 vs P1 ordering is within noise.
- Ranking and row building only; no reads, calling or phasing. Gene-uniform sampling. A strata have 12 genes, so their cluster intervals are wide.
- The kinase-domain boundary for P4 (766-1050) comes from public secondary sources. UNVERIFIED against UniProt.
- AlphaMissense data is licensed CC BY-NC-SA 4.0 (file header). Whether using it in this submission counts as non-commercial is UNVERIFIED and is a team or user decision.
- The decision is about expected scores over the trial population. For this child the automated score is unchanged (row 1 identical).

## 10. Files (box `~/Documents/HACKATON/_private/agent_out/rowmap/`)

PRE_REG_ROWMAP.md (+ .sha256), DEVIATIONS_ROWMAP.md, RESULT_ROWMAP.md, run_rowmap.log, sanity_rowmap.json, summary_rowmap.json, trials_rowmap.tsv, decoy_pool.tsv, decoy_draws.tsv, decoy_* tables, real_rows.tsv (child coordinates, box only), TRACK1_SUBMISSION_ROWMAP_PROPOSED.csv (box only), feasibility_decoy.py/.json, bub1b_interval.py, run_rowmap.py, analyze_rowmap.py, propose_csv.py, mech_check.py. Mac copies: PRE_REG, .sha256, DEVIATIONS_ROWMAP.md, RESULT_ROWMAP.md.
