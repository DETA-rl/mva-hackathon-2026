# DEVIATIONS from PRE_REG_ROWMAP.md (sha256 9f7a440ddbb427783a525e976f898b602cd95471654e9f681ded8ee50d1a0a45)

Written 2026-10-20 after the run. The pre-registration file was not edited (read-only on the box; its sha256 is logged at the start of run_rowmap.log and matches).

1. S-R5 implementation narrower than its wording (no effect on any decision). The wording covers causal genes with "<= 2 candidate calls and no homozygous-plus-het mix", which includes a gene with two homozygous calls. The code checked genes with one call, or with two calls neither of which is homozygous. A gene with two homozygous calls was left out, because there R0 forms a pair and P2 takes a single call, so they cannot agree. The implemented check passed with 0 mismatches. Of the 477 d0 trials whose causal gene had two candidate calls, the rules disagreed on the causal row in 2 (E-226, E-284, both HOM spikes with a second call in the gene), and those 2 fall outside the implemented check. In both, R0 and P1 lose the causal single and P2 to P5 keep it, which is the H-RM-4 mechanism. d0 trials are controls and enter no decision.

Post-hoc analyses are labelled as such in RESULT_ROWMAP.md (Section 3 near-tie comparisons, Section 5 class breakdown, `mech_check.py`, the comparison part of `propose_csv.py`). They do not change the pre-registered decision.

No other deviation.
