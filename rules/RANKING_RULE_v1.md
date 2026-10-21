# Ranking rule v1 (frozen before the run)

Input: child_exonic_consequence.tsv (first canonical transcript per call). No gene names are used to select, weight, or exclude genes, except the paralog exclusion list below, which is declared here and not changed after the run.

1. Candidate call: consequence in {nonsense, frameshift, stop_lost, missense, inframe_indel, splice_region} AND gnomAD class in {rare, unobserved}.
2. Weights: nonsense 3, frameshift 3, stop_lost 2, splice_region 2, inframe_indel 2, missense 1. Homozygous call multiplies the call weight by 1.5. Heterozygous calls are not phased.
3. Gene score = sum of call weights. Only genes with score >= 3 or at least one homozygous candidate are ranked.
4. Paralog-family exclusion (declared before the run): gene symbols starting with HLA-, TAS2R, MUC, LILRA, LILRB, OR followed by a digit, ZNF, PRDM9, NBPF, or SERPINA. These families are reported separately and are not ranked.
5. Ablation A (no weights): gene score = number of candidate calls. Same exclusions.
6. Ablation B (shuffled consequence labels, seed 1): same weights, consequence labels permuted across calls. Baseline for how much the weighting alone creates.
7. Positive control: none valid in this call set (TRIP13 has no exonic calls; see register H09). Reported as not available.
8. Reported per gene: score, rank under rule 3, rank under ablation A, the calls, and whether the gene carries a homozygous candidate.
9. BUB1B rank under each rule is reported as found. It is not a success criterion.

Hash: computed by the run script before any output is read.
