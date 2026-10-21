"""Non-choices eval B2, criterion C2. Method copied verbatim from p5_depmap_safety.py
(itself identical to p4_depmap_safety.py, sha256 c7d87310a11c...): per gene, fraction of
cell lines with Chronos gene effect < -0.5 over all lines with a value, plus median Chronos
in blood-lineage lines (OncotreeLineage in {Myeloid, Lymphoid}). Flag if fraction >= 0.25.
Genes with no column are "not measured", never 0. Descriptive; cancer lines, not normal marrow.
No existing file is read for writing and none is edited."""
import csv, statistics
DIR = "/home/[redacted]/Documents/HACKATON/_private/public_data/depmap_24Q4/"
OUT = "/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B2/"
# Named targets claimed by batch B2 rows, then the real pharmacological targets of the
# artefact rows, reported as context beyond criterion C2.
NAMED = ["SIRT1", "SIRT2", "CREBBP", "EP300", "KAT2B"]
CONTEXT = ["FDPS", "EGFR", "TUBB", "GABRA1", "SLC6A3", "PDE10A"]
TARGETS = NAMED + CONTEXT
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
print("cell lines: %d; blood-lineage lines: %d" % (len(rows), sum(1 for m in model.values() if m in BLOOD)))
print("genes requested: %d; with a column: %d; not measured: %s"
      % (len(TARGETS), len(idx), ",".join(t for t in TARGETS if t not in idx) or "none"))
with open(OUT + "b2_c2_depmap.tsv", "w") as out:
    out.write("gene\tgroup\tn_lines\tfrac_chronos_lt_-0.5\tflag_ge_0.25\tblood_median\tblood_n\n")
    print("gene | group | n | frac<-0.5 | flag | blood_median | blood_n")
    for t in TARGETS:
        g = "named" if t in NAMED else "context"
        if t not in idx:
            out.write("%s\t%s\tnot measured\tnot measured\tnot measured\tnot measured\tnot measured\n" % (t, g))
            print("%s | %s | not measured (no column)" % (t, g)); continue
        i = idx[t]; vals, bv = [], []
        for r in rows:
            if i >= len(r) or r[i] in ("", "NA"): continue
            v = float(r[i]); vals.append(v)
            if model.get(r[0], "") in BLOOD: bv.append(v)
        frac = sum(1 for v in vals if v < THRESH) / len(vals)
        bmed = statistics.median(bv) if bv else float("nan")
        flag = "YES" if frac >= FLAG_FRAC else "no"
        out.write("%s\t%s\t%d\t%.3f\t%s\t%.3f\t%d\n" % (t, g, len(vals), frac, flag, bmed, len(bv)))
        print("%s | %s | %d | %.3f | %s | %.3f | %d" % (t, g, len(vals), frac, flag, bmed, len(bv)))
