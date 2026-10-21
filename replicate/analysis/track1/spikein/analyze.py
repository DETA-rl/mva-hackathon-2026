# Analysis under PRE_REG_SPIKEIN_EPCR.md sections 7-9. Reads trials.tsv / alleles.tsv / sanity.json; writes summary.json,
# tables.md and TRACK1_SUBMISSION_EPCR_PROPOSED.csv in the work dir.
import collections, csv, gzip, json, os, random, statistics, sys
from scipy.stats import beta, binom
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spikelib as L
W, D = L.W, L.D
trials = list(csv.DictReader(open(W + "trials.tsv"), delimiter="\t"))
alleles = list(csv.DictReader(open(W + "alleles.tsv"), delimiter="\t"))
san = json.load(open(W + "sanity.json"))
def jeff(k, n): return (float(beta.ppf(0.025, k + 0.5, n - k + 0.5)), float(beta.ppf(0.975, k + 0.5, n - k + 0.5)))
def rk(t): return int(t["hit_rank"]) if t["hit_rank"] != "none" else None
def sel(stratum, ver, genes=None):
    return [t for t in trials if t["stratum"] == stratum and t["version"] == ver and (genes is None or t["gene"] in genes)]
def metrics(ts):
    n = len(ts); r = [rk(t) for t in ts]
    dist = {i: sum(1 for x in r if x == i) for i in range(1, 11)}
    k1 = dist[1]; k10 = sum(dist.values())
    return {"N": n, "dist_1_10": dist, "rank_11plus": sum(1 for x in r if x and x > 10), "none": sum(1 for x in r if x is None),
            "p1": k1 / n if n else None, "p1_ci": jeff(k1, n) if n else None, "top3": sum(dist[i] for i in (1, 2, 3)) / n if n else None,
            "top10": k10 / n if n else None, "top10_ci": jeff(k10, n) if n else None,
            "full_row_at_rank1": sum(1 for t in ts if rk(t) == 1 and t["full_row"] == "True"),
            "full_row_any": sum(1 for t in ts if t["full_row"] == "True") / n if n else None}
out = {"sanity": san}
strata = ["A", "A-BUB", "B", "C1", "C2-HOM", "C2-CH", "D", "E"]
out["strata"] = {s: {v: metrics(sel(s, v)) for v in ("v4", "v3")} for s in strata}
# A-pc subset
pc = set()
with gzip.open(D + "gencode.v44.basic.annotation.gtf.gz", "rt") as f:
    for line in f:
        if line[0] == "#": continue
        c = line.split("\t", 8)
        if c[2] != "transcript": continue
        if 'transcript_type "protein_coding"' in c[8] and 'tag "Ensembl_canonical"' in c[8]:
            pc.add(c[8].split('gene_name "')[1].split('"')[0])
out["strata"]["A-pc"] = {v: metrics(sel("A", v, pc)) for v in ("v4", "v3")}
out["strata"]["A-CH"] = {v: metrics([t for t in sel("A", v) if t["gtype"] == "CH"]) for v in ("v4", "v3")}
out["strata"]["A-HOM"] = {v: metrics([t for t in sel("A", v) if t["gtype"] == "HOM"]) for v in ("v4", "v3")}
# per gene, A, v4 and v3
pg = collections.defaultdict(list)
for t in sel("A", "v4"): pg[t["gene"]].append(t)
pg3 = collections.defaultdict(list)
for t in sel("A", "v3"): pg3[t["gene"]].append(t)
out["A_per_gene"] = {g: {"pheno": L.pheno(g), "n": len(ts), "rank1_v4": sum(1 for t in ts if rk(t) == 1),
                         "rank1_v3": sum(1 for t in pg3[g] if rk(t) == 1), "top10_v4": sum(1 for t in ts if rk(t) and rk(t) <= 10),
                         "none_v4": sum(1 for t in ts if rk(t) is None),
                         "ranks_v4": dict(collections.Counter(t["hit_rank"] for t in ts))} for g, ts in sorted(pg.items())}
# D5 McNemar (paired by tid)
a4 = {t["tid"]: rk(t) == 1 for t in sel("A", "v4")}; a3 = {t["tid"]: rk(t) == 1 for t in sel("A", "v3")}
b = sum(1 for k in a4 if a4[k] and not a3[k]); c = sum(1 for k in a4 if a3[k] and not a4[k])
p_mc = min(1.0, 2 * float(binom.cdf(min(b, c), b + c, 0.5))) if b + c else 1.0
out["D5"] = {"v4_only": b, "v3_only": c, "mcnemar_exact_p": p_mc}
# EPCR (section 8)
mA = out["strata"]["A"]["v4"]; N = mA["N"]
s = [(mA["dist_1_10"][r] + 0.5) / (N + 1) for r in range(1, 11)]
blocks = []
for v in s:
    blocks.append([v, 1])
    while len(blocks) > 1 and blocks[-2][0] < blocks[-1][0]:
        v2, w2 = blocks.pop(); v1, w1 = blocks.pop(); blocks.append([(v1 * w1 + v2 * w2) / (w1 + w2), w1 + w2])
iso = [v for v, w in blocks for _ in range(w)]
dec = 6
while True:
    e = [round(iso[i] - 1e-5 * i, dec) for i in range(10)]
    if all(0 < x <= 1 for x in e) and all(e[i] > e[i + 1] for i in range(9)): break
    dec += 1
out["epcr"] = {"smoothed": s, "isotonic": iso, "epcr": e, "decimals": dec,
               "raw_ci": [jeff(mA["dist_1_10"][r], N) for r in range(1, 11)],
               "p_top10": mA["top10"], "p_top10_ci": mA["top10_ci"]}
# expected score (section 8)
def trial_score(t, vec):
    rows, truth = [], set()
    ntruth = len(t["alleles"].split(";"))
    for i, cell in enumerate(t["rows10"].split("|")):
        sz, tp = map(int, cell.split(":"))
        rows.append([("t", i, j) for j in range(tp)] + [("f", i, j) for j in range(sz - tp)])
        truth |= {("t", i, j) for j in range(tp)}
    truth |= {("m", j) for j in range(ntruth - len(truth))}
    return L.score(rows, vec, truth)
ordv = [(11 - r) / 11 for r in range(1, 11)]
TA = sel("A", "v4")
sc = [trial_score(t, e) for t in TA]; sco = [trial_score(t, ordv) for t in TA]
out["score"] = {"mean_points": statistics.mean(x[0] for x in sc), "mean_fmax": statistics.mean(x[1] for x in sc),
                "ordinal_vector_identical": sc == sco}
rng = random.Random(1); bp, bf = [], []
for _ in range(2000):
    idx = [rng.randrange(len(sc)) for _ in range(len(sc))]
    bp.append(statistics.mean(sc[i][0] for i in idx)); bf.append(statistics.mean(sc[i][1] for i in idx))
bp.sort(); bf.sort()
out["score"]["points_ci"] = (bp[49], bp[1949]); out["score"]["fmax_ci"] = (bf[49], bf[1949])
out["score"]["dist_points"] = dict(collections.Counter(x[0] for x in sc))
# allele diagnostics
def adiag(st, src=None):
    a = [x for x in alleles if x["stratum"] == st and (src is None or x["source"] == src)]
    return {"n": len(a), "extracted": sum(x["extracted"] == "True" for x in a),
            "consequence": dict(collections.Counter(x["consequence"] for x in a)),
            "freq_class": dict(collections.Counter(x["freq_class"] for x in a)),
            "candidate": sum(x["candidate"] == "True" for x in a),
            "clinvar_visible": sum(x["clinvar_plp_visible"] == "True" for x in a),
            "af_src": dict(collections.Counter(x["af_src"] for x in a))}
out["alleles"] = {st: adiag(st) for st in strata}
out["alleles"]["C2-CH synthetic"] = adiag("C2-CH", "synthetic"); out["alleles"]["C2-CH partner"] = adiag("C2-CH", "clinvar")
c_stop = [x for x in alleles if x["stratum"] == "C1" or (x["stratum"] in ("C2-HOM", "C2-CH") and x["source"] == "synthetic")]
out["D3"] = {"stop_alleles": len(c_stop), "labelled_stop_lost": sum(x["consequence"] == "stop_lost" for x in c_stop),
             "stop_allele_candidate": sum(x["candidate"] == "True" for x in c_stop)}
# decisions
p1A, loA = mA["p1"], mA["p1_ci"][0]
out["decisions"] = {
    "D1": "recall-robust" if (p1A >= 0.80 and loA >= 0.70) else ("not recall-robust" if p1A < 0.50 else "partly robust"),
    "D1_falsified": p1A < 0.80,
    "D2": "finds without ClinVar" if out["strata"]["B"]["v4"]["top10"] >= 0.50 else "depends on ClinVar",
    "D2_falsified": out["strata"]["B"]["v4"]["top10"] < 0.50,
    "D3_known_limitation_falsified": out["D3"]["labelled_stop_lost"] > 0,
    "D3_blind_spot": out["D3"]["stop_allele_candidate"] / out["D3"]["stop_alleles"] < 0.10,
    "D4_diff": p1A - out["strata"]["D"]["v4"]["p1"],
    "D4": "separates" if p1A - out["strata"]["D"]["v4"]["p1"] >= 0.20 else "does not separate",
    "D5": ("v4 improves" if (p1A - out["strata"]["A"]["v3"]["p1"] >= 0.05 and p_mc < 0.05) else
           ("harm" if (p1A < out["strata"]["A"]["v3"]["p1"] and p_mc < 0.05) else "no detectable difference")),
    "D6_gate": bool(san["S2_masked_equals_original_minus_bub1b"] and san["S3_bub1b_v4_rank"] == 1 and N >= 50),
    "D7": "conservative for BUB1B row" if out["strata"]["A-BUB"]["v4"]["p1"] >= p1A else "optimistic for BUB1B row"}
json.dump(out, open(W + "summary.json", "w"), indent=1)
# proposed CSV (draft untouched)
src = os.environ["REPL_DRAFT_CSV"]
rows = list(csv.DictReader(open(src)))
assert len(rows) == 10
with open(W + "TRACK1_SUBMISSION_EPCR_PROPOSED.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    for i, r in enumerate(rows):
        r = dict(r); r["epcr"] = f"{e[i]:.{dec}f}"; w.writerow(r)
print(json.dumps(out["decisions"], indent=1)); print(json.dumps(out["epcr"], indent=1)); print(json.dumps(out["score"], indent=1))
