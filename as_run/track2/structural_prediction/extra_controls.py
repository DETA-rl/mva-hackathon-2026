"""PRE-REG-R2A: descriptive scoring of BUBR1 missense alleles with published abundance data (F4). Not used in the rule."""
import json, sys
from pathlib import Path
import pandas as pd
W = Path(sys.argv[1]); OUT = W / "out"
T = json.load(open(OUT / "calibration.json"))["T_star"]
PL = {int(k): v for k, v in json.load(open(W / "structures" / "plddt.json"))["O60566"].items()}
# allele, published abundance finding, source
PUB = [("Y155C", "WT-like level (ectopic); separation-of-function", "PMID 20516114"),
       ("R550Q", "WT-like level (ectopic); functional", "PMID 20516114"),
       ("W722R", "trend to reduced mRNA and protein, heterozygous carrier lymphocytes", "PMID 42434306 abstract"),
       ("R727C", "low (patient cells; ectopic), mRNA normal, ~2x faster turnover", "PMID 20516114"),
       ("A739S", "trend to reduced mRNA and protein, heterozygous carrier lymphocytes", "PMID 42434306 abstract"),
       ("R814H", "low (patient cells 753X/R814H; ectopic)", "PMID 20516114"),
       ("L844F", "low (poorly expressed, ectopic)", "PMID 20516114"),
       ("I909T", "low; rescued by overexpression", "PMID 20516114"),
       ("Q921H", "WT-like level and function (ectopic)", "PMID 20516114"),
       ("L1012P", "low; rescued by overexpression", "PMID 20516114")]
ssm = {s: pd.read_csv(OUT / f"ssm_O60566_{s}.csv") for s in ["primary", "S1"]}
rsa = pd.read_csv(OUT / "rsa_O60566_S1.csv").set_index("resnum")
rows = []
for a, find, src in PUB:
    wt, pos, mt = a[0], int(a[1:-1]), a[-1]
    r = dict(allele=a, published=find, source=src, plddt=round(PL[pos], 1), rsa_S1=round(float(rsa.loc[pos, "rsa"]), 3))
    for s in ssm:
        h = ssm[s][(ssm[s].resnum == pos) & (ssm[s].mutation == mt)]
        if len(h):
            assert h.wildtype.iloc[0] == wt
        r[f"ddG_{s}"] = round(float(h.ddG.iloc[0]), 3) if len(h) else None
    g = r["ddG_primary"] if r["ddG_primary"] is not None else r["ddG_S1"]
    r["call_at_Tstar"] = "destab" if g >= T else "neutral"
    rows.append(r)
df = pd.DataFrame(rows); df.to_csv(OUT / "bubr1_published_alleles.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70)
print(df.to_string(index=False))
