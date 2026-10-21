#!/usr/bin/env python3
"""C2 for eval_B4a: DepMap 24Q4 dependency flags for the target genes named by the screen in
Batch 4 part A. Method identical to p5_depmap_safety.py (T2-P5): per gene, fraction of lines
with Chronos gene effect < -0.5 over all lines with a value, plus the blood-lineage median
(OncotreeLineage in {Myeloid, Lymphoid}); flag if fraction >= 0.25; a gene with no column is
"not measured", never 0. Descriptive only: cancer lines, not normal marrow. No flag is a safety
verdict and no absent flag is a safety clearance.
"""
import csv
import statistics

DIR = "/home/[redacted]/Documents/HACKATON/_private/public_data/depmap_24Q4/"
OUT = "/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4a/"

# genes named by the Batch 4 part A rows (DGIdb target claims), plus the two T2-P4 genes
# re-measured as the check that the method reproduces.
TARGETS = ["MTOR", "AURKB", "PLK4", "CDC20", "KIF18A"]
BLOOD = {"Myeloid", "Lymphoid"}
THRESH = -0.5
FLAG_FRAC = 0.25

model = {}
with open(DIR + "Model.csv") as f:
    for r in csv.DictReader(f):
        model[r["ModelID"]] = r.get("OncotreeLineage", "")

with open(DIR + "CRISPRGeneEffect.csv") as f:
    rdr = csv.reader(f)
    header = next(rdr)
    idx = {}
    for t in TARGETS:
        hits = [i for i, c in enumerate(header) if c.split(" (")[0] == t]
        if hits:
            idx[t] = hits[0]
    rows = list(rdr)

print("cell lines: %d; genes with a column: %d; not measured: %s"
      % (len(rows), len(idx), ",".join(t for t in TARGETS if t not in idx) or "none"))

with open(OUT + "c2_depmap_b4a.tsv", "w") as out:
    out.write("gene\tn_lines\tfrac_chronos_lt_-0.5\tflag_ge_0.25\tblood_median\tblood_n\n")
    for t in TARGETS:
        if t not in idx:
            out.write("%s\tnot measured\tnot measured\tnot measured\tnot measured\tnot measured\n" % t)
            print("%s | not measured" % t)
            continue
        i = idx[t]
        vals, bvals = [], []
        for r in rows:
            if i >= len(r) or r[i] in ("", "NA"):
                continue
            v = float(r[i])
            vals.append(v)
            if model.get(r[0], "") in BLOOD:
                bvals.append(v)
        frac = sum(1 for v in vals if v < THRESH) / len(vals)
        bmed = statistics.median(bvals) if bvals else float("nan")
        flag = "YES" if frac >= FLAG_FRAC else "no"
        out.write("%s\t%d\t%.3f\t%s\t%.3f\t%d\n" % (t, len(vals), frac, flag, bmed, len(bvals)))
        print("%s | %d | %.3f | %s | %.3f | %d" % (t, len(vals), frac, flag, bmed, len(bvals)))
print("wrote", OUT + "c2_depmap_b4a.tsv")
