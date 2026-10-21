# Ranking rule v1 (see RANKING_RULE_v1.md). Reads the consequence table on the box; writes a derived summary to the project folder.
import collections, os, random, re
F = os.environ["REPL_OUT"] + "/child_exonic_consequence.tsv"
OUT = os.environ["REPL_OUT"] + "/ranking_v1_summary.tsv"
rows = [l.rstrip("\n").split("\t") for l in open(F)][1:]
seen = {}
for r in rows:
    seen.setdefault((r[0], r[1], r[2], r[3]), r)
CAND = {"nonsense", "frameshift", "stop_lost", "missense", "inframe_indel", "splice_region"}
W = {"nonsense": 3, "frameshift": 3, "stop_lost": 2, "splice_region": 2, "inframe_indel": 2, "missense": 1}
PARA = re.compile(r"^(HLA-|TAS2R|MUC|LILRA|LILRB|OR\d|ZNF|PRDM9|NBPF|SERPINA)")
cands = [r for r in seen.values() if r[12] in CAND and r[9] in ("rare", "unobserved")]
def is_hom(r): return r[4] in ("1/1", "1|1")
def score_w(r): return W[r[12]] * (1.5 if is_hom(r) else 1)
def rank(score_fn, labels=None):
    g = collections.defaultdict(float); nhom = collections.Counter(); ncalls = collections.Counter(); paralog = set()
    for r in (cands if labels is None else labels):
        gene = r[11]
        if PARA.match(gene): paralog.add(gene); continue
        g[gene] += score_fn(r); ncalls[gene] += 1
        if is_hom(r): nhom[gene] += 1
    ok = {k: v for k, v in g.items() if v >= 3 or nhom[k] >= 1}
    order = sorted(ok, key=lambda k: (-ok[k], k))
    return order, ok, nhom, ncalls, paralog
order, scores, nhom, ncalls, paralog = rank(score_w)
rankA, scoreA, *_ = rank(lambda r: 1)
rng = random.Random(1)
shuffled_labels = [r[:12] + [r[12]] for r in cands]
labs = [c[12] for c in cands]; rng.shuffle(labs)
shuf = []
for c, lab in zip(cands, labs):
    x = list(c); x[12] = lab; shuf.append(x)
orderB, *_ = rank(score_w, shuf)
print("candidate calls (rare or unobserved, protein-altering):", len(cands))
print("paralog-family calls excluded from ranking:", sum(1 for r in cands if PARA.match(r[11])), "genes:", len(paralog))
print("ranked genes under rule v1:", len(order))
print("BUB1B rank under v1:", order.index("BUB1B") + 1 if "BUB1B" in order else "not ranked", "| under ablation A:", rankA.index("BUB1B") + 1 if "BUB1B" in rankA else "not ranked", "| under shuffled B:", orderB.index("BUB1B") + 1 if "BUB1B" in orderB else "not ranked")
print("top 25 under rule v1 (gene, score, calls, hom genes, rankA):")
for i, g in enumerate(order[:25], 1):
    ra = rankA.index(g) + 1 if g in rankA else "-"
    print(f"  {i:2d} {g:14s} score={scores[g]:5.1f} calls={ncalls[g]} hom={nhom[g]} rankA={ra}")
print("top 10 under shuffled labels (baseline):", orderB[:10])
with open(OUT, "w") as fh:
    fh.write("gene\tscore_v1\tcalls\thom\trank_v1\trank_ablationA\n")
    for i, g in enumerate(order, 1):
        ra = rankA.index(g) + 1 if g in rankA else "NA"
        fh.write(f"{g}\t{scores[g]}\t{ncalls[g]}\t{nhom[g]}\t{i}\t{ra}\n")
print("summary written:", OUT)
