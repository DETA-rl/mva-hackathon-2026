# H08: chromosome-level depth from sampled 1 Mb bins (count of alignments per bin). Read-only. Normalised to autosome median.
import pysam, random, statistics, os, json
BAM = os.environ["REPL_BAM"]
OUT = os.environ["REPL_OUT"] + "/h08_depth_sampled.json"
rng = random.Random(7)
f = pysam.AlignmentFile(BAM, "rb")
lens = dict(zip(f.references, f.lengths))
res = {}
for c in [str(i) for i in range(1, 23)] + ["X"]:
    name = "chr" + c
    L = lens[name]
    vals = []
    for _ in range(12):
        s = rng.randrange(5_000_000, L - 6_000_000)
        vals.append(f.count(name, s, s + 1_000_000))
    res[c] = vals
f.close()
auto = [v for c, vs in res.items() if c != "X" for v in vs]
med_auto = statistics.median(auto)
summary = {c: round(statistics.median(vs) / med_auto, 3) for c, vs in res.items()}
json.dump({"bins_per_chrom": 12, "bin_size": 1000000, "median_autosome_count": med_auto, "ratio_to_autosome_median": summary}, open(OUT, "w"), indent=1)
for c in summary: print(c, summary[c])
