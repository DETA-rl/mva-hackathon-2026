# Ranking rule v2 (see RANKING_RULE_v2.md). Reads the consequence table on the box; writes derived summary to the project folder.
import collections, os, random, re
F = os.environ["REPL_OUT"] + "/child_exonic_consequence.tsv"
OUT = os.environ["REPL_OUT"] + "/ranking_v2_summary.tsv"
rows = [l.rstrip("\n").split("\t") for l in open(F)][1:]
seen = {}
for r in rows:
    seen.setdefault((r[0], r[1], r[2], r[3]), r)
CAND = {"nonsense", "frameshift", "stop_lost", "missense", "inframe_indel", "splice_region"}
W = {"nonsense": 3, "frameshift": 3, "stop_lost": 2, "splice_region": 2, "inframe_indel": 2, "missense": 1}
PARA = re.compile(r"^(HLA-|TAS2R|MUC|LILRA|LILRB|OR\d|ZNF|PRDM9|NBPF|SERPINA)")
PAR = [(10001, 2781479), (155701383, 156030895)]
def in_par(pos): return any(a <= pos <= b for a, b in PAR)
def is_hom(r): return r[4] in ("1/1", "1|1")
cands = [r for r in seen.values() if r[12] in CAND and r[9] in ("rare", "unobserved")]
# A. male X: exclude heterozygous non-PAR chrX calls
xfilter = [r for r in cands if r[0] == "X" and not in_par(int(r[1])) and not is_hom(r)]
cands = [r for r in cands if r not in xfilter]
print("A. male chrX het non-PAR calls excluded:", len(xfilter), "| genes:", sorted({r[11] for r in xfilter})[:12])
# B. cluster artifact: >=5 candidate calls in any 1 kb window in a gene, all homozygous
bygene = collections.defaultdict(list)
for r in cands: bygene[r[11]].append(r)
clustered = set()
for gene, calls in bygene.items():
    pos = sorted(int(c[1]) for c in calls)
    for i in range(len(pos)):
        win = [c for c in calls if pos[i] <= int(c[1]) <= pos[i] + 1000]
        if len(win) >= 5 and all(is_hom(c) for c in win):
            clustered.add(gene); break
print("B. cluster-artifact genes flagged and excluded:", sorted(clustered))
cands = [r for r in cands if r[11] not in clustered]
def rank(score_fn, labels):
    g = collections.defaultdict(float); nhom = collections.Counter(); ncalls = collections.Counter(); para = set()
    for r in labels:
        gene = r[11]
        if PARA.match(gene): para.add(gene); continue
        g[gene] += score_fn(r); ncalls[gene] += 1
        if is_hom(r): nhom[gene] += 1
    ok = {k: v for k, v in g.items() if v >= 3 or nhom[k] >= 1}
    return sorted(ok, key=lambda k: (-ok[k], k)), ok, nhom, ncalls
W_fn = lambda r: W[r[12]] * (1.5 if is_hom(r) else 1)
order, scores, nhom, ncalls = rank(W_fn, cands)
rankA, *_ = rank(lambda r: 1, cands)
rng = random.Random(1)
labs = [c[12] for c in cands]; rng.shuffle(labs)
shuf = []
for c, lab in zip(cands, labs):
    x = list(c); x[12] = lab; shuf.append(x)
orderB, *_ = rank(W_fn, shuf)
print("candidate calls after A and B:", len(cands))
print("ranked genes:", len(order))
def pos_of(lst, g): return lst.index(g) + 1 if g in lst else "not ranked"
print("BUB1B: rank v2", pos_of(order, "BUB1B"), "| ablation A", pos_of(rankA, "BUB1B"), "| shuffled baseline", pos_of(orderB, "BUB1B"))
print("top 20 under v2 (gene, score, calls, hom, ablationA rank):")
for i, g in enumerate(order[:20], 1):
    print(f"  {i:2d} {g:16s} score={scores[g]:5.1f} calls={ncalls[g]} hom={nhom[g]} rankA={pos_of(rankA, g)}")
print("top 10 shuffled baseline:", orderB[:10])
with open(OUT, "w") as fh:
    fh.write("gene\tscore_v2\tcalls\thom\trank_v2\trank_ablationA\n")
    for i, g in enumerate(order, 1):
        fh.write(f"{g}\t{scores[g]}\t{ncalls[g]}\t{nhom[g]}\t{i}\t{pos_of(rankA, g)}\n")
print("summary written:", OUT)
