"""T2-P5 (pre-registered PRE-REG-T2-P5): DepMap 24Q4 on-target dependency for the candidate
targets not covered by T2-P4.

Method copied from p4_depmap_safety.py (sha256 c7d87310a11c2448ba2a3d2845dd8bd6750d6c675a1e7ff27d607ed6d889f524):
per gene, fraction of cell lines with Chronos gene effect < -0.5 over all lines with a value,
and the median Chronos in blood-lineage lines (OncotreeLineage in {Myeloid, Lymphoid}).
Flag if fraction >= 0.25. Genes with no column are reported "not measured", never 0.
Descriptive; cancer lines only, not normal marrow.
"""
import csv
import statistics
import sys

DIR = __import__("os").environ["REPL_OUT"] + "/"
OUT = __import__("os").environ["REPL_OUT"] + "/"

# Fixed in PRE-REG-T2-P5. Order: NAD route, sirtuins, fingolimod, arimoclomol, 4-PBA.
TARGETS = [
    "NAPRT", "HCAR2", "NAMPT", "NMNAT1", "NMNAT2", "NMNAT3", "NMRK1", "NMRK2", "SLC12A8",
    "SIRT1", "SIRT2",
    "SPHK2", "S1PR1", "S1PR3", "S1PR4", "S1PR5", "SET", "PPP2CA", "PPP2R1A",
    "HSF1", "HSPA1A", "HSPA1B",
    "HDAC1", "HDAC2", "HDAC3", "HDAC8",
]
# Candidate -> its target list (shared genes counted for every candidate that uses them).
CANDIDATES = {
    "niacin": ["NAPRT", "HCAR2", "NMNAT1", "NMNAT2", "NMNAT3"],
    "nicotinamide": ["NAMPT", "NMNAT1", "NMNAT2", "NMNAT3", "SIRT1", "SIRT2"],
    "NMN": ["NMNAT1", "NMNAT2", "NMNAT3", "SLC12A8"],
    "NR": ["NMRK1", "NMRK2", "NMNAT1", "NMNAT2", "NMNAT3"],
    "fingolimod": ["SPHK2", "S1PR1", "S1PR3", "S1PR4", "S1PR5", "SET", "PPP2CA", "PPP2R1A"],
    "arimoclomol": ["HSF1", "HSPA1A", "HSPA1B"],
    "4-PBA": ["HDAC1", "HDAC2", "HDAC3", "HDAC8"],
}
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

print("cell lines: %d; blood-lineage lines in Model.csv: %d"
      % (len(rows), sum(1 for m in model.values() if m in BLOOD)))
print("genes requested: %d; with a DepMap column: %d; not measured: %s"
      % (len(TARGETS), len(idx), ",".join(t for t in TARGETS if t not in idx) or "none"))

res = {}
with open(OUT + "t2_p5_depmap.tsv", "w") as out:
    out.write("gene\tn_lines\tfrac_chronos_lt_-0.5\tflag_ge_0.25\tblood_median\tblood_n\n")
    print("gene | n_lines | frac_Chronos<-0.5 | flag(>=0.25) | blood_median | blood_n")
    for t in TARGETS:
        if t not in idx:
            out.write("%s\tnot measured\tnot measured\tnot measured\tnot measured\tnot measured\n" % t)
            print("%s | not measured (no column in CRISPRGeneEffect.csv)" % t)
            res[t] = None
            continue
        i = idx[t]
        vals, blood_vals = [], []
        for r in rows:
            if i >= len(r) or r[i] in ("", "NA"):
                continue
            v = float(r[i])
            vals.append(v)
            if model.get(r[0], "") in BLOOD:
                blood_vals.append(v)
        frac = sum(1 for v in vals if v < THRESH) / len(vals)
        bmed = statistics.median(blood_vals) if blood_vals else float("nan")
        flag = "YES" if frac >= FLAG_FRAC else "no"
        res[t] = (len(vals), frac, flag, bmed, len(blood_vals))
        out.write("%s\t%d\t%.3f\t%s\t%.3f\t%d\n" % (t, len(vals), frac, flag, bmed, len(blood_vals)))
        print("%s | %d | %.3f | %s | %.3f | %d" % (t, len(vals), frac, flag, bmed, len(blood_vals)))

print("\ncandidate | flagged targets (count) | flagged genes | not measured")
with open(OUT + "t2_p5_candidate_counts.tsv", "w") as out:
    out.write("candidate\tn_flagged\tflagged_genes\tnot_measured\tmeasured_unflagged\n")
    for c, genes in CANDIDATES.items():
        fl = [g for g in genes if res.get(g) and res[g][2] == "YES"]
        nm = [g for g in genes if res.get(g) is None]
        uf = [g for g in genes if res.get(g) and res[g][2] == "no"]
        out.write("%s\t%d\t%s\t%s\t%s\n" % (c, len(fl), ",".join(fl) or "-", ",".join(nm) or "-", ",".join(uf) or "-"))
        print("%s | %d | %s | %s" % (c, len(fl), ",".join(fl) or "-", ",".join(nm) or "-"))
