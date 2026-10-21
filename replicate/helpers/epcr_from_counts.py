"""Re-derive the submitted EPCR column from the published rank counts, using nothing but this repository.

This is a SECOND implementation of section 8 of PRE_REG_SPIKEIN_EPCR.md, written from the pre-registration text.
It does not import or call analyze.py, which is the implementation that produced the submitted vector; the point
is to check that vector against the rule independently. Inputs are the counts published in
preregistration/spikein/summary.json, which ships, so this needs no data of any kind.

The rule, section 8: for each rank r in 1..10 take the share of primary-stratum trials whose causal landed at
rank r, smooth it as (k_r + 0.5)/(N + 1), enforce monotonic non-increase by isotonic regression (pool adjacent
violators), then subtract 1e-5 per rank and round, widening the number of decimals until every value lies in
(0, 1] and the vector is strictly decreasing.

Usage (by the harness only): epcr_from_counts.py <repository root>
"""
import json
import os
import sys


def smooth(counts, n):
    return [(counts[r] + 0.5) / (n + 1) for r in range(1, 11)]


def isotonic(values):
    """Pool adjacent violators: the closest non-increasing sequence in least squares."""
    blocks = []
    for v in values:
        blocks.append([v, 1])
        while len(blocks) > 1 and blocks[-2][0] < blocks[-1][0]:
            v2, w2 = blocks.pop()
            v1, w1 = blocks.pop()
            blocks.append([(v1 * w1 + v2 * w2) / (w1 + w2), w1 + w2])
    return [v for v, w in blocks for _ in range(w)]


def strictly_decreasing(iso, step=1e-5):
    dec = 6
    while True:
        e = [round(iso[i] - step * i, dec) for i in range(len(iso))]
        if all(0 < x <= 1 for x in e) and all(e[i] > e[i + 1] for i in range(len(e) - 1)):
            return e, dec
        dec += 1


def main():
    root = os.path.abspath(sys.argv[1])
    src = os.path.join(root, "preregistration", "spikein", "summary.json")
    s = json.load(open(src))
    a = s["strata"]["A"]["v4"]
    n = a["N"]
    counts = {int(k): v for k, v in a["dist_1_10"].items()}
    published = s["epcr"]["epcr"]

    sm = smooth(counts, n)
    iso = isotonic(sm)
    e, dec = strictly_decreasing(iso)

    print(f"primary stratum N: {n}")
    print(f"rank-1 to rank-10 counts: {[counts[r] for r in range(1, 11)]}")
    print(f"recomputed EPCR: {e}")
    print(f"published EPCR: {published}")
    print(f"decimals: {dec}")
    print(f"matches published: {e == published}")
    print(f"strictly decreasing: {all(e[i] > e[i + 1] for i in range(9))}")
    print(f"all in (0, 1]: {all(0 < x <= 1 for x in e)}")
    print(f"rank-1 recall from the counts: {counts[1] / n}")
    print(f"top-10 rate from the counts: {sum(counts[r] for r in range(1, 11)) / n}")


if __name__ == "__main__":
    main()
