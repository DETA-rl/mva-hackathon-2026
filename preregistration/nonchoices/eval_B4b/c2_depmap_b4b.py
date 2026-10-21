"""C2 for eval_B4b: DepMap 24Q4 on-target dependency for the claimed targets appearing in
Batch 4 items 50-98. Method identical to p5_depmap_safety.py (T2-P5): per gene, fraction of
lines with Chronos < -0.5 over all lines with a value, plus the blood-lineage median
(OncotreeLineage in {Myeloid, Lymphoid}). Flag if fraction >= 0.25. No column => not measured.
Descriptive only; cancer lines, not normal marrow. A flag removes nothing (pre-reg 5.2).
MTOR, PLK4 and KIF18A are included as reproduction checks against the T2-P4 values.
"""
import csv, statistics
DIR = "/home/[redacted]/Documents/HACKATON/_private/public_data/depmap_24Q4/"
OUT = "/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B4b/"
TARGETS = ["MTOR", "AURKB", "PLK4", "KIF18A"]
BLOOD = {"Myeloid", "Lymphoid"}
THRESH, FLAG_FRAC = -0.5, 0.25
model = {}
with open(DIR + "Model.csv") as f:
    for r in csv.DictReader(f):
        model[r["ModelID"]] = r.get("OncotreeLineage", "")
with open(DIR + "CRISPRGeneEffect.csv") as f:
    rdr = csv.reader(f); header = next(rdr)
    idx = {}
    for t in TARGETS:
        hits = [i for i, c in enumerate(header) if c.split(" (")[0] == t]
        if hits: idx[t] = hits[0]
    rows = list(rdr)
print("cell lines: %d; blood-lineage lines in Model.csv: %d" % (len(rows), sum(1 for m in model.values() if m in BLOOD)))
print("genes requested: %d; with a column: %d; not measured: %s" % (len(TARGETS), len(idx), ",".join(t for t in TARGETS if t not in idx) or "none"))
with open(OUT + "c2_depmap_b4b.tsv", "w") as out:
    out.write("gene\tn_lines\tfrac_chronos_lt_-0.5\tflag_ge_0.25\tblood_median\tblood_n\n")
    for t in TARGETS:
        if t not in idx:
            out.write("%s\tnot measured\tnot measured\tnot measured\tnot measured\tnot measured\n" % t)
            print("%s | not measured" % t); continue
        i = idx[t]; vals = []; bv = []
        for r in rows:
            if i >= len(r) or r[i] in ("", "NA"): continue
            v = float(r[i]); vals.append(v)
            if model.get(r[0], "") in BLOOD: bv.append(v)
        frac = sum(1 for v in vals if v < THRESH) / len(vals)
        bmed = statistics.median(bv) if bv else float("nan")
        flag = "YES" if frac >= FLAG_FRAC else "no"
        out.write("%s\t%d\t%.3f\t%s\t%.3f\t%d\n" % (t, len(vals), frac, flag, bmed, len(bv)))
        print("%s | %d | %.3f | %s | %.3f | %d" % (t, len(vals), frac, flag, bmed, len(bv)))
