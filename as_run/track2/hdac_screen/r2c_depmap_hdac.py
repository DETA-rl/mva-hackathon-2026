"""R2-C (pre-registered PRE-REG-R2C-HDAC, C2): DepMap 24Q4 dependency for every HDAC isoform.

Method identical to p5_depmap_safety.py / p4_depmap_safety.py: per gene, fraction of lines with
Chronos gene effect < -0.5 over all lines with a value, plus median Chronos in blood-lineage lines
(OncotreeLineage in {Myeloid, Lymphoid}). Flag if fraction >= 0.25. No column => "not measured",
never 0. Descriptive only; cancer lines, not normal marrow. HDAC1/2/3/8 are re-measured as the
F5 check against the T2-P5 values.
"""
import csv, statistics

DIR = "/home/[redacted]/Documents/HACKATON/_private/public_data/depmap_24Q4/"
OUT = "/home/[redacted]/Documents/HACKATON/_private/agent_out/r2_hdac/"

TARGETS = ["HDAC1","HDAC2","HDAC3","HDAC4","HDAC5","HDAC6","HDAC7","HDAC8","HDAC9","HDAC10","HDAC11"]
CLASS_I = ["HDAC1","HDAC2","HDAC3","HDAC8"]
CLASS_IIA = ["HDAC4","HDAC5","HDAC7","HDAC9"]
CLASS_IIB = ["HDAC6","HDAC10"]
CLASS_IV = ["HDAC11"]
DRUGS = {
    "valproate":            CLASS_I + CLASS_IIA,
    "sodium phenylbutyrate": CLASS_I,
    "vorinostat":           CLASS_I + CLASS_IIB,
    "romidepsin":           CLASS_I,
    "belinostat":           CLASS_I + CLASS_IIA + CLASS_IIB + CLASS_IV,
    "panobinostat":         CLASS_I + CLASS_IIA + CLASS_IIB + CLASS_IV,
    "givinostat":           CLASS_I + CLASS_IIA + CLASS_IIB,
}
BLOOD = {"Myeloid", "Lymphoid"}
THRESH, FLAG_FRAC = -0.5, 0.25

model = {}
with open(DIR + "Model.csv") as f:
    for r in csv.DictReader(f):
        model[r["ModelID"]] = r.get("OncotreeLineage", "")

with open(DIR + "CRISPRGeneEffect.csv") as f:
    rdr = csv.reader(f); header = next(rdr)
    idx = {t: [i for i, c in enumerate(header) if c.split(" (")[0] == t][0]
           for t in TARGETS if any(c.split(" (")[0] == t for c in header)}
    rows = list(rdr)

print("cell lines: %d; blood-lineage lines: %d" % (len(rows), sum(1 for m in model.values() if m in BLOOD)))
print("genes requested: %d; with a column: %d; not measured: %s"
      % (len(TARGETS), len(idx), ",".join(t for t in TARGETS if t not in idx) or "none"))

res = {}
with open(OUT + "r2c_hdac_depmap.tsv", "w") as out:
    out.write("gene\tn_lines\tfrac_chronos_lt_-0.5\tflag_ge_0.25\tblood_median\tblood_n\n")
    print("gene | n_lines | frac_Chronos<-0.5 | flag | blood_median | blood_n")
    for t in TARGETS:
        if t not in idx:
            out.write("%s\tnot measured\tnot measured\tnot measured\tnot measured\tnot measured\n" % t)
            print("%s | not measured" % t); res[t] = None; continue
        i = idx[t]; vals, bv = [], []
        for r in rows:
            if i >= len(r) or r[i] in ("", "NA"): continue
            v = float(r[i]); vals.append(v)
            if model.get(r[0], "") in BLOOD: bv.append(v)
        frac = sum(1 for v in vals if v < THRESH) / len(vals)
        bmed = statistics.median(bv) if bv else float("nan")
        flag = "YES" if frac >= FLAG_FRAC else "no"
        res[t] = (len(vals), frac, flag, bmed, len(bv))
        out.write("%s\t%d\t%.3f\t%s\t%.3f\t%d\n" % (t, len(vals), frac, flag, bmed, len(bv)))
        print("%s | %d | %.3f | %s | %.3f | %d" % (t, len(vals), frac, flag, bmed, len(bv)))

print("\ndrug | n_flagged | flagged genes | not measured")
with open(OUT + "r2c_hdac_drug_counts.tsv", "w") as out:
    out.write("drug\tn_flagged\tflagged_genes\tnot_measured\tmeasured_unflagged\n")
    for d, genes in DRUGS.items():
        fl = [g for g in genes if res.get(g) and res[g][2] == "YES"]
        nm = [g for g in genes if res.get(g) is None]
        uf = [g for g in genes if res.get(g) and res[g][2] == "no"]
        out.write("%s\t%d\t%s\t%s\t%s\n" % (d, len(fl), ",".join(fl) or "-", ",".join(nm) or "-", ",".join(uf) or "-"))
        print("%s | %d | %s | %s" % (d, len(fl), ",".join(fl) or "-", ",".join(nm) or "-"))
