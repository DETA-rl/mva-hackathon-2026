"""Rebuild the 10 draft submission rows that the spike-in scripts read, from the upstream ranking artifacts.

The authors' TRACK1_SUBMISSION_DRAFT.csv is child-derived and is not in this repository, so the harness rebuilds
the rows it needs here, into the workdir's private folder. No analysis decision is made: the row sets come from
the analysis library's own draft ROW-MAP (spikelib.row_map) applied to the v4 ranking with Amendment 1, which is
how the draft CSV was built. One consequence is stated in the step note and in expected.yaml: gate G1e of
PRE-REG-SPIKEIN-EPCR compares spikelib.row_map against this file, so in the harness G1e is a self-consistency
check, not the independent comparison against the submitted CSV that it was in the original run.

Usage (by the harness only): draft_rows_csv.py <replicate/analysis/track1/spikein> <output csv>
The step folder must already hold child_exonic_consequence_fixed.tsv, clinvar.vcf.gz, hp.obo and
genes_to_phenotype.txt under those names (REPL_OUT); spikelib reads them from there.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.abspath(sys.argv[1]))

import spikelib as L  # noqa: E402  (imported after sys.path is set, like the analysis scripts do)

HEADER = ["proband_id", "chrom_1", "pos_1", "ref_1", "alt_1", "chrom_2", "pos_2", "ref_2", "alt_2",
          "epcr", "finding_type", "notes"]


def main():
    out_path = os.path.abspath(sys.argv[2])
    rows = L.read_consequence(L.D + "child_exonic_consequence_fixed.tsv")
    cands = L.v3_candidates(L.seen_from_rows(rows).values())
    clin = L.clinvar_lookup({L.key(f) for f in cands})
    o3, t3, g3 = L.rank_v3(cands, clin)
    o4, _, _ = L.rank_v4(o3, t3, g3, amendment1=True)
    top = o4[:10]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(HEADER)
        for g in top:
            ks = sorted(L.row_map(g3[g]), key=lambda k: (k[0], int(k[1]), k[2], k[3]))
            v1 = ks[0]
            v2 = ks[1] if len(ks) > 1 else ("", "", "", "")
            w.writerow(["PROBAND01", "chr" + v1[0], v1[1], v1[2], v1[3],
                        ("chr" + v2[0]) if v2[0] else "", v2[1], v2[2], v2[3], "", "primary", g])
    print(f"draft rows rebuilt: {len(top)} rows, genes {top}")


if __name__ == "__main__":
    main()
