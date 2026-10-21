# PRE-REG-ROWMAP (frozen 2026-10-20, written BEFORE any ROW-MAP trial is run)

- Public copy: lines that cite the authors' internal research notes are not reproduced. The frozen original's sha256 is recorded in the register (POINTER-ROWMAP).
- Status: frozen at the sha256 in `PRE_REG_ROWMAP.md.sha256`. Never edited after freezing. Departures go to `DEVIATIONS_ROWMAP.md`. Results are recorded whatever they are.
- Work dir (box): `~/Documents/HACKATON/_private/agent_out/rowmap/`. Child-derived data stays on the box. No network call of any kind. CPU only. Existing files are only read; the child VCF is never modified (sha256 checked before and after).

## 0. Question

The frozen ranking (v4 with Amendment 1) orders genes. The CSV holds up to 10 rows of one or two variants. ROW-MAP is the rule that turns a ranked gene's candidate calls into a row, and the construction is how rows are laid out. Which mechanical pair-selection rule and which row construction give the highest expected score under the organisers' scorer, when the causal gene also carries extra rare heterozygous calls so that the choice matters?

## 1. Known before freezing (stated so nothing is hidden)

- Spike-in calibration (PRE-REG-SPIKEIN-EPCR, sha256 6d40e58f..., RESULT.md, audit VERIFY.md): known in full, including per-gene hit ranks. In its trials the causal gene had only the spiked calls, so pair choice never mattered there.
- Scorer: `track1/scorer_check/evaluation.py`, git blob 2aed492247fc98be1b775e646f9b75aadec9e999 (matches Space commit 60e1c30e, checked today), sha256 6d18b581... Read in full. Facts used below: rows sorted by EPCR descending (ties keep file order); full match = row variant set equals the key; partial (half points) only when the key has two variants and no full match exists, at the first row sharing a variant; rank points 100 (rank 1), 50 (2-3), 25 (4-5), 10 (6-10); F-max at variant level over every distinct EPCR threshold.
- Real data, BUB1B gene interval (GENCODE v44 chr15:40,161,023-40,221,123), read-only listing of the child VCF (`bub1b_interval.py`, output not saved): 14 calls (8 heterozygous, one of them LowQual; 6 homozygous). Only the two calls of the submitted pair lie inside a protein-coding exon (distance 0); every other call is at least 905 bp from the nearest protein-coding exon of BUB1B. So the "third heterozygous call" is intronic, not coding, and is not a candidate call in our pipeline. VERIFIED.
- Real candidate calls of the draft top 10 (`track1/rank_calls_v4.tsv`, read): BUB1B 2 hets; LZTR1 1; GNRHR 1; POU6F2 3 hets (frameshift, missense, frameshift within 3 bp); EIF4EBP1 4 hets (missense, frameshift, missense, missense within 32 bp); HRNR 2; IGBP1 1 (chrX 1/1); ADAMTS1 2; AGAP3 1 (1/1); FOXO6 1 (1/1). AlphaMissense values of these calls were NOT looked up before freezing.
- Draft rule R0 = TRACK1_METHODS_ADDITIONS.md section 7 as implemented in `spikein/spikelib.py:row_map` (with the fill-in logged in PRE-REG-SPIKEIN-EPCR section 7). Current CSV: `track1/TRACK1_SUBMISSION_FINAL_PROPOSED.csv` (sha256 a6527da7...).
- Decoy feasibility, PUBLIC ClinVar only, no child data, no ranking, no consequence step (`feasibility_decoy.py` -> `feasibility_decoy.json`): autosomal non-P/LP records with a coding ClinVar MC term and no ClinVar AF >= 0.001, per SET18 gene: PCNT 1845, BUB1B 1502, CEP57 619, CENPF 595, CEP192 347, TRIM37 231, ESCO2 208, SLF2 162, MAD1L1 129, SMC5 124, TRIP13 82, CENATAC 73, CDC20 58, SNRNP48 48, MAD2L1BP 37; ZRSR2 (chrX), RNU4ATAC, RNU6ATAC 0.
- Base-trial gene mix (from spike-in `trials.tsv`): stratum A has 8 RNU4ATAC CH and 8 RNU4ATAC HOM trials and 5 ZRSR2 HOM trials; stratum E covers 278 distinct genes in 300 trials.
- No ROW-MAP trial, no rule-on-trial computation and no AlphaMissense lookup ran before this file was frozen.

## 2. Hypotheses

- H-RM-1 (primary): on trials where a compound-heterozygous causal gene also carries 1 or 2 rare heterozygous decoys, some mechanical rule x construction gives a higher mean rank points than R0 x C1 by at least the margin (Section 8).
- H-RM-2: rules that use a per-variant score (P2, P3, P5) choose the exact causal pair more often than R0 and P1.
- H-RM-3: C3 (alternate pairs) scores at least as high as C1 on compound-heterozygous decoy trials; C2 (halves) cannot raise rank points there (a pair row sharing one true allele already earns the same half credit at a better rank).
- H-RM-4: with a homozygous causal plus a heterozygous decoy, R0 and P1 lose the causal row (R0 pairs the homozygous allele with the decoy; P1 drops homozygous calls when a het exists); P2, P3, P5 keep it.
- H-RM-5 (real data): no rule changes row 1 (BUB1B pair).

## 3. Inputs (read-only; hashes checked at run start, run aborts on mismatch)

| input | path (box) | sha256 prefix |
|---|---|---|
| frozen ranking library (v3/v4 logic, Amendment 1, R0) | agent_out/spikein/spikelib.py | c64c87cf |
| extraction step (work copy) | agent_out/spikein/calls_param.py | 33cc8270 |
| consequence step (work copy) | agent_out/spikein/consequence_param.py | 5c1d37d1 |
| masked background consequence table | agent_out/spikein/bg_consequence.tsv | ffbb969d |
| spiked-allele consequence rows, visible and hidden modes | agent_out/spikein/spike_cons_visible.tsv, spike_cons_hidden.tsv | d31406ec, 81edfe45 |
| base trials (allele sets, genotype type, gene) | agent_out/spikein/trials.tsv | 9b669a72 |
| P/LP pool | agent_out/spikein/pools.tsv | 90e82fb9 |
| organisers' scorer, unmodified | agent_out/track1/scorer_check/evaluation.py | 6d18b581 (git blob 2aed4922) |
| current CSV | agent_out/track1/TRACK1_SUBMISSION_FINAL_PROPOSED.csv | a6527da7 |
| unmasked consequence table (real data) | blind_gnomad/child_exonic_consequence_fixed.tsv | as in spike-in G1 |
| ClinVar GRCh38 2026-10-11 | blind_gnomad/clinvar.vcf.gz | 05d9481d |
| AlphaMissense hg38 | models/protein/alphamissense/AlphaMissense_hg38.tsv.gz | recorded in run log |
| child VCF (not read by the trials; hash before and after) | data/WGS_EX2312012_HGWCNDSX7.vcf.gz | bec64c68 |

`spikelib.py` is imported from its folder (it writes nothing). `calls_param.py` and `consequence_param.py` are run as subprocesses with input and output paths inside the rowmap work dir; they write only their output argument.

## 4. Trials

4.1 Base trials. Reuse the spike-in trials exactly (allele sets from `trials.tsv`, genotypes CH = each allele 0/1, HOM = one allele 1/1; consequence rows from `spike_cons_visible.tsv` or `spike_cons_hidden.tsv`; background `bg_consequence.tsv`, i.e. the child's call set with the two BUB1B calls masked). Strata used: A (SET18, seeds 101/102), A-BUB (other BUB1B P/LP pairs, seed 103), E (AR genes with HPO score >= 1, seeds 501/502).

4.2 Decoy pool (public ClinVar). Record: one ALT; REF and ALT only A/C/G/T, length 1 to 50; chromosome 1-22; GENEINFO present; final CLNSIG under the v3 lookup semantics (last record in file order wins) in {Uncertain_significance, Conflicting_classifications_of_pathogenicity, Conflicting_interpretations_of_pathogenicity, Likely_benign, Benign, Benign/Likely_benign}; key not in the child's exonic call table and not one of the two BUB1B keys; a GENEINFO gene is a base-trial gene. These records go through `calls_param.py` (extraction, exons +/-3 bp) and `consequence_param.py` with visible-mode frequency (gnomad_status `found` with AF = AF_EXAC, else AF_ESP, else AF_TGP; no AF field gives `absent_site`), exactly as spiked alleles were treated. Decoy pool D(g) = keys whose first consequence row has gene column == g, consequence in the candidate set {nonsense, frameshift, stop_lost, missense, inframe_indel, splice_region} and class rare or unobserved; sorted by (chrom, int pos, ref, alt).

4.3 Decoy draws. Per stratum, `random.Random(seed)`, base trials in `trials.tsv` order (v4 lines). A trial is decoy-eligible if its sampled gene is autosomal and |D(g)| >= 1; otherwise it is skipped without consuming random numbers. If |D(g)| >= 2: draw `r.sample(D(g), 2)`; the d = 1 trial uses the first, the d = 2 trial uses both. If |D(g)| = 1: d = 1 only. Decoys are written 0/1 (cis or trans unknown; the pipeline does not phase). Seeds: A 601, E 602, A-BUB 603. Decoy ClinVar labels stay visible (they are non-P/LP by construction). Decoys are never part of the answer key.

4.4 Strata of this test.

| stratum | base | decoys | ClinVar of causal | role | expected N |
|---|---|---|---|---|---|
| A-CH-dec | A, CH | d = 1, 2 | visible | PRIMARY (part 1) | about 384 |
| E-CH-dec | E, CH | d = 1, 2 | visible | PRIMARY (part 2) | about 400 |
| A-HOM-dec, E-HOM-dec | A, E, HOM | d = 1, 2 | visible | secondary (homozygous handling) | about 174, 200 |
| A-BUB-dec | A-BUB | d = 1, 2 | visible | secondary (P4 template) | about 200 |
| A-hid-dec | A-dec trials (CH and HOM) | same decoys | hidden, frequency absent (spike-in B mode) | secondary (novel causal) | about 558 |
| d0 | A, A-BUB, E | none | visible | control (sanity S-R2) | 700 |

N >= 200 holds for each primary stratum; if a primary stratum falls below 200 the result is reported with that N and labelled underpowered.

4.5 Per trial. Background rows, then causal rows (trial genotype in the gt column), then decoy rows; `seen.setdefault` keeps the first row per allele (as v3). Candidate calls by the v3 filters, v3 tiers, v4 order with Amendment 1 (`spikelib.v3_candidates`, `rank_v3`, `rank_v4`). ClinVar lookup with v3 semantics over background candidate keys, all causal keys, all decoy keys and the two BUB1B keys (one file scan, a key's value does not depend on the key set); hidden mode removes the trial's causal keys. The gene ranking is the same for every rule and construction; only the rows differ.

## 5. Pair-selection rules (each maps one gene's candidate-call list to a row of 1 or 2 variants)

Common per-variant terms. T(v) = 1 if consequence is nonsense or frameshift, else 0. s(v) = 1.0 for nonsense or frameshift; for missense the maximum AlphaMissense am_pathogenicity over AlphaMissense rows with the same chrom, pos, ref, alt (0.5 if none); 0.5 for splice_region, inframe_indel, stop_lost (no AlphaMissense value exists; 0.5 is a fixed, arbitrary middle value). pk(v) = (int pos, ref, alt). K(v) = (-T(v), -s(v), pk(v)), sorted ascending. hom(v) = genotype 1/1. ESM is not used (AlphaMissense is precomputed and offline; ESM would need fresh model runs).

| code | rule (mechanical) |
|---|---|
| R0 | Draft ROW-MAP as frozen in `spikelib.row_map`: 1 call -> single; 2 calls -> pair (genotype ignored); more than 2 -> highest-weight LoF-type call (nonsense, frameshift weight 3, then splice_region 2; ties lowest position) + lowest-position missense; fill-in if no LoF-type or no missense: first two by (-v3 weight, position) |
| P1 | Consequence/genotype filter. Keep heterozygous calls. If >= 1 het: sort by (impact, pk) with impact HIGH = {nonsense, frameshift, splice_region, stop_lost} before MODERATE = {missense, inframe_indel}; take the first two (one if one). Tie behaviour when more than two survive: HIGH first, then lowest position (what a "first two after filtering" script does). If no het: single = lowest-pk homozygous call |
| P2 | Top two hets by a fixed sort key; a homozygote wins outright. If any homozygous call: single = min by K. Else the two hets with smallest K (one if one) |
| P3 | Score every hypothesis, keep the best by the weaker allele. Hypotheses: every pair of distinct het calls, and every single homozygous call. Score = min s over its alleles; ties by larger max s, then smaller sorted pks. If no hypothesis (one het, no hom): that het as a single |
| P4 | MVA1 template, else P3. Template applies only to BUB1B, the only gene with a kinase-domain annotation available offline (UniProt O60566 protein kinase domain 766-1050; UNVERIFIED against UniProt, no network). If the gene has >= 1 truncating het (T = 1) and >= 1 missense het whose AlphaMissense O60566 residue lies in 766-1050: pair = min-K truncating het + min-K in-domain missense het. Otherwise P3 |
| P5 | ClinVar P/LP anchor + highest-scoring partner. Anchors = calls whose ClinVar P/LP is visible to the ranker in that trial. If none: P2. Else anchor = min-K anchor; if the anchor is homozygous: single anchor; else partner = min-K het among the other calls (ClinVar not used for the partner); no other het: single anchor |

Excluded: hand pairing (P7), tool-decides (P6, needs Exomiser, not offline here), oracle use (P8).

## 6. Row constructions (applied to the ranked genes in v4 order)

- C1: one row per gene, genes ranked 1 to 10, row = the rule's row.
- C2: C1, then after the lead pair row (the first C1 row holding two variants) insert its two halves as single rows, ordered by K; truncate to 10 rows. No pair row in the top 10: C2 = C1.
- C3: C1, then if the lead pair's gene has >= 3 heterozygous candidate calls: c = min-K het not in the pair; insert after the lead pair the alternates {a, c} and {b, c}, where a is the min-K allele of the pair; truncate to 10 rows. Otherwise C3 = C1.
- The lead pair in the real data is row 1 (BUB1B). Halves and alternates are inserted directly below it.

EPCR for every construction (frozen spike-in rule applied by final row position): the row at final position r (after insertion and truncation) gets e_r of the frozen vector 0.533223, 0.413611, 0.001641, 0.001631, 0.001621, 0.001611, 0.001601, 0.001591, 0.001581, 0.001571 (strictly decreasing, distinct; fewer rows take the first n values). Under C1 this is the spike-in assignment. Under C2 and C3 an inserted row takes the value of its position, which keeps values strictly decreasing and distinct; it is then an ordinal label, not the spike-in rank-slot probability, and the methods must say so if C2 or C3 is adopted. The score depends only on row order (spike-in RESULT, verified), so the choice of magnitudes cannot change any score here.

## 7. Scoring and outcomes

- Each trial x rule x construction: rows written to a CSV in the template format (proband PROBAND01, `chr`-prefixed chrom, finding_type primary), loaded with `evaluation.load_submission`, scored with `evaluation.score_proband` against the synthetic key = the spiked causal set (two variants for CH, one for HOM). Unmodified scorer, imported from its file.
- Outcomes: rank points; F-max; row1_exact (final row 1 variant set == key); causal_row_exact (the rule's row for the highest-ranked gene holding a causal allele == key, a pair-choice diagnostic independent of rank); full and partial match ranks.
- 6 rules x 3 constructions = 18 combinations; 17 comparisons with R0 x C1.

## 8. Statistics and decision rule (fixed now)

- Primary population PRIM = A-CH-dec and E-CH-dec, both decoy levels, every trial weighted equally.
- Estimand: mean rank points of each combination over PRIM, and the paired difference Delta_X = mean(points_X - points_R0C1).
- Intervals: stratified gene-cluster bootstrap (clusters = sampled gene within stratum, resampled with replacement within A and within E separately; all trials of a resampled gene, both decoy levels, come along), 10,000 resamples, numpy default_rng(1). 95% percentile intervals for means and differences; for the adoption gate the two-sided 1 - 0.05/17 level (percentiles 0.147 and 99.853). Trial-level counts of wins and losses against R0 x C1 are reported. P(row 1 exact) with Jeffreys 95% intervals (trial level) and the cluster interval.
- Winner W = combination with the highest mean rank points on PRIM; ties go to the simpler one, lexicographic (construction C1 < C2 < C3, then rule R0 < P1 < P2 < P5 < P3 < P4).
- D-RM-1 (adoption). Adopt W if all three hold: (a) Delta_W >= 2.0 rank points (margin); (b) the 1 - 0.05/17 gene-cluster lower bound of Delta_W > 0; (c) Delta_W >= 0 in A-CH-dec and in E-CH-dec separately. Otherwise keep R0 x C1. If W is not adopted because (b) or (c) fails while (a) holds, the outcome is labelled "inconclusive", not "equivalent".
- D-RM-2 (secondary, not binding: best rule if hedge rows are ruled out by policy). Same gate, restricted to the 6 C1 combinations.
- D-RM-3 (real data). Every combination is applied to the real, unmasked v4 ranking. Reported: whether row 1 changes (H-RM-5) and which of rows 2-10 change. If D-RM-1 adopts W, the real rows under W are written to `TRACK1_SUBMISSION_ROWMAP_PROPOSED.csv` on the box (EPCR by Section 6, notes in the draft style); the current CSV is not edited. If R0 x C1 is kept, no CSV is written.
- F-max is reported for every combination and is not part of the decision.

Falsifiers, per outcome.
- Outcome "adopt W": the claim is that W beats R0 x C1 on decoy trials. It is contradicted inside this test by gate (b) or (c). Cross-checks reported with it: if Delta_W <= -2.0 in A-hid-dec or in either HOM-dec stratum, W is flagged "helps only with visible ClinVar" or "harms homozygous causals"; the decision stands but the methods must state the flag.
- Outcome "keep R0 x C1, no material gain" (Delta_W < 2.0): contradicted by any combination with Delta >= 2.0 in a larger rerun of the same design; this test claims only that no gain >= 2.0 points is seen at this N.
- Outcome "inconclusive": no claim either way beyond the reported intervals.
- H-RM-5 is falsified if any combination changes the variant set of real row 1 or moves it from row 1.

## 9. Sanity checks (after freezing, before the trials; the run stops if S-R1 to S-R5 fail)

- S-R1: base-trial allele sets from `trials.tsv` equal sets regenerated from `pools.tsv` with seeds 101, 102, 103, 501, 502 and the spike-in sampling code (strata A, A-BUB, E).
- S-R2: d0 trials reproduce the spike-in v4 hit rank and hit gene of every A, A-BUB and E trial.
- S-R3: on the real data, the v4 top 10 equals the CSV genes and R0 x C1 rows equal the variant sets of the current CSV in 10 of 10 rows; my CSV writer plus `evaluation.py` with key = row 1 gives 100 points and F-max 1.0 (as `check_final_csv.out`).
- S-R4: scorer git blob 2aed4922... and sha256 6d18b581...; all input hashes of Section 3.
- S-R5: in d0, all six rules give the same causal row for every trial whose causal gene has <= 2 candidate calls and no homozygous-plus-het mix.
- Reported, not a gate: fraction of drawn decoys that are candidate calls of the causal gene in their trial (a decoy can be removed by the cluster filter).

## 10. Predictions (written now)

- P-a (real data): row 1 is the BUB1B pair under all 18 combinations. C3 = C1 on the real data (BUB1B has two coding hets, so no alternate exists). C2 inserts the two BUB1B halves at rows 2 and 3 and pushes LZTR1 to row 4; AGAP3 and FOXO6 fall out.
- P-b (real data): row 4 (POU6F2) changes under P1, P2, P3, P4, P5 (the two frameshifts are chosen instead of frameshift + missense). Row 5 (EIF4EBP1) is unchanged under P1; under P2, P3, P4, P5 it changes only if the highest-AlphaMissense missense is not the lowest-position one. Rows 6 and 8 (two calls each) and single rows never change.
- P-c (PRIM): causal_row_exact is higher for P2, P3, P5 than for R0 and P1. C3 >= C1 >= C2 in mean rank points. Predicted W = an AlphaMissense-using rule (P2, P3 or P5) with C3, Delta_W >= 2.0.
- P-d (HOM-dec): R0 and P1 get 0 rank points in most trials; R0 x C2 recovers part of it (the homozygous allele alone as a half row gives a full match lower down).
- P-e (A-BUB-dec): P4 <= P3, because the template forces a missense partner even when both causal alleles are truncating.
- P-f (A-hid-dec): rank points are low for every combination (causal mostly at ranks 3 to 10); C2 and C3 cost points there when the lead pair is a background gene above the causal (POU6F2 or EIF4EBP1).

## 11. Outputs

Box work dir: `decoy_pool.tsv`, `decoy_*` intermediate tables, `trials_rowmap.tsv` (one line per trial x combination), `real_rows.tsv` (real-data rows per combination; coordinates, box only), `sanity_rowmap.json`, `summary_rowmap.json`, `run_rowmap.log`, `RESULT_ROWMAP.md`, `DEVIATIONS_ROWMAP.md` if any, `TRACK1_SUBMISSION_ROWMAP_PROPOSED.csv` only under Section 8 D-RM-3. Mac copies (`$S/agent_out/rowmap/`): PRE_REG_ROWMAP.md, its .sha256, RESULT_ROWMAP.md, DEVIATIONS_ROWMAP.md if any. The Mac copies name genes and classes, never child coordinates.

## 12. Limits stated now

- Ranking and row building only; no reads, calling or phasing. Decoys are public ClinVar non-P/LP alleles, not the child's own extra calls; their consequence mix and AlphaMissense distribution may differ from a real child's passenger hets.
- Causal alleles are ClinVar P/LP, which are enriched for high AlphaMissense; this favours AlphaMissense-using rules relative to a truly novel causal. A-hid-dec does not remove that (AlphaMissense is a ClinVar-independent score but trained against benign-labelled variation), so the gain of score-based rules may be optimistic.
- Gene-uniform sampling as in the spike-in. The kinase-domain boundary for P4 is from public secondary sources only.
- The decision is about expected scores over the trial population, not about this child's answer, which the scorer already credits in full if the BUB1B pair is the key (row 1 is unchanged by prediction P-a).
