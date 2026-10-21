import pandas as pd, numpy as np
from scipy.stats import spearmanr
g = pd.read_csv("CRISPRGeneEffect.csv", index_col=0)
cols = {}
for sym in ["BUB1B","SIRT2","NAMPT","NMNAT1","BUB1","TRIP13","CEP57"]:
    hits = [c for c in g.columns if c.split(" (")[0]==sym]
    if hits: cols[sym]=g[hits[0]]
    else: print("missing", sym)
df = pd.DataFrame(cols).dropna()
print("n cell lines with all genes:", len(df))
print("Spearman vs BUB1B (rho, p) — hypothesis: SIRT2 positive if SIRT2 acts via BUBR1")
for s in df.columns:
    if s!="BUB1B":
        r,p = spearmanr(df["BUB1B"], df[s]); print(f"  {s:7s} rho={r:+.3f} p={p:.2e}")
print("Medians (gene effect):", df.median().round(3).to_dict())
