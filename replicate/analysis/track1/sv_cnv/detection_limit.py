# Per-chromosome depth noise from the child's BAM and the smallest whole-chromosome shift detectable. Read-only.
import pysam, random, statistics, json, os, math
BAM = os.environ["REPL_BAM"]
OUT = os.environ["REPL_OUT"] + "/detection_limit.json"
rng = random.Random(11)
f = pysam.AlignmentFile(BAM, "rb")
lens = dict(zip(f.references, f.lengths))
chroms = ["chr" + str(i) for i in range(1, 23)]
res = {}
for c in chroms:
    L = lens[c]
    vals = []
    for _ in range(40):
        s = rng.randrange(5_000_000, L - 6_000_000)
        vals.append(f.count(c, s, s + 1_000_000))
    m = statistics.mean(vals); sd = statistics.stdev(vals)
    res[c] = {"mean": m, "cv": sd / m}
f.close()
cvs = [v["cv"] for v in res.values()]
cv_med = statistics.median(cvs)
# Smallest whole-chromosome mean-depth shift detectable with 40 bins and a 3-SD rule: delta ~ 3 * cv / sqrt(40)
det = 3 * cv_med / math.sqrt(40)
out = {"bins_per_chrom": 40, "bin_size_bp": 1000000, "median_cv_1Mb": round(cv_med, 4),
       "min_detectable_whole_chrom_shift_fraction": round(det, 4),
       "per_chrom_cv": {c: round(v["cv"], 4) for c, v in res.items()}}
json.dump(out, open(OUT, "w"), indent=1)
print("median CV per 1 Mb bin:", round(cv_med, 4))
print("smallest whole-chromosome mean-depth shift detectable (3-SD rule, 40 bins):", round(det, 4), "=", round(100*det, 2), "%")
