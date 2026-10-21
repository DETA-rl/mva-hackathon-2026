# RESULT: spike-in calibration of EPCR (PRE-REG-SPIKEIN-EPCR)

- Pre-registration: `PRE_REG_SPIKEIN_EPCR.md`, sha256 `6d40e58fe2d34d92fa9ff42b7171ad5034b45c2409591779c4cc3775650ede69`. Frozen and synced to the Mac at 2026-10-20T09:06:29Z (Mac copy verified with `shasum -c`). First spiked ranking (S3 unmask) at about 09:09:3xZ; trial loop started 09:09:39Z (`run.log`). VERIFIED.
- Deviations: one, no effect on results (`DEVIATIONS.md`).
- Child VCF sha256 before and after: `bec64c68...42175`, unchanged. VERIFIED. No network call was made.
- Everything below is computed from `trials.tsv` (sha256 9b669a72...), `alleles.tsv` (607575a2...), `summary.json` (e7d7b536...). Intervals are Jeffreys 95% unless stated.

## 1. Gates and sanity checks (all pass, VERIFIED)

| check | result |
|---|---|
| G1 (before freezing, real unspiked data): consequence, extraction, v3 and v4 summaries byte-identical; amended top 10 and ROW-MAP rows equal the draft CSV | pass |
| S1: masked background has no BUB1B row, no BUB1B candidate, BUB1B not ranked | pass |
| S2: masked consequence table = original minus the two BUB1B rows | pass |
| S3: adding the real pair back puts BUB1B at v4 rank 1 and v3 rank 1; full v4 and v3 orders equal the unspiked orders | pass |
| Technical fix applied: Amendment 1 (MT-* excluded) in every v4 run; ranking_v4_fixed.py omits it | logged in the pre-registration |

Masked v4 top 10 (the competition every spike faces): LZTR1 (tier A, pheno 1), GNRHR (A, 0), POU6F2, EIF4EBP1, HRNR (B), IGBP1, ADAMTS1, AGAP3, FOXO6, ADPRHL1 (C).

## 2. Strata (hit rank = best rank of a gene row holding a spiked allele)

| stratum | N | v4 rank-1 recall | v4 top-10 | v3 rank-1 recall | v4 rank distribution (r1, r2, r3-10, >10, not ranked) |
|---|---|---|---|---|---|
| A primary (SET18, gene-uniform, 200 CH + 100 HOM) | 300 | **0.533 [0.477, 0.589]** | 0.947 [0.917, 0.968] | 0.840 [0.795, 0.878] | 160, 124, 0, 0, 16 |
| A-CH | 200 | 0.565 [0.496, 0.632] | 0.960 | 0.890 | 113, 79, 0, 0, 8 |
| A-HOM | 100 | 0.470 [0.374, 0.568] | 0.920 | 0.740 | 47, 45, 0, 0, 8 |
| A-pc (protein-coding genes only, subset) | 284 | 0.563 [0.505, 0.620] | 1.000 | 0.887 | 160, 124, 0, 0, 0 |
| A-BUB (other BUB1B P/LP pairs) | 100 | **1.000 [0.975, 1.000]** | 1.000 | 1.000 | 100, 0, 0, 0, 0 |
| B novel (A trials, ClinVar hidden, no frequency) | 300 | **0.000 [0.000, 0.008]** | **0.790 [0.741, 0.833]** | 0.000 | 0, 0, 237 (r3 15, r6 155, r8 42), 43, 20 |
| C1 ClinVar stop_lost SNVs, 1/1 | 100 | 0.050 | 0.080 | 0.010 | 5, 3, 0, 0, 92 |
| C2-HOM synthetic stop-loss, 1/1 | 120 | 0.000 | 0.000 | 0.000 | 0, 0, 0, 0, 120 |
| C2-CH synthetic stop-loss + ClinVar partner | 91 | 0.341 | 1.000 (via partner) | 0.341 | 31, 60, 0, 0, 0; full row 0/91 |
| D control (AR genes, HPO score 0) | 300 | **0.010 [0.003, 0.026]** | 0.957 | 0.760 [0.709, 0.806] | 3, 284, 0, 0, 13 |
| E secondary (AR genes, HPO score >= 1, not SET18) | 300 | 0.857 [0.814, 0.893] | 0.987 | 0.800 | 257, 39, 0, 0, 4 |

Per gene, stratum A, v4 (rank-1 / trials; HPO score in brackets): BUB1B 23/23 [3], CEP57 26/26 [3], ESCO2 19/19 [2], TRIP13 20/20 [2], ZRSR2 5/5 [2], MAD1L1 27/27 [1], PCNT 18/18 [1], TRIM37 22/25 [1], CDC20 0/27 [0], CENATAC 0/27 [0], CENPF 0/24 [0], SLF2 0/16 [0], SMC5 0/27 [0], RNU4ATAC 0/16 [4, never ranked]. Every HPO-score-0 trial landed at rank 2, behind LZTR1. Pools empty (cannot be sampled): RNU6ATAC, SNRNP48, CEP192, MAD2L1BP.

Frequency bias check: of 500 spiked alleles in A, 62 carried a ClinVar AF field (61 ExAC, 1 1000G); none reached AF >= 0.001; 416 were treated as unobserved. In D, 1 of 500 was dropped as common.

## 3. Decisions (pre-registered rules applied as written)

| rule | result | what it rules out |
|---|---|---|
| D1 (H-SPK-1, bar 0.80) | **partly robust**; H-SPK-1 **falsified** (0.533 < 0.80) | Rules out "v4 puts any MVA-set biallelic P/LP causal at rank 1". Rank 1 needs an HPO score above LZTR1's (or a tie won on v2): 5 of the 13 sampled genes (CDC20, CENATAC, CENPF, SLF2, SMC5) never reach rank 1 (0/121), and RNU4ATAC is invisible to the exonic pipeline (0/16 ranked). |
| D2 (H-SPK-2, top-10 bar 0.50) | **finds without ClinVar (top 10 only)**; not falsified (0.790) | Rules out "the method needs ClinVar to list the causal". It does not rule out dependence for rank 1: 0/300 novel causals reach rank 1, because LZTR1 and GNRHR hold tier A. Most land at rank 6 (top of tier C). |
| D3 (H-SPK-3) | known limitation **confirmed**, not falsified: 0/311 stop-loss alleles labelled stop_lost (C1: 91 UTR_noncoding_exon, 6 splice_region, 1 missense, 1 nonsense, 1 no canonical transcript; C2: 211/211 UTR_noncoding_exon). Stop-loss allele was a ranked candidate in 8/311 = 2.6% (only through other labels) | **Blind spot, must be listed in the methods.** A stop-loss causal is never scored as stop-loss; in a pair it gives half credit at most (C2-CH full row 0/91). |
| D4 (H-SPK-4, gap 0.20) | **separates**: 0.533 - 0.010 = 0.523 | Rules out "any ClinVar P/LP pair gets rank 1 under v4": unrelated-gene pairs reach rank 1 in 3/300, all through an overlapping phenotype-matched gene (LHX4, IDUA, DLL3). |
| D5 (H-SPK-5, v4 vs v3) | **harm** in stratum A: v4 0.533 vs v3 0.840; discordant pairs 9 (v4 only) vs 101 (v3 only); McNemar exact p = 7.8e-21 | H-SPK-5 falsified. The phenotype layer trades MVA-set recall for specificity: unrelated genes drop from 0.760 (v3) to 0.010 (v4). The loss comes from MVA genes that HPO does not annotate with the child's terms. |
| D6 (adoption gate) | pass (G1, S1-S3, N_A = 300) | EPCR vector proposed (Section 4). |
| D7 (EPCR_1 vs the BUB1B row) | **conservative**: A-BUB rank-1 recall 1.000 > 0.533 | Rules out that BUB1B's rank 1 depends on the child's specific alleles: 100/100 other BUB1B P/LP pairs rank 1 under v4 and v3. |

## 4. EPCR vector (stratum A, v4 with Amendment 1, Section 8 rule)

| row | draft gene | k_r / 300 | raw [Jeffreys 95%] | smoothed (k+0.5)/301 | isotonic | **EPCR** |
|---|---|---|---|---|---|---|
| 1 | BUB1B pair | 160 | 0.533 [0.477, 0.589] | 0.533223 | 0.533223 | **0.533223** |
| 2 | LZTR1 | 124 | 0.413 [0.359, 0.470] | 0.413621 | 0.413621 | **0.413611** |
| 3 | GNRHR | 0 | 0.000 [0.000002, 0.0083] | 0.001661 | 0.001661 | **0.001641** |
| 4 | POU6F2 | 0 | same | 0.001661 | 0.001661 | **0.001631** |
| 5 | EIF4EBP1 | 0 | same | 0.001661 | 0.001661 | **0.001621** |
| 6 | HRNR | 0 | same | 0.001661 | 0.001661 | **0.001611** |
| 7 | IGBP1 | 0 | same | 0.001661 | 0.001661 | **0.001601** |
| 8 | ADAMTS1 | 0 | same | 0.001661 | 0.001661 | **0.001591** |
| 9 | AGAP3 | 0 | same | 0.001661 | 0.001661 | **0.001581** |
| 10 | FOXO6 | 0 | same | 0.001661 | 0.001661 | **0.001571** |

- P(causal in top 10) = 284/300 = 0.947 [0.917, 0.968]. The 16 misses are all RNU4ATAC (non-coding).
- All values in (0, 1], strictly decreasing at 6 decimals. VERIFIED.
- Proposed CSV (box only): `TRACK1_SUBMISSION_EPCR_PROPOSED.csv` (sha256 5ab5827e...). The draft CSV is untouched.

Expected score under the scorer re-implementation (from SPACE_RULES_T1.md; NOT VERIFIED against evaluation.py):
- Over the 300 A trials: mean rank points 73.8 [70.3, 77.2], mean F-max 0.843 [0.815, 0.868] (2,000 bootstrap resamples, seed 1). Points: 100 in 159 trials, 50 in 125, 0 in 16.
- Rescoring with the ordinal vector (11 - r)/11 gives identical points and F-max in every trial. VERIFIED. With strictly decreasing EPCR the automated score does not depend on the magnitudes; the values only matter for what the methods text claims.
- On the actual draft rows with this vector: if the BUB1B pair is the answer, 100 points and F-max 1.0; if only the nonsense were the answer, 50 points and F-max 0.667.

## 5. Observation after the run (NOT a pre-registered result; the vector above is not changed by it)

The rank-2 mass (124 trials) is entirely MVA-set genes with HPO score 0 (plus 3 TRIM37 trials) sitting behind LZTR1 in the masked background. In the real ranking, row 2 is LZTR1 itself, a non-MVA gene with one heterozygous P/LP allele. A real causal of that kind would sit at rank 3, behind BUB1B and LZTR1. So EPCR_2 = 0.414 measures "the slot behind the strongest phenotype-matched tier-A gene", not the probability that LZTR1 is causal. Because the score ignores magnitudes, this affects only the wording: describe EPCR as a rank-slot calibration from spike-in. A row-conditional EPCR would need its own pre-registration.

## 6. Limits

- Ranking only: no reads simulated, no calling or phasing tested.
- Frequency for spikes comes from ClinVar's ExAC/ESP/1000G fields, not gnomAD v4.1 (optimistic direction; measured exposure small, Section 2).
- Gene-uniform sampling: EPCR_1 = 0.533 depends on the gene mix (5 of 13 sampleable genes have HPO score 0). Per-gene results above let a reader reweight.
- The scorer is re-implemented from a description of the code, not executed from it.
- ROW-MAP is still a draft rule (needs approval); it affects only the score simulation.

## 7. Files (box: `~/Documents/HACKATON/_private/agent_out/spikein/`)

PRE_REG_SPIKEIN_EPCR.md (+ .sha256), DEVIATIONS.md, RESULT.md, run.log, sanity.json, val_G1.json, feasibility.json, pools.tsv, trials.tsv, alleles.tsv, summary.json, TRACK1_SUBMISSION_EPCR_PROPOSED.csv; code: make_params.py, consequence_param.py (+ .diff), calls_param.py (+ .diff), spikelib.py, validate.py, run_spikein.py (b96c6787...), analyze.py (dfd4bddf...). Intermediate tables (masked_part*.tsv, bg_consequence.tsv, spike_*) contain child-derived rows and stay on the box. Mac copies: PRE_REG, .sha256, DEVIATIONS.md, RESULT.md only.
