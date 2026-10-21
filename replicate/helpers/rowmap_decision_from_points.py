"""Re-apply the ROW-MAP decision rule to the published points distributions, using nothing but this repository.

This is a SECOND implementation of decision D-RM-1 of PRE_REG_ROWMAP.md, written from the pre-registration text.
It does not import analyze_rowmap.py, which is the implementation that produced the adopted rule. Inputs are the
per-combination points distributions published in preregistration/rowmap/summary_rowmap.json, which ships, so this
needs no data of any kind.

D-RM-1 as written: over the primary strata, the winner is the combination with the highest total rank points, ties
broken by the simpler construction and then the simpler rule. Adopt it over the draft R0 x C1 only if (a) its mean
gain is at least 2.0 points, (b) the lower end of the Bonferroni-adjusted bootstrap interval over 17 comparisons is
above 0, and (c) the gain is non-negative in both primary strata. Otherwise keep R0 x C1.

What this check can and cannot redo: the means, the gain and conditions (a) and (c) come straight from the
published distributions and per-stratum gains. Condition (b) is a stratified gene-cluster bootstrap over the
per-trial scores, which are not shipped, so its interval is read from the published result rather than recomputed;
the step note says so.

Usage (by the harness only): rowmap_decision_from_points.py <repository root>
"""
import json
import os
import sys

RULES = ["R0", "P1", "P2", "P3", "P4", "P5"]
CONS = ["C1", "C2", "C3"]
SIMPLE_R = {"R0": 0, "P1": 1, "P2": 2, "P5": 3, "P3": 4, "P4": 5}
SIMPLE_C = {"C1": 0, "C2": 1, "C3": 2}
MARGIN = 2.0
BASE = "R0xC1"


def mean_points(dist):
    n = sum(dist.values())
    return sum(float(p) * c for p, c in dist.items()) / n, n


def main():
    root = os.path.abspath(sys.argv[1])
    s = json.load(open(os.path.join(root, "preregistration", "rowmap", "summary_rowmap.json")))
    prim = s["PRIM"]["combos"]
    combos = [f"{r}x{c}" for r in RULES for c in CONS]
    missing = [c for c in combos if c not in prim]
    if missing:
        sys.exit(f"published result has no entry for: {missing}")

    means, totals, n_trials = {}, {}, None
    for c in combos:
        m, n = mean_points(prim[c]["pts_dist"])
        means[c] = m
        totals[c] = m * n
        n_trials = n if n_trials is None else n_trials
        if n != n_trials:
            sys.exit(f"{c}: {n} trials, expected {n_trials}")

    winner = min(combos, key=lambda c: (-totals[c], SIMPLE_C[c.split("x")[1]], SIMPLE_R[c.split("x")[0]]))
    delta = means[winner] - means[BASE]
    gate = prim[winner]["delta_ci_gate"]          # published: needs the per-trial scores, not shipped
    d_a = s["strata"]["A-CH-dec"]["combos"][winner]["delta"]
    d_e = s["strata"]["E-CH-dec"]["combos"][winner]["delta"]
    a = delta >= MARGIN
    b = gate[0] > 0
    c_ = d_a >= 0 and d_e >= 0
    if winner == BASE:
        verdict = f"keep {BASE} ({BASE} is the top combination)"
    elif a and b and c_:
        verdict = f"adopt {winner}"
    elif a:
        verdict = f"keep {BASE} (inconclusive: margin met, gate (b) or (c) failed)"
    else:
        verdict = f"keep {BASE} (no material gain: Delta_W < margin)"

    print(f"primary trials per combination: {n_trials}")
    print(f"mean rank points {BASE}: {means[BASE]:.2f}")
    print(f"mean rank points {winner}: {means[winner]:.2f}")
    print(f"winner: {winner}")
    print(f"delta vs {BASE}: {delta:.2f}")
    print(f"condition a, delta >= {MARGIN}: {a}")
    print(f"condition b, published gate interval lower bound {gate[0]:.2f} > 0: {b}")
    print(f"condition c, per-stratum deltas {d_a:.2f} and {d_e:.2f} both >= 0: {c_}")
    print(f"verdict: {verdict}")


if __name__ == "__main__":
    main()
