# Intermediates

Outputs of full-tier steps (GPU or network) that a quick-tier run can use instead of recomputing them. Give one in
`config.yaml` under `intermediates`; the report then marks the downstream steps as using a supplied intermediate
and says whether it is byte-identical to our stored output (sha256 in `replicate/expected.yaml`, section
`artifacts`).

Only public-derived intermediates are in this folder. Child-derived ones are not in the repository (data terms);
the authors can hand them to the organisers if the organisers approve.

| key in `intermediates` | file | produced by | how to regenerate | in this folder |
|---|---|---|---|---|
| `evo2_control_scores` | `evo2_rule_controls_out.tsv` (198 ClinVar controls, sha256 `2a1b2a09...`) | M-EVO2-CAL-01-SCORE | GPU with 16 GB free, Evo 2 7B weights, full-tier venv; about 4 min after model load | yes: public data only (ClinVar control variants scored by Evo 2) |
| `gnomad_parts` | folder with `child_exonic_gnomad_exomes.part0.tsv` to `part3.tsv` | BLIND-01B | network (byte ranges of the public gnomAD v4.1 exome VCFs), about 3.5 h with 4 workers: `REPLICATE_ALLOW_NETWORK=1 ./replicate.sh run --tier full --steps BLIND-01B --with-deps`, then `./replicate.sh run --tier quick --rerun` in the same workdir | no: one row per exonic call of the child |
| `protein_scores` | `scores.tsv` | M-PROT-CAL-02-SCORE | GPU, ESM-1v, ESM-2 and AlphaMissense files; needs the candidate (T1-CANDIDATE), so `gnomad_parts` first | no: it holds the candidate's row |

`borzoi_control_scores.tsv` (sha256 `64262aefa3753b2350589502366674e1480f07bce77893b8231db190006a3404`) is the
control set and scores of the external step M-REG-BORZOI as our run wrote them: for each of 120 GTEx v8 Whole Blood
eQTL variants and 120 random positions near the same genes' TSS on chromosome 15, the gene, position, alleles, GTEx
effect size and p-value (eQTLs only), label and the two Borzoi scores. No harness step reads it. It is here because
the step reads a live API that returns only the first page of each gene's eQTLs, so without our copy the control set
cannot be rebuilt exactly (`replicate/EXTERNAL_STEPS.md`). Public data only: no position or value from the child's
data.

With `evo2_rule_controls_out.tsv`, M-EVO2-CAL-01 runs in the quick tier. Without `gnomad_parts`, the whole Track 1
exonic chain (BLIND-01C to P2, 19 steps) is NOT RUN; see the README section "What an outsider's quick tier runs".
