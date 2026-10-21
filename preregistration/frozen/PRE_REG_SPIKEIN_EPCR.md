# PRE-REG-SPIKEIN-EPCR (frozen 2026-10-20, written BEFORE any spiked ranking is run)

- Written: 2026-10-20T09:06Z (18:06 JST) by agent spikein-epcr (Claude Opus 5.5) for team-lead. The user chose "measure it with spike-in".
- Status: frozen at the sha256 recorded in PRE_REG_SPIKEIN_EPCR.md.sha256. Not edited after freezing. Deviations go to DEVIATIONS.md in the same folder.
- Work dir (box): `~/Documents/HACKATON/_private/agent_out/spikein/`. Child-derived data stays on the box. No network calls of any kind in this task.

## 0. Purpose

Spike known causal events (public ClinVar Pathogenic/Likely_pathogenic alleles) into the child's own background call set with the real BUB1B pair removed, rerun the frozen ranking, and record where the spiked causal lands. The empirical rank distribution in the primary stratum becomes the EPCR value of each of the 10 Track 1 draft rows. This replaces the ordinal proposal in `agent_out/track1/PRE_REG_EPCR_DRAFT.md` (never approved) with a measured value.

The test checks ranking, not calling: no reads are simulated, spiked genotypes are written directly.

## 1. What is known before freezing (stated so nothing is hidden)

- Gate G1 (code equivalence) was run BEFORE freezing on the real, unspiked data, with no spike-in. Result, all VERIFIED (`val_G1.json`):
  - `consequence_param.py` on the original part tables reproduces `child_exonic_consequence_fixed.tsv` byte for byte.
  - `calls_param.py` round-trips 6,000 rows of `child_exonic_calls.tsv` (first and last 3,000) unchanged, header included.
  - `spikelib.py` reproduces `ranking_v3_summary_fixed.tsv` and `ranking_v4_summary_fixed.tsv` byte for byte (v4 without Amendment 1, as that script runs).
  - With Amendment 1, the top 10 is BUB1B, LZTR1, GNRHR, POU6F2, EIF4EBP1, HRNR, IGBP1, ADAMTS1, AGAP3, FOXO6, and ROW-MAP rows equal the variant content of `TRACK1_SUBMISSION_DRAFT.csv` exactly.
- Public gene properties computed before freezing (`feasibility.json`, ClinVar + HPO only, no child data): ClinVar P/LP pool sizes and v4 phenotype scores of the 18-gene set (Section 11).
- Background structure known from the frozen v4 output: without BUB1B, tier A holds LZTR1 (pheno 1, v2 3.0) and GNRHR (pheno 0, v2 1.0); tier B holds POU6F2 (v2 7), EIF4EBP1 (6), HRNR (4), all pheno 0.
- The exonic call table has exactly two rows in chr15:40,150,000-40,230,000: the two BUB1B calls (VERIFIED by listing).

## 2. Hypotheses

- H-SPK-1 (primary, recall robustness): under v4 with Amendment 1, a biallelic ClinVar P/LP event in the project's MVA/phenocopy gene set lands at rank 1 in at least 80% of trials.
- H-SPK-2 (novel variant): with the spiked alleles' ClinVar labels hidden from the ranker and no frequency record, the same events still reach the top 10 in at least 50% of trials.
- H-SPK-3 (stop_lost): the consequence step never labels a stop-loss allele `stop_lost` (known limitation: GENCODE CDS features exclude the stop codon). Measured, not assumed.
- H-SPK-4 (control): for recessive genes unrelated to the phenotype (HPO score 0), rank-1 recall is at least 0.20 lower than in the primary stratum.
- H-SPK-5 (v3 cross-check): v4 rank-1 recall exceeds v3 rank-1 recall in the primary stratum (paired trials).

## 3. Data (all local, read-only)

| input | path | sha256 |
|---|---|---|
| child VCF (not read by this test; hash checked before and after) | data/WGS_EX2312012_HGWCNDSX7.vcf.gz | bec64c68...42175 |
| child exonic calls with frequency (the call set) | blind_gnomad/child_exonic_gnomad_exomes.part0-3.tsv | 9089795834..., 2b547723..., ef59ab45..., 8ac870cb... |
| ClinVar GRCh38, fileDate 2026-10-11 | blind_gnomad/clinvar.vcf.gz | 05d9481d... |
| HPO | blind_gnomad/hp.obo, genes_to_phenotype.txt | 93dace95..., 507a17bf... |
| GENCODE v44 basic GTF, GRCh38 analysis-set FASTA | as in consequence_fixed.py | |
| frozen scripts | consequence_fixed.py c64e8f56...; ranking_v3_fixed.py e32e2ec1...; ranking_v4_fixed.py f906b4d3...; ranking_v4b.py 28fb677b...; analysis_scripts/child_exonic_calls.py fdeacbcb... | |
| work copies | consequence_param.py 5c1d37d1...; calls_param.py 33cc8270...; spikelib.py c64c87cf... | |

gnomAD v4.1 sites files are not on the box and no network is used, so the frequency step for spiked alleles is replaced (Section 4.2).

## 4. Pipeline per trial (identical to the real path except the frequency source of spiked alleles)

4.1 Background. Copy of the four part tables with the two BUB1B rows removed (chr15:40209701 T>G, chr15:40220612 T>G), run through `consequence_param.py`. Every step is row-wise, so this equals running the pipeline on a VCF copy with the two calls masked (checked by S2).

4.2 Spiked alleles, extraction then frequency.
- Extraction: spiked alleles are written to a VCF (FILTER PASS, GT 0/1) and passed through `calls_param.py`. An allele outside protein-coding exons +/-3 bp drops out exactly as a real call would.
- Frequency (forced deviation from the real path): visible mode, AF = AF_EXAC if present, else AF_ESP, else AF_TGP, written as gnomad_status `found` with that AF; no AF field gives `absent_site`. Hidden (novel) mode and synthetic alleles: `absent_site`. The class is then set by the unchanged consequence_fixed.py code: unobserved (absent or AF 0), rare (AF < 0.001), common_or_low (AF >= 0.001, not a candidate).
- Bias of this choice: ExAC, ESP and 1000G are smaller and older than gnomAD v4.1 exomes. An allele with no AF field becomes unobserved, which rule v3 treats exactly like rare (both pass), so frequency can only remove a spike when AF >= 0.001 in those cohorts. A P/LP allele with gnomAD v4.1 AF >= 0.001 and no ClinVar AF field passes here and would fail in the real pipeline. Direction: optimistic (recall over-estimated). Expected size small: of 320,170 eligible ClinVar P/LP records, 18,196 carry an AF field and 106 have AF >= 0.001 under this rule. The number of sampled spikes with an AF field is reported.

4.3 Consequence. `consequence_param.py` (consequence_fixed.py with only the input glob and output path changed; diff saved) is run once over all distinct spiked alleles per frequency mode. A row's consequence does not depend on other rows, so the per-trial table is the masked background rows followed by the trial's spiked rows with the trial genotype written into the gt column.

4.4 Ranking. `spikelib.py`, logic copied from ranking_v3_fixed.py and ranking_v4_fixed.py (G1 equivalence above).
- Amendment 1 is applied as ranking_v4b.py implements it (genes named MT-* skipped when the v4 step loads tiers).
- Technical bug fix, logged here: ranking_v4_fixed.py omits the Amendment 1 line that ranking_v4b.py has, so its output carries MT-ATP6, MT-CYB and MT-ND2 at ranks 7, 9 and 10 (VERIFIED in G1). Every v4 run in this test applies Amendment 1 as the frozen rule is written. The rule is unchanged.
- v3 runs as rule v3 is written (no chrM amendment exists for v3; MT genes sit at v3 ranks 49 to 51).
- ClinVar lookup: same semantics as ranking_v3_fixed.py (exact chrom/pos/ref/alt, any alt of a record, last record in file order wins), computed once over the union of background candidate keys and all spiked keys. Hidden mode removes the trial's spiked keys from the lookup.
- Spiked rows are appended after background rows; `seen.setdefault` keeps the first transcript row per allele, as in v3.

4.5 Found while building, before freezing (not deviations): `blind_gnomad/child_exonic_calls.py` (0589ccd3...) does not parse under Python 3.13 (escaped quotes inside an f-string expression) and writes the header `gene`; the table on disk has the header `genes`, which matches `analysis_scripts/child_exonic_calls.py` (fdeacbcb...). That copy is the one used.

## 5. Spike pools (public ClinVar only)

- Eligible record: one ALT; REF and ALT only A/C/G/T, length 1 to 50; chromosome 1-22 or X; GENEINFO present; and the key's final CLNSIG under the v3 lookup semantics is exactly Pathogenic, Likely_pathogenic or Pathogenic/Likely_pathogenic (rule v3's is_plp). A record joins the pool of every gene symbol in its GENEINFO.
- Exclusions: every key present in the child's exonic call table (this includes the child's BUB1B nonsense chr15:40209701 T>G) and, explicitly, the child's BUB1B missense chr15:40220612 T>G.
- SET18 = the P2 phenocopy and MVA set (p2_sweep.py): RNU4ATAC, RNU6ATAC, ZRSR2, SNRNP48, ESCO2, PCNT, CENPF, BUB1B, TRIP13, CEP57, SMC5, MAD1L1, CEP192, TRIM37, CDC20, MAD2L1BP, CENATAC, SLF2. Genes with empty pools cannot be sampled and are listed.
- AR = genes annotated HP:0000007 (autosomal recessive inheritance) in genes_to_phenotype.txt.
- Phenotype score = the v4 score (child terms matched through is_a closure).

## 6. Strata, trial unit, N

- Trial unit: one spiked causal event (one biallelic genotype in one gene) added to the masked background; the full ranking is rerun. P(row r is causal) is estimated as the fraction of trials whose spiked causal lands at rank r.
- Genotypes: CH = two distinct alleles of one gene, each 0/1 (phase is not represented; the pipeline does not phase). HOM = one allele 1/1. chrX non-PAR alleles are spiked 1/1 only (male child, hemizygous), never CH.
- Sampling: Python `random.Random(seed)`; gene drawn uniformly from the alphabetically sorted eligible gene list, then allele(s) uniformly from the gene's pool sorted by (chrom, pos, ref, alt); without replacement within a trial, with replacement across trials.

| stratum | role | genes | design | seed | N |
|---|---|---|---|---|---|
| A | PRIMARY, sets EPCR | SET18 | 200 CH (autosomal genes with >= 2 pool alleles) + 100 HOM (genes with >= 1 allele, X included) | 101, 102 | 300 |
| A-BUB | secondary | BUB1B other alleles | 100 CH | 103 | 100 |
| B | novel variant, paired | same trials as A | ClinVar hidden for spiked alleles, frequency absent | (A) | 300 |
| C1 | stop_lost, ClinVar | any gene | pool alleles that are SNVs with ClinVar MC containing "stop_lost"; up to 100 drawn without replacement, each 1/1 alone; ClinVar visible | 301 | <= 100 |
| C2-HOM | stop_lost, synthetic | SET18 genes with an Ensembl_canonical protein-coding transcript | every SNV at the 3 GENCODE stop_codon positions that turns the stop into a sense codon (strand-aware, ref from FASTA), each 1/1 alone; ClinVar hidden, frequency absent | none | enumerated |
| C2-CH | stop_lost, synthetic + partner | same, autosomal genes with >= 1 pool allele | each synthetic allele 0/1 plus one ClinVar P/LP partner 0/1 from the gene's pool (partner visible) | 302 | enumerated |
| D | control | AR genes, phenotype score 0, autosomal, not in SET18 | 200 CH (>= 2 alleles) + 100 HOM | 401, 402 | 300 |
| E | secondary | AR genes, phenotype score >= 1, autosomal, not in SET18 | 200 CH + 100 HOM | 501, 502 | 300 |

A-pc (secondary, no new trials): the subset of A trials in genes with an Ensembl_canonical protein-coding transcript in GENCODE v44.

## 7. Outcomes per trial (v4 with Amendment 1, and v3)

- Hit rank r (primary outcome): the smallest rank of a ranked gene whose candidate calls (after the v3 filters) include at least one spiked allele; "none" if there is no such gene.
- Full row: the ROW-MAP row of that gene equals the spiked allele set exactly (scorer full credit). Half row: shares at least one allele.
- Per-allele diagnostics: passes extraction; consequence class; frequency class; candidate after filters; ClinVar P/LP visible to the ranker.
- ROW-MAP is the draft rule in TRACK1_METHODS_ADDITIONS.md section 7. Fill-in for cases it does not cover (more than 2 calls with no LoF-type or no missense call): the first two calls by (-v2 weight, position). It affects the score simulation only.

## 8. EPCR derivation (stratum A, v4 with Amendment 1)

- k_r = number of A trials with hit rank r, r = 1..10; N = 300 (every A trial, including trials with no hit).
- Smoothed: s_r = (k_r + 0.5) / (N + 1) (Jeffreys posterior mean, Beta(0.5, 0.5) prior), so no value is 0.
- Monotone: iso_r = isotonic non-increasing fit of s_1..s_10 (pool-adjacent-violators, equal weights).
- Strict decrease (tie handling): e_r = iso_r - 1e-5 x (r - 1), rounded to 6 decimals. Check: every e_r in (0, 1] and strictly decreasing after rounding; if not, 7 decimals.
- Row r of the draft (v4 with Amendment 1 order, which the draft already follows) gets e_r. Row 1 EPCR is therefore the smoothed empirical probability that the causal lands at rank 1.
- Intervals: Jeffreys 95% equal-tailed interval for each k_r / N (Beta(k_r + 0.5, N - k_r + 0.5) quantiles 0.025 and 0.975), and for P(top 10) = sum k_r / N.
- Expected score: each A trial's v4 top-10 ROW-MAP rows get e_1..e_10 and are scored against that trial's spiked set by the scorer re-implementation (sort by EPCR descending, ties keep file order; rank points 100 / 50 / 25 / 10, half for a row sharing one variant; F-max over every distinct EPCR threshold at variant level). Report mean rank points, mean F-max, and 2.5/97.5 percentile bootstrap intervals (2,000 resamples, seed 1). Check: rescoring with the ordinal vector (11 - r) / 11 gives identical scores (with strictly decreasing EPCR the score cannot depend on the magnitudes). The scorer is re-implemented from SPACE_RULES_T1.md, not from evaluation.py: NOT VERIFIED against the code.

## 9. Decision rules (fixed now)

- D1 (H-SPK-1). p1 = k_1 / N in A with Jeffreys 95% interval [lo, hi]. "Recall-robust" if p1 >= 0.80 and lo >= 0.70. "Not recall-robust" if p1 < 0.50. Otherwise "partly robust". Falsifier: p1 < 0.80.
- D2 (H-SPK-2). Top-10 recall in B, t10. t10 >= 0.50: "finds MVA-gene causals without ClinVar". t10 < 0.50: "depends on ClinVar". Rank-1 recall in B is reported. Falsifier: t10 < 0.50.
- D3 (H-SPK-3). Any C1 or synthetic C2 allele labelled stop_lost falsifies the known-limitation statement. If the stop-loss allele itself is a ranked candidate in fewer than 10% of C1 + C2 trials, the methods report must list stop_lost as a blind spot.
- D4 (H-SPK-4). "Phenotype layer separates" if p1(A) - p1(D) >= 0.20. Falsifier: difference < 0.20.
- D5 (H-SPK-5). Paired v4 vs v3 rank-1 hits in A, McNemar exact two-sided p. "v4 improves rank-1 recall" if p1(v4) - p1(v3) >= 0.05 and p < 0.05; "harm" if p1(v4) < p1(v3) with p < 0.05; otherwise "no detectable difference".
- D6 (EPCR adoption gate). The Section 8 vector is proposed for the CSV only if G1 passed, S1 to S3 pass and N_A >= 50. Otherwise no vector is proposed.
- D7 (fit of EPCR_1 to the BUB1B row). If A-BUB rank-1 recall >= p1(A), EPCR_1 from A is conservative for the BUB1B row; if lower, optimistic. Reported; the vector is not changed by it.

## 10. Sanity checks (not results), run after freezing and before the spiked trials

- S1: the masked background has no row at chr15:40209701 T>G or chr15:40220612 T>G, no BUB1B candidate call, and BUB1B is absent from the v3 and v4 rankings. (No other BUB1B row exists in the call table.)
- S2: the masked consequence table equals the original consequence table minus the rows of those two calls (line-level equality).
- S3: adding back the two original BUB1B rows (real frequency, real genotypes) returns BUB1B to v4 rank 1 and v3 rank 1, and the full v4 (Amendment 1) order equals the unspiked amended order.
- The child VCF sha256 is checked before and after the run.

## 11. Predictions (written now, from the frozen rule's arithmetic and public gene properties)

- v4 phenotype scores, SET18: RNU4ATAC 4, RNU6ATAC 3, BUB1B 3, CEP57 3, ZRSR2 2, ESCO2 2, TRIP13 2, PCNT 1, MAD1L1 1, TRIM37 1, CENPF 0, SMC5 0, CDC20 0, CENATAC 0, SLF2 0, SNRNP48 0, CEP192 0, MAD2L1BP 0.
- Pre-freeze pool sizes (single-gene GENEINFO only; the run uses any listed gene, so counts can grow): PCNT 382, ESCO2 156, TRIM37 114, CENPF 83, BUB1B 74 (before excluding the child's allele), CEP57 18, CDC20 11, TRIP13 9, MAD1L1 8, SLF2 8, ZRSR2 6, SMC5 5, CENATAC 2; RNU4ATAC, RNU6ATAC, SNRNP48, CEP192, MAD2L1BP 0.
- A: a spiked tier-A gene outranks LZTR1 (pheno 1, v2 3.0) only if its pheno >= 2, or pheno 1 with v2 > 3 (or v2 = 3 and a name sorting before LZTR1). Predicted p1(A) about 0.4 to 0.6, below the 0.80 bar: rank 1 in this pipeline needs a strong HPO match, which BUB1B has and several MVA genes lack. Pheno-0 genes predicted mostly at rank 2. Non-coding RNU4ATAC/RNU6ATAC alleles, if any enter the pools, predicted unrankable (outside protein-coding exons).
- A-BUB: predicted p1 close to 1 among trials whose alleles pass the filters; misses come from deep intronic or synonymous-labelled alleles.
- B: predicted p1 near 0 (LZTR1 and GNRHR keep tier A); LoF + missense CH can reach tier B, so top-10 recall depends on the consequence mix.
- C: predicted zero stop_lost labels; synthetic stop-loss alleles labelled UTR_noncoding_exon and never ranked; C2-CH genes ranked through the partner only (half credit at best).
- D: predicted p1 near 0 (tier A pheno 0 sits behind LZTR1), most hits at rank 2.
- v3: rank depends on v2 against LZTR1's 3.0 within tier A; predicted p1(v3) differs from p1(v4) mainly through pheno-0 genes with high v2 (v3 favours them) and pheno >= 2 genes with low v2 (v4 favours them).

## 12. Outputs (box work dir; copies of the .md files to the Mac at $S/agent_out/spikein/)

- `pools.tsv`, `trials.tsv` (one line per trial and ranking version), `alleles.tsv` (per-allele diagnostics), `sanity.json`, `RESULT.md`, `DEVIATIONS.md` (if any), `TRACK1_SUBMISSION_EPCR_PROPOSED.csv` (the draft rows with the proposed EPCR; the draft itself is not edited).

## 13. Not tested, and limits stated now

- Read-level calling (no reads simulated); phase; structural variants and copy-number events; regulatory or deep intronic alleles beyond the pipeline's reach are included and count as misses.
- EPCR from A is P(rank r) for a gene-uniform random biallelic small ClinVar P/LP event in SET18. It assumes the child's true causal is that kind of event; it is a measured calibration of the ranking, not a posterior for this child.
- Gene-uniform sampling weights genes with few ClinVar alleles as much as genes with many; per-gene results are reported so the weighting can be changed by a reader.
