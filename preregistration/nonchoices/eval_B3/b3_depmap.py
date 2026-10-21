"""Criterion C2 for batch B3. Method identical to p5_depmap_safety.py (T2-P5), itself the
T2-P4 method: DepMap 24Q4, fraction of lines with Chronos < -0.5, flag if >= 0.25,
blood lineage = OncotreeLineage in {Myeloid, Lymphoid}. Genes with no column: not measured.
Descriptive only. A flag removes nothing (PRE-REG-NONCHOICES 5.2)."""
import csv, statistics
DIR = "/home/[redacted]/Documents/HACKATON/_private/public_data/depmap_24Q4/"
OUT = "/home/[redacted]/Documents/HACKATON/_private/agent_out/nonchoices/eval_B3/"
TARGETS = ["PSMB1","PSMB2","PSMB5","PPP2CA","PPP2R1A","PPP2R5D","FBXW7",
           "PDCD1","TUBB","TUBB1","TYMS","KDR","ATP6V0C"]
BLOOD = {"Myeloid","Lymphoid"}
model = {}
for r in csv.DictReader(open(DIR+"Model.csv")):
    model[r["ModelID"]] = r.get("OncotreeLineage","")
rdr = csv.reader(open(DIR+"CRISPRGeneEffect.csv"))
header = next(rdr)
idx = {}
for t in TARGETS:
    h = [i for i,c in enumerate(header) if c.split(" (")[0] == t]
    if h: idx[t] = h[0]
rows = list(rdr)
print("cell lines: %d" % len(rows))
print("not measured: %s" % (",".join(t for t in TARGETS if t not in idx) or "none"))
with open(OUT+"b3_depmap.tsv","w") as out:
    out.write("gene\tn_lines\tfrac_chronos_lt_-0.5\tflag_ge_0.25\tblood_median\tblood_n\n")
    print("gene | n | frac<-0.5 | flag | blood_median | blood_n")
    for t in TARGETS:
        if t not in idx:
            out.write("%s\tnot measured\tnot measured\tnot measured\tnot measured\tnot measured\n" % t)
            print("%s | not measured" % t); continue
        i = idx[t]; vals=[]; bv=[]
        for r in rows:
            if i >= len(r) or r[i] in ("","NA"): continue
            v = float(r[i]); vals.append(v)
            if model.get(r[0],"") in BLOOD: bv.append(v)
        frac = sum(1 for v in vals if v < -0.5)/len(vals)
        bmed = statistics.median(bv) if bv else float("nan")
        flag = "YES" if frac >= 0.25 else "no"
        out.write("%s\t%d\t%.3f\t%s\t%.3f\t%d\n" % (t,len(vals),frac,flag,bmed,len(bv)))
        print("%s | %d | %.3f | %s | %.3f | %d" % (t,len(vals),frac,flag,bmed,len(bv)))
