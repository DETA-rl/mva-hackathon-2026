# Analysis under PRE_REG_ROWMAP.md section 8. Reads trials_rowmap.tsv and sanity_rowmap.json; writes summary_rowmap.json.
import collections, json, os
import numpy as np
from scipy.stats import beta
R = os.path.expanduser("~/Documents/HACKATON/_private/agent_out/rowmap/")
RULES = ["R0", "P1", "P2", "P3", "P4", "P5"]; CONS = ["C1", "C2", "C3"]
COMBOS = [(r, c) for r in RULES for c in CONS]
SIMPLE_R = {"R0": 0, "P1": 1, "P2": 2, "P5": 3, "P3": 4, "P4": 5}; SIMPLE_C = {"C1": 0, "C2": 1, "C3": 2}
B = 10000; MARGIN = 2.0; NCOMP = 17
LO_G, HI_G = 100 * 0.05 / NCOMP / 2, 100 * (1 - 0.05 / NCOMP / 2)
trials = collections.OrderedDict()  # (stratum, tid) -> {"gene", "gtype", combo -> (pts, fmax, r1, crow)}
for l in open(R + "trials_rowmap.tsv"):
    f = l.rstrip("\n").split("\t")
    if f[0] == "stratum": continue
    t = trials.setdefault((f[0], f[1]), {"gene": f[2], "gtype": f[3], "d": f[4], "hit_rank": f[6], "dc": int(f[9])})
    t[(f[10], f[11])] = (float(f[12]), float(f[13]), f[16] == "True", f[17] == "True")
def arr(keys, j):
    return np.array([[trials[k][c][j] for c in COMBOS] for k in keys], dtype=float)
def boot(groups, j):
    """groups: list of trial-key lists (one per stratum). Stratified gene-cluster bootstrap of combo means."""
    rng = np.random.default_rng(1)
    parts = []
    for keys in groups:
        genes = sorted({trials[k]["gene"] for k in keys}); gi = {g: i for i, g in enumerate(genes)}
        X = arr(keys, j); gs = np.zeros((len(genes), len(COMBOS))); gc = np.zeros(len(genes))
        for row, k in zip(X, keys): gs[gi[trials[k]["gene"]]] += row; gc[gi[trials[k]["gene"]]] += 1
        parts.append((len(genes), gs, gc))
    tot = np.zeros((B, len(COMBOS))); n = np.zeros(B)
    for b in range(B):
        for G, gs, gc in parts:
            w = np.bincount(rng.integers(0, G, G), minlength=G)
            tot[b] += w @ gs; n[b] += w @ gc
    return tot / n[:, None]
def jeff(k, n): return [float(x) for x in beta.ppf([0.025, 0.975], k + 0.5, n - k + 0.5)]
def summarize(groups, gate=False):
    keys = [k for g in groups for k in g]
    out = {"N": len(keys), "n_genes": len({trials[k]["gene"] for k in keys}), "combos": {}}
    P = arr(keys, 0); F = arr(keys, 1); R1 = arr(keys, 2); CR = arr(keys, 3)
    bp = boot(groups, 0); bf = boot(groups, 1)
    i0 = COMBOS.index(("R0", "C1"))
    for i, (r, c) in enumerate(COMBOS):
        d = P[:, i] - P[:, i0]; db = bp[:, i] - bp[:, i0]
        e = {"points": float(P[:, i].mean()), "points_ci": [float(x) for x in np.percentile(bp[:, i], [2.5, 97.5])],
             "fmax": float(F[:, i].mean()), "fmax_ci": [float(x) for x in np.percentile(bf[:, i], [2.5, 97.5])],
             "row1_exact": float(R1[:, i].mean()), "row1_exact_jeffreys": jeff(R1[:, i].sum(), len(keys)),
             "causal_row_exact": float(CR[:, i].mean()),
             "delta": float(d.mean()), "delta_ci95": [float(x) for x in np.percentile(db, [2.5, 97.5])],
             "wins": int((d > 0).sum()), "losses": int((d < 0).sum()),
             "pts_dist": dict(collections.Counter(P[:, i].tolist()))}
        if gate: e["delta_ci_gate"] = [float(x) for x in np.percentile(db, [LO_G, HI_G])]
        out["combos"][f"{r}x{c}"] = e
    return out
by_stratum = collections.defaultdict(list)
for k in trials: by_stratum[k[0]].append(k)
S = {"strata": {}}
PRIM = [by_stratum["A-CH-dec"], by_stratum["E-CH-dec"]]
S["PRIM"] = summarize(PRIM, gate=True)
for s, keys in by_stratum.items(): S["strata"][s] = summarize([keys])
for s in ("A-CH-dec", "E-CH-dec"):
    for d in ("1", "2"):
        S["strata"][f"{s}-d{d}"] = summarize([[k for k in by_stratum[s] if trials[k]["d"] == d]])
def decide(pool):
    sums = {c: sum(trials[k][c][0] * 2 for k in PRIM[0] + PRIM[1]) for c in pool}
    w = min(pool, key=lambda c: (-sums[c], SIMPLE_C[c[1]], SIMPLE_R[c[0]]))
    e = S["PRIM"]["combos"][f"{w[0]}x{w[1]}"]
    dA = S["strata"]["A-CH-dec"]["combos"][f"{w[0]}x{w[1]}"]["delta"]; dE = S["strata"]["E-CH-dec"]["combos"][f"{w[0]}x{w[1]}"]["delta"]
    a = e["delta"] >= MARGIN; b = e["delta_ci_gate"][0] > 0; c = dA >= 0 and dE >= 0
    if w == ("R0", "C1"): verdict = "keep R0xC1 (R0xC1 is the top combination)"
    elif a and b and c: verdict = f"adopt {w[0]}x{w[1]}"
    elif a: verdict = "keep R0xC1 (inconclusive: margin met, gate (b) or (c) failed)"
    else: verdict = "keep R0xC1 (no material gain: Delta_W < margin)"
    cross = {s: S["strata"][s]["combos"][f"{w[0]}x{w[1]}"]["delta"] for s in ("A-hid-dec", "A-HOM-dec", "E-HOM-dec", "A-BUB-dec") if s in S["strata"]}
    return {"winner": f"{w[0]}x{w[1]}", "delta": e["delta"], "gate_ci": e["delta_ci_gate"], "delta_A": dA, "delta_E": dE,
            "a_margin": a, "b_gate_ci_above_0": b, "c_both_strata_ge_0": c, "verdict": verdict,
            "cross_checks_delta": cross, "flags": [s for s, v in cross.items() if v <= -2.0 and s != "A-BUB-dec"]}
S["D_RM_1"] = decide(COMBOS)
S["D_RM_2"] = decide([c for c in COMBOS if c[1] == "C1"])
S["sanity"] = json.load(open(R + "sanity_rowmap.json"))
json.dump(S, open(R + "summary_rowmap.json", "w"), indent=1)
print(json.dumps({"D_RM_1": S["D_RM_1"], "D_RM_2": S["D_RM_2"]}, indent=1))
for name, blk in [("PRIM", S["PRIM"])] + [(s, S["strata"][s]) for s in sorted(S["strata"])]:
    print(f"\n== {name} N={blk['N']} genes={blk['n_genes']}")
    for c, e in blk["combos"].items():
        print(f"{c:7s} pts {e['points']:6.2f} [{e['points_ci'][0]:6.2f},{e['points_ci'][1]:6.2f}] fmax {e['fmax']:.3f} "
              f"r1 {e['row1_exact']:.3f} crow {e['causal_row_exact']:.3f} d {e['delta']:+6.2f} "
              f"[{e['delta_ci95'][0]:+6.2f},{e['delta_ci95'][1]:+6.2f}] w/l {e['wins']}/{e['losses']}"
              + (f" gate [{e['delta_ci_gate'][0]:+.2f},{e['delta_ci_gate'][1]:+.2f}]" if "delta_ci_gate" in e else ""))
