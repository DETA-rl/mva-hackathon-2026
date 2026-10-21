"""T2-P4 (pre-registered PRE-REG-2026-10-20): DepMap 24Q4 on-target dependency for candidate targets.
Per target: fraction of cell lines with Chronos gene effect < -0.5 (all lines), and median in blood lineages.
Flag if fraction >= 0.25. Descriptive; cancer lines only, not normal marrow.
"""
import csv
import statistics

DIR = __import__("os").environ["REPL_OUT"] + "/"
TARGETS = ["MTOR", "CDC20", "SIRT2", "PLK4", "ANAPC4", "UBE2C", "KIF18A", "ABL1", "SRC", "NAMPT", "NMNAT1"]
BLOOD = {"Myeloid", "Lymphoid"}

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

print(f"cell lines: {len(rows)}; blood-lineage lines in Model.csv: "
      f"{sum(1 for m in model.values() if m in BLOOD)}")
print("target | n_lines | frac_Chronos<-0.5 | flag(>=0.25) | blood_median | blood_n")
for t in TARGETS:
    if t not in idx:
        print(f"{t} | not in DepMap columns")
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
    frac = sum(1 for v in vals if v < -0.5) / len(vals)
    bmed = statistics.median(blood_vals) if blood_vals else float("nan")
    flag = "YES" if frac >= 0.25 else "no"
    print(f"{t} | {len(vals)} | {frac:.3f} | {flag} | {bmed:.3f} | {len(blood_vals)}")
