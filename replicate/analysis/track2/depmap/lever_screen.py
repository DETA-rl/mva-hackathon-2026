"""PRE-REG-2026-10-20-B: DepMap 24Q4 lever screen against BUB1B (Spearman across cell lines, empirical genome null)."""
import csv
import random
import statistics

import numpy as np
from scipy.stats import spearmanr

DIR = __import__("os").environ["REPL_OUT"] + "/"
CAND = ["FBXW7", "AURKB", "PPP2R5A", "PPP2R5B", "PPP2R5C", "PPP2R5D", "PPP2R5E", "KIF18A",
        "ANAPC1", "ANAPC2", "ANAPC4", "ANAPC5", "ANAPC10", "ANAPC11", "ANAPC13", "ANAPC15",
        "ANAPC16", "CDC16", "CDC23", "CDC27", "UBE2C", "UBE2S", "MAD2L1BP"]
CTRL = ["SIRT2", "NAMPT", "NMNAT1", "ABL1", "SRC"]

with open(DIR + "CRISPRGeneEffect.csv") as f:
    rdr = csv.reader(f)
    header = next(rdr)
    rows = [r for r in rdr]

sym = [c.split(" (")[0] for c in header]
bub = sym.index("BUB1B")
M = np.full((len(rows), len(header)), np.nan)
for i, r in enumerate(rows):
    for j, v in enumerate(r):
        if j == 0 or v in ("", "NA"):
            continue
        M[i, j] = float(v)

B = M[:, bub]
ok = ~np.isnan(B)
genome_rhos = []
gene_rho = {}
for j in range(1, len(header)):
    v = M[:, j]
    m = ok & ~np.isnan(v)
    if m.sum() < 200:
        continue
    r, _ = spearmanr(B[m], v[m])
    gene_rho[sym[j]] = r
    genome_rhos.append(r)
genome_rhos = np.array(genome_rhos)


def pct(x):
    return float((genome_rhos < x).mean() * 100)


print(f"genes tested genome-wide: {len(genome_rhos)}; lines with BUB1B: {int(ok.sum())}")
print("gene | rho | genome percentile | label")
for g in CAND + CTRL:
    if g not in gene_rho:
        print(f"{g} | not tested")
        continue
    r = gene_rho[g]
    p = pct(r)
    if r >= 0.20 and p >= 95:
        lab = "CO-DEPENDENT"
    elif r < 0.10 or p < 50:
        lab = "not co-dependent"
    else:
        lab = "indeterminate"
    tag = " (control)" if g in CTRL else ""
    print(f"{g}{tag} | {r:+.3f} | {p:.1f} | {lab}")
print("genome-wide 95th percentile of rho:", round(float(np.percentile(genome_rhos, 95)), 3))
print("genome-wide median rho:", round(float(np.median(genome_rhos)), 3))
