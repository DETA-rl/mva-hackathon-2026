# Ranking rule v3, hierarchical evidence (frozen before the run)

Purpose: rank genes by evidence strength, strongest source first. v2 weights alone did not separate BUB1B from background.

Inputs: child_exonic_consequence.tsv (candidate calls: protein-altering, rare or unobserved; male chrX and cluster filters from v2 applied) and ClinVar GRCh38 VCF (public).

Tier A (strongest): gene has at least one candidate call that matches a ClinVar record classified Pathogenic or Likely_pathogenic (including Pathogenic/Likely_pathogenic).
Tier B: gene not in Tier A that has a compound-het pattern: at least one nonsense, frameshift, or splice-region call AND at least one missense call (any genotype), with >= 2 calls total.
Tier C: all other genes that pass v2 (score >= 3 or one homozygous call).

Within each tier, rank by the v2 weighted score (descending), then gene name.
Paralog-family exclusion and cluster-artifact exclusion from v2 apply unchanged.

Not used (not available on the box, declared missing): HPO phenotype ranking, AlphaMissense, CADD, REVEL, SpliceAI. These must be added as separate, pre-registered steps, not silently.

Ablations, reported together:
- A0: v2 ranking only (no ClinVar tier, no compound tier).
- A1: ClinVar tier only, then v2.
- Shuffled baseline: ClinVar labels permuted across candidate calls (seed 1), then the full v3 hierarchy. Shows how much the tier assignment alone creates.

Positive control: none valid (TRIP13 has no exonic call). Reported as unavailable.

Caveat declared before the run: ClinVar encodes existing knowledge, so a known disease gene is expected to rank high. This is evidence, not discovery, and is reported as such.
