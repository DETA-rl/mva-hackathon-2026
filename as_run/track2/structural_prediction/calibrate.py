"""PRE-REG-R2A calibration: ThermoMPNN ddG vs VAMP-seq abundance class (PTEN, TPMT; Matreyek 2018).

Primary: class 1 (low) vs class 4 (WT-like), residues with pLDDT >= 70, primary structure.
Gate G1: pooled AUC >= 0.70 and each protein >= 0.65. T* = Youden-optimal ddG threshold.
CI: residue-level cluster bootstrap, 2000 resamples, seed 20261020.
Usage: python -I calibrate.py <work_dir>
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, roc_curve

W = Path(sys.argv[1])
OUT = W / "out"
PL = json.load(open(W / "structures" / "plddt.json"))
THREE = {"Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C", "Gln": "Q", "Glu": "E", "Gly": "G",
         "His": "H", "Ile": "I", "Leu": "L", "Lys": "K", "Met": "M", "Phe": "F", "Pro": "P", "Ser": "S",
         "Thr": "T", "Trp": "W", "Tyr": "Y", "Val": "V"}
SETS = {"PTEN": ("00000013-a-1", "P60484"), "TPMT": ("00000013-b-1", "P51580")}
PAT = re.compile(r"^p\.([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2})$")
rng = np.random.default_rng(20261020)
NBOOT = 2000


def load(prot, struct):
    urn, acc = SETS[prot]
    mv = pd.read_csv(W / "data" / f"mavedb_{urn}.csv")
    ssm = pd.read_csv(OUT / f"ssm_{acc}_{struct}.csv")
    rsa = pd.read_csv(OUT / f"rsa_{acc}_{struct}.csv")
    seq = {int(k): v for k, v in PL[acc].items()}
    rows, n_parse, n_mismatch = [], 0, 0
    for _, r in mv.iterrows():
        m = PAT.match(str(r.hgvs_pro))
        if not m or m.group(3) not in THREE or m.group(1) not in THREE:
            continue
        wt, pos, mt = THREE[m.group(1)], int(m.group(2)), THREE[m.group(3)]
        if wt == mt or pd.isna(r.abundance_class):
            continue
        n_parse += 1
        rows.append(dict(protein=prot, resnum=pos, wt=wt, mt=mt, cls=int(r.abundance_class),
                         score=r.score, plddt=seq.get(pos, np.nan)))
    df = pd.DataFrame(rows)
    df = df.merge(ssm.rename(columns={"wildtype": "wt_model", "mutation": "mt"}), on=["resnum", "mt"], how="left")
    n_mismatch = int(((df.wt_model.notna()) & (df.wt_model != df.wt)).sum())
    df = df[df.wt_model == df.wt]
    df = df.merge(rsa[["resnum", "rsa"]], on="resnum", how="left")
    return df, n_parse, n_mismatch


def auc_ci(df, col, sign=1.0):
    y = (df.cls == 1).astype(int).values
    x = sign * df[col].values
    auc = roc_auc_score(y, x)
    keys = list(df.groupby(["protein", "resnum"]).groups.items())
    idx_by = [np.asarray(v) for _, v in keys]
    pos = {k: i for i, k in enumerate(df.index)}
    idx_by = [np.array([pos[i] for i in v]) for v in idx_by]
    boots = []
    for _ in range(NBOOT):
        pick = rng.integers(0, len(idx_by), len(idx_by))
        ii = np.concatenate([idx_by[p] for p in pick])
        yy = y[ii]
        if yy.min() == yy.max():
            continue
        boots.append(roc_auc_score(yy, x[ii]))
    return auc, np.percentile(boots, 2.5), np.percentile(boots, 97.5), int(y.sum()), int(len(y) - y.sum())


res = {}
frames = {}
for struct in ["primary", "S1"]:
    parts = []
    for prot in SETS:
        df, n_parse, n_mm = load(prot, struct)
        res[f"{prot}_{struct}_parsed_missense_with_class"] = n_parse
        res[f"{prot}_{struct}_wt_mismatch_excluded"] = n_mm
        parts.append(df)
    frames[struct] = pd.concat(parts, ignore_index=True)

prim = frames["primary"]
P = prim[(prim.plddt >= 70) & prim.cls.isin([1, 4])].copy()
for name, sub in [("pooled", P)] + [(p, P[P.protein == p]) for p in SETS]:
    a, lo, hi, npos, nneg = auc_ci(sub, "ddG")
    res[f"primary_AUC_ddG_{name}"] = dict(auc=round(a, 4), ci95=[round(lo, 4), round(hi, 4)], n_low=npos, n_wtlike=nneg)
    a, lo, hi, _, _ = auc_ci(sub, "rsa", sign=-1.0)
    res[f"primary_AUC_burial_{name}"] = dict(auc=round(a, 4), ci95=[round(lo, 4), round(hi, 4)])

g1 = res["primary_AUC_ddG_pooled"]["auc"] >= 0.70 and all(res[f"primary_AUC_ddG_{p}"]["auc"] >= 0.65 for p in SETS)
res["G1_pass"] = bool(g1)

y = (P.cls == 1).astype(int).values
fpr, tpr, thr = roc_curve(y, P.ddG.values)
j = tpr - fpr
k = int(np.argmax(j))
T = float(thr[k])
res["T_star"] = round(T, 4)
res["T_star_sens"] = round(float(tpr[k]), 4)
res["T_star_spec"] = round(float(1 - fpr[k]), 4)
res["T_star_youdenJ"] = round(float(j[k]), 4)
res["calib_low_ddG_quartiles"] = [round(float(q), 3) for q in np.percentile(P[P.cls == 1].ddG, [25, 50, 75])]
res["calib_wtlike_ddG_quartiles"] = [round(float(q), 3) for q in np.percentile(P[P.cls == 4].ddG, [25, 50, 75])]
res["calib_prior_low_fraction"] = round(float(y.mean()), 4)

# secondary analyses (reported, not gates)
S1 = frames["S1"]
sec_all = S1[S1.cls.isin([1, 4])]
a, lo, hi, npos, nneg = auc_ci(sec_all, "ddG")
res["secondary_AUC_ddG_allresidues_S1"] = dict(auc=round(a, 4), ci95=[round(lo, 4), round(hi, 4)], n_low=npos, n_wtlike=nneg)
sec_pr = prim[prim.cls.isin([1, 4])]
a, lo, hi, npos, nneg = auc_ci(sec_pr, "ddG")
res["secondary_AUC_ddG_allresidues_primary(pLDDT>=50)"] = dict(auc=round(a, 4), ci95=[round(lo, 4), round(hi, 4)], n_low=npos, n_wtlike=nneg)
s12 = prim[prim.plddt >= 70].copy()
s12["cls"] = np.where(s12.cls.isin([1, 2]), 1, 4)
a, lo, hi, npos, nneg = auc_ci(s12, "ddG")
res["secondary_AUC_ddG_cls12_vs_34_primary"] = dict(auc=round(a, 4), ci95=[round(lo, 4), round(hi, 4)], n_low=npos, n_wtlike=nneg)

P.to_csv(OUT / "calibration_primary_set.csv", index=False)
json.dump(res, open(OUT / "calibration.json", "w"), indent=1)
print(json.dumps(res, indent=1))
