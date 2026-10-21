# Ranking rule v4, phenotype layer (frozen before the run)

Inputs: child's HPO terms from the organizer clinical document (8 IDs: HP:0000121, HP:0001508, HP:0001518, HP:0001622, HP:0002859, HP:0003202, HP:0004322, HP:0200067). HPO release from GitHub (genes_to_phenotype.txt, hp.obo, both in the box blind_gnomad folder).

Phenotype score for a gene = number of the child's terms c such that at least one HPO term annotated to the gene is c itself or a descendant of c (is_a ancestry in hp.obo). Each child term counts once per gene.

Ranking: v3 hierarchy is kept (tier A ClinVar P/LP, tier B compound pattern, tier C others). Within each tier, order by phenotype score (descending), then v2 weighted score (descending), then gene name.

Ablations, reported together:
- P0: v3 hierarchy with v2 score inside tiers (the previous run, no phenotype).
- P-only: all candidate genes ordered by phenotype score alone (ties broken by v2 score).
- Shuffled baseline: phenotype gene labels permuted across genes (seed 1), then the v4 ordering.

Positive control: none valid in this call set (TRIP13 has no exonic call), reported as unavailable.

Caveats declared before the run: HPO gene annotation is literature and clinical knowledge, so a known disease gene will score high for the matching terms. Phenotype score is evidence, not diagnosis.

## Amendment 1 (2026-10-18, before reading the corrected output)
- chrM calls (MT-*) are excluded. They are not in the gnomAD exome release, so "unobserved" is not a valid class for them, and mitochondrial calls depend on heteroplasmy. The v4 run that included them is kept as a record.
