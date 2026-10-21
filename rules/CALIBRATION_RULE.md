# Calibration rule for Track 1 model scores

Written before any model is run. Source: ClinVar VCF `~/Documents/HACKATON/_private/blind_gnomad/clinvar.vcf.gz` (fileDate 2026-10-11, public data). Eligibility counts computed by `count_controls.awk` in this folder.

## 1. Control sets

**Eligibility (per record):** `CLNVC=single_nucleotide_variant`; `CLNREVSTAT` is one of `criteria_provided,_single_submitter`, `criteria_provided,_multiple_submitters,_no_conflicts`, `reviewed_by_expert_panel`, `practice_guideline`; `CLNSIG` is `Pathogenic`/`Likely_pathogenic` (class P) or `Benign`/`Likely_benign` (class B); `MC` contains `missense_variant` or `nonsense`/`stop_gained`. Conflicting-classification records are excluded. BUB1B records are excluded from the pool.

**Eligible counts:** P missense 48,651; P nonsense 61,500; B missense 130,286; B nonsense 858.

**Selection (no model scores used):**
- Per cell (P/B × missense/nonsense), take the 5 genes with the most eligible records; ties broken alphabetically.
- Per gene, take the 10 records with the lowest SHA-256 of the ClinVar VariationID (column 3). If a gene has fewer than 10, take all.
- Expected pool: up to 200 controls (100 P, 100 B), with B-nonsense capped by availability.

**BUB1B sub-check:** the BUB1B candidate calls are scored separately and reported apart from the control AUC.

## 2. Metric

- AUC of the model score for P (positive) vs B (negative) controls.
- 95% CI from 2,000 stratified bootstrap resamples (percentile method), resampling within class.
- **Informative** only if the AUC lower bound is above 0.7.
- AUC lower bound between 0.6 and 0.7: report as exploratory, not as informative.

## 3. Decision rule for the child's two calls

- For each call, report the model's percentile rank among the pooled control scores (same model, same scoring run).
- Report the percentile with its control-set size, and state that a model score is not evidence of causation.
- Percentiles are reported only for models that pass section 2.

## 4. Falsifier

- A model whose AUC lower bound is below 0.6 is not used, for any purpose, in the Track 1 write-up.
- This rule is fixed; changing the gene count, the variant count or the class definitions after results are seen requires a new hash and a written reason.

## Hash

Recorded in `CALIBRATION_RULE.sha256` in this folder.
