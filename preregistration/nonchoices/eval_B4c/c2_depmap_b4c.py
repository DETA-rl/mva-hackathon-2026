# C2 for batch B4c claimed targets. Method identical to p5_depmap_safety.py / p4_depmap_safety.py:
# per gene, fraction of lines with Chronos < -0.5 over all lines with a value, plus blood-lineage median.
# Flag if fraction >= 0.25. Genes with no column are "not measured", never 0. Public data only.
import csv, statistics
DIR="/home/[redacted]/Documents/HACKATON/_private/public_data/depmap_24Q4/"
TARGETS=["MTOR","AURKB","PLK4","FBXW7","SIRT1","HSP90AA1"]
BLOOD={"Myeloid","Lymphoid"}; THRESH=-0.5; FLAG=0.25
model={}
for r in csv.DictReader(open(DIR+"Model.csv")): model[r["ModelID"]]=r.get("OncotreeLineage","")
f=open(DIR+"CRISPRGeneEffect.csv"); rdr=csv.reader(f); header=next(rdr)
idx={t:[i for i,c in enumerate(header) if c.split(" (")[0]==t][0] for t in TARGETS if any(c.split(" (")[0]==t for c in header)}
rows=list(rdr)
print("lines: %d"%len(rows))
print("gene\tn_with_value\tfraction_lt_-0.5\tblood_median\tflag")
for t in TARGETS:
    if t not in idx: print("%s\tnot measured"%t); continue
    i=idx[t]; vals=[]; blood=[]
    for r in rows:
        v=r[i]
        if v=="" : continue
        v=float(v); vals.append(v)
        if model.get(r[0],"") in BLOOD: blood.append(v)
    fr=sum(1 for v in vals if v<THRESH)/len(vals)
    print("%s\t%d\t%.3f\t%s\t%s"%(t,len(vals),fr,("%.3f"%statistics.median(blood)) if blood else "n/a","FLAG" if fr>=FLAG else "-"))
