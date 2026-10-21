# SV rule v1 (frozen before run)
Input: Manta 1.6.0 diploidSV.vcf.gz on the child's BAM (GRCh38).
1. Keep calls with FILTER = PASS.
2. Support: alt-supporting reads PR (alt) + SR (alt) >= 4, computed from the sample field.
3. Size: DEL, DUP, INS with SVLEN >= 50, or BND.
4. Dosage-sensitive genes: ClinGen haploinsufficiency score 3 or triplosensitivity score 3 (ClinGen curation list, 16 Oct 2026 release), gene span from GENCODE v44.
5. Output per gene: calls, types, genotypes. Gene rank = number of qualifying calls, no weights.
6. Phenotype match is NOT part of the rank. It is annotated afterwards from the organizer HPO terms, and recorded separately.
7. H03 (BUB1B locus): all Manta calls within BUB1B gene +/-50 kb, same filters 1 to 3, reported with no rank.
8. Positive control: none valid (no TRIP13 SV is required; reported as not available).
