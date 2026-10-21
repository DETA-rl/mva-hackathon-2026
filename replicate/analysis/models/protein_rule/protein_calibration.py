"""AUC and stratified percentile bootstrap (2,000, seed 1) for each protein model on the rule-compliant
missense control pool, per CALIBRATION_RULE.md section 2. Damage orientation: ESM = -LLR; AlphaMissense as given.
Also reports the child's candidate missense damage and its percentile among controls (only if the model passes).
Usage: protein_calibration.py <scores.tsv>
"""
import csv
import random
import sys

rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
ctrl = [r for r in rows if r["label"] in ("0", "1")]
child = [r for r in rows if r["label"] not in ("0", "1")][0]


def auc(P, N):
    s = 0.0
    for p in P:
        for n in N:
            s += 1.0 if p > n else (0.5 if p == n else 0.0)
    return s / (len(P) * len(N))


MODELS = [("ESM-1v", "esm1v_llr", -1.0), ("ESM-2", "esm2_llr", -1.0), ("AlphaMissense", "am", 1.0)]
for name, col, sign in MODELS:
    P = [sign * float(r[col]) for r in ctrl if r["label"] == "1" and r[col] not in ("", "None")]
    N = [sign * float(r[col]) for r in ctrl if r["label"] == "0" and r[col] not in ("", "None")]
    a = auc(P, N)
    random.seed(1)
    bs = sorted(auc([random.choice(P) for _ in P], [random.choice(N) for _ in N]) for _ in range(2000))
    lo, hi = bs[49], bs[1949]
    if lo > 0.7:
        verdict = "INFORMATIVE"
    elif lo >= 0.6:
        verdict = "EXPLORATORY (lower bound 0.6 to 0.7)"
    else:
        verdict = "NOT USED (lower bound below 0.6)"
    print(f"{name}: nP={len(P)} nB={len(N)} AUC={a:.3f} CI=[{lo:.3f},{hi:.3f}] -> {verdict}")
    if lo > 0.6:
        cv = sign * float(child[col]) if child[col] not in ("", "None") else None
        if cv is not None:
            allv = [sign * float(r[col]) for r in ctrl if r[col] not in ("", "None")]
            pct = sum(1 for v in allv if v <= cv) / len(allv)
            print(f"   child candidate_missense damage={cv:.4f} percentile among {len(allv)} controls={pct:.3f}")
    else:
        print("   child value not reported (model not used)")
