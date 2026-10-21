# DEVIATIONS from PRE_REG_SPIKEIN_EPCR.md (sha256 6d40e58fe2d34d92fa9ff42b7171ad5034b45c2409591779c4cc3775650ede69)

Written 2026-10-20 after the run. The pre-registration file was not edited (read-only on the box; its sha256 is logged at the start of run.log and matches).

1. ClinVar lookup key set (no effect on results). Section 4.4 says the lookup is computed over "the union of background candidate keys and all spiked keys". It was computed over background rows that pass the per-call candidate filters (consequence class and frequency class) before the gene-level cluster and paralog filters, plus all spiked keys, plus the two real BUB1B keys (needed for sanity check S3). This set contains the pre-registered one. A key's lookup value does not depend on the other keys in the set (same file scan, same last-record-wins rule), so no trial outcome changes.

No other deviation. All gates and strata ran as written: G1 (before freezing, as disclosed in the pre-registration), S1 to S3, the child VCF hash before and after, N per stratum as designed (C2-CH has 91 trials, the enumerated count).
