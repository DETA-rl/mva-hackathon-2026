"""PRE-REG-R2A: BUBR1 features F1-F3 and the pre-registered decision rule. Local only.

Usage: python -I bubr1_decide.py <work_dir>
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from Bio.PDB import PDBParser

W = Path(sys.argv[1])
OUT = W / "out"
CAL = json.load(open(OUT / "calibration.json"))
T = CAL["T_star"]
CALSET = pd.read_csv(OUT / "calibration_primary_set.csv")
PL = {int(k): v for k, v in json.load(open(W / "structures" / "plddt.json"))["O60566"].items()}

# child allele (local only) and published MVA1 kinase-domain missense alleles (UniProt O60566)
ALLELES = [("N", 1002, "K", "child"), ("I", 909, "T", "control_low_abundance"),
           ("L", 1012, "P", "control_low_abundance"), ("R", 814, "H", "MVA1_other"),
           ("L", 844, "F", "MVA1_other"), ("Q", 921, "H", "MVA1_other")]
DOMAINS = {"UniProt_Protein_kinase": (766, 1050), "CDD_cd14029": (750, 1045),
           "CATH_1.10.510.10": (782, 1042), "SSF56112_IPR011009": (791, 984)}
FUNC_RES = list(range(772, 781)) + [795, 882]  # UniProt ATP binding sites + active site
NEAR = 25

ssm = {s: pd.read_csv(OUT / f"ssm_O60566_{s}.csv") for s in ["primary", "S1", "S2"]}
rsa = {s: pd.read_csv(OUT / f"rsa_O60566_{s}.csv").set_index("resnum") for s in ["primary", "S1", "S2"]}
kin = ssm["primary"][(ssm["primary"].resnum.between(766, 1050)) & (ssm["primary"].wildtype != ssm["primary"].mutation)]

model = PDBParser(QUIET=True).get_structure("bubr1", W / "structures" / "O60566_S1.pdb")[0]["A"]


def heavy(res):
    return np.array([a.coord for a in res if a.element != "H"])


def min_dist(r1, r2):
    a, b = heavy(model[r1]), heavy(model[r2])
    return float(np.sqrt(((a[:, None, :] - b[None, :, :]) ** 2).sum(-1)).min())


def domain_pos(pos, start, end):
    if start <= pos <= end:
        return "inside", min(pos - start, end - pos)
    d = start - pos if pos < start else pos - end
    return ("near" if d <= NEAR else "far"), -d


low = CALSET[CALSET.cls == 1].ddG.values
wtl = CALSET[CALSET.cls == 4].ddG.values
rows = []
for wt, pos, mt, role in ALLELES:
    r = dict(allele=f"{wt}{pos}{mt}", role=role)
    for s in ["primary", "S1", "S2"]:
        hit = ssm[s][(ssm[s].resnum == pos) & (ssm[s].mutation == mt)]
        if len(hit):
            assert hit.wildtype.iloc[0] == wt, (s, pos, hit.wildtype.iloc[0])
            r[f"ddG_{s}"] = round(float(hit.ddG.iloc[0]), 3)
            r[f"destab_{s}"] = bool(hit.ddG.iloc[0] >= T)
        else:
            r[f"ddG_{s}"] = None
            r[f"destab_{s}"] = None
        r[f"rsa_{s}"] = round(float(rsa[s].loc[pos, "rsa"]), 3) if pos in rsa[s].index else None
        r[f"buried_{s}"] = (r[f"rsa_{s}"] < 0.25) if r[f"rsa_{s}"] is not None else None
    r["plddt"] = round(PL[pos], 2)
    r["plddt_mean_pm5"] = round(float(np.mean([PL[p] for p in range(pos - 5, pos + 6) if p in PL])), 2)
    for dn, (a, b) in DOMAINS.items():
        cls, dist = domain_pos(pos, a, b)
        r[f"F1_{dn}"] = f"{cls} ({dist:+d})"
    g = r["ddG_primary"]
    if g is not None:
        r["pct_in_kinase_domain_SSM"] = round(float((kin.ddG < g).mean() * 100), 1)
        cal_ge = CALSET[CALSET.ddG >= g]
        r["calib_frac_low_at_ge_ddG"] = round(float((cal_ge.cls == 1).mean()), 3) if len(cal_ge) else None
        r["calib_n_at_ge_ddG"] = int(len(cal_ge))
        r["pct_within_calib_low"] = round(float((low < g).mean() * 100), 1)
        r["pct_within_calib_wtlike"] = round(float((wtl < g).mean() * 100), 1)
    r["min_dist_to_ATP_or_active_site_A"] = round(min(min_dist(pos, f) for f in FUNC_RES), 2)
    r["nearest_func_res"] = min(FUNC_RES, key=lambda f: min_dist(pos, f))
    rows.append(r)

tab = pd.DataFrame(rows)
tab.to_csv(OUT / "bubr1_alleles.csv", index=False)
child = tab[tab.role == "child"].iloc[0].to_dict()
ctrl = tab[tab.role == "control_low_abundance"]

# decision rule, in the pre-registered order
log = []
G1 = CAL["G1_pass"]
G2 = bool(ctrl.destab_primary.all())
conf = child["plddt"] >= 70
F1_in = child["F1_UniProt_Protein_kinase"].split()[0] in ("inside", "near")
robust_destab = len({child["destab_primary"], child["destab_S1"], child["destab_S2"]}) == 1
robust_buried = len({child["buried_primary"], child["buried_S1"], child["buried_S2"]}) == 1
robust = robust_destab and robust_buried
func_surface = {"a_region_or_motif": False,  # UniProt Regions/Motifs: 152-185 KNL1, 368-393, 456-480, 111-118, 224-232
                "b_within_6A_of_binding_or_active_site": child["min_dist_to_ATP_or_active_site_A"] <= 6.0,
                "c_partner_contact_in_experimental_structure": False}  # no PDB entry resolves residues > 345
has_func = any(func_surface.values())
if not G1:
    outcome = "UNRESOLVED (non-informative: calibration bar not met)"
elif not G2:
    outcome = "UNRESOLVED (G2 failed: method does not call both published low-abundance alleles destabilising)"
elif not conf:
    outcome = "UNRESOLVED (pLDDT at 1002 < 70)"
elif child["destab_primary"] and F1_in and child["buried_primary"] and robust:
    outcome = "ABUNDANCE-LIKE"
elif (not child["destab_primary"]) and (not child["buried_primary"]) and has_func and robust:
    outcome = "FUNCTION-LIKE"
else:
    outcome = "UNRESOLVED (criteria not jointly met)"
decision = dict(T_star=T, G1_pass=G1, G2_pass=G2, plddt_1002_ge70=bool(conf), F1_inside_or_near=bool(F1_in),
                destab_primary=child["destab_primary"], buried_primary=child["buried_primary"],
                robust_destab=robust_destab, robust_buried=robust_buried, functional_surface=func_surface,
                outcome=outcome)
json.dump(decision, open(OUT / "decision.json", "w"), indent=1, default=bool)
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
print(tab.T.to_string())
print(json.dumps(decision, indent=1, default=bool))
print("kinase-domain SSM n =", len(kin), "median ddG", round(float(kin.ddG.median()), 3),
      "frac >= T*", round(float((kin.ddG >= T).mean()), 3))
print("context distances (A): 1002-1008", round(min_dist(1002, 1008), 2), "1002-909", round(min_dist(1002, 909), 2),
      "1002-1012", round(min_dist(1002, 1012), 2))
