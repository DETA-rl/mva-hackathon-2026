# Ranking rule v2 (frozen before the run). Supersedes v1 for the rerun; v1 results stay in the register.

Changes from v1, declared before the run:
A. Sex: the child is male (user-declared; read counts agree). chrX calls outside the pseudoautosomal regions (GRCh38 PAR1 chrX:10,001-2,781,479; PAR2 chrX:155,701,383-156,030,895) are hemizygous. Heterozygous non-PAR chrX calls are excluded as artifacts. Homozygous non-PAR chrX calls are kept. Counts of excluded calls are reported.
B. Cluster artifact flag: within a gene, if 5 or more candidate calls fall within any 1 kb window and all are homozygous, the gene is flagged as a cluster artifact, excluded from ranking, and reported separately.
C. chrM is outside the exome release and is excluded (already the case).

Unchanged from v1: candidate calls, weights (nonsense 3, frameshift 3, stop_lost 2, splice_region 2, inframe 2, missense 1; homozygous x1.5), score threshold (>=3 or one homozygous candidate), paralog-family exclusion list, ablation A (unweighted counts), shuffled-label baseline (seed 1), BUB1B reported under each rule without being a success criterion.

Positive control: still not available in this call set.
