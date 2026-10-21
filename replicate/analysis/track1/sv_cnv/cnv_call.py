# CNV rule v1 (amended, hash f15a869924beba1f233f0160ec1bd7e7b6afae0c39c0334eb58e082fe2f649fd). Read-only inputs.
import glob, os, statistics, math, json
D = os.environ["REPL_OUT"] + "/"
rows = []
for f in sorted(glob.glob(D + "chr*.tsv")):
    for line in open(f):
        if line.startswith("chrom"): continue
        c, s, e, n, gc, nf = line.rstrip("\n").split("\t")
        rows.append({"c": c, "s": int(s), "e": int(e), "n": int(n), "gc": float(gc), "nf": float(nf)})
rows = [r for r in rows if r["nf"] <= 0.10 and r["n"] > 0]
# GC quantile medians (20 bins of GC)
cuts = sorted(r["gc"] for r in rows)
q = [cuts[int(len(cuts) * i / 20)] for i in range(20)] + [1.01]
def qi(g):
    for i in range(20):
        if g < q[i + 1]: return i
    return 19
groups = {}
for r in rows: groups.setdefault(qi(r["gc"]), []).append(r["n"])
gmed = {k: statistics.median(v) for k, v in groups.items()}
for r in rows: r["cc"] = r["n"] / gmed[qi(r["gc"])]
gl = statistics.median(r["cc"] for r in rows)
for r in rows: r["ratio"] = r["cc"] / gl
out = {}
for c in sorted({r["c"] for r in rows}, key=lambda x: (len(x), x)):
    bins = [r for r in rows if r["c"] == c and r["s"] >= 5_000_000]
    L = max(r["e"] for r in rows if r["c"] == c)
    bins = [r for r in bins if r["e"] <= L - 5_000_000]
    rat = [r["ratio"] for r in bins]
    if len(rat) < 10: continue
    rc = statistics.median(rat)
    sd = statistics.stdev(rat); se = sd / math.sqrt(len(rat))
    exp = 0.5 if c == "chrX" else 1.0
    rel = rc / exp
    f = 2 * (rel - 1) if rel > 1 else 2 * (1 - rel)
    call = abs(f) >= 0.14 and abs(rc - exp) > 3 * se
    out[c] = {"r": round(rc, 4), "se": round(se, 4), "f": round(f, 4), "n_bins": len(rat), "call": bool(call)}
    print(f"{c:6s} r={rc:.4f} se={se:.4f} f={f:+.3f} bins={len(rat)} call={call}")
json.dump(out, open(os.environ["REPL_OUT"] + "/cnv_calls_v1.json", "w"), indent=1)
print("calls:", [c for c in out if out[c]["call"]])
